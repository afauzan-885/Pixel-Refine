"""Dependency-free AV1 arithmetic/CDF coding primitives.

This module is the first executable layer for the general native AV1 path.  It
implements the Q15 range coder used by the AV1 reference implementation; it
does not yet encode an AV1 frame by itself.  Keeping the coder isolated makes
it possible to test the most error-sensitive part of the future tile encoder
without weakening the already-qualified fixed AV1 payload profile.

The implementation follows the non-adaptive Q15 path (``EC_PROB_SHIFT=6``
and ``EC_MIN_PROB=4``).  AV1 stores inverse CDF values (iCDF): values are
monotonically decreasing and the final value is zero.  CDF adaptation is
provided as an explicit helper but is not performed implicitly by the coder;
the first still-picture milestone uses immutable default CDF tables.

Only the Python standard library is used here.  External AV1 decoders remain
validation tools and are not runtime dependencies.
"""
from __future__ import annotations

from collections.abc import Sequence


CDF_PROB_BITS = 15
CDF_PROB_TOP = 1 << CDF_PROB_BITS
EC_PROB_SHIFT = 6
EC_MIN_PROB = 4
_WINDOW_BITS = 32
_WINDOW_MASK = (1 << _WINDOW_BITS) - 1
_ENCODER_WINDOW_BITS = 64
_ENCODER_WINDOW_MASK = (1 << _ENCODER_WINDOW_BITS) - 1
_MAX_SYMBOLS = 16
_MAX_LITERAL_BITS = 32
_LOTS_OF_BITS = 0x4000


class AV1EntropyError(ValueError):
    """Base error for malformed or unsupported entropy-coder input."""


class AV1EntropyMalformedError(AV1EntropyError):
    """A byte stream or CDF is malformed."""


class AV1EntropyStateError(AV1EntropyError):
    """An encoder or decoder operation is invalid for its current state."""


def aom_icdf(cumulative: int) -> int:
    """Convert an AV1 cumulative probability to the stored inverse CDF."""

    cumulative = int(cumulative)
    if cumulative < 0 or cumulative > CDF_PROB_TOP:
        raise ValueError("cumulative probability is outside Q15")
    return CDF_PROB_TOP - cumulative


def validate_icdf(icdf: Sequence[int]) -> tuple[int, ...]:
    """Validate and freeze one AV1 inverse-CDF table.

    The table contains one entry per symbol and must end in zero.  AV1's
    entropy code has a minimum-probability correction, so equal adjacent iCDF
    entries are accepted by the structural validator but are rejected if the
    resulting symbol interval is empty during coding.
    """

    try:
        values = tuple(int(item) for item in icdf)
    except (TypeError, ValueError) as exc:
        raise AV1EntropyMalformedError("iCDF must be an integer sequence") from exc
    if not 1 <= len(values) <= _MAX_SYMBOLS:
        raise AV1EntropyMalformedError(
            f"AV1 iCDF symbol count must be in [1, {_MAX_SYMBOLS}]"
        )
    if values[-1] != 0:
        raise AV1EntropyMalformedError("AV1 iCDF must terminate at zero")
    previous = CDF_PROB_TOP
    for value in values:
        if value < 0 or value > CDF_PROB_TOP:
            raise AV1EntropyMalformedError("AV1 iCDF value is outside Q15")
        if value > previous:
            raise AV1EntropyMalformedError("AV1 iCDF must be monotonically decreasing")
        previous = value
    return values


def _ilog_nz(value: int) -> int:
    if value <= 0:
        raise AV1EntropyStateError("range must be positive")
    return int(value).bit_length()


def _propagate_carry(output: bytearray, offset: int) -> None:
    if offset < 0:
        raise AV1EntropyStateError("range-coder carry escaped the output buffer")
    while True:
        value = int(output[offset]) + 1
        output[offset] = value & 0xFF
        if value <= 0xFF:
            return
        offset -= 1
        if offset < 0:
            raise AV1EntropyStateError("range-coder carry escaped the output buffer")


class AV1RangeEncoder:
    """AV1-compatible Q15 range encoder for symbols and boolean bins."""

    __slots__ = ("_output", "_low", "_rng", "_cnt", "_finished")

    def __init__(self) -> None:
        self._output = bytearray()
        self._low = 0
        self._rng = 0x8000
        # The -9 offset is part of the reference byte-flushing schedule.
        self._cnt = -9
        self._finished = False

    @property
    def bytes_written(self) -> int:
        return len(self._output)

    @property
    def range(self) -> int:
        return self._rng

    def _require_open(self) -> None:
        if self._finished:
            raise AV1EntropyStateError("encoder has already been finalized")

    def _normalize(self, low: int, rng: int) -> None:
        if not 0 < rng <= 0xFFFF:
            raise AV1EntropyStateError("normalized AV1 range is outside 16 bits")
        d = 16 - _ilog_nz(rng)
        c = self._cnt
        s = c + d

        # This is the bounded equivalent of AOM's write_enc_data_to_out_buf:
        # emit ready bytes in big-endian order and propagate a carry backward.
        if s >= 40:
            num_bytes_ready = (s >> 3) + 1
            c += 24 - (num_bytes_ready << 3)
            output = low >> c
            low &= (1 << c) - 1 if c else 0
            carry_mask = 1 << (num_bytes_ready << 3)
            carry = output & carry_mask
            output &= carry_mask - 1
            if output >= 1 << (8 * num_bytes_ready):
                raise AV1EntropyStateError("range-coder output width overflow")
            self._output.extend(output.to_bytes(num_bytes_ready, "big"))
            if carry:
                _propagate_carry(self._output, len(self._output) - num_bytes_ready - 1)
            s = c + d - 24

        self._low = (low << d) & _ENCODER_WINDOW_MASK
        self._rng = rng << d
        self._cnt = s

    def encode_bool(self, value: int | bool, probability_one: int) -> None:
        """Encode one bin using Q15 probability of the value ``1``."""

        self._require_open()
        value = int(value)
        probability_one = int(probability_one)
        if value not in (0, 1):
            raise ValueError("AV1 boolean symbol must be 0 or 1")
        if not 0 < probability_one < CDF_PROB_TOP:
            raise ValueError("AV1 boolean probability must be in (0, 32768)")
        low = self._low
        rng = self._rng
        v = ((rng >> 8) * (probability_one >> EC_PROB_SHIFT) >> 1) + EC_MIN_PROB
        if value:
            low += rng - v
            rng = v
        else:
            rng -= v
        self._normalize(low, rng)

    def encode_symbol(self, symbol: int, icdf: Sequence[int]) -> None:
        """Encode one symbol using an AV1 inverse CDF table."""

        self._require_open()
        table = validate_icdf(icdf)
        symbol = int(symbol)
        nsyms = len(table)
        if symbol < 0 or symbol >= nsyms:
            raise ValueError("AV1 symbol is outside the supplied iCDF")
        fl = table[symbol - 1] if symbol else CDF_PROB_TOP
        fh = table[symbol]
        if fh > fl:
            raise AV1EntropyMalformedError("AV1 symbol interval is inverted")
        low = self._low
        rng = self._rng
        remaining = nsyms - 1
        if fl < CDF_PROB_TOP:
            upper = (
                ((rng >> 8) * (fl >> EC_PROB_SHIFT) >> 1)
                + EC_MIN_PROB * (remaining - (symbol - 1))
            )
            lower = (
                ((rng >> 8) * (fh >> EC_PROB_SHIFT) >> 1)
                + EC_MIN_PROB * (remaining - symbol)
            )
            low += rng - upper
            rng = upper - lower
        else:
            rng -= (
                ((rng >> 8) * (fh >> EC_PROB_SHIFT) >> 1)
                + EC_MIN_PROB * (remaining - symbol)
            )
        if rng <= 0:
            raise AV1EntropyMalformedError("AV1 symbol interval has zero range")
        self._normalize(low, rng)

    def encode_literal(self, value: int, bits: int) -> None:
        """Encode an AV1 MSB-first literal using half-probability bins."""

        self._require_open()
        value = int(value)
        bits = int(bits)
        if bits < 0 or bits > _MAX_LITERAL_BITS:
            raise ValueError("literal width is outside the supported range")
        if value < 0 or value >= (1 << bits):
            raise ValueError("literal does not fit the requested width")
        for shift in range(bits - 1, -1, -1):
            self.encode_bool((value >> shift) & 1, CDF_PROB_TOP // 2)

    def finish(self) -> bytes:
        """Finalize using the minimum AOM-compatible terminating interval."""

        self._require_open()
        low = self._low
        c = self._cnt
        s = c + 10
        mask = 0x3FFF
        end = ((low + mask) & ~mask) | (mask + 1)
        if s > 0:
            trailing_mask = (1 << (c + 16)) - 1
            while s > 0:
                value = (end >> (c + 16)) & 0xFFFF
                self._output.append(value & 0xFF)
                if value & 0x0100:
                    _propagate_carry(self._output, len(self._output) - 2)
                end &= trailing_mask
                s -= 8
                c -= 8
                trailing_mask >>= 8
        self._finished = True
        return bytes(self._output)


class AV1RangeDecoder:
    """Matching bounded decoder for :class:`AV1RangeEncoder`."""

    __slots__ = ("_data", "_offset", "_dif", "_rng", "_cnt", "_tell_offs")

    def __init__(self, data: bytes | bytearray | memoryview):
        try:
            self._data = memoryview(data).cast("B")
        except (TypeError, ValueError) as exc:
            raise AV1EntropyMalformedError("range input must be bytes-like") from exc
        if not self._data:
            raise AV1EntropyMalformedError("range input must not be empty")
        self._offset = 0
        # The reference AV1 reader seeds the difference window with all ones
        # in its top 31 bits.  This is the complement representation of the
        # encoder's low interval and is required for CDF symbol orientation.
        self._dif = (1 << (_WINDOW_BITS - 1)) - 1
        self._rng = 0x8000
        self._cnt = -15
        self._tell_offs = 10 - (_WINDOW_BITS - 8)
        self._refill()

    @property
    def bytes_read(self) -> int:
        return self._offset

    @property
    def range(self) -> int:
        return self._rng

    def _refill(self) -> None:
        dif = self._dif
        cnt = self._cnt
        shift = _WINDOW_BITS - 9 - (cnt + 15)
        while shift >= 0 and self._offset < len(self._data):
            # The complemented difference window is filled with XOR in the
            # AV1 reference reader (its initial high bits are all ones).
            dif ^= int(self._data[self._offset]) << shift
            cnt += 8
            self._offset += 1
            shift -= 8
        if self._offset >= len(self._data):
            self._tell_offs += _LOTS_OF_BITS - cnt
            cnt = _LOTS_OF_BITS
        self._dif = dif & _WINDOW_MASK
        self._cnt = cnt

    def _normalize(self, dif: int, rng: int) -> None:
        if not 0 < rng <= 0xFFFF:
            raise AV1EntropyMalformedError("decoded AV1 range is invalid")
        d = 16 - _ilog_nz(rng)
        self._cnt -= d
        # ``(dif + 1) << d) - 1`` is the reference refill-preserving form;
        # it keeps the implicit trailing-one termination bits in the window.
        self._dif = (((dif + 1) << d) - 1) & _WINDOW_MASK
        self._rng = rng << d
        if self._cnt < 0:
            self._refill()

    def decode_bool(self, probability_one: int) -> int:
        """Decode one bin using Q15 probability of the value ``1``."""

        probability_one = int(probability_one)
        if not 0 < probability_one < CDF_PROB_TOP:
            raise ValueError("AV1 boolean probability must be in (0, 32768)")
        dif = self._dif
        rng = self._rng
        v = ((rng >> 8) * (probability_one >> EC_PROB_SHIFT) >> 1) + EC_MIN_PROB
        boundary = v << (_WINDOW_BITS - 16)
        # The bool primitive's ``f`` is the probability of the zero-side
        # interval in the legacy AV1 Q15 helper.  This is opposite to the
        # public symbol value convention used by the surrounding API, so the
        # decoder returns zero when the complemented window is above the
        # boundary and one otherwise.
        if dif >= boundary:
            dif -= boundary
            rng -= v
            value = 0
        else:
            rng = v
            value = 1
        self._normalize(dif, rng)
        return value

    def decode_symbol(self, icdf: Sequence[int]) -> int:
        """Decode one symbol using an AV1 inverse CDF table."""

        table = validate_icdf(icdf)
        dif = self._dif
        rng = self._rng
        nsyms = len(table)
        # This is the same interval walk as AOM's
        # ``od_ec_decode_cdf_q15``.  The decoder stores the complemented
        # difference window, so the comparison is ``c < v`` and the selected
        # interval is [v, u), rather than the more familiar lower-bound walk
        # used by ordinary arithmetic decoders.  Keeping the official walk is
        # important for parity with bitstreams produced by libaom; a reversed
        # self-consistent walk can still pass local round-trip tests while
        # decoding every external AV1 symbol incorrectly.
        code = dif >> (_WINDOW_BITS - 16)
        previous = rng
        symbol = -1
        while True:
            upper = previous
            symbol += 1
            lower = (
                ((rng >> 8) * (table[symbol] >> EC_PROB_SHIFT) >> (7 - EC_PROB_SHIFT))
                + EC_MIN_PROB * (nsyms - 1 - symbol)
            )
            if not (code < lower):
                break
            if symbol >= nsyms - 1:
                raise AV1EntropyMalformedError("AV1 CDF decode did not select a symbol")
            previous = lower
        if lower >= upper:
            raise AV1EntropyMalformedError("AV1 CDF interval is empty")
        rng = upper - lower
        dif -= lower << (_WINDOW_BITS - 16)
        self._normalize(dif, rng)
        return symbol

    def decode_literal(self, bits: int) -> int:
        """Decode an AV1 MSB-first literal encoded with half-probability bins."""

        bits = int(bits)
        if bits < 0 or bits > _MAX_LITERAL_BITS:
            raise ValueError("literal width is outside the supported range")
        value = 0
        for _ in range(bits):
            value = (value << 1) | self.decode_bool(CDF_PROB_TOP // 2)
        return value


def update_icdf(icdf: Sequence[int], symbol: int, *, count: int = 0) -> tuple[tuple[int, ...], int]:
    """Apply the AV1 default CDF adaptation rule to an iCDF table.

    Returns ``(updated_icdf, updated_count)``.  The helper is deliberately
    separate from the coder so a still-picture encoder can freeze defaults and
    later enable adaptation only when its frame-header flags and decoder
    parity are implemented.
    """

    table = validate_icdf(icdf)
    symbol = int(symbol)
    count = int(count)
    if not 0 <= symbol < len(table):
        raise ValueError("symbol is outside the iCDF")
    if not 0 <= count <= 32:
        raise ValueError("CDF adaptation count must be in [0, 32]")
    rate = 4 + (count >> 4) + (len(table) > 4)
    updated = list(table)
    for index in range(len(table) - 1):
        if index < symbol:
            updated[index] += (CDF_PROB_TOP - updated[index]) >> rate
        else:
            updated[index] -= updated[index] >> rate
    return validate_icdf(tuple(updated)), min(32, count + 1)


def encode_symbols(symbols: Sequence[int], icdf: Sequence[int]) -> bytes:
    """Encode a finite symbol sequence with one immutable iCDF table."""

    encoder = AV1RangeEncoder()
    for symbol in symbols:
        encoder.encode_symbol(int(symbol), icdf)
    return encoder.finish()


def decode_symbols(data: bytes | bytearray | memoryview, count: int, icdf: Sequence[int]) -> tuple[int, ...]:
    """Decode exactly ``count`` symbols with one immutable iCDF table."""

    count = int(count)
    if count < 0:
        raise ValueError("symbol count must be non-negative")
    decoder = AV1RangeDecoder(data)
    return tuple(decoder.decode_symbol(icdf) for _ in range(count))


def av1_entropy_capability_report() -> dict[str, object]:
    """Describe the implemented entropy layer without claiming a frame encoder."""

    return {
        "codec": "AV1",
        "profile": "q15-range-coder-primitive",
        "native_runtime": True,
        "q15_range_coder": True,
        "cdf_symbol_coding": True,
        "boolean_coding": True,
        "literal_coding": True,
        "explicit_cdf_adaptation": True,
        "general_encoder": False,
        "runtime_dependencies": (),
        "external_decoder_validation_required": True,
    }


__all__ = [
    "CDF_PROB_BITS",
    "CDF_PROB_TOP",
    "EC_PROB_SHIFT",
    "EC_MIN_PROB",
    "AV1EntropyError",
    "AV1EntropyMalformedError",
    "AV1EntropyStateError",
    "AV1RangeEncoder",
    "AV1RangeDecoder",
    "aom_icdf",
    "validate_icdf",
    "update_icdf",
    "encode_symbols",
    "decode_symbols",
    "av1_entropy_capability_report",
]
