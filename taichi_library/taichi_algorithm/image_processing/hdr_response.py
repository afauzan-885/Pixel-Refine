"""HDR response calibration and radiance merging.

This module implements bounded Debevec-style and Robertson-style response
solves plus weighted radiance merge.  It consumes aligned, same-shaped
exposure images in the normalised encoded range ``[0, 1]``.  ``backend="numpy"``
is the reference path; ``backend="taichi"`` dispatches response quantisation,
weighting, and merge kernels on an explicitly initialised CPU JIT runtime,
then performs the small bounded solver on the host (an explicit
Taichi/NumPy hybrid).
The host solve is intentional: a target-qualified Taichi QR/SVD or iterative
Robertson reduction primitive is not available in this library yet.
``backend="aot"`` dispatches target-qualified response quantisation and
weighted/log merge leaves; the bounded solver remains explicit host work until
a target-qualified QR/SVD/Robertson reduction exists.  Robertson is never
silently substituted for Debevec.
"""

from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np

from ..pipeline_common import validate_same_shape

try:  # Importing Taichi is cheap; initialisation remains explicit/lazy below.
    import taichi as ti
except ImportError:  # pragma: no cover - exercised only in minimal installs
    ti = None


MAX_HDR_PIXELS = 55_000_000
DEFAULT_MAX_WORKING_BYTES = 1_500_000_000


@dataclass(frozen=True)
class ResponseCalibration:
    """Estimated log response curve for each channel."""

    curve: np.ndarray
    exposure_times: np.ndarray
    levels: int
    sample_count: int
    backend: str
    reference_value: float = 0.5
    # ``numpy-lstsq`` is retained as the default for backwards-compatible
    # construction by callers that persisted the original fields.  A
    # Taichi calibration reports ``taichi-quantize+numpy-lstsq`` here so the
    # host solve is observable rather than being mistaken for an AOT solver.
    solver_backend: str = "numpy-lstsq"
    # Added as a trailing field so persisted/positional constructions using
    # the original six fields remain valid.
    method: str = "debevec"


def _backend_name(backend: str) -> str:
    value = str(backend).lower()
    if value not in {"numpy", "taichi", "aot"}:
        raise ValueError("backend must be 'numpy', 'taichi', or 'aot'")
    return value


def _ensure_taichi_cpu() -> None:
    """Initialise a CPU JIT runtime, or fail if another arch owns the runtime."""

    if ti is None:
        raise ImportError("Taichi is required for backend='taichi'")
    from taichi.lang import impl

    runtime = impl.get_runtime()
    if getattr(runtime, "prog", None) is None:
        ti.init(arch=ti.cpu, offline_cache=False)
        return
    current_arch = getattr(getattr(ti, "cfg", None), "arch", None)
    if current_arch != ti.cpu:
        raise RuntimeError(
            "backend='taichi' requires a CPU JIT runtime; the current Taichi runtime is already initialised on another arch"
        )


if ti is not None:

    @ti.func
    def _quantize_unit(value, levels):
        clipped = ti.min(ti.max(value, 0.0), 1.0)
        scaled = clipped * ti.cast(levels - 1, ti.f32)
        lower = ti.cast(ti.floor(scaled), ti.i32)
        fraction = scaled - ti.cast(lower, ti.f32)
        # Match NumPy's np.rint (nearest-even) rather than silently changing
        # the response LUT at half-bin values.
        odd = (lower & 1) != 0
        # Do not use Python's bitwise boolean operators here.  Taichi's
        # Vulkan lowering in older toolchains can emit OpBitwiseAnd with a
        # boolean result, which SPIR-V validation rejects.  Nested select is
        # logically identical and lowers to integer-safe select operations.
        use_upper = ti.select(
            fraction > 0.5,
            True,
            ti.select(fraction == 0.5, odd, False),
        )
        quantised = ti.select(use_upper, lower + 1, lower)
        return ti.max(0, ti.min(levels - 1, quantised))

    @ti.func
    def _triangular_weight(quantised, levels):
        return ti.cast(ti.min(quantised, levels - 1 - quantised), ti.f32)

    @ti.kernel
    def _response_weight_kernel(
        values: ti.types.ndarray(dtype=ti.f32, ndim=1),
        weights: ti.types.ndarray(dtype=ti.f32, ndim=1),
        levels: ti.i32,
    ):
        for index in range(values.shape[0]):
            quantised = _quantize_unit(values[index], levels)
            weights[index] = _triangular_weight(quantised, levels)

    @ti.kernel
    def _response_quantise_kernel(
        values: ti.types.ndarray(dtype=ti.f32, ndim=1),
        quantised: ti.types.ndarray(dtype=ti.i32, ndim=1),
        levels: ti.i32,
    ):
        """Quantise sampled response values with NumPy-compatible rounding.

        This is deliberately a separate kernel from the weighting kernel.  The
        Debevec linear system uses the integer code values directly, so keeping
        this operation on the Taichi side makes the hybrid calibration path
        explicit while leaving the numerically sensitive QR/SVD solve to the
        existing NumPy reference routine.
        """

        for index in range(values.shape[0]):
            quantised[index] = _quantize_unit(values[index], levels)

    @ti.kernel
    def _debevec_system_kernel(
        quantised: ti.types.ndarray(dtype=ti.i32, ndim=2),
        log_times: ti.types.ndarray(dtype=ti.f64, ndim=1),
        matrix: ti.types.ndarray(dtype=ti.f64, ndim=2),
        rhs: ti.types.ndarray(dtype=ti.f64, ndim=1),
        levels: ti.i32,
        smooth_lambda: ti.f64,
        reference_value: ti.f64,
        midpoint: ti.i32,
    ):
        """Assemble one bounded Debevec system without a Python row loop.

        Every data row has a unique ``(sample, frame)`` pair, so the kernel
        writes are race-free.  The NumPy solver still consumes the resulting
        f64 system; this split preserves the existing numerical contract while
        moving the deterministic, embarrassingly parallel assembly to Taichi.
        """

        frame_count = quantised.shape[0]
        sample_count = quantised.shape[1]
        data_rows = frame_count * sample_count
        for sample, frame in ti.ndrange(sample_count, frame_count):
            row = sample * frame_count + frame
            code = quantised[frame, sample]
            mirrored = levels - 1 - code
            weight = ti.cast(ti.min(code, mirrored), ti.f64)
            if weight > 0.0:
                matrix[row, code] = weight
                matrix[row, levels + sample] = weight
                rhs[row] = weight * log_times[frame]

        for code in range(1, levels - 1):
            row = data_rows + code - 1
            mirrored = levels - 1 - code
            weight = smooth_lambda * ti.cast(ti.min(code, mirrored), ti.f64)
            matrix[row, code - 1] = weight
            matrix[row, code] = -2.0 * weight
            matrix[row, code + 1] = weight

        gauge_row = data_rows + levels - 2
        matrix[gauge_row, ti.max(0, ti.min(levels - 1, midpoint))] = 1.0
        rhs[gauge_row] = ti.log(ti.max(reference_value, 1.0e-6))

    @ti.kernel
    def _merge_linear_kernel(
        stack: ti.types.ndarray(dtype=ti.f32, ndim=4),
        times: ti.types.ndarray(dtype=ti.f32, ndim=1),
        output: ti.types.ndarray(dtype=ti.f32, ndim=3),
        h: ti.i32,
        w: ti.i32,
        channels: ti.i32,
        frame_count: ti.i32,
        levels: ti.i32,
    ):
        for y, x, channel in ti.ndrange(h, w, channels):
            numerator = 0.0
            denominator = 0.0
            for frame in range(frame_count):
                value = ti.min(ti.max(stack[frame, y, x, channel], 0.0), 1.0)
                quantised = _quantize_unit(value, levels)
                weight = ti.max(_triangular_weight(quantised, levels), 1.0e-3)
                numerator += weight * value / ti.max(times[frame], 1.0e-12)
                denominator += weight
            output[y, x, channel] = numerator / ti.max(denominator, 1.0e-6)

    @ti.kernel
    def _merge_log_kernel(
        stack: ti.types.ndarray(dtype=ti.f32, ndim=4),
        times: ti.types.ndarray(dtype=ti.f32, ndim=1),
        curve: ti.types.ndarray(dtype=ti.f32, ndim=2),
        output: ti.types.ndarray(dtype=ti.f32, ndim=3),
        h: ti.i32,
        w: ti.i32,
        channels: ti.i32,
        frame_count: ti.i32,
        levels: ti.i32,
    ):
        for y, x, channel in ti.ndrange(h, w, channels):
            numerator = 0.0
            denominator = 0.0
            for frame in range(frame_count):
                value = ti.min(ti.max(stack[frame, y, x, channel], 0.0), 1.0)
                quantised = _quantize_unit(value, levels)
                weight = ti.max(_triangular_weight(quantised, levels), 1.0e-3)
                numerator += weight * (curve[quantised, channel] - ti.log(ti.max(times[frame], 1.0e-12)))
                denominator += weight
            output[y, x, channel] = ti.exp(numerator / ti.max(denominator, 1.0e-6))


def _response_weight_taichi(values: Any, levels: int) -> np.ndarray:
    _ensure_taichi_cpu()
    data = np.ascontiguousarray(np.asarray(values, dtype=np.float32)).reshape(-1)
    output = np.empty_like(data, dtype=np.float32)
    _response_weight_kernel(data, output, int(levels))
    return output.reshape(np.asarray(values).shape)


def _response_quantise_taichi(values: Any, levels: int) -> np.ndarray:
    """Return integer response codes from the explicit CPU-JIT kernel."""

    _ensure_taichi_cpu()
    original = np.asarray(values)
    data = np.ascontiguousarray(original, dtype=np.float32).reshape(-1)
    output = np.empty(data.shape, dtype=np.int32)
    _response_quantise_kernel(data, output, int(levels))
    return output.reshape(original.shape)


def _debevec_system_taichi(
    quantised: np.ndarray,
    log_times: np.ndarray,
    *,
    levels: int,
    smooth_lambda: float,
    reference_value: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Assemble a Debevec matrix/rhs with the explicit CPU-JIT kernel."""

    _ensure_taichi_cpu()
    codes = np.ascontiguousarray(np.asarray(quantised, dtype=np.int32))
    if codes.ndim != 2:
        raise ValueError("quantised samples must be a two-dimensional array")
    times = np.ascontiguousarray(np.asarray(log_times, dtype=np.float64).reshape(-1))
    if times.shape[0] != codes.shape[0]:
        raise ValueError("log_times length must match quantised frame count")
    frame_count, sample_count = (int(codes.shape[0]), int(codes.shape[1]))
    rows = frame_count * sample_count + max(int(levels) - 2, 0) + 1
    cols = int(levels) + sample_count
    matrix = np.zeros((rows, cols), dtype=np.float64)
    rhs = np.zeros(rows, dtype=np.float64)
    midpoint = int(round((int(levels) - 1) * float(reference_value)))
    _debevec_system_kernel(
        codes,
        times,
        matrix,
        rhs,
        int(levels),
        float(smooth_lambda),
        float(reference_value),
        midpoint,
    )
    return matrix, rhs


def _validate_times(exposure_times: Sequence[float], frame_count: int) -> np.ndarray:
    times = np.asarray(exposure_times, dtype=np.float64).reshape(-1)
    if len(times) != int(frame_count):
        raise ValueError("exposure_times length must match frame count")
    if len(times) < 2 or not np.isfinite(times).all() or np.any(times <= 0.0):
        raise ValueError("exposure_times must contain at least two finite positive values")
    return np.ascontiguousarray(times)


def _estimate_stack_working_bytes(pixels: int, channels: int, frame_count: int) -> int:
    """Estimate materialised stack/output/scratch bytes for preflight guards."""

    # ``np.stack`` in both calibration and merge materialises every frame;
    # include all frames rather than only counting the output and one temporary.
    return int(pixels) * (int(channels) * 4 * (int(frame_count) + 3) + 8)


def _estimate_debevec_solver_bytes(frame_count: int, sample_count: int, levels: int) -> int:
    """Conservative f64 matrix plus LAPACK workspace estimate.

    ``np.linalg.lstsq`` may allocate several matrix-sized work buffers.  A
    four-times multiplier is intentionally conservative and keeps pathological
    ``levels=4096, sample_count=4096`` requests from bypassing the public
    working-memory limit just because the source frame itself is tiny.
    """

    rows = int(frame_count) * int(sample_count) + max(int(levels) - 2, 0) + 1
    cols = int(levels) + int(sample_count)
    matrix_and_rhs = (rows * cols + rows) * np.dtype(np.float64).itemsize
    return int(matrix_and_rhs * 4)


def _estimate_robertson_solver_bytes(frame_count: int, sample_count: int, levels: int) -> int:
    """Conservative workspace estimate for the bounded Robertson update.

    Robertson alternates per-sample irradiance and per-code response updates;
    unlike Debevec it does not materialise a ``(F*S+L) x (S+L)`` matrix.  The
    estimate nevertheless includes the quantised samples, float64 weight and
    residual planes, sample state, and several temporary ``bincount`` buffers
    so a caller's pressure budget remains meaningful rather than relying on
    the eventual NumPy allocator to fail.
    """

    frame_count = int(frame_count)
    sample_count = int(sample_count)
    levels = int(levels)
    fs = frame_count * sample_count
    # q (i32), weight/residual temporaries (f64), and a few reductions.  The
    # factor is deliberately conservative for NumPy's transient copies.
    sample_planes = fs * (np.dtype(np.int32).itemsize + 4 * np.dtype(np.float64).itemsize)
    curve_state = levels * 8 * 8
    per_sample_state = sample_count * 8 * 4
    return int((sample_planes + curve_state + per_sample_state) * 2)


def _validate_stack(
    images: Sequence[Any],
    *,
    max_pixels: int,
    max_working_bytes: int,
) -> tuple[list[np.ndarray], int]:
    if isinstance(images, np.ndarray):
        images = [images] if images.ndim <= 2 else list(images)
    arrays = validate_same_shape(images, name="images")
    pixels = int(arrays[0].shape[0]) * int(arrays[0].shape[1])
    if pixels < 1 or pixels > int(max_pixels):
        raise ValueError(f"HDR response input has {pixels:,} pixels; maximum is {int(max_pixels):,}")
    if int(max_working_bytes) <= 0:
        raise ValueError("max_working_bytes must be positive")
    if not all(np.isfinite(array).all() for array in arrays):
        raise ValueError("HDR response images must contain only finite values")
    if any(float(np.min(array)) < 0.0 or float(np.max(array)) > 1.0 for array in arrays):
        raise ValueError("HDR response images must be normalised to [0, 1]")
    channels = 1 if arrays[0].ndim == 2 else int(arrays[0].shape[2])
    estimate = _estimate_stack_working_bytes(pixels, channels, len(arrays))
    if estimate > int(max_working_bytes):
        raise MemoryError(f"HDR response requires about {estimate} bytes, limit is {int(max_working_bytes)}")
    return arrays, channels


def response_weight(values: Any, *, levels: int = 256, backend: str = "numpy") -> np.ndarray:
    """Triangular Debevec weight for normalised encoded values.

    ``backend="taichi"`` runs the bounded elementwise quantisation/weighting
    kernel on a CPU JIT runtime.  ``backend="numpy"`` remains the reference
    implementation.  AOT response weighting is not silently substituted.
    """

    if int(levels) < 16 or int(levels) > 4096:
        raise ValueError("levels must be between 16 and 4096")
    backend_name = str(backend).lower()
    if backend_name == "taichi":
        return _response_weight_taichi(values, int(levels))
    if backend_name == "aot":
        raise NotImplementedError(
            "HDR response weighting has no qualified AOT artifact; use backend='taichi' for CPU JIT"
        )
    if backend_name != "numpy":
        raise ValueError("backend must be 'numpy' or 'taichi'")
    values_array = np.asarray(values, dtype=np.float32)
    quantised = np.rint(np.clip(values_array, 0.0, 1.0) * float(int(levels) - 1)).astype(np.int32)
    midpoint = 0.5 * float(int(levels) - 1)
    weights = np.where(quantised <= midpoint, quantised, int(levels) - 1 - quantised)
    return np.asarray(weights, dtype=np.float32)


def _fallback_curve(levels: int, reference_value: float) -> np.ndarray:
    values = np.linspace(0.0, 1.0, int(levels), dtype=np.float64)
    curve = np.log(np.maximum(values, 1.0 / max(255.0, float(levels - 1))))
    midpoint = int(round((levels - 1) * reference_value))
    curve -= curve[midpoint] - np.log(max(reference_value, 1.0e-6))
    return curve.astype(np.float32)


def _solve_channel(
    quantised: np.ndarray,
    log_times: np.ndarray,
    *,
    levels: int,
    smooth_lambda: float,
    reference_value: float,
    backend: str = "numpy",
) -> np.ndarray:
    """Solve g(z)+ln(E)=ln(t) for one channel.

    ``backend="taichi"`` only changes deterministic system assembly; the
    least-squares solve remains NumPy f64 so this function has one numerical
    oracle for both public backends.
    """

    frame_count, sample_count = quantised.shape
    midpoint = int(round((levels - 1) * reference_value))
    if str(backend).lower() == "taichi":
        matrix, rhs = _debevec_system_taichi(
            quantised,
            log_times,
            levels=int(levels),
            smooth_lambda=float(smooth_lambda),
            reference_value=float(reference_value),
        )
    else:
        rows = frame_count * sample_count + max(levels - 2, 0) + 1
        cols = levels + sample_count
        matrix = np.zeros((rows, cols), dtype=np.float64)
        rhs = np.zeros(rows, dtype=np.float64)
        row = 0
        for sample in range(sample_count):
            for frame in range(frame_count):
                z = int(quantised[frame, sample])
                weight = float(z if z <= (levels - 1) * 0.5 else levels - 1 - z)
                if weight <= 0.0:
                    # Keep saturated samples in the system with zero influence
                    # so row count remains deterministic and no clipping bias
                    # enters.
                    row += 1
                    continue
                matrix[row, z] = weight
                matrix[row, levels + sample] = weight
                rhs[row] = weight * float(log_times[frame])
                row += 1
        smooth = float(smooth_lambda)
        for z in range(1, levels - 1):
            weight = smooth * float(z if z <= (levels - 1) * 0.5 else levels - 1 - z)
            matrix[row, z - 1] = weight
            matrix[row, z] = -2.0 * weight
            matrix[row, z + 1] = weight
            row += 1
        matrix[row, max(0, min(levels - 1, midpoint))] = 1.0
        rhs[row] = np.log(max(float(reference_value), 1.0e-6))
    try:
        solution, _, _, _ = np.linalg.lstsq(matrix, rhs, rcond=None)
    except np.linalg.LinAlgError:
        return _fallback_curve(levels, reference_value)
    curve = np.asarray(solution[:levels], dtype=np.float64)
    if not np.isfinite(curve).all():
        return _fallback_curve(levels, reference_value)
    # A response should be monotone for a camera channel.  Isotonic regression
    # is unnecessary here; cumulative clamping is deterministic and prevents
    # an ill-conditioned solve from creating negative differential response.
    curve = np.maximum.accumulate(curve)
    curve -= curve[midpoint] - np.log(max(float(reference_value), 1.0e-6))
    return curve.astype(np.float32)


def _normalise_response_method(method: str) -> str:
    """Resolve explicit response-solver spellings without implicit fallback."""

    value = str(method).strip().lower().replace("_", "-")
    aliases = {
        "debevec": "debevec",
        "debevec-lstsq": "debevec",
        "least-squares": "debevec",
        "lstsq": "debevec",
        "robertson": "robertson",
        "robertson-iterative": "robertson",
        "iterative": "robertson",
    }
    try:
        return aliases[value]
    except KeyError as exc:
        raise ValueError("method must be 'debevec' or 'robertson'") from exc


def _solve_channel_robertson(
    quantised: np.ndarray,
    log_times: np.ndarray,
    *,
    levels: int,
    smooth_lambda: float,
    reference_value: float,
    iterations: int,
    tolerance: float = 1.0e-5,
) -> np.ndarray:
    """Solve a bounded Robertson-style alternating response update.

    The implementation follows Robertson's alternating maximum-likelihood
    structure in log exposure space: estimate one latent irradiance state per
    sample from the current response, then update each response code from all
    observations carrying that code.  Samples at either saturation endpoint
    have zero triangular weight.  ``np.bincount`` keeps the update bounded by
    ``frame_count * sample_count`` and avoids a dense code-by-sample matrix.

    This is intentionally a host reduction.  The Taichi backend supplies the
    exact same quantised samples, after which this solver runs with NumPy
    float64 reductions; the distinction is reported through
    ``ResponseCalibration.solver_backend``.
    """

    codes = np.asarray(quantised, dtype=np.int32)
    if codes.ndim != 2:
        raise ValueError("quantised samples must be a two-dimensional array")
    frame_count, sample_count = (int(codes.shape[0]), int(codes.shape[1]))
    if frame_count < 2 or sample_count < 1:
        raise ValueError("Robertson requires at least two frames and one sample")
    levels = int(levels)
    iterations = int(iterations)
    if levels < 16 or levels > 4096:
        raise ValueError("levels must be between 16 and 4096")
    if iterations < 1 or iterations > 64:
        raise ValueError("iterations must be between 1 and 64")
    times = np.asarray(log_times, dtype=np.float64).reshape(-1)
    if times.shape[0] != frame_count or not np.isfinite(times).all():
        raise ValueError("log_times must match frame count and contain finite values")
    if not np.isfinite(codes).all() or np.any(codes < 0) or np.any(codes >= levels):
        raise ValueError("quantised samples contain an invalid response code")

    # Use the same triangular weighting contract as response_weight().  The
    # direct integer LUT avoids re-quantising already quantised samples.
    weight_lut = np.minimum(np.arange(levels, dtype=np.float64), np.arange(levels - 1, -1, -1, dtype=np.float64))
    weights = weight_lut[codes]
    log_t = np.ascontiguousarray(times, dtype=np.float64)
    midpoint = int(round((levels - 1) * float(reference_value)))
    midpoint = max(0, min(levels - 1, midpoint))
    log_reference = np.log(max(float(reference_value), 1.0e-6))

    # Initialise with the same monotonic/gauge contract as the Debevec
    # fallback.  This gives stable behaviour even if every observation is
    # saturated and no update has positive weight.
    curve = _fallback_curve(levels, float(reference_value)).astype(np.float64)
    for _ in range(iterations):
        # Latent per-sample state is ``ln(t) - g(z)`` (the sign convention
        # used by the existing Debevec matrix and log merge).
        denominator = np.sum(weights, axis=0, dtype=np.float64)
        state_numerator = np.sum(
            weights * (log_t[:, None] - curve[codes]),
            axis=0,
            dtype=np.float64,
        )
        sample_state = np.divide(
            state_numerator,
            denominator,
            out=np.zeros(sample_count, dtype=np.float64),
            where=denominator > 0.0,
        )

        # Aggregate all (frame, sample) observations by response code.  Keep
        # the current curve for unseen codes instead of injecting an arbitrary
        # zero that could violate monotonicity.
        residual = weights * (log_t[:, None] - sample_state[None, :])
        flat_codes = codes.reshape(-1)
        numerator = np.bincount(
            flat_codes,
            weights=residual.reshape(-1),
            minlength=levels,
        ).astype(np.float64, copy=False)
        code_denominator = np.bincount(
            flat_codes,
            weights=weights.reshape(-1),
            minlength=levels,
        ).astype(np.float64, copy=False)
        updated = np.divide(
            numerator,
            code_denominator,
            out=curve.copy(),
            where=code_denominator > 0.0,
        )

        # ``smooth_lambda`` is a mild, deterministic curvature prior.  It is
        # deliberately bounded so a large user value cannot erase measured
        # response structure.  This serves the same regularising role as the
        # Debevec second-difference rows without creating a dense matrix.
        if float(smooth_lambda) > 0.0 and levels > 2:
            alpha = min(0.5, float(smooth_lambda) / (float(smooth_lambda) + 100.0))
            smooth_prior = 0.5 * (updated[:-2] + updated[2:])
            updated[1:-1] = (1.0 - alpha) * updated[1:-1] + alpha * smooth_prior

        if not np.isfinite(updated).all():
            return _fallback_curve(levels, float(reference_value))
        updated = np.maximum.accumulate(updated)
        updated -= updated[midpoint] - log_reference
        delta = float(np.max(np.abs(updated - curve)))
        curve = updated
        if delta <= float(tolerance):
            break

    return np.ascontiguousarray(curve, dtype=np.float32)


def estimate_response_curve(
    images: Sequence[Any],
    exposure_times: Sequence[float],
    *,
    levels: int = 256,
    sample_count: int = 512,
    smooth_lambda: float = 10.0,
    reference_value: float = 0.5,
    backend: str = "numpy",
    max_pixels: int = MAX_HDR_PIXELS,
    max_working_bytes: int = DEFAULT_MAX_WORKING_BYTES,
    method: str = "debevec",
    iterations: int = 8,
) -> ResponseCalibration:
    """Estimate a Debevec- or Robertson-style log response curve per channel.

    Sampling is evenly spaced over the flattened image stack, making the
    result reproducible and keeping the linear solve bounded independently of
    a 50 MP frame size.  ``method="debevec"`` retains the existing bounded
    weighted least-squares solve.  ``method="robertson"`` performs an explicit
    bounded alternating response/irradiance update; it does not silently
    replace Debevec.  ``backend="taichi"`` runs sampled value quantisation
    through the explicit CPU-JIT kernel before either bounded host reduction.
    This is a hybrid contract, not a claim that Taichi currently provides
    QR/SVD, Robertson reductions, or target-qualified AOT response calibration.
    """

    backend_name = _backend_name(backend)
    method_name = _normalise_response_method(method)
    if int(levels) < 16 or int(levels) > 4096:
        raise ValueError("levels must be between 16 and 4096")
    if int(sample_count) < 16 or int(sample_count) > 4096:
        raise ValueError("sample_count must be between 16 and 4096")
    if int(iterations) < 1 or int(iterations) > 64:
        raise ValueError("iterations must be between 1 and 64")
    if not np.isfinite(float(smooth_lambda)) or float(smooth_lambda) < 0.0:
        raise ValueError("smooth_lambda must be finite and non-negative")
    if not np.isfinite(float(reference_value)) or not 0.0 < float(reference_value) < 1.0:
        raise ValueError("reference_value must be finite and between 0 and 1")
    arrays, channel_count = _validate_stack(
        images,
        max_pixels=int(max_pixels),
        max_working_bytes=int(max_working_bytes),
    )
    times = _validate_times(exposure_times, len(arrays))
    pixel_count = int(arrays[0].shape[0]) * int(arrays[0].shape[1])
    requested = min(int(sample_count), pixel_count)
    stack_bytes = _estimate_stack_working_bytes(pixel_count, channel_count, len(arrays))
    if method_name == "robertson":
        solver_bytes = _estimate_robertson_solver_bytes(len(arrays), requested, int(levels))
    else:
        solver_bytes = _estimate_debevec_solver_bytes(len(arrays), requested, int(levels))
    total_estimate = int(stack_bytes + solver_bytes)
    if total_estimate > int(max_working_bytes):
        raise MemoryError(
            f"HDR response calibration requires about {total_estimate} bytes "
            f"(including bounded response-solver workspace), limit is {int(max_working_bytes)}"
        )
    sample_indices = np.linspace(0, pixel_count - 1, requested, dtype=np.int64)
    stack = np.stack([array.reshape(pixel_count, -1) for array in arrays], axis=0)
    curves = np.empty((int(levels), channel_count), dtype=np.float32)
    for channel in range(channel_count):
        values = stack[:, sample_indices, channel]
        if backend_name == "taichi":
            # The sampled value-to-code conversion is a bounded, independent
            # Taichi kernel.  The selected response solver remains an explicit
            # bounded host reduction and is intentionally not hidden behind a
            # claimed native QR/SVD/Robertson implementation.
            quantised = _response_quantise_taichi(values, int(levels))
        elif backend_name == "aot":
            from ..aot_api.research import hdr_response_quantise_aot

            # The AOT leaf operates on one flattened channel at a time; the
            # bounded Debevec/Robertson reduction remains explicit host work.
            quantised = hdr_response_quantise_aot(
                np.ascontiguousarray(values.reshape(-1), dtype=np.float32),
                levels=int(levels),
            ).reshape(values.shape)
        else:
            quantised = np.rint(np.clip(values, 0.0, 1.0) * float(int(levels) - 1)).astype(np.int32)
        if method_name == "robertson":
            curves[:, channel] = _solve_channel_robertson(
                quantised,
                np.log(times),
                levels=int(levels),
                smooth_lambda=float(smooth_lambda),
                reference_value=float(reference_value),
                iterations=int(iterations),
            )
        else:
            curves[:, channel] = _solve_channel(
                quantised,
                np.log(times),
                levels=int(levels),
                smooth_lambda=float(smooth_lambda),
                reference_value=float(reference_value),
                backend=backend_name,
            )
    if method_name == "robertson":
        solver_backend = {
            "taichi": "taichi-quantize+numpy-robertson",
            "aot": "aot-quantize+numpy-robertson",
            "numpy": "numpy-robertson",
        }[backend_name]
    else:
        solver_backend = {
            "taichi": "taichi-quantize+numpy-lstsq",
            "aot": "aot-quantize+numpy-lstsq",
            "numpy": "numpy-lstsq",
        }[backend_name]
    return ResponseCalibration(
        curve=np.ascontiguousarray(curves),
        exposure_times=np.ascontiguousarray(times),
        levels=int(levels),
        sample_count=int(requested),
        backend=backend_name,
        reference_value=float(reference_value),
        solver_backend=solver_backend,
        method=method_name,
    )


def estimate_response_curve_robertson(
    images: Sequence[Any],
    exposure_times: Sequence[float],
    *,
    levels: int = 256,
    sample_count: int = 512,
    smooth_lambda: float = 10.0,
    reference_value: float = 0.5,
    iterations: int = 8,
    backend: str = "numpy",
    max_pixels: int = MAX_HDR_PIXELS,
    max_working_bytes: int = DEFAULT_MAX_WORKING_BYTES,
) -> ResponseCalibration:
    """Explicit Robertson response-calibration convenience wrapper.

    The wrapper delegates to :func:`estimate_response_curve` so sampling,
    validation, memory guards, and backend semantics cannot drift between
    response solvers.
    """

    return estimate_response_curve(
        images,
        exposure_times,
        levels=levels,
        sample_count=sample_count,
        smooth_lambda=smooth_lambda,
        reference_value=reference_value,
        backend=backend,
        max_pixels=max_pixels,
        max_working_bytes=max_working_bytes,
        method="robertson",
        iterations=iterations,
    )


def _validate_calibration(calibration: ResponseCalibration, channels: int) -> np.ndarray:
    curve = np.asarray(calibration.curve, dtype=np.float32)
    if curve.ndim != 2 or curve.shape[1] != int(channels) or curve.shape[0] != int(calibration.levels):
        raise ValueError("calibration curve shape must be (levels, channel_count)")
    if not np.isfinite(curve).all():
        raise ValueError("calibration curve must contain only finite values")
    return curve


def _merge_radiance_taichi(
    arrays: Sequence[np.ndarray],
    times: np.ndarray,
    *,
    calibration: ResponseCalibration | None,
    levels: int,
) -> np.ndarray:
    """Run the bounded radiance merge kernels on the CPU JIT backend."""

    _ensure_taichi_cpu()
    first = arrays[0]
    height, width = int(first.shape[0]), int(first.shape[1])
    channels = 1 if first.ndim == 2 else int(first.shape[2])
    stack = np.stack(
        [array[..., None] if array.ndim == 2 else array for array in arrays],
        axis=0,
    ).astype(np.float32, copy=False)
    times_f32 = np.ascontiguousarray(times, dtype=np.float32)
    output = np.empty((height, width, channels), dtype=np.float32)
    if calibration is None:
        _merge_linear_kernel(
            stack,
            times_f32,
            output,
            height,
            width,
            channels,
            len(arrays),
            int(levels),
        )
    else:
        curve = _validate_calibration(calibration, channels)
        if int(curve.shape[0]) != int(levels):
            raise ValueError("calibration levels do not match the requested merge levels")
        _merge_log_kernel(
            stack,
            times_f32,
            np.ascontiguousarray(curve, dtype=np.float32),
            output,
            height,
            width,
            channels,
            len(arrays),
            int(levels),
        )
    result = output[..., 0] if first.ndim == 2 else output
    return np.ascontiguousarray(result, dtype=np.float32)


def merge_radiance(
    images: Sequence[Any],
    exposure_times: Sequence[float],
    *,
    calibration: ResponseCalibration | None = None,
    method: str = "weighted",
    levels: int = 256,
    backend: str = "numpy",
    max_pixels: int = MAX_HDR_PIXELS,
    max_working_bytes: int = DEFAULT_MAX_WORKING_BYTES,
) -> np.ndarray:
    """Merge exposure images into a floating-point radiance estimate.

    With ``calibration`` this evaluates the calibrated log response and
    computes ``exp(weighted(g(z)-log(t)))``.  Without it, the explicit
    ``method="weighted"`` path assumes linear encoded values and averages
    ``image / exposure_time`` using the same triangular weights.
    """

    backend_name = _backend_name(backend)
    arrays, channel_count = _validate_stack(
        images,
        max_pixels=int(max_pixels),
        max_working_bytes=int(max_working_bytes),
    )
    times = _validate_times(exposure_times, len(arrays))
    method_name = str(method).lower()
    if method_name not in {"weighted", "log"}:
        raise ValueError("method must be 'weighted' or 'log'")
    if method_name == "log" and calibration is None:
        raise ValueError("method='log' requires a ResponseCalibration")
    if int(levels) < 16 or int(levels) > 4096:
        raise ValueError("levels must be between 16 and 4096")
    if calibration is not None:
        levels = int(calibration.levels)
        curve = _validate_calibration(calibration, channel_count)
    else:
        curve = None
    if backend_name == "taichi":
        return _merge_radiance_taichi(
            arrays,
            times,
            calibration=calibration,
            levels=int(levels),
        )
    if backend_name == "aot":
        from ..aot_api.research import hdr_merge_linear_aot, hdr_merge_log_aot

        stack = np.stack(
            [array[..., None] if array.ndim == 2 else array for array in arrays],
            axis=0,
        ).astype(np.float32, copy=False)
        if calibration is None:
            output = hdr_merge_linear_aot(stack, times, levels=int(levels))
        else:
            output = hdr_merge_log_aot(
                stack,
                times,
                curve,
                levels=int(levels),
            )
        result = output[..., 0] if arrays[0].ndim == 2 else output
        return np.ascontiguousarray(result, dtype=np.float32)
    pixel_count = int(arrays[0].shape[0]) * int(arrays[0].shape[1])
    stack = np.stack([array.reshape(pixel_count, -1) for array in arrays], axis=0)
    values = np.clip(stack, 0.0, 1.0)
    quantised = np.rint(values * float(int(levels) - 1)).astype(np.int32)
    weights = np.where(
        quantised <= 0.5 * float(int(levels) - 1),
        quantised,
        int(levels) - 1 - quantised,
    ).astype(np.float32)
    weights = np.maximum(weights, 1.0e-3)
    if curve is None:
        estimates = values / times[:, None, None]
        numerator = np.sum(weights * estimates, axis=0)
        denominator = np.sum(weights, axis=0)
        merged = numerator / np.maximum(denominator, 1.0e-6)
    else:
        log_values = np.empty_like(values, dtype=np.float32)
        for channel in range(channel_count):
            log_values[:, :, channel] = curve[quantised[:, :, channel], channel]
        log_estimates = log_values - np.log(times)[:, None, None].astype(np.float32)
        numerator = np.sum(weights * log_estimates, axis=0)
        denominator = np.sum(weights, axis=0)
        merged = np.exp(numerator / np.maximum(denominator, 1.0e-6))
    output_shape = arrays[0].shape
    output = np.asarray(merged.reshape(output_shape), dtype=np.float32)
    return np.ascontiguousarray(output)


def merge_radiance_weighted(*args: Any, **kwargs: Any) -> np.ndarray:
    """Compatibility spelling for the explicit weighted merge path."""

    kwargs["method"] = "weighted"
    return merge_radiance(*args, **kwargs)


__all__ = [
    "ResponseCalibration",
    "response_weight",
    "estimate_response_curve",
    "estimate_response_curve_robertson",
    "merge_radiance",
    "merge_radiance_weighted",
]
