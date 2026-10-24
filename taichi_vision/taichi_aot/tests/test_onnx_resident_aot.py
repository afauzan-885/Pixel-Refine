"""Execute compiled ONNX with C API buffers and forbid host transfer in run."""

import numpy as np
import onnx
from onnx import helper as h, TensorProto as T
import pytest

from taichi_vision.taichi_algorithm.denoising.onnx_resident_aot import (
    ResidentONNXGraph, compile_resident_onnx,
)


def test_same_runtime_onnx_reuses_device_buffers_without_host_transfer(tmp_path, monkeypatch):
    shape = (1, 1, 4, 4)
    graph = h.make_graph(
        [h.make_node("Add", ["x", "z"], ["sum"]),
         h.make_node("Relu", ["sum"], ["result"])],
        "resident", [h.make_tensor_value_info(name, T.FLOAT, shape) for name in ("x", "z")],
        [h.make_tensor_value_info("result", T.FLOAT, shape)],
    )
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    model_bytes = model.SerializeToString()
    artifact = compile_resident_onnx(model_bytes, tmp_path / "tiny.tcm", "cpu")
    from taichi_vision import taichi_aot as aot
    from taichi_vision.taichi_aot.engine import TaichiGPUBuffer
    assert aot.engine.arch == "cpu"
    import hashlib
    executor = ResidentONNXGraph(
        artifact, model_sha256=hashlib.sha256(model_bytes).hexdigest()
    )
    x = np.arange(16, dtype=np.float32) - 8
    z = np.full(16, 2, dtype=np.float32)
    x_gpu, z_gpu = aot.engine.upload(x), aot.engine.upload(z)
    try:
        def forbidden(*args, **kwargs):
            raise AssertionError("host transfer attempted during resident inference")
        with monkeypatch.context() as checks:
            checks.setattr(TaichiGPUBuffer, "to_numpy", forbidden)
            checks.setattr(aot.engine, "upload", forbidden)
            first = executor.run_device({"x": x_gpu, "z": z_gpu})["result"]
            second = executor.run_device({"x": x_gpu, "z": z_gpu})["result"]
            assert first is second
        np.testing.assert_array_equal(second.to_numpy(), np.maximum(x + z, 0))
        np.testing.assert_array_equal(x_gpu.to_numpy(), x)
        with pytest.raises(ValueError, match="same-runtime"):
            executor.run_device({"x": x, "z": z_gpu})
    finally:
        executor.close()
        x_gpu.destroy()
        z_gpu.destroy()


def test_resident_patch_stitch_matches_existing_helper_and_never_downloads(tmp_path, monkeypatch):
    import onnxruntime as ort
    from taichi_vision import taichi_aot as aot
    from taichi_vision.taichi_aot.engine import TaichiGPUBuffer
    from taichi_vision.taichi_algorithm.denoising.resident_weightnet import ResidentWeightNet, ResidentImage
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.fusionet_engine.weightnet_inference import infer_single_support_weight_map
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.patch_process.multi_patch import CandidateTelemetry, search_candidate_offsets, select_topk_candidates
    shape = (1, 1, 4, 4)
    graph = h.make_graph([
        h.make_node("Add", ["ref_img", "support_img"], ["sum"]),
        h.make_node("Sigmoid", ["sum"], ["weight_map"]),
        h.make_node("ReduceMean", ["weight_map"], ["alpha"], keepdims=0),
    ], "patches", [h.make_tensor_value_info(name, T.FLOAT, shape) for name in ("ref_img", "support_img")],
        [h.make_tensor_value_info("weight_map", T.FLOAT, shape), h.make_tensor_value_info("alpha", T.FLOAT, [])])
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    model.ir_version = 10
    source = model.SerializeToString()
    artifact = compile_resident_onnx(source, tmp_path / "patches.tcm", "cpu", patch_tools=True)
    import hashlib
    executor = ResidentWeightNet(
        artifact, model_sha256=hashlib.sha256(source).hexdigest()
    )
    rng = np.random.default_rng(4)
    reference = rng.uniform(0, 1, (1, 14, 14)).astype(np.float32)
    support = rng.uniform(0, 1, reference.shape).astype(np.float32)
    ref_gpu = ResidentImage(executor, aot.engine.upload(reference.reshape(-1)), reference.shape)
    support_gpu = ResidentImage(executor, aot.engine.upload(support.reshape(-1)), support.shape)
    baseline = ort.InferenceSession(source, providers=["CPUExecutionProvider"])
    expected, expected_alpha = infer_single_support_weight_map(
        baseline, reference, support, tile_size=4, overlap=.5,
        ghost_penalty=1.5, ghost_cutoff=.05, return_scalar=True)
    options = dict(overlap=.5, ghost_penalty=1.5, ghost_cutoff=.05)
    offsets = search_candidate_offsets((28, 28), (14, 14), search_radius=3, patch_stride=2)
    expected_selection = select_topk_candidates(
        reference, support, offsets, max_neighbors=2, patch_size=5)
    cell_size = 10
    coarse_h, coarse_w = (14 + cell_size - 1) // cell_size, (14 + cell_size - 1) // cell_size
    coarse = executor.allocate((2, coarse_h, coarse_w), np.int32)
    try:
        proxy_offsets, _ = executor.offset_buffers(offsets)
        from taichi_vision.taichi_algorithm.denoising.resident_weightnet import view
        executor.dispatch(
            "multi_patch_topk_kernel", reference=view(ref_gpu.buffer, reference.shape),
            candidate=view(support_gpu.buffer, support.shape), offsets=proxy_offsets,
            indices=coarse, height=14, width=14, channels=1,
            candidate_count=len(offsets), neighbor_count=2, cell_size=cell_size)
        actual_coarse = coarse.buffer if hasattr(coarse, "buffer") else coarse
        actual_coarse = actual_coarse.to_numpy()
        assert actual_coarse.shape == (2, coarse_h, coarse_w)
        assert np.all((actual_coarse >= -1) & (actual_coarse < len(offsets)))
        pixelwise_gpu = executor.allocate((2, 14, 14), np.int32)
        try:
            executor.dispatch(
                "multi_patch_topk_kernel", reference=view(ref_gpu.buffer, reference.shape),
                candidate=view(support_gpu.buffer, support.shape), offsets=proxy_offsets,
                indices=pixelwise_gpu, height=14, width=14, channels=1,
                candidate_count=len(offsets), neighbor_count=2, cell_size=1)
            actual_pixelwise = (pixelwise_gpu.buffer if hasattr(pixelwise_gpu, "buffer") else pixelwise_gpu).to_numpy()
            np.testing.assert_array_equal(actual_pixelwise, expected_selection.indices)
        finally:
            pixelwise_gpu.destroy()
        def forbidden(*args, **kwargs):
            raise AssertionError("patch/candidate host readback")
        with monkeypatch.context() as checks:
            checks.setattr(TaichiGPUBuffer, "to_numpy", forbidden)
            result, alpha = executor.infer(ref_gpu, support_gpu, **options)
            candidates = executor.candidates(ref_gpu, support_gpu, offsets, max_neighbors=2,
                                             telemetry=CandidateTelemetry(), **options)
            total_alpha = alpha
            for rank, _, confidence, candidate_alpha in candidates:
                flow = rank.flow(full_shape=(28, 28), flow_shape=(14, 14))
                flow.destroy()
                confidence.device().destroy()
                total_alpha += candidate_alpha
        np.testing.assert_allclose(result.buffer.to_numpy(), expected[0], rtol=0, atol=2e-6)
        assert float(alpha) == pytest.approx(expected_alpha, abs=1e-7)
        assert np.isfinite(float(total_alpha))
        for height, width in ((14, 14), (32, 32), (33, 40)):
            gray = rng.uniform(0, 1, (height, width)).astype(np.float32)
            gray[0, :2] = (0, 1)
            gray_gpu = aot.engine.upload(gray)
            try:
                resident_ref, _ = executor.prepare_reference(gray_gpu)
                actual_ref = resident_ref.buffer.to_numpy().reshape(height, width)
                np.testing.assert_array_equal(actual_ref, gray)
            finally:
                gray_gpu.destroy()
    finally:
        coarse.destroy()
        executor.close()
