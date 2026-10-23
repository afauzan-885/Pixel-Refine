"""RAW Bayer-CFA carrier mechanics for the shared resident lifecycle.

The analysis contract is owned by ``resident_pipeline``.  This module keeps
only the RAW-specific carrier work auditable: RGB is used for alignment and
WeightNet/SpatialFusion analysis, while CFA planes receive the final warp and
accumulation for Average, SpatialFusion, or FusionNet.  The compatibility
runner remains temporarily available as a migration oracle.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional, Sequence, Tuple

import numpy as np
import os

from .metadata import normalize_cfa_rgb_codes
from .result import RawPipelineResult
from ..contracts import (
    FrameMetadata,
    ProviderFrame,
    ResidentAnalysisContext,
    ResidentResult,
    ResidentGeometry,
    scale_homography,
)

_NO_ALIGNMENT = {"", "none", "no alignment", "no_alignment", "off"}

def _release(buffer) -> None:
    if buffer is None:
        return
    if isinstance(buffer, (tuple, list)):
        for item in buffer:
            _release(item)
        return
    from ....pipeline_runtime import current_pipeline_runtime
    runtime = current_pipeline_runtime()
    if runtime is not None and runtime.buffer_session is not None:
        runtime.buffer_session.release_tree(buffer)
        return
    for method_name in ("release", "destroy"):
        method = getattr(buffer, method_name, None)
        if callable(method):
            method()
            return

def _is_cancelled(stop_event) -> bool:
    if stop_event is None:
        return False
    if hasattr(stop_event, "is_set"):
        return bool(stop_event.is_set())
    return bool(stop_event()) if callable(stop_event) else False

def _phase_planes(frame, normalized: np.ndarray) -> tuple[np.ndarray, ...]:
    """Return contiguous, phase-correct Bayer planes in tile order."""
    planes = []
    phase_origin = getattr(frame, "phase_origin", (0, 0))
    phase_y, phase_x = (int(phase_origin[0]) & 1, int(phase_origin[1]) & 1)
    for index in range(4):
        plane_y, plane_x = divmod(index, 2)
        row = (plane_y - phase_y) & 1
        col = (plane_x - phase_x) & 1
        planes.append(np.ascontiguousarray(normalized[row::2, col::2], dtype=np.float32))
    return tuple(planes)

def _normalize_phase_planes_into(frame, destinations) -> tuple[np.ndarray, ...]:
    """Normalize each CFA lattice with its own sensor black/white levels."""

    if len(destinations) != 4:
        raise ValueError("RAW Native CFA workspace must contain four planes")
    samples = np.asarray(frame.samples)
    black_levels = tuple(float(value) for value in frame.black_level)
    white_levels = tuple(float(value) for value in frame.white_level)
    if len(black_levels) not in (1, 4) or len(white_levels) not in (1, 4):
        raise ValueError("RAW Native normalization requires one or four CFA levels")
    phase_origin = getattr(frame, "phase_origin", (0, 0))
    phase_y, phase_x = (int(phase_origin[0]) & 1, int(phase_origin[1]) & 1)
    for index, destination in enumerate(destinations):
        plane_y, plane_x = divmod(index, 2)
        row = (plane_y - phase_y) & 1
        col = (plane_x - phase_x) & 1
        source = samples[row::2, col::2]
        if destination.shape != source.shape or destination.dtype != np.float32:
            raise ValueError(
                "RAW Native CFA workspace shape/dtype mismatch: "
                f"expected {source.shape}/float32, got "
                f"{destination.shape}/{destination.dtype}"
            )
        black = np.float32(black_levels[index if len(black_levels) == 4 else 0])
        white = np.float32(white_levels[index if len(white_levels) == 4 else 0])
        inverse_range = np.float32(1.0) / np.maximum(
            np.float32(1.0), np.float32(white - black)
        )
        np.subtract(source, black, out=destination, dtype=np.float32)
        np.multiply(destination, inverse_range, out=destination)
        np.clip(
            destination,
            np.float32(0.0),
            np.float32(1.0),
            out=destination,
        )
    return tuple(destinations)

def _normalized_for_rgb_parity(frame) -> np.ndarray:
    """Normalize a CFA carrier while preserving per-plane sensor levels.

    The legacy name remains for internal compatibility. Fusion consumes RAW
    sensor samples, so black and white levels follow the DNG's four spatial
    CFA entries (including fractional black levels) before phase-aware
    warping. Values remain clamped to the normalized sensor interval.
    """

    samples = np.asarray(frame.samples)
    if samples.ndim != 2:
        raise ValueError("RAW Native normalization requires a 2D CFA mosaic")
    normalized = np.empty(samples.shape, dtype=np.float32)
    black_levels = tuple(float(value) for value in frame.black_level)
    white_levels = tuple(float(value) for value in frame.white_level)
    if len(black_levels) not in (1, 4) or len(white_levels) not in (1, 4):
        raise ValueError("RAW Native normalization requires one or four CFA levels")
    phase_origin = getattr(frame, "phase_origin", (0, 0))
    phase_y, phase_x = (int(phase_origin[0]) & 1, int(phase_origin[1]) & 1)
    for index in range(4):
        plane_y, plane_x = divmod(index, 2)
        row = (plane_y - phase_y) & 1
        col = (plane_x - phase_x) & 1
        black = np.float32(black_levels[index if len(black_levels) == 4 else 0])
        white = np.float32(white_levels[index if len(white_levels) == 4 else 0])
        inverse_range = np.float32(1.0) / np.maximum(
            np.float32(1.0), np.float32(white - black)
        )
        destination = normalized[row::2, col::2]
        np.subtract(samples[row::2, col::2], black, out=destination, dtype=np.float32)
        np.multiply(destination, inverse_range, out=destination)
        np.clip(destination, np.float32(0.0), np.float32(1.0), out=destination)
    return np.ascontiguousarray(normalized, dtype=np.float32)

def _plane_homography(matrix: np.ndarray, frame, index: int) -> np.ndarray:
    """Conjugate a support-to-reference homography into one Bayer lattice."""
    plane_y, plane_x = divmod(int(index), 2)
    origin_y = (plane_y - int(frame.phase_origin[0])) & 1
    origin_x = (plane_x - int(frame.phase_origin[1])) & 1
    plane_to_sensor = np.asarray(
        ((2.0, 0.0, origin_x), (0.0, 2.0, origin_y), (0.0, 0.0, 1.0)),
        dtype=np.float32,
    )
    return np.ascontiguousarray(
        np.linalg.inv(plane_to_sensor) @ np.asarray(matrix, dtype=np.float32) @ plane_to_sensor,
        dtype=np.float32,
    )

def _analysis_proxy(
    path: str | Path,
    *,
    width: int,
    height: int,
    scale: float,
    source_gpu=None,
    auto_enhance_params: Optional[dict] = None,
):
    """Build the RGB analysis proxy while keeping RAW fusion linear.

    ``auto_enhance_params`` is computed once from the full-resolution
    reference and reused for WeightNet frames when supplied. SpatialFusion
    passes no parameters and uses linear reference/support proxies. The CFA
    carrier is never tone-mapped or contrast-enhanced.
    """
    from taichi_vision import taichi_aot
    from ..resident_pipeline import _managed_api
    taichi_aot = _managed_api(taichi_aot)

    from ..resident_pipeline import prepare_analysis_proxy_gpu

    proxy = source_gpu
    owns_proxy = proxy is None
    if proxy is None:
        proxy = taichi_aot.demosaic(str(path), method="hamilton", return_gpu=True)
    work_h = max(32, int(height * scale))
    work_w = max(32, int(width * scale))
    work = prepare_analysis_proxy_gpu(
        proxy,
        work_shape=(work_h, work_w),
        analysis_params=auto_enhance_params,
    )
    # A caller-provided source remains caller-owned.  The helper returns a
    # temporary only when resize/enhancement was required.
    if work is not proxy and proxy is not None:
        _release(proxy)
    return work

def _warp_analysis_proxy(proxy_gpu, transform, *, height: int, width: int):
    """Warp a work-resolution analysis proxy for SpatialFusion weights."""
    from taichi_vision import taichi_aot
    from ..resident_pipeline import _managed_api
    taichi_aot = _managed_api(taichi_aot)

    if isinstance(transform, np.ndarray) and transform.ndim == 2 and transform.shape == (3, 3):
        return taichi_aot.warp_perspective(
            proxy_gpu,
            transform,
            (int(width), int(height)),
            return_gpu=True,
        )
    return taichi_aot.remap_with_flow(
        proxy_gpu,
        transform,
        int(height),
        int(width),
        return_gpu=True,
    )

def _analysis_transform(transform, *, full_shape, proxy_shape):
    """Return the transform in the proxy coordinate system.

    Feature matching returns a full-resolution homography.  Dense optical
    flow already carries work-resolution vectors, so it must pass through
    unchanged.  Keeping this conversion at the provider boundary prevents a
    full-resolution translation from being magnified when the proxy is
    downscaled.
    """

    if transform is None or not isinstance(transform, np.ndarray):
        return transform
    # Dense flow is already expressed in work-grid pixel units.  Only a
    # 3x3 matrix is a full-resolution feature transform here.
    if transform.ndim != 2 or transform.shape != (3, 3):
        return transform
    return scale_homography(
        transform,
        source_shape=(int(full_shape[0]), int(full_shape[1])),
        destination_shape=(int(proxy_shape[0]), int(proxy_shape[1])),
    )

def _accumulate_homography_cfa(
    source_planes,
    homography,
    *,
    frame,
    zero_flow_gpu,
    weight_map_gpu,
    sum_gpu,
    weight_gpu,
):
    """Warp CFA planes independently, then accumulate them in reference phase."""
    from taichi_vision import taichi_aot
    from ..resident_pipeline import _managed_api
    taichi_aot = _managed_api(taichi_aot)
    from taichi_vision.taichi_algorithm.spatial_fusion import (
        accumulate_cfa_homography_taichi,
        remap_accumulate_cfa_weighted_taichi,
    )

    # Phase-aware direct gather is the production RAW path: the inverse
    # homography is evaluated at each destination CFA site and the source is
    # interpolated only within the matching colour plane.  The historical
    # plane-warp implementation remains available explicitly through
    # ``PIXEL_REFINE_CFA_WARP_MODE=legacy_plane`` for parity/rollback tests.
    # Keeping this switch internal preserves the public alignment API.
    direct_mode = os.environ.get(
        "PIXEL_REFINE_CFA_WARP_MODE", "direct_homography"
    ).strip().lower()
    if direct_mode in {"direct", "direct_homography", "gather"}:
        accumulate_cfa_homography_taichi(
            source_planes,
            homography,
            weight_map_gpu,
            sum_gpu,
            weight_gpu,
            full_shape=frame.shape,
            cfa_pattern=normalize_cfa_rgb_codes(frame.cfa_pattern),
            phase_origin=frame.phase_origin,
        )
        return

    warped_planes = []
    try:
        for index, source_plane in enumerate(source_planes):
            h_plane, w_plane = (int(source_plane.shape[0]), int(source_plane.shape[1]))
            warped_planes.append(
                taichi_aot.warp_perspective(
                    source_plane,
                    _plane_homography(homography, frame, index),
                    (w_plane, h_plane),
                    return_gpu=True,
                )
            )
        remap_accumulate_cfa_weighted_taichi(
            warped_planes,
            zero_flow_gpu,
            weight_map_gpu,
            sum_gpu,
            weight_gpu,
            full_shape=frame.shape,
            cfa_pattern=normalize_cfa_rgb_codes(frame.cfa_pattern),
            phase_origin=frame.phase_origin,
        )
    finally:
        for plane in warped_planes:
            _release(plane)

def _validate_support(reference, support, path: str | Path) -> None:
    """Fail before mixing sensor contracts that cannot be fused safely."""
    checks = {
        "shape": (reference.shape, support.shape),
        "bits_per_sample": (reference.bits_per_sample, support.bits_per_sample),
        "cfa_pattern": (reference.cfa_pattern, support.cfa_pattern),
        "phase_origin": (reference.phase_origin, support.phase_origin),
        "orientation": (reference.orientation, support.orientation),
    }
    mismatches = [name for name, (left, right) in checks.items() if left != right]
    if mismatches:
        raise ValueError(
            f"RAW Native requires an identical DNG sensor contract; {Path(path).name} "
            f"differs in {', '.join(mismatches)}"
        )

def _preview_from_mosaic(
    mosaic,
    frame,
    reference_path: str | Path,
    *,
    return_gpu: bool = False,
):
    """Demosaic once after CFA accumulation, solely for the desktop preview."""
    from taichi_vision import taichi_aot
    from ..resident_pipeline import _managed_api
    taichi_aot = _managed_api(taichi_aot)

    from .metadata import extract_demosaic_parameters

    try:
        params = extract_demosaic_parameters(
            reference_path, frame.cfa_pattern, frame=frame
        )
        print(
            "[RAW Native] Preview colour contract: "
            f"{params.pop('white_balance_source')} WB + ColorMatrix1"
        )
    except Exception as exc:
        # The DNG output still retains its colour metadata.  This fallback is
        # only for a corrupt/unsupported source preview and is deliberately
        # visible in the log, never used for a normal camera DNG.
        c00, c01, c10, c11 = normalize_cfa_rgb_codes(frame.cfa_pattern)
        print(f"[RAW Native] Preview colour metadata unavailable: {exc}; using neutral preview")
        params = {
            "wb_r": 1.0, "wb_g1": 1.0, "wb_b": 1.0, "wb_g2": 1.0,
            "cmatrix": np.eye(3, dtype=np.float32), "black_level": 0.0,
            "white_level": 1.0, "c00": c00, "c01": c01, "c10": c10, "c11": c11,
        }
    source = (
        mosaic
        if hasattr(mosaic, "to_numpy")
        else np.ascontiguousarray(mosaic, dtype=np.float32)
    )
    return taichi_aot.demosaic(
        source,
        **params,
        method="hamilton",
        return_gpu=bool(return_gpu),
    )

def _demosaic_carrier_gpu(carrier, *, method="bilinear", dst=None, half_res=False):
    """Demosaic an already-decoded carrier without a second file decode.

    Analysis uses bilinear demosaicing (half_res=True directly produces the
    half-resolution analysis proxy, eliminating redundant full-resolution buffer
    allocation and downscaling); the final CFA preview remains Hamilton.
    Sensor normalization, WB and camera matrix still come from the decoded
    carrier. No file re-open or CPU demosaic is introduced. ``method``
    permits an explicit Hamilton quality oracle, not a silent backend fallback.
    """
    from taichi_vision import taichi_aot
    from ..resident_pipeline import _managed_api
    taichi_aot = _managed_api(taichi_aot)

    from .metadata import carrier_demosaic_parameters

    params = carrier_demosaic_parameters(carrier)
    extra_kwargs = {"half_res": True} if half_res else {}
    return taichi_aot.demosaic(
        np.ascontiguousarray(carrier.samples),
        **params,
        method=method,
        return_gpu=True,
        dst=dst,
        **extra_kwargs,
    )

class _RawDngHostPayload:
    """Queue-owned RAW bytes that can be dropped immediately after decoding."""

    __slots__ = ("_data",)

    def __init__(self, data: bytes):
        self._data: bytes | None = data

    def __len__(self) -> int:
        return 0 if self._data is None else len(self._data)

    def take(self) -> bytes:
        if self._data is None:
            raise RuntimeError("RAW DNG payload was already consumed or released")
        data = self._data
        self._data = None
        return data

    def close(self) -> None:
        self._data = None

class RawPipelineProvider:
    """RAW Native carrier boundary used by the resident dispatcher.

    ``run`` is retained as a compatibility entry point, but delegates to the
    shared resident executor.  The former standalone runner remains available
    privately as ``_legacy_run_raw_resident_pipeline`` for comparison.
    """

    source_mode = "raw"
    carrier_kind = "cfa"

    def __init__(self, image_paths, **options):
        self.image_paths = tuple(str(path) for path in image_paths)
        self.options = dict(options)
        self._engine = None
        self._reference_frame = None
        self._sum_gpu = None
        self._weight_gpu = None
        self._zero_flow_gpu = None
        self._one_weight_gpu = None
        self._cfa_plane_shape = None
        self._cfa_planes_host = None
        self._cfa_planes_gpu = None
        self._cfa_buffer_session = None
        self._cfa_planes_initialized = False
        self._cfa_staged_carrier = None
        self._finalized = False

    def _read_frame(self, index: int):
        from taichi_vision.taichi_algorithm.compression import RawMosaicFrame, read_dng_aot

        path = self.image_paths[int(index)]
        return RawMosaicFrame.from_dng(
            read_dng_aot(path),
            source_id=path,
        )

    def load_support_dng_bytes_host(self, index: int) -> bytes:
        """Read an unchanged support DNG container for the bounded host queue."""

        return Path(self.image_paths[int(index)]).read_bytes()

    def load_support_dng_payload_host(self, index: int) -> _RawDngHostPayload:
        """Read a DNG container into a releasable queue payload."""

        return _RawDngHostPayload(self.load_support_dng_bytes_host(index))

    def decode_support_dng_bytes_host(
        self, index: int, dng_bytes: bytes
    ) -> ProviderFrame:
        """Decode a prefetched DNG after it has left the host queue."""

        from taichi_vision.taichi_algorithm.compression import RawMosaicFrame, read_dng_aot

        path = self.image_paths[int(index)]
        frame = RawMosaicFrame.from_dng(read_dng_aot(dng_bytes), source_id=path)
        return self._support_provider_frame(index, frame)

    def _support_provider_frame(self, index: int, frame) -> ProviderFrame:
        return ProviderFrame(
            carrier=frame,
            metadata=FrameMetadata(
                source_id=self.image_paths[int(index)],
                shape=tuple(int(value) for value in frame.shape),
                dtype="float32",
                color_model="cfa_linear",
                carrier_kind="cfa",
                orientation=int(frame.orientation),
                extra={
                    "bits_per_sample": int(frame.bits_per_sample),
                    "cfa_pattern": tuple(int(value) for value in frame.cfa_pattern),
                    "phase_origin": tuple(int(value) for value in frame.phase_origin),
                },
            ),
        )

    def load_reference(self) -> ProviderFrame:
        if self._reference_frame is None:
            self._reference_frame = self._read_frame(0)
        frame = self._reference_frame
        return ProviderFrame(
            carrier=frame,
            metadata=FrameMetadata(
                source_id=self.image_paths[0],
                shape=tuple(int(value) for value in frame.shape),
                dtype="float32",
                color_model="cfa_linear",
                carrier_kind="cfa",
                orientation=int(frame.orientation),
                extra={
                    "bits_per_sample": int(frame.bits_per_sample),
                    "cfa_pattern": tuple(int(value) for value in frame.cfa_pattern),
                    "phase_origin": tuple(int(value) for value in frame.phase_origin),
                },
            ),
        )

    def load_support(self, index: int) -> ProviderFrame:
        return self._support_provider_frame(index, self._read_frame(index))

    def load_analysis_proxy(self, frame: ProviderFrame, *, work_shape, analysis_params=None):
        """Build the shared RGB proxy used only for alignment/weight analysis."""

        from ..resident_pipeline import prepare_analysis_proxy_gpu

        carrier_h, carrier_w = frame.carrier.samples.shape[:2]
        use_half_res = (
            work_shape is not None
            and work_shape[0] <= carrier_h // 2
            and work_shape[1] <= carrier_w // 2
        )
        proxy = _demosaic_carrier_gpu(frame.carrier, half_res=use_half_res)
        try:
            analysis = prepare_analysis_proxy_gpu(
                proxy,
                work_shape=work_shape,
                analysis_params=analysis_params,
                in_place=True,
                source_is_disposable=True,
            )
            if analysis is not proxy:
                _release(proxy)
            return analysis
        except Exception:
            _release(proxy)
            raise

    def bind_accumulator(self, engine, reference: ProviderFrame | None = None) -> None:
        """Allocate the persistent CFA accumulator for the shared frame loop."""

        if self._sum_gpu is not None:
            raise RuntimeError("RAW Native accumulator is already bound")
        if reference is None:
            reference = self.load_reference()
        frame = reference.carrier
        self._engine = engine
        normalized = _normalized_for_rgb_parity(frame)
        try:
            self._sum_gpu = engine.upload(
                np.ascontiguousarray(normalized, dtype=np.float32)
            )
            self._weight_gpu = engine.upload(
                np.ones(frame.shape, dtype=np.float32)
            )
            self._zero_flow_gpu = engine.upload(
                np.zeros((1, 1, 2), dtype=np.float32),
                is_vector=False,
            )
            self._one_weight_gpu = engine.upload(
                np.ones((1, 1, 3), dtype=np.float32),
                is_vector=False,
            )
        finally:
            del normalized

    def _ensure_cfa_workspace(self, frame) -> None:
        """Allocate one reusable host/GPU CFA plane set for this burst."""

        samples = np.asarray(frame.samples)
        phase_y, phase_x = (int(frame.phase_origin[0]) & 1, int(frame.phase_origin[1]) & 1)
        shapes = []
        for index in range(4):
            plane_y, plane_x = divmod(index, 2)
            row = (plane_y - phase_y) & 1
            col = (plane_x - phase_x) & 1
            shapes.append(tuple(int(value) for value in samples[row::2, col::2].shape))
        shape_key = tuple(shapes)
        if self._cfa_planes_gpu is not None:
            if self._cfa_plane_shape != shape_key:
                raise ValueError("RAW Native CFA carrier shape changed within one burst")
            return

        host_planes = [np.empty(shape, dtype=np.float32) for shape in shapes]
        gpu_planes = []
        try:
            from ....pipeline_runtime import current_pipeline_runtime

            runtime = current_pipeline_runtime()
            buffer_session = (
                runtime.buffer_session if runtime is not None else None
            )
            for index, shape in enumerate(shapes):
                if buffer_session is not None:
                    buffer = buffer_session.acquire_buffer(
                        shape,
                        dtype=np.float32,
                        is_vector=False,
                        tag=f"raw-native-cfa-plane-{id(self)}-{index}",
                    )
                else:
                    buffer = self._engine.allocate(
                        shape, dtype=np.float32, is_vector=False
                    )
                gpu_planes.append(buffer)
        except Exception:
            for buffer in gpu_planes:
                _release(buffer)
            raise
        self._cfa_plane_shape = shape_key
        self._cfa_planes_host = host_planes
        self._cfa_planes_gpu = gpu_planes
        self._cfa_buffer_session = buffer_session

    def accumulate(self, frame: ProviderFrame, transform=None, weight_map=None) -> None:
        """Warp one CFA carrier and accumulate it with the shared weight map."""

        if self._sum_gpu is None or self._weight_gpu is None or self._engine is None:
            raise RuntimeError("RAW Native accumulator is not bound")
        if frame is None or frame.carrier is None:
            raise ValueError("RAW Native accumulate requires a provider frame")
        reference = self.load_reference().carrier
        support = frame.carrier
        _validate_support(reference, support, frame.metadata.source_id)

        from taichi_vision import taichi_aot

        from ..resident_pipeline import _managed_api

        taichi_aot = _managed_api(taichi_aot)
        from taichi_vision.taichi_algorithm.spatial_fusion import (
            remap_accumulate_cfa_weighted_taichi,
        )

        self._ensure_cfa_workspace(support)
        gpu_planes = self._cfa_planes_gpu
        active_weight = weight_map if weight_map is not None else self._one_weight_gpu
        # Deep Analysis accumulates several confidence maps for the same RAW
        # frame (center plus selected neighboring patches). Its CFA samples do
        # not change between those calls, so normalize and upload the four Bayer
        # planes once, then reuse the resident planes for every candidate map.
        # Keep the existing staging behavior when a different frame arrives.
        if self._cfa_staged_carrier is not support:
            planes = _normalize_phase_planes_into(support, self._cfa_planes_host)
            # A mapped host-accessible plane can still be read by queued
            # kernels; synchronize once before overwriting the set.
            # Device-local writes use the engine's staging/copy route, which
            # orders against prior work.
            if self._cfa_planes_initialized and any(
                bool(getattr(buffer, "host_accessible", False))
                for buffer in gpu_planes
            ):
                self._engine.sync()
            for destination, plane in zip(gpu_planes, planes):
                self._engine.write_into(destination, plane, synchronize=False)
            self._cfa_planes_initialized = True
            self._cfa_staged_carrier = support
        if isinstance(transform, np.ndarray) and transform.ndim == 2 and transform.shape == (3, 3):
            _accumulate_homography_cfa(
                gpu_planes,
                transform,
                frame=reference,
                zero_flow_gpu=self._zero_flow_gpu,
                weight_map_gpu=active_weight,
                sum_gpu=self._sum_gpu,
                weight_gpu=self._weight_gpu,
            )
        else:
            remap_accumulate_cfa_weighted_taichi(
                gpu_planes,
                transform if transform is not None else self._zero_flow_gpu,
                active_weight,
                self._sum_gpu,
                self._weight_gpu,
                full_shape=reference.shape,
                cfa_pattern=normalize_cfa_rgb_codes(reference.cfa_pattern),
                phase_origin=reference.phase_origin,
            )

    def finalize(self, mean_alpha: float = 1.0) -> ResidentResult:
        """Normalize the CFA accumulator and create the one-time RGB preview."""

        if self._sum_gpu is None or self._weight_gpu is None or self._engine is None:
            raise RuntimeError("RAW Native accumulator is not bound")
        from taichi_vision.taichi_algorithm.spatial_fusion import (
            normalize_accumulator_cfa_taichi,
        )

        normalize_accumulator_cfa_taichi(self._sum_gpu, self._weight_gpu)
        self._engine.sync()
        reference = self.load_reference().carrier
        preview = None
        try:
            preview = _preview_from_mosaic(
                self._sum_gpu,
                reference,
                self.image_paths[0],
                return_gpu=True,
            )
            mosaic = np.empty(self._sum_gpu.shape, dtype=np.float32)
            self._sum_gpu.to_numpy(out=mosaic)
            preview_rgb = preview.to_numpy()
        finally:
            _release(preview)
        result = RawPipelineResult(
            normalized_mosaic=mosaic,
            preview_rgb=np.ascontiguousarray(preview_rgb, dtype=np.float32),
            reference_frame=reference,
            source_paths=self.image_paths,
            report={
                "mean_alpha": float(mean_alpha),
                "supports": max(0, len(self.image_paths) - 1),
                "mode": "shared_cfa_provider",
            },
        )
        self._finalized = True
        return ResidentResult(
            value=result,
            mean_alpha=float(mean_alpha),
            source_mode="raw",
            report=dict(result.report or {}),
        )

    def run(self):
        from ..resident_pipeline import _run_shared_raw_provider_pipeline

        return _run_shared_raw_provider_pipeline(
            self.image_paths,
            **self.options,
        )

    def close(self) -> None:
        for name in (
            "_sum_gpu",
            "_weight_gpu",
            "_zero_flow_gpu",
            "_one_weight_gpu",
        ):
            _release(getattr(self, name, None))
            setattr(self, name, None)
        if self._cfa_planes_gpu is not None:
            if self._cfa_buffer_session is not None:
                self._cfa_buffer_session.release_tree(self._cfa_planes_gpu)
            else:
                _release(self._cfa_planes_gpu)
            self._cfa_planes_gpu = None
        # The cached RawMosaicFrame owns the decoded host carrier.  Drop it at
        # the same lifecycle boundary as the GPU accumulator so a completed
        # burst cannot retain its reference image in the provider instance.
        self._reference_frame = None
        self._cfa_planes_host = None
        self._cfa_plane_shape = None
        self._cfa_buffer_session = None
        self._cfa_planes_initialized = False
        self._cfa_staged_carrier = None
        self._engine = None
        return None

def run_raw_resident_pipeline(image_paths, **kwargs):
    """Run the canonical RAW path through the shared resident executor."""
    from ..resident_pipeline import _run_shared_raw_provider_pipeline

    return _run_shared_raw_provider_pipeline(image_paths, **kwargs)

__all__ = ["RawPipelineProvider", "run_raw_resident_pipeline"]
