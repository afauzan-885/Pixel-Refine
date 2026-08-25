"""Pre-demosaic RAW reference stages and block-friendly orchestration.

These routines are the correctness oracle for the future Taichi kernels.  They
operate on :class:`RawMosaicFrame`, retain sensor headroom, and never turn a
RAW mosaic into RGB implicitly.  Native AOT adapters can replace individual
stages later without changing the frame contract or public call shape.
"""

from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Any, Callable, Mapping, Optional, Sequence

import numpy as np

from .raw_frame import RawMosaicFrame


def _dispatch_native_raw(graph: str, *, inputs, outputs, scalars):
    """Dispatch a RAW graph without silently changing backend.

    The reference functions in this module remain available for validation,
    but a caller asking for a native stage must receive an actionable error if
    the target-qualified ``compression_raw`` artifact is not installed.
    """

    try:
        from taichi_vision.taichi_algorithm.aot_api.research import _dispatch

        return _dispatch(
            "compression_raw",
            graph,
            inputs=inputs,
            outputs=outputs,
            scalars=scalars,
            plain_ndarray=False,
        )
    except Exception as exc:
        raise RuntimeError(
            f"native RAW graph {graph!r} is unavailable for the selected "
            "backend; compile compression_raw for the active target"
        ) from exc


@dataclass(frozen=True)
class RawFusionReport:
    shape: tuple[int, int]
    block_size: tuple[int, int]
    block_count: int
    elapsed_seconds: float
    output_dtype: str
    output_min: float
    output_max: float
    headroom_pixels: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "shape": self.shape,
            "block_size": self.block_size,
            "block_count": self.block_count,
            "elapsed_seconds": self.elapsed_seconds,
            "output_dtype": self.output_dtype,
            "output_min": self.output_min,
            "output_max": self.output_max,
            "headroom_pixels": self.headroom_pixels,
        }


@dataclass(frozen=True)
class RawFlowTileContract:
    """Explicit contract for a tiled flow runner on a RAW green guide.

    A dense optical-flow solver is not automatically tile-safe: pyramids,
    reductions, and iterative neighbourhoods can require global context.  A
    caller must therefore opt in with this small contract before
    :func:`raw_optical_flow_dng` partitions the guide.  ``halo`` is measured
    in half-resolution green-guide pixels, not full-resolution sensor pixels.

    The contract deliberately describes the *guide* domain.  It does not
    claim that a resulting flow can be applied directly to a mosaic; callers
    must still use :func:`phase_safe_integer_warp` (or a future phase-aware
    adapter) before moving RAW samples.
    """

    halo: int = 0
    guide_scale: int = 2
    domain: str = "green_guide"
    deterministic: bool = True
    phase_preserving: bool = True

    def __post_init__(self) -> None:
        halo = int(self.halo)
        if halo < 0:
            raise ValueError("RAW flow tile halo must be non-negative")
        if int(self.guide_scale) != 2:
            raise ValueError(
                "RAW flow tile contracts currently require a 2x CFA green guide"
            )
        if str(self.domain) != "green_guide":
            raise ValueError(
                "RAW flow tiles must be declared in the pre-demosaic green_guide domain"
            )
        if not bool(self.deterministic):
            raise ValueError("non-deterministic RAW flow tile runners are not supported")
        if not bool(self.phase_preserving):
            raise ValueError(
                "RAW flow tile runners must preserve CFA phase; use a phase-aware adapter"
            )
        object.__setattr__(self, "halo", halo)
        object.__setattr__(self, "guide_scale", 2)
        object.__setattr__(self, "domain", "green_guide")
        object.__setattr__(self, "deterministic", True)
        object.__setattr__(self, "phase_preserving", True)


def raw_flow_tile_contract(
    *,
    halo: int = 0,
    guide_scale: int = 2,
    domain: str = "green_guide",
    deterministic: bool = True,
    phase_preserving: bool = True,
):
    """Decorate a flow runner with an explicit RAW tile-safety contract.

    The decorator is additive and does not alter the runner signature.  It is
    intentionally opt-in; an undecorated runner remains on the established
    full-guide path.
    """

    contract = RawFlowTileContract(
        halo=halo,
        guide_scale=guide_scale,
        domain=domain,
        deterministic=deterministic,
        phase_preserving=phase_preserving,
    )

    def decorate(runner):
        setattr(runner, "__raw_flow_tile_contract__", contract)
        return runner

    return decorate


def _coerce_raw_flow_tile_contract(runner, contract):
    candidate = contract
    if candidate is None and runner is not None:
        candidate = getattr(runner, "__raw_flow_tile_contract__", None)
    if candidate is None:
        return None
    if isinstance(candidate, RawFlowTileContract):
        return candidate
    if isinstance(candidate, Mapping):
        return RawFlowTileContract(**dict(candidate))
    raise TypeError(
        "flow_contract must be RawFlowTileContract, a mapping, or None"
    )


def raw_alignment_guide(
    frame: RawMosaicFrame,
    *,
    apply_white_balance: bool = True,
) -> np.ndarray:
    """Return a CFA-phase-aware guide without demosaicing."""
    return frame.green_guide(apply_white_balance=apply_white_balance)


def raw_alignment_guide_dng(
    frame: Any,
    *,
    block_size: int | tuple[int, int] = 2048,
    apply_white_balance: bool = True,
    native: bool = False,
) -> np.ndarray:
    """Build a pre-demosaic green guide from a parsed DNG stream.

    Only native sensor tiles are materialized.  The guide itself is a compact
    float32 half-resolution field required by optical-flow solvers; no RGB
    interpolation or demosaic is introduced.  ``native=True`` dispatches
    each tile's normalization through the selected ``compression_raw`` AOT
    graph and keeps the final two-green pairing deterministic on the host.
    """
    if not hasattr(frame, "sample_region"):
        raise TypeError("raw_alignment_guide_dng expects a parsed DNGFrame")
    if isinstance(block_size, int):
        block_h = block_w = int(block_size)
    else:
        block_h, block_w = (int(block_size[0]), int(block_size[1]))
    if block_h <= 0 or block_w <= 0:
        raise ValueError("block_size must be positive")
    height, width = int(frame.height), int(frame.width)
    tags = dict(getattr(frame, "tags", {}) or {})
    cfa = tags.get(33422, (1, 0, 0, 1))
    if isinstance(cfa, (bytes, bytearray)):
        cfa = tuple(int(item) for item in cfa[:4])
    else:
        cfa = tuple(int(item) for item in cfa)
    green_indices = [index for index, value in enumerate(cfa) if int(value) == 1]
    if len(green_indices) != 2:
        green_indices = [0]
    phase = tuple(int(item) & 1 for item in tags.get("phase_origin", (0, 0)))
    first_plane_row, first_plane_col = divmod(int(green_indices[0]), 2)
    first_row_phase = (first_plane_row - phase[0]) & 1
    first_col_phase = (first_plane_col - phase[1]) & 1
    # ``RawMosaicFrame.green_guide`` crops the two green planes to their
    # common dimensions (odd sensor sizes can differ by one sample).
    plane_shapes = []
    for index in green_indices:
        plane_row, plane_col = divmod(int(index), 2)
        row_phase = (plane_row - phase[0]) & 1
        col_phase = (plane_col - phase[1]) & 1
        plane_shapes.append(
            (max(0, (height - row_phase + 1) // 2), max(0, (width - col_phase + 1) // 2))
        )
    guide_height = min(shape[0] for shape in plane_shapes)
    guide_width = min(shape[1] for shape in plane_shapes)
    plane_guides = [
        np.empty(shape, dtype=np.float32) for shape in plane_shapes
    ]

    for y0 in range(0, height, block_h):
        y1 = min(height, y0 + block_h)
        for x0 in range(0, width, block_w):
            x1 = min(width, x0 + block_w)
            tile = RawMosaicFrame.from_dng_region(frame, y0, y1, x0, x1)
            normalized = (
                raw_normalize_headroom_native(
                    tile, apply_white_balance=apply_white_balance
                )
                if native
                else tile.normalized_headroom(
                    apply_white_balance=apply_white_balance
                )
            )
            for plane_index, green_index in enumerate(green_indices):
                plane_row, plane_col = divmod(int(green_index), 2)
                local_row_phase = (plane_row - tile.phase_origin[0]) & 1
                local_col_phase = (plane_col - tile.phase_origin[1]) & 1
                tile_plane = normalized[
                    local_row_phase::2, local_col_phase::2
                ]
                global_row_phase = (plane_row - phase[0]) & 1
                global_col_phase = (plane_col - phase[1]) & 1
                absolute_first_row = y0 + local_row_phase
                absolute_first_col = x0 + local_col_phase
                target_y0 = (absolute_first_row - global_row_phase) // 2
                target_x0 = (absolute_first_col - global_col_phase) // 2
                target_y1 = min(
                    plane_guides[plane_index].shape[0],
                    target_y0 + tile_plane.shape[0],
                )
                target_x1 = min(
                    plane_guides[plane_index].shape[1],
                    target_x0 + tile_plane.shape[1],
                )
                if target_y0 < target_y1 and target_x0 < target_x1:
                    plane_guides[plane_index][target_y0:target_y1, target_x0:target_x1] = tile_plane[
                        : target_y1 - target_y0,
                        : target_x1 - target_x0,
                    ]
    guide = plane_guides[0][:guide_height, :guide_width]
    if len(plane_guides) > 1:
        guide = (guide + plane_guides[1][:guide_height, :guide_width]) * np.float32(0.5)
    return np.ascontiguousarray(guide, dtype=np.float32)


def raw_normalize_headroom_native(
    frame: RawMosaicFrame,
    *,
    y0: int = 0,
    y1: int | None = None,
    x0: int = 0,
    x1: int | None = None,
    apply_white_balance: bool = False,
) -> np.ndarray:
    """Run black/white normalization for one sensor tile in native AOT.

    Samples travel as contiguous ``i32`` so 8--16 bit RAW values are lossless
    even on graphics targets without a proven native ``u16`` ABI.  The output
    remains float32 headroom and is never upper-clamped.
    """

    y1 = frame.height if y1 is None else int(y1)
    x1 = frame.width if x1 is None else int(x1)
    y0, x0 = int(y0), int(x0)
    if not (0 <= y0 <= y1 <= frame.height and 0 <= x0 <= x1 <= frame.width):
        raise ValueError("RAW native normalization region is outside the frame")
    source = np.ascontiguousarray(frame.samples[y0:y1, x0:x1], dtype=np.int32)
    destination = np.empty(source.shape, dtype=np.float32)
    result = _dispatch_native_raw(
        "compression_raw_normalize_headroom_i32",
        inputs={
            "src": source,
            "black_level": np.asarray(frame.black_level, dtype=np.float32),
            "white_level": np.asarray(frame.white_level, dtype=np.float32),
            "white_balance": np.asarray(frame.white_balance, dtype=np.float32),
        },
        outputs={"dst": destination},
        scalars={
            "phase_y": int(frame.phase_origin[0]),
            "phase_x": int(frame.phase_origin[1]),
            "origin_y": y0,
            "origin_x": x0,
            "apply_white_balance": int(bool(apply_white_balance)),
            "exposure_scale": float(frame.exposure_scale),
        },
    )
    return np.ascontiguousarray(result, dtype=np.float32)


def raw_alignment_guide_native(
    frame: RawMosaicFrame,
    *,
    apply_white_balance: bool = True,
) -> np.ndarray:
    """Build the CFA guide from a native-normalized sensor frame.

    The normalization graph runs on the selected AOT backend.  The final
    two-green plane reduction is intentionally a tiny deterministic merge in
    the semantic layer so arbitrary CFA phase origins remain correct.
    """

    normalized = raw_normalize_headroom_native(
        frame, apply_white_balance=apply_white_balance
    )
    green_indices = [
        index for index, value in enumerate(frame.cfa_pattern) if int(value) == 1
    ]

    def plane(index: int) -> np.ndarray:
        plane_row, plane_col = divmod(int(index), 2)
        row_phase = (plane_row - frame.phase_origin[0]) & 1
        col_phase = (plane_col - frame.phase_origin[1]) & 1
        return normalized[row_phase::2, col_phase::2]

    if len(green_indices) != 2:
        return np.ascontiguousarray(plane(0), dtype=np.float32)
    first, second = (plane(index) for index in green_indices)
    height = min(first.shape[0], second.shape[0])
    width = min(first.shape[1], second.shape[1])
    return np.ascontiguousarray(
        (first[:height, :width] + second[:height, :width]) * np.float32(0.5),
        dtype=np.float32,
    )


def raw_weight_map(
    reference: np.ndarray,
    current: np.ndarray,
    *,
    noise_floor: float = 0.0,
    sensitivity: float = 1.0,
) -> np.ndarray:
    """Build a deterministic residual weight map in normalized RAW space."""
    ref = np.asarray(reference, dtype=np.float32)
    cur = np.asarray(current, dtype=np.float32)
    if ref.shape != cur.shape:
        raise ValueError("RAW weight-map inputs must have identical shapes")
    floor = max(0.0, float(noise_floor))
    scale = max(1e-6, float(sensitivity))
    residual = np.maximum(np.abs(cur - ref) - floor, 0.0)
    weights = 1.0 / (1.0 + residual * scale)
    return np.nan_to_num(weights, nan=0.0, posinf=0.0, neginf=0.0).astype(np.float32, copy=False)


def raw_weight_map_native(
    reference: np.ndarray,
    current: np.ndarray,
    *,
    noise_floor: float = 0.0,
    sensitivity: float = 1.0,
) -> np.ndarray:
    """Run the residual weight map on the selected native AOT backend."""

    ref = np.ascontiguousarray(reference, dtype=np.float32)
    cur = np.ascontiguousarray(current, dtype=np.float32)
    if ref.ndim != 2 or cur.shape != ref.shape:
        raise ValueError("native RAW weight-map inputs must be matching 2D arrays")
    result = _dispatch_native_raw(
        "compression_raw_weight_map_f32",
        inputs={"reference": ref, "current": cur},
        outputs={"dst": np.empty(ref.shape, dtype=np.float32)},
        scalars={"noise_floor": float(noise_floor), "sensitivity": float(sensitivity)},
    )
    return np.ascontiguousarray(result, dtype=np.float32)


def fuse_raw_pair_native(
    reference: np.ndarray,
    current: np.ndarray,
    local_weight: np.ndarray,
    *,
    reference_weight: float = 1.0,
    current_weight: float = 1.0,
) -> np.ndarray:
    """Fuse two aligned normalized RAW tiles on the selected AOT backend."""

    ref = np.ascontiguousarray(reference, dtype=np.float32)
    cur = np.ascontiguousarray(current, dtype=np.float32)
    weights = np.ascontiguousarray(local_weight, dtype=np.float32)
    if ref.ndim != 2 or cur.shape != ref.shape or weights.shape != ref.shape:
        raise ValueError("native RAW fuse inputs must be matching 2D arrays")
    result = _dispatch_native_raw(
        "compression_raw_fuse_pair_f32",
        inputs={"reference": ref, "current": cur, "local_weight": weights},
        outputs={"dst": np.empty(ref.shape, dtype=np.float32)},
        scalars={
            "reference_weight": float(reference_weight),
            "current_weight": float(current_weight),
        },
    )
    return np.ascontiguousarray(result, dtype=np.float32)


def fuse_raw_accumulate_native(
    accum: np.ndarray,
    denominator: np.ndarray,
    current: np.ndarray,
    local_weight: np.ndarray,
    *,
    current_weight: float = 1.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Append one frame to a native weighted RAW accumulator."""

    arrays = tuple(
        np.ascontiguousarray(value, dtype=np.float32)
        for value in (accum, denominator, current, local_weight)
    )
    if arrays[0].ndim != 2 or any(value.shape != arrays[0].shape for value in arrays[1:]):
        raise ValueError("native RAW accumulator inputs must be matching 2D arrays")
    result = _dispatch_native_raw(
        "compression_raw_fuse_accumulate_f32",
        inputs={
            "accum": arrays[0],
            "denominator": arrays[1],
            "current": arrays[2],
            "local_weight": arrays[3],
        },
        outputs={
            "dst_accum": np.empty(arrays[0].shape, dtype=np.float32),
            "dst_denominator": np.empty(arrays[0].shape, dtype=np.float32),
        },
        scalars={"current_weight": float(current_weight)},
    )
    return (
        np.ascontiguousarray(result["dst_accum"], dtype=np.float32),
        np.ascontiguousarray(result["dst_denominator"], dtype=np.float32),
    )


def phase_safe_integer_warp(
    frame: RawMosaicFrame,
    flow: np.ndarray,
    *,
    tolerance: float = 1e-4,
    border: str = "clamp",
) -> np.ndarray:
    """Warp a mosaic only when displacement preserves CFA phase.

    A full-resolution odd-pixel displacement would map red/green/blue samples
    onto a different CFA plane.  Until a phase-aware subpixel AOT kernel is
    available, rejecting that case is safer than interpolating baked RGB-like
    values.  Integer even displacements are handled with a zero-copy-friendly
    indexed gather and preserve the input dtype.
    """
    if border != "clamp":
        raise ValueError("only clamp border is currently supported for RAW warp")
    displacement = np.asarray(flow, dtype=np.float32)
    if displacement.shape[:2] != frame.shape or displacement.shape[-1:] != (2,):
        raise ValueError("RAW flow must have shape (height, width, 2)")
    if not np.isfinite(displacement).all():
        raise ValueError("RAW flow contains non-finite values")
    rounded = np.rint(displacement)
    if not np.all(np.abs(displacement - rounded) <= float(tolerance)):
        raise ValueError("subpixel RAW warp requires a phase-aware plane adapter")
    if np.any((rounded.astype(np.int64) & 1) != 0):
        raise ValueError("odd-pixel RAW displacement would change CFA phase")
    yy, xx = np.indices(frame.shape, dtype=np.int64)
    source_y = np.clip(yy + rounded[..., 1].astype(np.int64), 0, frame.height - 1)
    source_x = np.clip(xx + rounded[..., 0].astype(np.int64), 0, frame.width - 1)
    return np.ascontiguousarray(frame.samples[source_y, source_x])


def raw_optical_flow(
    reference: RawMosaicFrame,
    current: RawMosaicFrame,
    *,
    flow_runner: Optional[Callable[..., Any]] = None,
    native: bool = False,
    flow_input_scale: float | None = None,
    **kwargs: Any,
) -> Any:
    """Run an existing flow backend on CFA guides, never on demosaiced RGB.

    ``flow_runner`` is injectable for tests and future native kernels.  When
    omitted, the maintained Taichi AOT Farneback wrapper is loaded lazily.
    The function intentionally returns the runner's native result unchanged.
    """
    if reference.shape != current.shape:
        raise ValueError("RAW optical-flow frames must have identical shapes")
    if reference.cfa_pattern != current.cfa_pattern:
        raise ValueError("RAW optical-flow frames must use the same CFA pattern")
    guide = raw_alignment_guide_native if native else raw_alignment_guide
    previous_guide = guide(reference)
    current_guide = guide(current)
    default_runner = flow_runner is None
    if flow_runner is None:
        from taichi_vision import taichi_aot

        flow_runner = taichi_aot.farneback_flow
    previous_guide, current_guide = _prepare_flow_inputs(
        previous_guide,
        current_guide,
        flow_input_scale=flow_input_scale,
        default_runner=default_runner,
    )
    return flow_runner(previous_guide, current_guide, **kwargs)


def raw_optical_flow_dng(
    reference: Any,
    current: Any,
    *,
    flow_runner: Optional[Callable[..., Any]] = None,
    block_size: int | tuple[int, int] = 2048,
    native: bool = False,
    flow_contract: RawFlowTileContract | Mapping[str, Any] | None = None,
    flow_mode: str = "auto",
    flow_input_scale: float | None = None,
    **kwargs: Any,
) -> Any:
    """Run optical flow on pre-demosaic DNG green guides.

    The default remains the established full-guide path.  ``flow_mode`` may
    be ``"full_frame"`` to force it, ``"auto"`` (the default) to use a tile
    runner only when an explicit :class:`RawFlowTileContract` is supplied, or
    ``"force"`` to require that contract.  This fail-closed admission rule is
    important for Farneback/LK-style solvers whose pyramid and reduction
    state cannot be inferred from a Python callable.

    Tiled flow operates on normalized half-resolution green guides.  It never
    demosaics or interpolates RGB, but the resulting displacement still must
    pass :func:`phase_safe_integer_warp` before it is applied to RAW samples.
    ``return_gpu=True`` is intentionally rejected for the tiled contract
    because stitching requires a validated host-visible flow tile; callers
    wanting a GPU-resident result should use the established full-frame API.
    """
    if (int(reference.height), int(reference.width)) != (
        int(current.height),
        int(current.width),
    ):
        raise ValueError("DNG optical-flow frames must have identical dimensions")
    mode = str(flow_mode).strip().lower()
    if mode not in {"auto", "full_frame", "force"}:
        raise ValueError("flow_mode must be 'auto', 'full_frame', or 'force'")
    if bool(kwargs.get("return_gpu", False)) and mode == "force":
        raise ValueError(
            "RAW tiled optical flow requires host-visible flow tiles; "
            "use flow_mode='full_frame' for return_gpu=True"
        )
    if mode == "force" and flow_contract is None and flow_runner is None:
        raise ValueError(
            "flow_mode='force' requires an explicit RawFlowTileContract; "
            "the default Farneback runner is not admitted as tile-safe"
        )
    previous_guide = raw_alignment_guide_dng(
        reference, block_size=block_size, native=native
    )
    current_guide = raw_alignment_guide_dng(
        current, block_size=block_size, native=native
    )
    default_runner = flow_runner is None
    if flow_runner is None:
        from taichi_vision import taichi_aot

        flow_runner = taichi_aot.farneback_flow
    previous_guide, current_guide = _prepare_flow_inputs(
        previous_guide,
        current_guide,
        flow_input_scale=flow_input_scale,
        default_runner=default_runner,
    )
    contract = _coerce_raw_flow_tile_contract(flow_runner, flow_contract)
    if mode == "force" and contract is None:
        raise ValueError(
            "flow_mode='force' requires an explicit RawFlowTileContract; "
            "automatic source inspection is not sufficient"
        )
    if mode == "full_frame" or contract is None:
        return flow_runner(previous_guide, current_guide, **kwargs)
    return _run_raw_flow_guide_tiled(
        previous_guide,
        current_guide,
        flow_runner,
        block_size=block_size,
        contract=contract,
        kwargs=kwargs,
    )


def raw_flow_tile_parity_report(
    reference: Any,
    current: Any,
    *,
    flow_runner: Callable[..., Any],
    block_size: int | tuple[int, int] = 2048,
    flow_contract: RawFlowTileContract | Mapping[str, Any],
    expected_translation: tuple[float, float] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Run a read-only full/tiled RAW-flow parity diagnostic.

    The exact same runner is executed once on the complete green guide and
    twice through the explicit :class:`RawFlowTileContract` tile path.  The
    second tiled run makes deterministic merge/repeatability observable.  The
    result is deliberately ``candidate_only``: this helper never registers
    native evidence or changes dispatch policy, and a Python runner is not
    treated as proof of a native backend.
    """

    contract = _coerce_raw_flow_tile_contract(flow_runner, flow_contract)
    if contract is None:
        raise ValueError("flow_contract must be an explicit RawFlowTileContract")
    call_kwargs = dict(kwargs)
    call_kwargs.pop("return_gpu", None)
    full = np.asarray(
        raw_optical_flow_dng(
            reference,
            current,
            flow_runner=flow_runner,
            block_size=block_size,
            flow_mode="full_frame",
            **call_kwargs,
        ),
        dtype=np.float32,
    )
    tiled = np.asarray(
        raw_optical_flow_dng(
            reference,
            current,
            flow_runner=flow_runner,
            block_size=block_size,
            flow_contract=contract,
            flow_mode="force",
            **call_kwargs,
        ),
        dtype=np.float32,
    )
    tiled_repeat = np.asarray(
        raw_optical_flow_dng(
            reference,
            current,
            flow_runner=flow_runner,
            block_size=block_size,
            flow_contract=contract,
            flow_mode="force",
            **call_kwargs,
        ),
        dtype=np.float32,
    )
    shape_ok = bool(
        full.ndim == 3
        and full.shape[-1] == 2
        and tiled.shape == full.shape
        and tiled_repeat.shape == full.shape
    )
    finite = bool(
        shape_ok
        and np.isfinite(full).all()
        and np.isfinite(tiled).all()
        and np.isfinite(tiled_repeat).all()
    )
    parity_error = (
        float(np.max(np.abs(full.astype(np.float64) - tiled.astype(np.float64))))
        if shape_ok and full.size
        else float("inf")
    )
    repeat_error = (
        float(np.max(np.abs(tiled.astype(np.float64) - tiled_repeat.astype(np.float64))))
        if shape_ok and full.size
        else float("inf")
    )
    median = (
        np.median(tiled.reshape(-1, 2), axis=0)
        if shape_ok and tiled.size
        else np.asarray((np.nan, np.nan), dtype=np.float64)
    )
    translation_error = None
    if expected_translation is not None:
        expected = np.asarray(expected_translation, dtype=np.float64)
        if expected.shape != (2,) or not np.isfinite(expected).all():
            raise ValueError("expected_translation must contain two finite values")
        translation_error = float(np.max(np.abs(median - expected)))
    passed = bool(
        shape_ok
        and finite
        and parity_error <= 1.0e-4
        and repeat_error <= 1.0e-6
        and bool(contract.deterministic)
        and (translation_error is None or translation_error <= 0.5)
    )
    return {
        "scope": "raw_moving_flow_full_vs_explicit_tile_parity",
        "shape": list(full.shape),
        "block_size": (
            [int(block_size), int(block_size)]
            if isinstance(block_size, int)
            else [int(block_size[0]), int(block_size[1])]
        ),
        "halo": int(contract.halo),
        "finite": finite,
        "median_translation": [float(median[0]), float(median[1])],
        "expected_translation": (
            None if expected_translation is None else [float(value) for value in expected_translation]
        ),
        "translation_error": translation_error,
        "parity_max_abs_error": parity_error,
        "repeat_max_abs_error": repeat_error,
        "block_selected": True,
        "deterministic_merge": bool(contract.deterministic and repeat_error <= 1.0e-6),
        "same_runner": True,
        "passed": passed,
        "native_runtime": False,
        "evidence_status": "candidate_only",
        "dispatch_changed": False,
    }


def _prepare_flow_inputs(
    previous: np.ndarray,
    current: np.ndarray,
    *,
    flow_input_scale: float | None,
    default_runner: bool,
) -> tuple[np.ndarray, np.ndarray]:
    """Adapt normalized RAW guides to the maintained flow ABI.

    ``raw_alignment_guide*`` deliberately returns headroom-normalized
    float32 values.  The default Taichi Farneback wrapper follows the
    OpenCV-compatible convention of receiving grayscale values in ``[0,255]``.
    A caller-owned runner is left untouched unless it explicitly supplies a
    scale, preserving existing custom-runner semantics and tests.
    """

    if flow_input_scale is None:
        scale = 255.0 if default_runner else 1.0
    else:
        scale = float(flow_input_scale)
        if not np.isfinite(scale) or scale <= 0.0:
            raise ValueError("flow_input_scale must be a finite positive number")
    previous = np.ascontiguousarray(previous, dtype=np.float32)
    current = np.ascontiguousarray(current, dtype=np.float32)
    if scale == 1.0:
        return previous, current
    return previous * np.float32(scale), current * np.float32(scale)


def _run_raw_flow_guide_tiled(
    previous_guide: np.ndarray,
    current_guide: np.ndarray,
    flow_runner: Callable[..., Any],
    *,
    block_size: int | tuple[int, int],
    contract: RawFlowTileContract,
    kwargs: Mapping[str, Any],
) -> np.ndarray:
    """Execute and stitch one explicitly admitted green-guide flow grid.

    This helper is deliberately serialized and deterministic.  It does not
    claim cross-tile GPU overlap and does not use the generic image block
    registry, because a flow runner owns its own algorithmic state.  Every
    tile is validated before its core is committed; an invalid tile raises an
    actionable error instead of silently substituting CPU or full-frame work.
    """
    previous = np.ascontiguousarray(previous_guide, dtype=np.float32)
    current = np.ascontiguousarray(current_guide, dtype=np.float32)
    if previous.ndim != 2 or current.shape != previous.shape:
        raise ValueError("RAW green guides must be matching 2D arrays")
    if bool(kwargs.get("return_gpu", False)):
        raise ValueError(
            "RAW tiled optical flow requires return_gpu=False for validated stitching"
        )
    if isinstance(block_size, int):
        sensor_h = sensor_w = int(block_size)
    else:
        sensor_h, sensor_w = (int(block_size[0]), int(block_size[1]))
    if sensor_h <= 0 or sensor_w <= 0:
        raise ValueError("block_size must be positive")
    guide_h = max(1, (sensor_h + 1) // 2)
    guide_w = max(1, (sensor_w + 1) // 2)
    height, width = previous.shape
    halo = int(contract.halo)
    output = np.empty((height, width, 2), dtype=np.float32)
    tile_index = 0
    for y0 in range(0, height, guide_h):
        y1 = min(height, y0 + guide_h)
        for x0 in range(0, width, guide_w):
            x1 = min(width, x0 + guide_w)
            read_y0 = max(0, y0 - halo)
            read_y1 = min(height, y1 + halo)
            read_x0 = max(0, x0 - halo)
            read_x1 = min(width, x1 + halo)
            tile_previous = np.ascontiguousarray(previous[read_y0:read_y1, read_x0:read_x1])
            tile_current = np.ascontiguousarray(current[read_y0:read_y1, read_x0:read_x1])
            try:
                tile_flow = flow_runner(tile_previous, tile_current, **dict(kwargs))
            except Exception as exc:
                raise RuntimeError(
                    f"RAW tiled optical-flow runner failed on guide tile {tile_index}"
                ) from exc
            if hasattr(tile_flow, "to_numpy") and not isinstance(tile_flow, np.ndarray):
                tile_flow = tile_flow.to_numpy()
            tile_flow = np.asarray(tile_flow)
            expected_shape = (read_y1 - read_y0, read_x1 - read_x0, 2)
            if tile_flow.shape != expected_shape:
                raise ValueError(
                    "RAW tiled optical-flow runner must return an HxWx2 tile; "
                    f"got {tile_flow.shape}, expected {expected_shape}"
                )
            if not np.issubdtype(tile_flow.dtype, np.number) or not np.isfinite(tile_flow).all():
                raise ValueError(
                    f"RAW tiled optical-flow runner returned invalid values on guide tile {tile_index}"
                )
            core_y0 = y0 - read_y0
            core_y1 = core_y0 + (y1 - y0)
            core_x0 = x0 - read_x0
            core_x1 = core_x0 + (x1 - x0)
            output[y0:y1, x0:x1] = np.asarray(
                tile_flow[core_y0:core_y1, core_x0:core_x1], dtype=np.float32
            )
            tile_index += 1
    return output


def fuse_raw_frames_blockwise(
    frames: Sequence[RawMosaicFrame],
    *,
    block_size: int | tuple[int, int] = 512,
    weights: Optional[Sequence[float]] = None,
    weight_map: Optional[Callable[[np.ndarray, np.ndarray], np.ndarray]] = None,
    apply_white_balance: bool = False,
    output: Optional[np.ndarray] = None,
    native: bool = False,
    native_weight_map: bool = False,
) -> tuple[np.ndarray, RawFusionReport]:
    """Fuse aligned RAW frames in normalized headroom space.

    This implementation is intentionally block-streamed: at most one
    normalized tile per input frame is resident at a time.  With ``native``
    true, normalization, residual weights, and accumulation use the selected
    ``compression_raw`` AOT graphs; false retains the dependency-free NumPy
    oracle.  ``native_weight_map=True`` opts into the native residual weight
    graph when no custom ``weight_map`` callback is supplied; the default
    preserves the historical scalar-weight semantics exactly.  The output is
    float32 and may exceed one until the caller performs highlight recovery
    and the final public clamp.  No demosaic or interpolation is performed.
    """
    frame_list = tuple(frames)
    if not frame_list:
        raise ValueError("at least one RAW frame is required")
    first = frame_list[0]
    if any(item.shape != first.shape for item in frame_list[1:]):
        raise ValueError("all RAW frames must have identical shapes")
    if any(item.cfa_pattern != first.cfa_pattern for item in frame_list[1:]):
        raise ValueError("all RAW frames must use the same CFA pattern")
    if isinstance(block_size, int):
        block_h = block_w = int(block_size)
    else:
        block_h, block_w = (int(block_size[0]), int(block_size[1]))
    if block_h <= 0 or block_w <= 0:
        raise ValueError("block_size must be positive")
    if weights is None:
        scalar_weights = np.ones(len(frame_list), dtype=np.float32)
    else:
        scalar_weights = np.asarray(tuple(weights), dtype=np.float32)
        if scalar_weights.shape != (len(frame_list),) or np.any(scalar_weights < 0):
            raise ValueError("weights must contain one non-negative value per frame")
    if not np.any(scalar_weights > 0):
        raise ValueError("at least one frame weight must be positive")
    if output is None:
        destination = np.empty(first.shape, dtype=np.float32)
    else:
        destination = np.asarray(output)
        if destination.shape != first.shape or destination.dtype != np.dtype(np.float32):
            raise ValueError("output must be a float32 array with the RAW frame shape")
    started = time.perf_counter()
    blocks = 0
    for y0 in range(0, first.height, block_h):
        y1 = min(first.height, y0 + block_h)
        for x0 in range(0, first.width, block_w):
            x1 = min(first.width, x0 + block_w)
            if native:
                normalized = [
                    raw_normalize_headroom_native(
                        frame,
                        y0=y0,
                        y1=y1,
                        x0=x0,
                        x1=x1,
                        apply_white_balance=apply_white_balance,
                    )
                    for frame in frame_list
                ]
            else:
                normalized = [
                    frame.normalized_headroom_region(
                        y0, y1, x0, x1, apply_white_balance=apply_white_balance
                    )
                    for frame in frame_list
                ]
            reference = normalized[0]
            first_weight = np.float32(scalar_weights[0])
            if native:
                accum = reference * first_weight
                denominator = np.full_like(reference, first_weight, dtype=np.float32)
            else:
                finite_reference = np.isfinite(reference)
                accum = np.where(finite_reference, reference, 0.0) * first_weight
                denominator = finite_reference.astype(np.float32) * first_weight
            for index, tile in enumerate(normalized[1:], start=1):
                tile_weight = np.float32(scalar_weights[index])
                if weight_map is not None:
                    local_weight = np.asarray(weight_map(reference, tile), dtype=np.float32)
                    if local_weight.shape != tile.shape:
                        raise ValueError("weight_map must preserve the tile shape")
                    local_weight = np.nan_to_num(local_weight, nan=0.0, posinf=0.0, neginf=0.0)
                elif native and native_weight_map:
                    local_weight = raw_weight_map_native(reference, tile)
                else:
                    local_weight = np.ones_like(tile, dtype=np.float32) if native else None
                if native:
                    if local_weight is None:
                        raise AssertionError("native RAW weight map was not created")
                    accum, denominator = fuse_raw_accumulate_native(
                        accum,
                        denominator,
                        tile,
                        local_weight,
                        current_weight=float(tile_weight),
                    )
                elif local_weight is not None:
                    accum += tile * local_weight * tile_weight
                    denominator += local_weight * tile_weight
                else:
                    finite = np.isfinite(tile)
                    accum += np.where(finite, tile, 0.0) * tile_weight
                    denominator += finite.astype(np.float32) * tile_weight
            destination[y0:y1, x0:x1] = np.divide(
                accum,
                np.maximum(denominator, np.float32(1e-12)),
                out=np.zeros_like(accum),
            )
            blocks += 1
    elapsed = time.perf_counter() - started
    report = RawFusionReport(
        shape=first.shape,
        block_size=(block_h, block_w),
        block_count=blocks,
        elapsed_seconds=elapsed,
        output_dtype=destination.dtype.str,
        output_min=float(np.min(destination)),
        output_max=float(np.max(destination)),
        headroom_pixels=int(np.count_nonzero(destination > 1.0)),
    )
    return destination, report


def fuse_dng_frames_blockwise(
    frames: Sequence[Any],
    *,
    block_size: int | tuple[int, int] = 512,
    weights: Optional[Sequence[float]] = None,
    weight_map: Optional[Callable[[np.ndarray, np.ndarray], np.ndarray]] = None,
    apply_white_balance: bool = False,
    output: Optional[np.ndarray] = None,
    native: bool = False,
    native_weight_map: bool = False,
) -> tuple[np.ndarray, RawFusionReport]:
    """Fuse parsed DNG frames directly in the pre-demosaic domain.

    ``DNGFrame.sample_region`` supplies one native integer tile at a time;
    each tile is adapted to :class:`RawMosaicFrame` with an absolute CFA phase
    before entering the established RAW fusion path.  This keeps the public
    DNG/RAW operation native and high-bit-depth without first demosaicing or
    allocating a full-frame float/RGB intermediate.  ``native=True`` uses the
    selected backend's target-qualified ``compression_raw`` graphs for
    normalization and accumulation, with the same explicit error behavior as
    :func:`fuse_raw_frames_blockwise` when an artifact is unavailable.
    """
    frame_list = tuple(frames)
    if not frame_list:
        raise ValueError("at least one DNG frame is required")
    first = frame_list[0]
    shape = (int(first.height), int(first.width))
    if any((int(item.height), int(item.width)) != shape for item in frame_list[1:]):
        raise ValueError("all DNG frames must have identical dimensions")
    if isinstance(block_size, int):
        block_h = block_w = int(block_size)
    else:
        block_h, block_w = (int(block_size[0]), int(block_size[1]))
    if block_h <= 0 or block_w <= 0:
        raise ValueError("block_size must be positive")
    if output is None:
        destination = np.empty(shape, dtype=np.float32)
    else:
        destination = np.asarray(output)
        if destination.shape != shape or destination.dtype != np.dtype(np.float32):
            raise ValueError("output must be a float32 array with the DNG frame shape")

    started = time.perf_counter()
    blocks = 0
    for y0 in range(0, shape[0], block_h):
        y1 = min(shape[0], y0 + block_h)
        for x0 in range(0, shape[1], block_w):
            x1 = min(shape[1], x0 + block_w)
            tile_frames = [
                RawMosaicFrame.from_dng_region(item, y0, y1, x0, x1)
                for item in frame_list
            ]
            tile_output, _tile_report = fuse_raw_frames_blockwise(
                tile_frames,
                block_size=(y1 - y0, x1 - x0),
                weights=weights,
                weight_map=weight_map,
                apply_white_balance=apply_white_balance,
                native=native,
                native_weight_map=native_weight_map,
            )
            destination[y0:y1, x0:x1] = tile_output
            blocks += 1

    elapsed = time.perf_counter() - started
    report = RawFusionReport(
        shape=shape,
        block_size=(block_h, block_w),
        block_count=blocks,
        elapsed_seconds=elapsed,
        output_dtype=destination.dtype.str,
        output_min=float(np.min(destination)),
        output_max=float(np.max(destination)),
        headroom_pixels=int(np.count_nonzero(destination > 1.0)),
    )
    return destination, report


__all__ = [
    "RawFusionReport",
    "RawFlowTileContract",
    "raw_flow_tile_contract",
    "raw_alignment_guide",
    "raw_alignment_guide_dng",
    "raw_normalize_headroom_native",
    "raw_alignment_guide_native",
    "raw_weight_map",
    "raw_weight_map_native",
    "fuse_raw_pair_native",
    "fuse_raw_accumulate_native",
    "phase_safe_integer_warp",
    "raw_optical_flow",
    "raw_optical_flow_dng",
    "raw_flow_tile_parity_report",
    "fuse_raw_frames_blockwise",
    "fuse_dng_frames_blockwise",
]
