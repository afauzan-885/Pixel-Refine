"""Small, immutable subset of the default AV1 CDF tables.

This module deliberately contains table data only.  It is the narrow entropy
table boundary for the first native AV1 intra milestone and is not an AV1
frame encoder by itself.

The values are derived from the official AOM snapshot ``1389210``:

* ``av1/common/entropymode.c``: default LV_MAP probabilities;
* ``av1/common/txb_common.c``: probability-to-iCDF initialisation; and
* ``aom_dsp/prob.h`` / ``aom_dsp/entcode.h``: Q15 iCDF representation.

The supported build configuration is intentionally explicit:
``CONFIG_LV_MAP=1``, ``CONFIG_LV_MAP_MULTI=1`` and ``CONFIG_CTX1D=0``.
Only the luma (Y) ``TX_4X4`` context zero is included.  A caller asking for
another transform, plane, context, bit depth, or configuration is rejected
instead of receiving a plausible-looking but unverified default.

The tuples use AOM's in-memory CDF layout.  For a binary CDF this is
``(iCDF_boundary, iCDF_CDF_PROB_TOP, symbol_count)``; the last slot is the
mutable counter slot in libaom and is kept as zero here because these tables
are immutable defaults.

Only the Python standard library is used.
"""
from __future__ import annotations

from collections.abc import Sequence
from types import MappingProxyType


AOM_SOURCE_REF = "1389210"
AOM_ENTROPYMODE_SOURCE = (
    "https://aomedia.googlesource.com/aom/+/1389210/"
    "av1/common/entropymode.c"
)
AOM_TXB_SOURCE = (
    "https://aomedia.googlesource.com/aom/+/1389210/"
    "av1/common/txb_common.c"
)
AOM_PROB_SOURCE = (
    "https://aomedia.googlesource.com/aom/+/1389210/"
    "aom_dsp/prob.h"
)
AOM_ENTCODE_SOURCE = (
    "https://aomedia.googlesource.com/aom/+/1389210/"
    "aom_dsp/entcode.h"
)

CDF_PROB_BITS = 15
CDF_PROB_TOP = 1 << CDF_PROB_BITS
TX_4X4 = "TX_4X4"
PLANE_Y = "Y"
BIT_DEPTH_8 = 8

_SUPPORTED_CONFIG = MappingProxyType(
    {
        "CONFIG_LV_MAP": 1,
        "CONFIG_LV_MAP_MULTI": 1,
        "CONFIG_CTX1D": 0,
    }
)


class AV1CDFError(ValueError):
    """Base error for malformed or unsupported AV1 CDF requests."""


class AV1CDFValidationError(AV1CDFError):
    """Raised when an iCDF row or table shape is malformed."""


class AV1CDFUnsupportedContext(AV1CDFError):
    """Raised when a request falls outside the explicitly supported slice."""


def aom_icdf(cumulative: int) -> int:
    """Return AOM's stored inverse-CDF value for a Q15 cumulative value."""

    if isinstance(cumulative, bool) or not isinstance(cumulative, int):
        raise AV1CDFValidationError("cumulative probability must be an integer")
    if not 0 <= cumulative <= CDF_PROB_TOP:
        raise AV1CDFValidationError("cumulative probability is outside Q15")
    # OD_ICDF(x) in AOM's aom_dsp/entcode.h.
    return CDF_PROB_TOP - cumulative


def validate_icdf(
    icdf: Sequence[int], *, expected_symbols: int | None = None
) -> tuple[int, ...]:
    """Validate and freeze one AOM in-memory iCDF row.

    ``expected_symbols`` is the number of entropy symbols, not the number of
    stored integers.  AOM stores one boundary per symbol (the final boundary
    is zero for ``CDF_PROB_TOP``) and one counter slot, so a binary row has
    length three.
    Equal adjacent boundaries are accepted because a zero-probability symbol
    is structurally representable in the AOM tables.
    """

    if isinstance(icdf, (str, bytes, bytearray)) or not isinstance(icdf, Sequence):
        raise AV1CDFValidationError("iCDF must be an integer sequence")
    values = tuple(icdf)
    if len(values) < 3:
        raise AV1CDFValidationError("AOM iCDF must include a boundary and counter slot")
    if expected_symbols is not None:
        if isinstance(expected_symbols, bool) or not isinstance(expected_symbols, int):
            raise AV1CDFValidationError("expected_symbols must be an integer")
        if expected_symbols < 1 or len(values) != expected_symbols + 1:
            raise AV1CDFValidationError("iCDF row has an unexpected symbol count")

    normalized = []
    for value in values:
        if isinstance(value, bool) or not isinstance(value, int):
            raise AV1CDFValidationError("iCDF values must be integers")
        if not 0 <= value <= CDF_PROB_TOP:
            raise AV1CDFValidationError("iCDF value is outside Q15")
        normalized.append(value)

    if normalized[-1] != 0:
        raise AV1CDFValidationError("AOM iCDF counter slot must be zero")
    boundaries = normalized[:-1]
    if boundaries[-1] != 0:
        raise AV1CDFValidationError("AOM iCDF must terminate at zero")

    previous = CDF_PROB_TOP
    for value in boundaries:
        if value > previous:
            raise AV1CDFValidationError("iCDF must be monotonically decreasing")
        previous = value
    return tuple(normalized)


def _freeze_table(
    value: Sequence[object], expected_shape: tuple[int, ...], depth: int
) -> tuple[object, ...]:
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, Sequence):
        raise AV1CDFValidationError("CDF table has a non-sequence dimension")
    if len(value) != expected_shape[depth]:
        raise AV1CDFValidationError("CDF table has an unexpected shape")
    if depth == len(expected_shape) - 1:
        # One boundary is the terminal zero and one trailing slot is the
        # symbol counter, therefore symbols = stored_length - 1.
        return validate_icdf(value, expected_symbols=expected_shape[depth] - 1)
    return tuple(
        _freeze_table(item, expected_shape, depth + 1)  # type: ignore[arg-type]
        for item in value
    )


def validate_cdf_table(
    table: Sequence[object],
    expected_shape: Sequence[int],
    *,
    name: str = "CDF",
) -> tuple[object, ...]:
    """Validate exact nested shape and monotonic AOM iCDF leaves.

    The returned object is recursively tuple-frozen, which makes it safe to
    publish as a constant even when the input was a list supplied by a test or
    a future generator.
    """

    if isinstance(expected_shape, (str, bytes, bytearray)):
        raise AV1CDFValidationError(f"{name} shape must be an integer sequence")
    shape = tuple(expected_shape)
    if not shape or any(
        isinstance(dimension, bool)
        or not isinstance(dimension, int)
        or dimension < 1
        for dimension in shape
    ):
        raise AV1CDFValidationError(f"{name} shape must contain positive integers")
    try:
        frozen = _freeze_table(table, shape, 0)
    except AV1CDFValidationError as exc:
        raise AV1CDFValidationError(f"{name}: {exc}") from exc
    return frozen


# AOM source expressions for this slice (CONFIG_LV_MAP_MULTI=1):
#   txb_skip[TX_4X4][0] = 252       -> AOM_ICDF(128 * 252) = 512
#   dc_sign[Y][0]       = 125       -> AOM_ICDF(128 * 125) = 16768
#   eob_flag[TX_4X4][Y][0] = 220    -> AOM_ICDF(128 * 220) = 4608
#   eob_extra[...]      = 145       -> AOM_ICDF(128 * 145) = 14208
#   coeff_br[TX_4X4][Y][0][0] = 62 -> AOM_ICDF(128 * 62) = 24832
TXB_SKIP_CDF = ((512, 0, 0),)
DC_SIGN_CDF = ((16768, 0, 0),)
EOB_FLAG_CDF = ((4608, 0, 0),)
EOB_EXTRA_CDF = ((14208, 0, 0),)
COEFF_BR_CDF = ((24832, 0, 0),)

# coeff_base_cdf is the four-symbol LV_MAP_MULTI table.  For
# [TX_4X4][Y][context=0], entropymode.c provides nz_map=59, base[0]=139 and
# base[1]=118.  txb_common.c computes p with two integer >> 8 updates:
#   p0 = 59 * 128 = 7552
#   p1 = p0 + ((32768 - p0) * 139 >> 8) = 21243
#   p2 = p1 + ((32768 - p1) * 118 >> 8) = 26555
COEFF_BASE_CDF = ((25216, 11525, 6213, 0, 0),)


_TABLE_SHAPES = MappingProxyType(
    {
        "txb_skip": (1, 3),
        "dc_sign": (1, 3),
        "eob_flag": (1, 3),
        "eob_extra": (1, 3),
        "coeff_base": (1, 5),
        "coeff_br": (1, 3),
    }
)
_TABLE_SYMBOLS = MappingProxyType(
    {
        "txb_skip": 2,
        "dc_sign": 2,
        "eob_flag": 2,
        "eob_extra": 2,
        "coeff_base": 4,
        "coeff_br": 2,
    }
)
CDF_TABLES = MappingProxyType(
    {
        "txb_skip": TXB_SKIP_CDF,
        "dc_sign": DC_SIGN_CDF,
        "eob_flag": EOB_FLAG_CDF,
        "eob_extra": EOB_EXTRA_CDF,
        "coeff_base": COEFF_BASE_CDF,
        "coeff_br": COEFF_BR_CDF,
    }
)
SUPPORTED_TABLES = tuple(CDF_TABLES)
SUPPORTED_CONTEXT = (0,)


def _validate_builtin_tables() -> None:
    for name in SUPPORTED_TABLES:
        actual = validate_cdf_table(
            CDF_TABLES[name], _TABLE_SHAPES[name], name=name
        )
        if actual != CDF_TABLES[name]:
            raise AV1CDFValidationError(f"{name}: immutable table normalization changed data")


_validate_builtin_tables()


def get_av1_cdf(
    name: str,
    *,
    tx_size: str = TX_4X4,
    bit_depth: int = BIT_DEPTH_8,
    intra: bool = True,
    plane_type: str = PLANE_Y,
    context: int = 0,
    base_range_set: int = 0,
) -> tuple[int, ...]:
    """Return one supported immutable CDF row or fail closed.

    The API intentionally returns a row rather than pretending that the
    one-row subset is a complete frame-context table.
    """

    if name not in CDF_TABLES:
        raise AV1CDFUnsupportedContext(f"unsupported AV1 CDF table: {name!r}")
    if tx_size != TX_4X4:
        raise AV1CDFUnsupportedContext("only TX_4X4 is supported")
    if bit_depth != BIT_DEPTH_8:
        raise AV1CDFUnsupportedContext("only 8-bit AV1 is supported")
    if intra is not True:
        raise AV1CDFUnsupportedContext("only intra coding is supported")
    if plane_type != PLANE_Y:
        raise AV1CDFUnsupportedContext("only luma/Y plane context is supported")
    if context != 0:
        raise AV1CDFUnsupportedContext("only context index zero is supported")
    if base_range_set != 0:
        raise AV1CDFUnsupportedContext("only coeff_br base_range_set zero is supported")
    return CDF_TABLES[name][0]


def av1_cdf_capability_report() -> dict[str, object]:
    """Describe the exact supported subset without claiming full AV1 support."""

    return {
        "module": "av1_cdf_aot",
        "stdlib_only": True,
        "scope": "immutable-default-cdf-subset",
        "full_encoder": False,
        "profile": "AV1 intra, TX_4X4, 8-bit, luma/Y, context 0",
        "tx_size": TX_4X4,
        "bit_depth": BIT_DEPTH_8,
        "plane_type": PLANE_Y,
        "intra": True,
        "aom_source_ref": AOM_SOURCE_REF,
        "aom_config": dict(_SUPPORTED_CONFIG),
        "tables": SUPPORTED_TABLES,
        "table_shapes": tuple(
            (name, _TABLE_SHAPES[name]) for name in SUPPORTED_TABLES
        ),
        "table_symbols": tuple(
            (name, _TABLE_SYMBOLS[name]) for name in SUPPORTED_TABLES
        ),
        "supported_contexts": SUPPORTED_CONTEXT,
        "fail_closed": True,
        "runtime_dependencies": (),
    }


__all__ = (
    "AOM_ENTCODE_SOURCE",
    "AOM_ENTROPYMODE_SOURCE",
    "AOM_PROB_SOURCE",
    "AOM_SOURCE_REF",
    "AOM_TXB_SOURCE",
    "AV1CDFError",
    "AV1CDFUnsupportedContext",
    "AV1CDFValidationError",
    "BIT_DEPTH_8",
    "CDF_PROB_BITS",
    "CDF_PROB_TOP",
    "CDF_TABLES",
    "COEFF_BASE_CDF",
    "COEFF_BR_CDF",
    "DC_SIGN_CDF",
    "EOB_EXTRA_CDF",
    "EOB_FLAG_CDF",
    "PLANE_Y",
    "SUPPORTED_CONTEXT",
    "SUPPORTED_TABLES",
    "TXB_SKIP_CDF",
    "TX_4X4",
    "aom_icdf",
    "av1_cdf_capability_report",
    "get_av1_cdf",
    "validate_cdf_table",
    "validate_icdf",
)
