"""Small dependency-free bitstream and checksum primitives for image codecs.

The routines here intentionally use only the Python standard library.  They
are the bounded host-side companion to Taichi kernels that prepare symbols,
filters, predictors, and block data.
"""
from __future__ import annotations


class BitWriter:
    """Append bits in either JPEG/MSB or Deflate/LSB order."""

    __slots__ = ("_data", "_accumulator", "_count", "_lsb")

    def __init__(self, lsb_first: bool = False):
        self._data = bytearray()
        self._accumulator = 0
        self._count = 0
        self._lsb = bool(lsb_first)

    def write(self, value: int, count: int) -> None:
        if count < 0 or count > 32 or value < 0 or value >= (1 << count):
            raise ValueError("bit value does not fit requested width")
        if self._lsb:
            self._accumulator |= int(value) << self._count
            self._count += count
            while self._count >= 8:
                self._data.append(self._accumulator & 0xFF)
                self._accumulator >>= 8
                self._count -= 8
        else:
            self._accumulator = (self._accumulator << count) | int(value)
            self._count += count
            while self._count >= 8:
                shift = self._count - 8
                self._data.append((self._accumulator >> shift) & 0xFF)
                self._accumulator &= (1 << shift) - 1 if shift else 0
                self._count = shift

    def write_bytes_msb(self, data: bytes, bit_count: int | None = None) -> None:
        """Append an MSB-first byte slice without a Python call per bit.

        JPEG block payloads are usually not byte-aligned at block boundaries.
        This method keeps the carry bits in the writer while copying aligned
        runs directly into the output buffer.
        """
        if self._lsb:
            raise ValueError("write_bytes_msb requires an MSB-first writer")
        raw = memoryview(data).cast("B")
        count = len(raw) * 8 if bit_count is None else int(bit_count)
        if count < 0 or count > len(raw) * 8:
            raise ValueError("byte slice bit count is out of range")
        full_bytes, remainder = divmod(count, 8)
        if self._count == 0:
            self._data.extend(raw[:full_bytes])
        else:
            for index in range(full_bytes):
                combined = (self._accumulator << 8) | int(raw[index])
                total = self._count + 8
                shift = total - 8
                self._data.append((combined >> shift) & 0xFF)
                self._accumulator = combined & ((1 << shift) - 1 if shift else 0)
                self._count = shift
        if remainder:
            self.write(int(raw[full_bytes]) >> (8 - remainder), remainder)

    def align(self, fill: int = 0) -> None:
        if self._count:
            self.write((1 << (8 - self._count)) - 1 if fill else 0, 8 - self._count)

    def finish(self, fill: int = 0) -> bytes:
        self.align(fill)
        return bytes(self._data)

    @property
    def bit_count(self) -> int:
        return len(self._data) * 8 + self._count


class BitReader:
    """Bounded LSB/MSB reader used by internal round-trip tests."""

    __slots__ = ("_data", "_offset", "_lsb")

    def __init__(self, data: bytes, lsb_first: bool = False):
        self._data = memoryview(data)
        self._offset = 0
        self._lsb = bool(lsb_first)

    def read(self, count: int) -> int:
        if count < 0 or count > 32 or self._offset + count > len(self._data) * 8:
            raise ValueError("bitstream underflow")
        value = 0
        for local_bit in range(count):
            index, bit = divmod(self._offset, 8)
            current = (self._data[index] >> bit) & 1 if self._lsb else (self._data[index] >> (7 - bit)) & 1
            value = (value | (current << local_bit)) if self._lsb else ((value << 1) | current)
            self._offset += 1
        return value

    def align(self) -> None:
        """Skip padding up to the next byte boundary."""
        remainder = self._offset & 7
        if remainder:
            self._offset += 8 - remainder


class RbspWriter:
    """MSB-first writer for HEVC RBSP syntax elements.

    HEVC syntax uses MSB-first fixed-width fields, unsigned/signed
    Exp-Golomb codes, and ``rbsp_trailing_bits``.  Keeping this adapter
    separate from :class:`BitWriter` makes the codec-specific contract
    explicit while reusing the bounded byte accumulator.
    """

    __slots__ = ("_writer",)

    def __init__(self):
        self._writer = BitWriter(lsb_first=False)

    def write(self, value: int, count: int) -> None:
        self._writer.write(int(value), int(count))

    def write_bit(self, value: int) -> None:
        self.write(1 if value else 0, 1)

    def write_ue(self, value: int) -> None:
        value = int(value)
        if value < 0:
            raise ValueError("unsigned Exp-Golomb value must be non-negative")
        code_num = value + 1
        width = code_num.bit_length()
        self.write(0, width - 1)
        self.write(code_num, width)

    def write_se(self, value: int) -> None:
        value = int(value)
        code_num = -2 * value if value <= 0 else 2 * value - 1
        self.write_ue(code_num)

    def trailing_bits(self) -> None:
        self.write_bit(1)
        self._writer.align(0)

    def finish(self) -> bytes:
        return self._writer.finish(0)

    @property
    def bit_count(self) -> int:
        return self._writer.bit_count


class RbspReader:
    """Bounded reader for an already-unescaped HEVC RBSP payload."""

    __slots__ = ("_reader", "_total_bits")

    def __init__(self, data: bytes, *, bit_count: int | None = None):
        self._reader = BitReader(bytes(data), lsb_first=False)
        self._total_bits = len(data) * 8 if bit_count is None else int(bit_count)
        if self._total_bits < 0 or self._total_bits > len(data) * 8:
            raise ValueError("RBSP bit count is out of range")

    @property
    def bit_position(self) -> int:
        return self._reader._offset

    @property
    def remaining_bits(self) -> int:
        return self._total_bits - self._reader._offset

    def read(self, count: int) -> int:
        count = int(count)
        if count < 0 or count > 32 or count > self.remaining_bits:
            raise ValueError("RBSP bitstream underflow")
        return self._reader.read(count)

    def read_bit(self) -> int:
        return self.read(1)

    def read_ue(self) -> int:
        zeros = 0
        while self.remaining_bits and self.read_bit() == 0:
            zeros += 1
            if zeros > 31:
                raise ValueError("Exp-Golomb code is too long")
        if self.remaining_bits < zeros:
            raise ValueError("truncated Exp-Golomb code")
        suffix = self.read(zeros) if zeros else 0
        return ((1 << zeros) - 1) + suffix

    def read_se(self) -> int:
        code_num = self.read_ue()
        return -(code_num // 2) if code_num % 2 == 0 else (code_num + 1) // 2

    def require_trailing_bits(self) -> None:
        if self.remaining_bits <= 0 or self.read_bit() != 1:
            raise ValueError("missing rbsp_stop_one_bit")
        while self.remaining_bits:
            if self.read_bit() != 0:
                raise ValueError("non-zero rbsp_alignment_zero_bit")


def rbsp_escape(data: bytes) -> bytes:
    """Insert HEVC emulation-prevention bytes into an RBSP payload."""

    source = memoryview(data).cast("B")
    output = bytearray()
    zero_count = 0
    for value in source:
        if zero_count >= 2 and value <= 3:
            output.append(3)
            zero_count = 0
        output.append(int(value))
        zero_count = zero_count + 1 if value == 0 else 0
    return bytes(output)


def rbsp_unescape(data: bytes) -> bytes:
    """Remove only valid HEVC emulation-prevention bytes, rejecting malformed input."""

    source = memoryview(data).cast("B")
    output = bytearray()
    zero_count = 0
    index = 0
    while index < len(source):
        value = int(source[index])
        if value == 3 and zero_count >= 2:
            if index + 1 >= len(source) or int(source[index + 1]) > 3:
                raise ValueError("invalid HEVC emulation-prevention byte")
            index += 1
            value = int(source[index])
        output.append(value)
        zero_count = zero_count + 1 if value == 0 else 0
        index += 1
    return bytes(output)


def leb128_encode(value: int) -> bytes:
    """Encode an AV1 OBU unsigned LEB128 value with the 8-byte bound."""

    value = int(value)
    if value < 0 or value >= (1 << 56):
        raise ValueError("AV1 LEB128 value is outside the 56-bit bound")
    output = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        if value:
            output.append(byte | 0x80)
        else:
            output.append(byte)
            return bytes(output)


def leb128_decode(data: bytes, offset: int = 0) -> tuple[int, int]:
    """Decode one AV1 OBU LEB128 value and return ``(value, next_offset)``."""

    source = memoryview(data).cast("B")
    offset = int(offset)
    if offset < 0 or offset >= len(source):
        raise ValueError("truncated AV1 LEB128 value")
    value = 0
    for count in range(8):
        if offset + count >= len(source):
            raise ValueError("truncated AV1 LEB128 value")
        byte = int(source[offset + count])
        if count == 7 and (byte & 0x80):
            raise ValueError("AV1 LEB128 value exceeds eight bytes")
        value |= (byte & 0x7F) << (7 * count)
        if not (byte & 0x80):
            return value, offset + count + 1
    raise ValueError("unterminated AV1 LEB128 value")


def adler32(data: bytes) -> int:
    a, b = 1, 0
    for value in data:
        a = (a + value) % 65521
        b = (b + a) % 65521
    return (b << 16) | a


def crc32(data: bytes) -> int:
    crc = 0xFFFFFFFF
    for value in data:
        crc ^= value
        for _ in range(8):
            crc = (crc >> 1) ^ (0xEDB88320 if crc & 1 else 0)
    return crc ^ 0xFFFFFFFF


def reverse_bits(value: int, count: int) -> int:
    result = 0
    for _ in range(count):
        result = (result << 1) | (value & 1)
        value >>= 1
    return result


def canonical_codes(lengths: dict[int, int]) -> dict[int, tuple[int, int]]:
    """Return canonical MSB codes for ``symbol -> code length``."""
    code = 0
    previous = 0
    result: dict[int, tuple[int, int]] = {}
    for symbol, length in sorted(lengths.items(), key=lambda item: (item[1], item[0])):
        if length <= 0:
            continue
        code <<= length - previous
        result[symbol] = code, length
        code += 1
        previous = length
    return result


def packbits_encode(row: bytes) -> bytes:
    """Encode one TIFF PackBits row."""
    if not row:
        return b""
    out = bytearray()
    index = 0
    while index < len(row):
        run_end = index + 1
        while run_end < len(row) and row[run_end] == row[index] and run_end - index < 128:
            run_end += 1
        if run_end - index >= 3:
            out.append(257 - (run_end - index))
            out.append(row[index])
            index = run_end
            continue
        literal_start = index
        index = run_end
        while index < len(row) and index - literal_start < 128:
            probe = index + 1
            while probe < len(row) and row[probe] == row[index] and probe - index < 3:
                probe += 1
            if probe - index >= 3:
                break
            index = probe
        count = index - literal_start
        out.append(count - 1)
        out.extend(row[literal_start:index])
    return bytes(out)


def packbits_decode(data: bytes, expected_size: int) -> bytes:
    out = bytearray()
    index = 0
    while index < len(data) and len(out) < expected_size:
        header = data[index]
        index += 1
        signed = header if header < 128 else header - 256
        if signed >= 0:
            count = signed + 1
            if index + count > len(data):
                raise ValueError("truncated PackBits literal")
            out.extend(data[index:index + count])
            index += count
        elif signed != -128:
            count = 1 - signed
            if index >= len(data):
                raise ValueError("truncated PackBits repeat")
            out.extend(data[index:index + 1] * count)
            index += 1
    if len(out) != expected_size:
        raise ValueError("PackBits output length mismatch")
    return bytes(out)
