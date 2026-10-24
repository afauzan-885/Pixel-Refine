"""Regression tests for the resident pipeline package migration."""

from __future__ import annotations

from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.pipeline_process import (
    resident_pipeline as canonical_resident,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.pipeline_process.contracts import (
    FrameMetadata,
    ProviderFrame,
    ResidentGeometry,
    scale_homography,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.pipeline_process.telemetry import (
    PipelineTelemetry,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.pipeline_process.raw_pipeline.provider import (
    RawPipelineProvider,
    _analysis_transform,
    _normalize_phase_planes_into,
    _normalized_for_rgb_parity,
    _phase_planes,
    _warp_analysis_proxy,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.pipeline_process.rgb_pipeline.provider import (
    RGBFrameProvider,
)


def test_canonical_resident_exports_public_entrypoints():
    assert callable(canonical_resident.run_resident_pipeline)
    assert callable(canonical_resident.run_gpu_resident_pipeline)
    assert callable(canonical_resident.load_frame_to_gpu)


def test_weightnet_reference_has_no_clahe(monkeypatch):
    import cv2
    import numpy as np
    from taichi_vision import taichi_aot

    def forbidden(*args, **kwargs):
        raise AssertionError("CLAHE must not run in FusionNet")

    monkeypatch.setattr(cv2, "createCLAHE", forbidden)
    monkeypatch.setattr(taichi_aot, "clahe", forbidden, raising=False)
    gray = np.linspace(0, 1, 48, dtype=np.float32).reshape(6, 8)

    class AnalysisBuffer:
        shape = gray.shape

        def to_numpy(self):
            return gray.copy()

    reference, transfer = canonical_resident.prepare_weightnet_reference_input(
        AnalysisBuffer(), work_shape=gray.shape)
    np.testing.assert_array_equal(reference, gray[None, ...])
    assert transfer is None
    legacy_reference, legacy_transfer = canonical_resident.apply_clahe_16bit_reference(reference)
    np.testing.assert_array_equal(legacy_reference, reference)
    assert legacy_transfer is None


def test_legacy_resident_import_is_a_lazy_compatibility_facade():
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising import (
        resident_pipeline as legacy_resident,
    )

    assert legacy_resident.run_resident_pipeline is canonical_resident.run_resident_pipeline


def test_fusionet_engine_reexports_canonical_resident_entrypoint():
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising import fusionet_engine

    assert fusionet_engine.run_resident_pipeline is canonical_resident.run_resident_pipeline


def test_rgb_provider_contract_accepts_only_rgb_source_paths():
    provider = RGBFrameProvider(["reference.png", "support.png"])
    metadata = provider.metadata(1, shape=(32, 48, 3))
    assert metadata.source_id == "support.png"
    assert metadata.shape == (32, 48, 3)
    assert metadata.carrier_kind == "rgb"
    assert provider.source_path(0) == "reference.png"
    assert RGBFrameProvider(["reference.png"]).source_mode == "rgb"
    import pytest

    with pytest.raises(ValueError, match="already-RGB inputs only"):
        RGBFrameProvider(["raw.DNG"])


def test_raw_provider_preserves_public_dispatch_boundary():
    provider = RawPipelineProvider(["reference.dng", "support.dng"], weight_engine="average")
    assert provider.source_mode == "raw"
    assert provider.carrier_kind == "cfa"
    assert provider.options["weight_engine"] == "average"
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.pipeline_process.raw_pipeline import (
        run_raw_resident_pipeline,
    )

    assert callable(run_raw_resident_pipeline)
    provider.close()


def test_raw_host_prefetch_bytes_decode_to_the_same_cfa_carrier(tmp_path):
    import numpy as np

    from taichi_vision.taichi_algorithm.compression import encode_dng_aot

    source = (
        np.arange(32 * 36, dtype=np.uint16).reshape(32, 36) * np.uint16(7)
    ) & np.uint16(0x0FFF)
    encoded = encode_dng_aot(
        source,
        metadata={
            "cfa_pattern": (1, 0, 0, 1),
            "black_level": 64,
            "white_level": 4095,
        },
        compression="none",
        bits_per_sample=12,
    )
    support_path = tmp_path / "support.dng"
    support_path.write_bytes(encoded)
    provider = RawPipelineProvider(
        [str(tmp_path / "reference.dng"), str(support_path)],
        weight_engine="average",
    )
    payload = provider.load_support_dng_payload_host(1)
    try:
        assert len(payload) == len(encoded)
        assert provider.load_support_dng_bytes_host(1) == encoded

        prefetched_bytes = payload.take()
        prefetched = provider.decode_support_dng_bytes_host(1, prefetched_bytes)
        del prefetched_bytes
        assert len(payload) == 0

        decoded_from_path = provider.load_support(1)
        np.testing.assert_array_equal(
            prefetched.carrier.samples,
            decoded_from_path.carrier.samples,
        )
        assert prefetched.metadata == decoded_from_path.metadata
    finally:
        payload.close()
        provider.close()


def test_rgb_host_prefetch_holds_original_file_bytes_until_decode(tmp_path):
    import numpy as np
    from PIL import Image

    pixels = np.zeros((9, 13, 3), dtype=np.uint8)
    pixels[..., 0] = np.arange(13, dtype=np.uint8)[None, :] * 17
    pixels[..., 1] = np.arange(9, dtype=np.uint8)[:, None] * 23
    pixels[..., 2] = 91
    support_path = tmp_path / "support.png"
    Image.fromarray(pixels, mode="RGB").save(support_path)

    provider = RGBFrameProvider([str(tmp_path / "reference.png"), str(support_path)])
    payload = provider.load_support_bytes_host(1)
    try:
        original_bytes = support_path.read_bytes()
        assert len(payload) == len(original_bytes)
        assert payload.take() == original_bytes
        # take() transfers the exact encoded file payload and releases the queue slot.
        payload.close()
        assert len(payload) == 0

        payload = provider.load_support_bytes_host(1)
        prefetched = provider.decode_support_bytes_host(1, payload)
        decoded_from_path = provider.load_support_host(1)
        np.testing.assert_array_equal(prefetched, decoded_from_path)
        assert len(payload) == 0
    finally:
        payload.close()
        provider.close()


def test_contract_objects_are_dependency_light():
    metadata = FrameMetadata(
        source_id="frame.png",
        shape=(8, 8, 3),
        dtype="float32",
    )
    frame = ProviderFrame(carrier=None, metadata=metadata)
    assert frame.metadata.color_model == "normalized_rgb"


def test_resident_geometry_resolves_one_effective_work_contract():
    geometry = ResidentGeometry.resolve(
        (3072, 4096), align_scale=0.50, weight_scale=0.25
    )
    assert geometry.full_shape == (3072, 4096)
    assert geometry.align_shape == (1536, 2048)
    assert geometry.weight_shape == (768, 1024)
    assert geometry.effective_align_scale == 0.50
    assert geometry.effective_weight_scale == 0.25


def test_full_resolution_homography_is_converted_to_work_coordinates():
    full_h = __import__("numpy").asarray(
        ((1.0, 0.0, 40.0), (0.0, 1.0, 20.0), (0.0, 0.0, 1.0)),
        dtype="float32",
    )
    work_h = scale_homography(
        full_h, source_shape=(3072, 4096), destination_shape=(768, 1024)
    )
    assert abs(float(work_h[0, 2]) - 10.0) < 1.0e-6
    assert abs(float(work_h[1, 2]) - 5.0) < 1.0e-6


def test_raw_analysis_transform_keeps_dense_flow_in_work_domain():
    import numpy as np

    flow = np.zeros((768, 1024, 2), dtype=np.float32)
    assert _analysis_transform(
        flow,
        full_shape=(3072, 4096),
        proxy_shape=(768, 1024),
    ) is flow


def test_raw_feature_apap_returns_local_flow_and_cleans_up_failed_remap(monkeypatch):
    import numpy as np
    import pytest
    from taichi_vision import taichi_aot
    from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.feature_matching.OFB import OFBAlgorithm
    from taichi_vision.taichi_algorithm.alignment import apap as apap_module

    class Buffer:
        def __init__(self, data):
            self.data = np.asarray(data, dtype=np.float32)
            self.shape = self.data.shape
            self.releases = 0

        def destroy(self):
            self.releases += 1

    yy, xx = np.meshgrid(np.linspace(0, 47, 6), np.linspace(0, 63, 8), indexing="ij")
    reference = np.column_stack((xx.ravel(), yy.ravel())).astype(np.float32)
    support = reference.copy()
    support[:, 0] += 2.0 * np.sin(reference[:, 0] / 15.0)
    source = Buffer(np.zeros((48, 64, 3), dtype=np.float32))
    uploads, remaps = [], []

    def upload(data, **kwargs):
        buffer = Buffer(data)
        uploads.append(buffer)
        return buffer

    def remap(src, flow, height, width, **kwargs):
        remaps.append((src, flow, height, width))
        return Buffer(np.zeros((height, width, 3), dtype=np.float32))

    monkeypatch.setattr(taichi_aot, "cvtColor", lambda *args, **kwargs: Buffer(np.zeros((48, 64))))
    monkeypatch.setattr(taichi_aot, "resize", lambda *args, **kwargs: Buffer(np.zeros((48, 64))))
    monkeypatch.setattr(taichi_aot, "match_feature_reference", lambda *args, **kwargs: (reference, support))
    monkeypatch.setattr(taichi_aot, "upload", upload)
    monkeypatch.setattr(taichi_aot, "remap_with_flow", remap)
    monkeypatch.setattr(OFBAlgorithm, "_find_homography", lambda *args, **kwargs: (np.eye(3), None))
    original_fit_apap = apap_module.fit_apap
    fit_calls = []

    def capture_fit_apap(src, dst, **kwargs):
        fit_calls.append(kwargs)
        return original_fit_apap(src, dst, **kwargs)

    monkeypatch.setattr(apap_module, "fit_apap", capture_fit_apap)

    aligner = canonical_resident.FeatureMatchingGPUAligner.__new__(canonical_resident.FeatureMatchingGPUAligner)
    aligner.work_h, aligner.work_w = 48, 64
    aligner.target_h, aligner.target_w = 96, 128
    aligner.feature_type = "ofb"
    aligner.warp_method = "apap"
    aligner.config = {}
    aligner.apap_fit_grid_size = 17
    aligner._feature_reference_cache = object()
    aligner._feature_resident_matches = False
    preview, _, transform = aligner.align_frame(source, return_transform=True)
    np.testing.assert_array_equal(fit_calls[0]["global_homography"], np.eye(3))
    assert transform is uploads[-1]
    assert transform.shape == (33, 33, 2)
    assert float(np.ptp(transform.data[..., 0])) > 0.5
    assert remaps[-1] == (source, transform, 48, 64)
    # The existing RAW provider recognises this as a local flow, not a 3x3 H.
    assert _analysis_transform(transform, full_shape=(96, 128), proxy_shape=(48, 64)) is transform
    assert source.releases == transform.releases == 0
    preview.destroy()
    transform.destroy()

    def fail_remap(*args, **kwargs):
        raise RuntimeError("injected APAP remap failure")

    monkeypatch.setattr(taichi_aot, "remap_with_flow", fail_remap)
    with pytest.raises(RuntimeError, match="injected APAP remap failure"):
        aligner.align_frame(source, return_transform=True)
    assert uploads[-1].releases == 1
    assert source.releases == 0


def test_feature_apap_alignment_keeps_image_carriers_on_device(monkeypatch):
    import numpy as np
    from taichi_vision import taichi_aot
    from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.feature_matching.OFB import OFBAlgorithm
    from taichi_vision.taichi_algorithm.alignment import mesh_warp

    class Buffer:
        def __init__(self, shape):
            self.shape = tuple(shape)
            self.data = np.zeros(self.shape, dtype=np.float32)
            self.readbacks = 0
            self.releases = 0

        def to_numpy(self):
            self.readbacks += 1
            return self.data

        def destroy(self):
            self.releases += 1

    yy, xx = np.meshgrid(np.linspace(5, 42, 6), np.linspace(5, 58, 8), indexing="ij")
    reference = np.column_stack((xx.ravel(), yy.ravel())).astype(np.float32)
    support = reference.copy()
    support[:, 0] += 1.5 * np.sin(reference[:, 0] / 15.0)
    source = Buffer((48, 64, 3))
    secondary = Buffer((48, 64, 3))
    warped = [Buffer(source.shape), Buffer(secondary.shape)]
    calls = []
    tracked = []

    monkeypatch.setattr(
        taichi_aot, "cvtColor", lambda *_args, **_kwargs: Buffer((48, 64))
    )
    monkeypatch.setattr(
        taichi_aot,
        "match_feature_reference",
        lambda *_args, **_kwargs: (reference.copy(), support.copy()),
    )
    monkeypatch.setattr(
        OFBAlgorithm,
        "_find_homography",
        lambda src, *_args, **_kwargs: (np.eye(3), np.ones(len(src), dtype=bool)),
    )

    def resident_warp(image, *args, **kwargs):
        calls.append((image, kwargs.get("return_gpu"), kwargs.get("global_homography")))
        return warped[len(calls) - 1]

    monkeypatch.setattr(mesh_warp, "warp_apap", resident_warp)
    monkeypatch.setattr(
        canonical_resident,
        "_track_gpu_result",
        lambda result: tracked.append(result) or result,
    )
    aligner = canonical_resident.FeatureMatchingGPUAligner.__new__(
        canonical_resident.FeatureMatchingGPUAligner
    )
    aligner.work_h = aligner.target_h = 48
    aligner.work_w = aligner.target_w = 64
    aligner.feature_type = "ofb"
    aligner.warp_method = "apap"
    aligner.config = {}
    aligner.apap_fit_grid_size = 17
    aligner._feature_reference_cache = object()
    aligner._feature_resident_matches = False

    primary, secondary_result = aligner.align_frame(
        source, secondary_frame_to_warp=secondary
    )

    assert primary is warped[0]
    assert secondary_result is warped[1]
    assert tracked == warped
    assert calls[:2][0][:2] == (source, True)
    assert calls[:2][1][:2] == (secondary, True)
    np.testing.assert_array_equal(calls[0][2], np.eye(3))
    np.testing.assert_array_equal(calls[1][2], np.eye(3))
    assert source.readbacks == secondary.readbacks == 0


def test_apap_fit_grid_follows_batch_preset_without_changing_flow_resolution():
    assert canonical_resident._resolve_apap_fit_grid_size({"mode": "fast"}) == 13
    assert canonical_resident._resolve_apap_fit_grid_size({"mode": "balance"}) == 17
    assert canonical_resident._resolve_apap_fit_grid_size({"mode": "high"}) == 25
    assert canonical_resident._resolve_apap_fit_grid_size(
        {"mode": "balance", "apap_fit_grid_size": 11}
    ) == 11


def test_raw_analysis_flow_warp_uses_supported_remap_arguments(monkeypatch):
    import numpy as np

    class Buffer:
        handle = object()
        dtype = np.dtype(np.float32)

    class FakeAOT:
        engine = type("Engine", (), {"arch": "cuda"})()

        def remap_with_flow(self, _src, _flow, _height, _width, *, return_gpu=False):
            self.return_gpu = return_gpu
            return object()

    fake_aot = FakeAOT()
    monkeypatch.setattr(canonical_resident, "_managed_api", lambda _api: fake_aot)
    source = Buffer()
    flow = Buffer()

    _warp_analysis_proxy(source, flow, height=48, width=64)
    assert fake_aot.return_gpu is True

    host_flow = np.zeros((12, 16, 2), dtype=np.float32)
    _warp_analysis_proxy(source, host_flow, height=48, width=64)
    assert fake_aot.return_gpu is True

    fake_aot.engine.arch = "vulkan"
    _warp_analysis_proxy(source, flow, height=48, width=64)
    assert fake_aot.return_gpu is True


def test_raw_provider_normalization_preserves_fractional_per_plane_levels():
    import numpy as np

    class FakeRawFrame:
        samples = np.asarray(
            ((63, 64, 1023), (1024, 543, 100)), dtype=np.uint16
        )
        black_level = (64.01, 63.9, 63.9, 64.0)
        white_level = (1023.0, 1023.0, 1023.0, 1023.0)

    actual = _normalized_for_rgb_parity(FakeRawFrame())
    expected = np.empty(FakeRawFrame.samples.shape, dtype=np.float32)
    for index, (black, white) in enumerate(
        zip(FakeRawFrame.black_level, FakeRawFrame.white_level)
    ):
        row, col = divmod(index, 2)
        target = expected[row::2, col::2]
        source = FakeRawFrame.samples[row::2, col::2].astype(np.float32)
        target[:] = np.clip(
            (source - np.float32(black))
            * (np.float32(1.0) / np.float32(white - black)),
            np.float32(0.0),
            np.float32(1.0),
        )

    assert actual.dtype == np.float32
    assert actual.flags.c_contiguous
    np.testing.assert_allclose(actual, expected, rtol=0.0, atol=1.0e-7)


def test_raw_normalization_removes_plane_level_pattern_from_known_flat_field():
    import numpy as np

    class FakeRawFrame:
        phase_origin = (0, 0)
        black_level = (64.0, 68.0, 72.0, 76.0)
        white_level = (1088.0, 1092.0, 1096.0, 1100.0)

        def __init__(self):
            self.samples = np.empty((32, 32), dtype=np.uint16)
            for index, black in enumerate(self.black_level):
                row, col = divmod(index, 2)
                self.samples[row::2, col::2] = int(black + 256)

    frame = FakeRawFrame()
    normalized = _normalized_for_rgb_parity(frame)
    np.testing.assert_allclose(normalized, 0.25, rtol=0.0, atol=1.0e-7)


def test_reusable_raw_cfa_plane_normalization_is_bit_exact_for_all_phases():
    import numpy as np

    class FakeRawFrame:
        def __init__(self, phase):
            self.samples = np.asarray(
                [
                    [0, 64, 128, 256, 512, 1023],
                    [32, 96, 192, 384, 768, 1200],
                    [12, 72, 140, 300, 600, 1050],
                    [24, 88, 176, 352, 704, 1150],
                ],
                dtype=np.uint16,
            )
            self.black_level = (64.9, 63.0, 66.0, 64.0)
            self.white_level = (1023.9, 1023.0, 1024.0, 1024.0)
            self.phase_origin = phase

    for phase_y in (0, 1):
        for phase_x in (0, 1):
            frame = FakeRawFrame((phase_y, phase_x))
            expected = _phase_planes(
                frame, _normalized_for_rgb_parity(frame)
            )
            destinations = tuple(
                np.empty(plane.shape, dtype=np.float32) for plane in expected
            )

            actual = _normalize_phase_planes_into(frame, destinations)

            assert actual is destinations
            for actual_plane, expected_plane in zip(actual, expected):
                np.testing.assert_array_equal(actual_plane, expected_plane)


def test_raw_pipeline_provider_reuses_host_and_gpu_cfa_plane_slots(monkeypatch):
    import numpy as np
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.pipeline_process.raw_pipeline import (
        provider as raw_provider,
    )

    class FakeRawFrame:
        def __init__(self, samples):
            self.samples = np.asarray(samples, dtype=np.uint16)
            self.black_level = (64.0, 64.0, 64.0, 64.0)
            self.white_level = (1023.0, 1023.0, 1023.0, 1023.0)
            self.phase_origin = (0, 0)
            self.shape = self.samples.shape
            self.height, self.width = self.shape
            self.bits_per_sample = 10
            self.cfa_pattern = (1, 0, 0, 2)
            self.orientation = 1

    class FakeBuffer:
        def __init__(self, shape):
            self.shape = tuple(shape)
            self.dtype = np.dtype(np.float32)
            self.host_accessible = False
            self.data = np.zeros(self.shape, dtype=np.float32)
            self.released = False

        def release(self):
            self.released = True

    class FakeEngine:
        def __init__(self):
            self.allocations = []
            self.writes = []

        def allocate(self, shape, **_kwargs):
            buffer = FakeBuffer(shape)
            self.allocations.append(buffer)
            return buffer

        def write_into(self, destination, data, *, synchronize):
            assert synchronize is False
            np.copyto(destination.data, data)
            self.writes.append(destination)
            return destination

    reference = FakeRawFrame(np.arange(48).reshape(6, 8) + 64)
    support = FakeRawFrame(np.arange(48).reshape(6, 8) + 128)
    engine = FakeEngine()
    provider = RawPipelineProvider(["reference.dng", "support.dng"])
    provider._engine = engine
    provider._reference_frame = reference
    provider._sum_gpu = object()
    provider._weight_gpu = object()
    provider._zero_flow_gpu = object()
    provider._one_weight_gpu = object()
    provider_frame = provider._support_provider_frame(1, support)
    seen_planes = []

    monkeypatch.setattr(
        raw_provider,
        "_accumulate_homography_cfa",
        lambda planes, *_args, **_kwargs: seen_planes.append(
            tuple(plane.data.copy() for plane in planes)
        ),
    )
    transform = np.eye(3, dtype=np.float32)
    provider.accumulate(provider_frame, transform=transform)
    first_buffers = tuple(engine.allocations)
    provider.accumulate(provider_frame, transform=transform)

    assert len(engine.allocations) == 4
    assert len(engine.writes) == 4
    assert tuple(engine.writes[:4]) == first_buffers
    expected = _phase_planes(support, _normalized_for_rgb_parity(support))
    for actual, reference_plane in zip(seen_planes[-1], expected):
        np.testing.assert_array_equal(actual, reference_plane)

    provider.close()
    assert all(buffer.released for buffer in first_buffers)


def test_aot_engine_write_into_reuses_existing_host_visible_buffer(monkeypatch):
    import importlib
    import threading
    import numpy as np

    engine_module = importlib.import_module("taichi_vision.taichi_aot.engine")
    calls = []

    class FakeLibrary:
        @staticmethod
        def write_to_gpu_buffer(runtime, handle, address, size):
            calls.append(("write", runtime, handle, address, size))

    engine = engine_module.AOTEngine.__new__(engine_module.AOTEngine)
    engine.runtime = object()
    engine._generation = 0
    engine.arch = "vulkan"
    engine._native_context_owner_thread_id = None
    engine._lock = threading.RLock()
    engine.sync = lambda: calls.append(("sync",))
    monkeypatch.setattr(engine_module, "_LIB", FakeLibrary())
    monkeypatch.setattr(engine_module, "_init_aot_bridge", lambda: None)
    monkeypatch.setattr(engine_module, "_heartbeat", lambda: None)
    monkeypatch.setattr(engine_module, "_op_begin", lambda _name: None)
    monkeypatch.setattr(engine_module, "_op_end", lambda: None)

    source = np.arange(12, dtype=np.float32).reshape(3, 4)
    destination = engine_module.TaichiGPUBuffer(
        size_bytes=source.nbytes,
        handle=123,
        shape=source.shape,
        dtype=np.float32,
        engine=engine,
        host_accessible=True,
    )

    result = engine.write_into(destination, source)

    assert result is destination
    assert calls[0] == ("sync",)
    assert calls[1][0:3] == ("write", engine.runtime, 123)
    assert calls[1][3] == source.ctypes.data
    assert calls[1][4] == source.nbytes


def test_resident_source_mode_rejects_unknown_domains_before_execution():
    import pytest

    with pytest.raises(ValueError, match="Unsupported resident source_mode"):
        canonical_resident.run_resident_pipeline([], source_mode="unknown")


def test_pipeline_telemetry_reports_engine_memory_counters():
    class FakeEngine:
        def get_memory_status(self, force=False):
            return {"live_bytes": 10, "pooled_bytes": 20, "retired_bytes": 3}

    telemetry = PipelineTelemetry(FakeEngine(), enabled=True)
    telemetry.emit("unit")
    report = telemetry.report()
    assert report["enabled"] is True
    assert report["peak_live_bytes"] == 10
    assert report["peak_pooled_bytes"] == 20
    assert report["peak_retired_bytes"] == 3


def test_weightnet_transfer_workspaces_reuse_readback_and_upload_arrays():
    import numpy as np

    class FakeGPU:
        shape = (2, 3, 3)
        dtype = np.float32

        def __init__(self):
            self.readback_ids = []

        def to_numpy(self, out=None):
            source = np.arange(18, dtype=np.float32).reshape(2, 3, 3)
            if out is None:
                return source
            self.readback_ids.append(id(out))
            out[...] = source
            return out

    readback = canonical_resident._WeightNetReadbackWorkspace((2, 3))
    upload = canonical_resident._WeightNetUploadWorkspace((2, 3))
    gpu = FakeGPU()

    first = readback.read(gpu)
    second = readback.read(gpu)
    staged = upload.stage(first)

    assert first is readback.chw
    assert second is first
    assert len(set(gpu.readback_ids)) == 1
    np.testing.assert_array_equal(staged, np.transpose(first, (1, 2, 0)))
    assert staged is upload.hwc


def test_weightnet_single_channel_readback_workspace_reuses_gray_storage():
    import numpy as np

    class FakeGPU:
        shape = (2, 3)
        dtype = np.float32

        def __init__(self):
            self.readback_ids = []

        def to_numpy(self, out=None):
            source = np.arange(6, dtype=np.float32).reshape(2, 3)
            if out is None:
                return source
            self.readback_ids.append(id(out))
            out[...] = source
            return out

    readback = canonical_resident._WeightNetReadbackWorkspace(
        (2, 3), channels=1
    )
    gpu = FakeGPU()

    first = readback.readback(gpu)
    first_chw = readback.as_chw(first)
    second = readback.readback(gpu)

    assert first is readback.hwc
    assert first_chw is readback.chw
    assert second is first
    assert readback.chw.shape == (1, 2, 3)
    assert len(set(gpu.readback_ids)) == 1
    np.testing.assert_array_equal(first_chw[0], np.arange(6).reshape(2, 3))


def test_weightnet_scalar_upload_workspace_returns_map_without_rgb_expansion():
    import numpy as np

    upload = canonical_resident._WeightNetUploadWorkspace((2, 3), channels=1)
    scalar = np.arange(6, dtype=np.float32).reshape(1, 2, 3)
    staged = upload.stage(scalar)

    assert staged.shape == (2, 3)
    assert staged.dtype == np.float32
    assert np.shares_memory(staged, scalar)
    np.testing.assert_array_equal(staged, scalar[0])


def test_weightnet_inference_forwards_to_resident_tcm_session():
    import numpy as np
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.fusionet_engine.weightnet_inference import (
        infer_single_support_weight_map,
    )

    class FakeTcmSession:
        runtime = "taichi_aot"
        max_safety = 0.30

        def __init__(self):
            self.calls = []

        def infer(self, ref_work, supp_work, **options):
            self.calls.append((ref_work, supp_work, options))
            weight = np.full((1, 4, 4), 0.75, dtype=np.float32)
            return weight, np.float32(0.8)

    ref = np.full((1, 4, 4), 0.5, dtype=np.float32)
    support = np.full((1, 4, 4), 0.4, dtype=np.float32)
    session = FakeTcmSession()
    weights, alpha = infer_single_support_weight_map(
        session, ref, support, tile_size=4, overlap=0.0,
        ghost_penalty=1.5, ghost_cutoff=0.05, max_safety=0.42,
    )

    assert weights.shape == (1, 4, 4)
    assert alpha == np.float32(0.8)
    forwarded_ref, forwarded_support, options = session.calls[0]
    assert forwarded_ref is ref
    assert forwarded_support is support
    assert options["overlap"] == 0.0
    assert options["ghost_penalty"] == 1.5
    assert options["ghost_cutoff"] == 0.05
    assert options["max_safety"] == 0.42


def test_weightnet_inference_rejects_non_tcm_sessions():
    import numpy as np
    import pytest
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.fusionet_engine.weightnet_inference import (
        infer_single_support_weight_map,
    )

    class LegacyOrtSession:
        def run(self, names, feed):  # pragma: no cover - must never be called
            raise AssertionError("ONNX Runtime route was removed")

    ref = np.full((1, 4, 4), 0.5, dtype=np.float32)
    with pytest.raises(RuntimeError, match="resident TCM session"):
        infer_single_support_weight_map(LegacyOrtSession(), ref, ref, tile_size=4)


def test_fusionnet_keeps_luminance_model_as_default_and_only_route():
    from types import SimpleNamespace
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.FusionNet import (
        FusionNetDenoisingAlgorithm,
    )
    algorithm = FusionNetDenoisingAlgorithm()
    default_config = algorithm._resolve_config(
        SimpleNamespace(batch_id=None, params={}, alignment_selection_name=None)
    )
    experimental_config = algorithm._resolve_config(
        SimpleNamespace(
            batch_id=None,
            params={"input_channels": 3},
            alignment_selection_name=None,
        )
    )

    assert default_config["input_channels"] == 1
    assert experimental_config["input_channels"] == 1


def test_analysis_proxy_enhances_disposable_same_size_source_in_place(monkeypatch):
    from types import SimpleNamespace
    from taichi_vision import taichi_aot
    from taichi_vision.taichi_algorithm.enhancement import auto_enhance

    source = SimpleNamespace(shape=(4, 6, 3))
    resize_calls = []
    enhance_calls = []

    def fake_resize(*args, **kwargs):
        resize_calls.append((args, kwargs))
        return SimpleNamespace(shape=(4, 6, 3))

    def fake_enhance(image, params, *, dst=None, return_gpu=False):
        enhance_calls.append((image, dst, return_gpu))
        return dst if dst is not None else image

    monkeypatch.setattr(taichi_aot, "resize", fake_resize)
    monkeypatch.setattr(auto_enhance, "apply_auto_enhance_gpu", fake_enhance)

    result = canonical_resident.prepare_analysis_proxy_gpu(
        source,
        work_shape=(4, 6),
        analysis_params={"gain": 1.2},
        in_place=True,
        source_is_disposable=True,
    )

    assert result is source
    assert resize_calls == []
    assert enhance_calls == [(source, source, True)]


def test_analysis_proxy_uses_exact_copy_for_nondisposable_native_source(monkeypatch):
    from types import SimpleNamespace
    from taichi_vision import taichi_aot
    from taichi_vision.taichi_algorithm.enhancement import auto_enhance

    source = SimpleNamespace(shape=(4, 6, 3))
    proxy = SimpleNamespace(shape=(4, 6, 3))
    copy_calls = []
    resize_calls = []
    enhance_calls = []

    def fake_copy(image, *, return_gpu=False):
        copy_calls.append((image, return_gpu))
        return proxy

    def fake_resize(*args, **kwargs):
        resize_calls.append((args, kwargs))
        raise AssertionError("native-size proxy should use an exact copy")

    def fake_enhance(image, params, *, dst=None, return_gpu=False):
        enhance_calls.append((image, dst, return_gpu))
        return dst if dst is not None else image

    monkeypatch.setattr(taichi_aot, "copy", fake_copy)
    monkeypatch.setattr(taichi_aot, "resize", fake_resize)
    monkeypatch.setattr(auto_enhance, "apply_auto_enhance_gpu", fake_enhance)

    result = canonical_resident.prepare_analysis_proxy_gpu(
        source,
        work_shape=(4, 6),
        analysis_params={"gain": 1.2},
        in_place=True,
    )

    assert result is proxy
    assert copy_calls == [(source, True)]
    assert resize_calls == []
    assert enhance_calls == [(proxy, proxy, True)]


def test_raw_analysis_defaults_to_full_bilinear_and_preserves_cfa(monkeypatch):
    from types import SimpleNamespace
    import numpy as np
    from taichi_vision import taichi_aot
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.pipeline_process.raw_pipeline import provider, metadata

    samples = np.arange(48, dtype=np.uint16).reshape(6, 8)
    before = samples.copy()
    calls = []
    monkeypatch.setattr(metadata, "carrier_demosaic_parameters", lambda _: {"white_level": 4095.})
    monkeypatch.setattr(taichi_aot, "demosaic", lambda source, **kw: calls.append((source, kw)) or object())
    carrier = SimpleNamespace(samples=samples)
    provider._demosaic_carrier_gpu(carrier)
    provider._demosaic_carrier_gpu(carrier, method="hamilton", dst="destination")
    assert calls[0][0] is samples
    assert calls[0][1] == {"white_level": 4095., "method": "bilinear", "return_gpu": True, "dst": None}
    assert calls[1][1]["method"] == "hamilton"
    assert calls[1][1]["dst"] == "destination"
    assert "half_res" not in calls[0][1]
    np.testing.assert_array_equal(samples, before)


def test_shared_reference_analysis_params_are_analyzed_once_or_reused(monkeypatch):
    calls = []
    params = {"gain": 1.25}
    monkeypatch.delenv("PIXEL_REFINE_ANALYSIS_ENHANCE", raising=False)
    monkeypatch.setattr(canonical_resident, "analyze_auto_enhance_on_gpu",
                        lambda reference, mode: calls.append((reference, mode)) or params)
    result = canonical_resident._resolve_reference_analysis_params("reference", enabled=True)
    assert result is params
    assert canonical_resident._resolve_reference_analysis_params("reference", enabled=True, supplied=result) is params
    assert calls == [("reference", "natural")]
    monkeypatch.setenv("PIXEL_REFINE_ANALYSIS_ENHANCE", "off")
    assert canonical_resident._resolve_reference_analysis_params("reference", enabled=True, supplied=params) is None
    assert canonical_resident._resolve_reference_analysis_params("reference", enabled=True, needs_analysis=False) is None
    assert len(calls) == 1


def test_fusionnet_analysis_mode_ignores_stale_analysis_override(monkeypatch):
    from types import SimpleNamespace

    from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_denoising import (
        fusionnet_parameter_settings,
    )
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.FusionNet import (
        FusionNetDenoisingAlgorithm,
    )

    monkeypatch.setattr(
        fusionnet_parameter_settings,
        "load_fusionnet_config_for_batch",
        lambda _batch_id: {"analysis_auto_enhance_mode": "analysis"},
    )
    context = SimpleNamespace(
        batch_id=1,
        params={"analysis_auto_enhance_mode": "analysis"},
        alignment_selection_name="No Alignment",
    )

    config = FusionNetDenoisingAlgorithm()._resolve_config(context)

    assert config["analysis_auto_enhance_mode"] == "natural"


def test_reference_noise_is_estimated_once_from_prepared_analysis_proxy(monkeypatch):
    from types import SimpleNamespace

    source = SimpleNamespace(shape=(12, 16, 3), label="linear-carrier")
    enhanced_proxy = SimpleNamespace(shape=(6, 8, 3), label="autoenhanced-analysis")
    prepare_calls = []
    estimate_calls = []

    def fake_prepare(actual_source, **kwargs):
        prepare_calls.append((actual_source, kwargs))
        return enhanced_proxy

    def fake_estimate(actual_proxy, **kwargs):
        estimate_calls.append((actual_proxy, kwargs))
        return 0.72, 3.0

    monkeypatch.setattr(canonical_resident, "prepare_analysis_proxy_gpu", fake_prepare)
    monkeypatch.setattr(canonical_resident, "resolve_noise_adaptive_penalty", fake_estimate)

    result, score, penalty = canonical_resident.prepare_reference_analysis_and_noise(
        source,
        work_shape=(6, 8),
        analysis_params={"gain": 2.0},
        ghost_penalty=8.0,
        ghost_penalty_min=0.85,
        in_place=True,
        source_is_disposable=True,
    )

    assert result is enhanced_proxy
    assert score == 0.72
    assert penalty == 3.0
    assert prepare_calls == [
        (
            source,
            {
                "work_shape": (6, 8),
                "analysis_params": {"gain": 2.0},
                "in_place": True,
                "source_is_disposable": True,
            },
        )
    ]
    assert estimate_calls == [
        (
            enhanced_proxy,
            {"ghost_penalty": 8.0, "ghost_penalty_min": 0.85},
        )
    ]


def test_spatial_reference_noise_can_use_linear_proxy_while_analysis_is_enhanced(monkeypatch):
    from types import SimpleNamespace

    source = SimpleNamespace(shape=(12, 16, 3), label="linear-reference")
    enhanced_proxy = SimpleNamespace(shape=(6, 8, 3), label="natural-analysis")
    linear_proxy = SimpleNamespace(shape=(6, 8, 3), label="linear-noise")
    prepared = []
    estimated = []

    def fake_prepare(actual_source, **kwargs):
        prepared.append((actual_source, kwargs))
        return linear_proxy if kwargs.get("analysis_params") is None else enhanced_proxy

    def fake_estimate(actual_proxy, **kwargs):
        estimated.append(actual_proxy)
        return 0.42, 5.0

    monkeypatch.setattr(canonical_resident, "prepare_analysis_proxy_gpu", fake_prepare)
    monkeypatch.setattr(canonical_resident, "resolve_noise_adaptive_penalty", fake_estimate)

    result, score, penalty = canonical_resident.prepare_reference_analysis_and_noise(
        source,
        work_shape=(6, 8),
        analysis_params={"gain": 2.0},
        ghost_penalty=8.0,
        in_place=True,
        source_is_disposable=True,
        noise_source_gpu=source,
    )

    assert result is enhanced_proxy
    assert score == 0.42
    assert penalty == 5.0
    assert estimated == [linear_proxy]
    assert prepared[0][1]["source_is_disposable"] is False
    assert prepared[1][1]["analysis_params"] is None


def test_fusionnet_reference_noise_uses_analysis_mode_separate_from_natural_proxy(monkeypatch):
    from types import SimpleNamespace

    source = SimpleNamespace(shape=(12, 16, 3), label="linear-reference")
    natural_proxy = SimpleNamespace(shape=(6, 8, 3), label="natural-alignment-weight")
    noise_proxy = SimpleNamespace(shape=(6, 8, 3), label="analysis-noise")
    prepared = []
    estimated = []
    destroyed = []

    def fake_prepare(actual_source, **kwargs):
        prepared.append((actual_source, kwargs))
        if kwargs.get("analysis_params") == {"mode": "natural"}:
            return natural_proxy
        return noise_proxy

    def fake_estimate(actual_proxy, **kwargs):
        estimated.append(actual_proxy)
        return 0.61, 4.5

    monkeypatch.setattr(canonical_resident, "prepare_analysis_proxy_gpu", fake_prepare)
    monkeypatch.setattr(canonical_resident, "resolve_noise_adaptive_penalty", fake_estimate)
    monkeypatch.setattr(canonical_resident, "_destroy_work_item", destroyed.append)

    result, score, penalty = canonical_resident.prepare_reference_analysis_and_noise(
        source,
        work_shape=(6, 8),
        analysis_params={"mode": "natural"},
        noise_source_gpu=source,
        noise_analysis_params={"mode": "analysis"},
        ghost_penalty=8.0,
        in_place=True,
        source_is_disposable=True,
    )

    assert result is natural_proxy
    assert score == 0.61
    assert penalty == 4.5
    assert prepared[0][1]["analysis_params"] == {"mode": "natural"}
    assert prepared[0][1]["source_is_disposable"] is False
    assert prepared[1][1]["analysis_params"] == {"mode": "analysis"}
    assert estimated == [noise_proxy]
    assert destroyed == [noise_proxy]


def test_alignment_analysis_mode_enables_autoenhance_for_both_fusion_engines(monkeypatch):
    reference = object()
    calls = []

    def fake_reference_params(actual_reference, **kwargs):
        calls.append((actual_reference, kwargs))
        return {"gain": 2.0}

    monkeypatch.setattr(
        canonical_resident, "_resolve_reference_analysis_params", fake_reference_params
    )

    spatial_params = canonical_resident._resolve_engine_analysis_params(
        reference,
        weight_engine="spatial_fusion",
        enabled=True,
        mode="analysis",
    )
    fusionnet_params = canonical_resident._resolve_engine_analysis_params(
        reference,
        weight_engine="fusionet",
        enabled=True,
        mode="analysis",
    )
    spatial_weight_params = canonical_resident._resolve_engine_analysis_params(
        reference,
        weight_engine="spatial_fusion",
        enabled=True,
        mode="natural",
    )

    assert spatial_params == {"gain": 2.0}
    assert fusionnet_params == {"gain": 2.0}
    assert spatial_weight_params is None
    assert [kwargs["mode"] for _, kwargs in calls] == [
        "analysis", "analysis"
    ]


def test_autoenhance_analysis_gain_has_no_fixed_six_x_cap():
    import numpy as np

    from taichi_vision.taichi_algorithm.enhancement.auto_enhance import (
        _auto_enhance_params_from_luma,
    )

    params = _auto_enhance_params_from_luma(np.array([1.0e-4], dtype=np.float32), "analysis")

    assert params["gain"] > 6.0


def test_shared_spatial_policy_honors_canonical_sigma_and_noise_awareness():
    from taichi_vision.taichi_algorithm.spatial_fusion import auto_motion_sensitivity
    cfg = {"similarity_spatial_tile_size": 24, "similarity_spatial_noise_sigma": .1,
           "noise_sigma": .01, "motion_sensitivity": 150., "noise_offset": .2}
    state = canonical_resident._resolve_spatial_analysis_config(
        cfg, tile_size=512, overlap=.35, work_shape=(512, 512), noise_score=.8, is_raw=True)
    assert state == (24, .35, auto_motion_sensitivity(is_raw=True, base=150., noise_sigma=.1), .2, .1, "explicit_ui")
    cfg["similarity_spatial_noise_sigma"] = 0.
    state = canonical_resident._resolve_spatial_analysis_config(
        cfg, tile_size=512, overlap=.35, work_shape=(512, 512), noise_score=.8, is_raw=True)
    assert state[4:] == (.8, "linear_reference_score")


def test_rgb_host_normalization_uses_float32_in_place_range_contract():
    import numpy as np

    source = np.asarray(
        [[[0, 127, 255], [255, 64, 128]]],
        dtype=np.uint8,
    )
    normalized = canonical_resident._normalize_rgb_host_frame(source)

    assert normalized.dtype == np.float32
    assert normalized.flags.c_contiguous
    assert normalized is not source
    np.testing.assert_allclose(
        normalized,
        source.astype(np.float32) / np.float32(255.0),
        rtol=0.0,
        atol=0.0,
    )


def test_raw_weight_analysis_reuses_one_aligned_preview_without_second_warp():
    class FakeBuffer:
        def __init__(self, shape):
            self.shape = shape

    support = FakeBuffer((3072, 4096, 3))
    preview = FakeBuffer((3072, 4096, 3))
    transform = object()
    warp_calls = []

    analysis, discard = canonical_resident._prepare_raw_aligned_analysis(
        support,
        preview,
        transform,
        align_shape=(3072, 4096),
        warp_analysis=lambda *args: warp_calls.append(args),
    )

    assert analysis is preview
    assert discard is None
    assert warp_calls == []


def test_raw_weight_analysis_warps_original_proxy_once_when_preview_grid_is_wrong():
    class FakeBuffer:
        def __init__(self, shape):
            self.shape = shape

    support = FakeBuffer((1536, 2048, 3))
    expanded_preview = FakeBuffer((3072, 4096, 3))
    aligned = FakeBuffer((1536, 2048, 3))
    transform = object()
    warp_calls = []

    def warp_once(source, used_transform, shape):
        warp_calls.append((source, used_transform, shape))
        return aligned

    analysis, discard = canonical_resident._prepare_raw_aligned_analysis(
        support,
        expanded_preview,
        transform,
        align_shape=(1536, 2048),
        warp_analysis=warp_once,
    )

    assert analysis is aligned
    assert discard is expanded_preview
    assert warp_calls == [(support, transform, (1536, 2048))]


def test_raw_weight_analysis_stays_unwarped_when_alignment_has_no_transform():
    class FakeBuffer:
        shape = (3072, 4096, 3)

    support = FakeBuffer()
    unused_preview = FakeBuffer()
    warp_calls = []

    analysis, discard = canonical_resident._prepare_raw_aligned_analysis(
        support,
        unused_preview,
        None,
        align_shape=(3072, 4096),
        warp_analysis=lambda *args: warp_calls.append(args),
    )

    assert analysis is support
    assert discard is unused_preview
    assert warp_calls == []
