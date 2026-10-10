"""Resident preparation: exposure parity and no intermediate image readback."""
import os
os.environ.setdefault("PIXEL_REFINE_AOT_ARCH", "cpu")
import numpy as np
import pytest
from taichi_vision import taichi_aot as aot
from taichi_vision.taichi_aot.engine import TaichiGPUBuffer
from taichi_vision.taichi_algorithm.buffer_session import BufferSession


@pytest.mark.parametrize("count", [1, 31, 32, 33, 4096, 4097])
def test_resident_exposure_matches_float32_median(count):
    from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.splat_sr.legacy import SplatSRAlgorithm
    rng = np.random.default_rng(651)
    reference = rng.uniform(.031, .97, (1, count)).astype(np.float32)
    support = rng.uniform(.031, .97, (1, count)).astype(np.float32)
    if count > 100:
        reference[0, :20] = [0, np.nan, np.inf, .99] * 5
    expected = SplatSRAlgorithm._estimate_exposure_gain(reference, support)
    with BufferSession() as session:
        ref = session.own(aot.upload(reference))
        supp = session.own(aot.upload(support))
        gain = aot.resident_exposure_gain(ref, supp, session=session)
        observed = gain.to_numpy()[0]
        print(f"[EXPOSURE] backend={aot.backend_info()} shape={reference.shape} dtype=float32 expected={expected} got={observed}")
        np.testing.assert_allclose(observed, expected, atol=3e-7, rtol=3e-7)


@pytest.mark.parametrize("proxy_max", ["768", "128"])
def test_spatial_pipeline_has_no_intermediate_image_readback(tmp_path, monkeypatch, proxy_max):
    import tifffile
    from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.splat_SR import run_splat_sr_pipeline
    from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.splat_sr.streaming_pipeline import ImagePathSource
    rng = np.random.default_rng(39)
    reference = rng.uniform(.1, .6, (137, 149, 3)).astype(np.float32)
    monkeypatch.setenv("SPLATSR_FLOW_PROXY_MAX", proxy_max)
    monkeypatch.setattr(ImagePathSource, "_load", lambda self, index: np.roll(reference, index, axis=1).copy())
    original = TaichiGPUBuffer.to_numpy
    original_map = TaichiGPUBuffer.map
    image_maps = []
    def forbid_image(buffer, *args, **kwargs):
        if len(buffer.shape) >= 2 and buffer.nbytes > 4096 * 4:
            raise AssertionError(f"intermediate image readback: {buffer.shape}")
        return original(buffer, *args, **kwargs)
    monkeypatch.setattr(TaichiGPUBuffer, "to_numpy", forbid_image)
    def record_map(buffer, *args, **kwargs):
        if len(buffer.shape) >= 2 and buffer.nbytes > 4096 * 4:
            image_maps.append(buffer.shape)
        return original_map(buffer, *args, **kwargs)
    monkeypatch.setattr(TaichiGPUBuffer, "map", record_map)
    output = str(tmp_path / "resident.tif")
    assert run_splat_sr_pipeline(["reference.png", "support.png"], output_path=output,
        prefetch_depth=1, exposure_normalization=True, refinement_iterations=0) == output
    image = tifffile.imread(output)
    assert image.shape == (274, 298, 3)
    assert image.dtype == np.uint16
    assert image_maps == [(274, 298, 3)]


@pytest.mark.parametrize("work_scale", [.5, 1.0])
def test_weightnet_pipeline_reads_only_model_luma(tmp_path, monkeypatch, work_scale):
    """Exercise native SR preparation with a deterministic ONNX boundary stub."""
    import tifffile
    from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.splat_SR import run_splat_sr_pipeline
    from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.splat_sr.streaming_pipeline import ImagePathSource
    from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.splat_sr.weightnet_confidence import WeightNetConfidenceProvider
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.fusionet_engine import weightnet_inference

    class ModelSession:
        pass

    monkeypatch.setattr(weightnet_inference, "load_weightnet_onnx", lambda *args, **kwargs: ModelSession())
    inference_shapes = []

    def infer(model, reference, support, **kwargs):
        inference_shapes.append((reference.shape, support.shape))
        assert kwargs == dict(tile_size=256, overlap=.30, ghost_penalty=1.0, chroma_sensitivity=1.0)
        return np.repeat(np.clip(support, 0, 1), 3, axis=0), .25

    monkeypatch.setattr(weightnet_inference, "infer_single_support_weight_map", infer)
    provider = WeightNetConfidenceProvider(model_path="stub.onnx", runtime="cpu", work_scale=work_scale)
    rng = np.random.default_rng(173)
    reference = rng.uniform(.1, .6, (137, 149, 3)).astype(np.float32)
    monkeypatch.setattr(ImagePathSource, "_load", lambda self, index: np.roll(reference, index, axis=1).copy())
    monkeypatch.setenv("SPLATSR_FLOW_PROXY_MAX", "128")
    work_shape = (round(137 * work_scale), round(149 * work_scale))
    original = TaichiGPUBuffer.to_numpy
    readbacks = []

    def record_readback(buffer, *args, **kwargs):
        if len(buffer.shape) >= 2:
            readbacks.append(buffer.shape)
            assert buffer.shape == work_shape, f"unexpected readback: {buffer.shape}"
        return original(buffer, *args, **kwargs)

    monkeypatch.setattr(TaichiGPUBuffer, "to_numpy", record_readback)
    output = str(tmp_path / "weightnet_resident.tif")
    assert run_splat_sr_pipeline(["ref.png", "support.png"], output_path=output,
        weight_source="weightnet", reliability_provider=provider,
        prefetch_depth=1, exposure_normalization=True, refinement_iterations=0) == output
    assert tifffile.imread(output).shape == (274, 298, 3)
    assert readbacks == [work_shape, work_shape]
    assert inference_shapes == [((1, *work_shape), (1, *work_shape))]
    assert provider._resident_reference is None
    print(f"[WEIGHTNET BOUNDARY STUB] backend={aot.backend_info()} shape={reference.shape} dtype=float32 work_scale={work_scale} readbacks={readbacks}")


def test_resident_flow_resize_preserves_component_geometry():
    import cv2
    cv2.setNumThreads(1)
    rng = np.random.default_rng(122)
    source = rng.uniform(-2, 2, (31, 37, 2)).astype(np.float32)
    with BufferSession() as session:
        gpu = session.own(aot.upload(source))
        result = aot.resident_resize_flow(gpu, 49, 53, factor=1.37, session=session)
        observed = result.to_numpy()
    expected = cv2.resize(source, (53, 49), interpolation=cv2.INTER_LINEAR) * np.float32(1.37)
    error = float(np.max(np.abs(observed-expected)))
    print(f"[FLOW RESIZE] backend={aot.backend_info()} shape={source.shape} dtype=float32 max_abs={error}")
    np.testing.assert_allclose(observed, expected, atol=2e-5, rtol=2e-5)


def test_taichi_warp_difference_is_bounded():
    import cv2
    cv2.setNumThreads(1)
    rng = np.random.default_rng(561)
    image = rng.uniform(.1, .8, (61, 67)).astype(np.float32)
    flow = rng.uniform(-1, 1, (61, 67, 2)).astype(np.float32)
    # Measure the common interior; TV and OpenCV also have different border contracts.
    with BufferSession() as session:
        src = session.own(aot.upload(image))
        motion = session.own(aot.upload(flow))
        observed = aot.resident_warp_gray(src, motion, session=session).to_numpy()
    y, x = np.mgrid[:61, :67].astype(np.float32)
    expected = cv2.remap(image, x+flow[...,0], y+flow[...,1], cv2.INTER_LINEAR,
                         borderMode=cv2.BORDER_REFLECT101)
    error = float(np.max(np.abs(observed[2:-2, 2:-2]-expected[2:-2, 2:-2])))
    print(f"[WARP] backend={aot.backend_info()} shape={image.shape} dtype=float32 interior_max_abs={error}")
    assert error < .025


def test_resident_pipeline_tracks_host_contract_output(tmp_path, monkeypatch):
    import cv2
    import tifffile
    from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.splat_SR import run_splat_sr_pipeline
    from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.splat_sr.streaming_pipeline import ImagePathSource
    from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.splat_sr.reliability_confidence import ReliabilityConfidenceProvider
    cv2.setNumThreads(1)
    rng = np.random.default_rng(75)
    reference = rng.uniform(.1, .7, (137, 149, 3)).astype(np.float32)
    monkeypatch.setenv("SPLATSR_FLOW_PROXY_MAX", "128")
    monkeypatch.setattr(ImagePathSource, "_load", lambda self, index: np.roll(reference, index, axis=1).copy() * np.float32(1.0 if index == 0 else .97))
    class HostContractProvider:
        def __init__(self):
            self.delegate = ReliabilityConfidenceProvider()
        def prepare_reference(self, reference, *, session):
            return self.delegate.prepare_reference(reference, session=session)
        def generate_device(self, reference, aligned, *, session):
            return self.delegate.generate_device(reference, aligned, session=session)
    images = []
    for label, provider in (("host", HostContractProvider()), ("resident", None)):
        output = str(tmp_path / f"{label}.tif")
        run_splat_sr_pipeline(["ref.png", "support.png"], output_path=output,
            prefetch_depth=0, reliability_provider=provider, exposure_normalization=True)
        images.append(tifffile.imread(output).astype(np.float32) / np.float32(65535))
    delta = np.abs(images[0]-images[1])
    print(f"[PIPELINE PARITY] backend={aot.backend_info()} shape={reference.shape} dtype=float32 mean_abs={delta.mean()} max_abs={delta.max()}")
    assert float(delta.mean()) < 5e-4
    assert float(delta.max()) < .02
