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
    RawNativeProvider,
    _analysis_transform,
    _normalized_for_rgb_parity,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.pipeline_process.rgb_pipeline.provider import (
    RGBFrameProvider,
)


def test_canonical_resident_exports_public_entrypoints():
    assert callable(canonical_resident.run_resident_pipeline)
    assert callable(canonical_resident.run_gpu_resident_pipeline)
    assert callable(canonical_resident.load_frame_to_gpu)


def test_legacy_resident_import_is_a_lazy_compatibility_facade():
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising import (
        resident_pipeline as legacy_resident,
    )

    assert legacy_resident.run_resident_pipeline is canonical_resident.run_resident_pipeline


def test_fusionet_engine_reexports_canonical_resident_entrypoint():
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising import fusionet_engine

    assert fusionet_engine.run_resident_pipeline is canonical_resident.run_resident_pipeline


def test_rgb_provider_contract_is_metadata_only_until_executor_migration():
    provider = RGBFrameProvider(["reference.png", "support.png"], is_raw=False)
    metadata = provider.metadata(1, shape=(32, 48, 3))
    assert metadata.source_id == "support.png"
    assert metadata.shape == (32, 48, 3)
    assert metadata.carrier_kind == "rgb"
    assert provider.source_path(0) == "reference.png"
    assert RGBFrameProvider(["reference.dng"], is_raw=True).source_mode == "raw_rgb"


def test_raw_provider_preserves_public_dispatch_boundary():
    provider = RawNativeProvider(["reference.dng", "support.dng"], weight_engine="average")
    assert provider.source_mode == "raw_native"
    assert provider.carrier_kind == "cfa"
    assert provider.options["weight_engine"] == "average"
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.pipeline_process.raw_pipeline import (
        run_raw_native_resident_pipeline,
    )

    assert callable(run_raw_native_resident_pipeline)
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


def test_raw_provider_normalization_matches_rgb_demosaic_scalar_contract():
    import numpy as np

    class FakeRawFrame:
        samples = np.asarray(
            ((63, 64, 1023), (1024, 543, 100)), dtype=np.uint16
        )
        black_level = (64.01, 63.9, 63.9, 64.0)
        white_level = (1023.0, 1023.0, 1023.0, 1023.0)

    actual = _normalized_for_rgb_parity(FakeRawFrame())
    inverse_range = np.float32(1.0) / np.float32(1023 - 64)
    expected = np.clip(
        (FakeRawFrame.samples.astype(np.float32) - np.float32(64))
        * inverse_range,
        np.float32(0.0),
        np.float32(1.0),
    )

    assert actual.dtype == np.float32
    assert actual.flags.c_contiguous
    np.testing.assert_array_equal(actual, expected)


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


def test_weightnet_inference_accepts_precomputed_single_channel_inputs():
    import numpy as np
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.fusionet_engine.weightnet_inference import (
        infer_single_support_weight_map,
    )

    class FakeInput:
        shape = [1, 1, 4, 4]

    class FakeOutput:
        def __init__(self, shape):
            self.shape = shape

    class FakeSession:
        def get_inputs(self):
            return [FakeInput()]

        def get_outputs(self):
            return [FakeOutput([1, 1, 4, 4]), FakeOutput([1, 1])]

        def get_providers(self):
            return ["CPUExecutionProvider"]

        def run(self, names, feed):
            assert feed["ref_img"].shape == (1, 1, 4, 4)
            assert feed["support_img"].shape == (1, 1, 4, 4)
            return [
                np.full((1, 1, 4, 4), 0.75, dtype=np.float32),
                np.full((1, 1), 0.8, dtype=np.float32),
            ]

    ref = np.full((1, 4, 4), 0.5, dtype=np.float32)
    support = np.full((1, 4, 4), 0.4, dtype=np.float32)
    weights, alpha = infer_single_support_weight_map(
        FakeSession(), ref, support, tile_size=4, overlap=0.0
    )

    assert weights.shape == (3, 4, 4)
    assert weights.dtype == np.float32
    assert alpha == np.float32(0.8)


def test_weightnet_inference_reduces_rgb_callers_to_luminance_input():
    import numpy as np
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.fusionet_engine.weightnet_inference import (
        infer_single_support_weight_map,
    )

    class FakeInput:
        shape = [1, 1, 4, 4]

    class FakeOutput:
        def __init__(self, shape):
            self.shape = shape

    class FakeSession:
        def get_inputs(self):
            return [FakeInput()]

        def get_outputs(self):
            return [FakeOutput([1, 1, 4, 4]), FakeOutput([1, 1])]

        def get_providers(self):
            return ["CPUExecutionProvider"]

        def run(self, names, feed):
            assert feed["ref_img"].shape == (1, 1, 4, 4)
            assert feed["support_img"].shape == (1, 1, 4, 4)
            return [
                np.full((1, 1, 4, 4), 0.75, dtype=np.float32),
                np.full((1, 1), 0.8, dtype=np.float32),
            ]

    ref = np.full((3, 4, 4), 0.5, dtype=np.float32)
    support = np.full((3, 4, 4), 0.4, dtype=np.float32)
    weights, alpha = infer_single_support_weight_map(
        FakeSession(), ref, support, tile_size=4, overlap=0.0
    )

    assert weights.shape == (3, 4, 4)
    assert alpha == np.float32(0.8)


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
