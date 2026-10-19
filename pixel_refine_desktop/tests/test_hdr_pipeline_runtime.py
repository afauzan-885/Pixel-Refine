from types import SimpleNamespace

import numpy as np
import pytest


def test_hdr_array_entrypoint_uses_runtime_and_preserves_frame_order(monkeypatch):
    from pixel_refine_desktop.enhance_stack.core.algorithm.HDR import HDR
    from pixel_refine_desktop.enhance_stack.core.algorithm.HDR import runtime_recipe
    from pixel_refine_desktop.enhance_stack.core.algorithm.pipeline_runtime import (
        PipelineRuntime,
    )

    sessions = []

    class Session:
        def __init__(self):
            self.owned = []

        def own(self, resource, *, releaser=None):
            self.owned.append(resource)
            return resource

        def release_buffer(self, resource):
            self.owned.remove(resource)

        def close(self):
            self.closed = True

    class RecordingFusion:
        def __init__(self, shape, *, radiance_enabled):
            assert radiance_enabled is False
            self.frames = []

        def add_frame(self, frame, **_kwargs):
            self.frames.append(np.array(frame, copy=True))

        def finalize(self, _reference):
            return np.mean(self.frames, axis=0), None

    class RecordingRuntime(PipelineRuntime):
        def __init__(self, **kwargs):
            super().__init__(
                **kwargs,
                session_factory=lambda _engine: sessions.append(Session()) or sessions[-1],
            )

    monkeypatch.setattr(
        "pixel_refine_desktop.enhance_stack.core.algorithm.pipeline_runtime.PipelineRuntime",
        RecordingRuntime,
    )
    monkeypatch.setattr(runtime_recipe, "WeightedHDRFusion", RecordingFusion)
    monkeypatch.setattr(
        runtime_recipe,
        "estimate_noise_taichi",
        lambda _gray, _session: 0.0,
    )

    frames = [
        np.full((8, 9, 3), value, dtype=np.float32)
        for value in (0.1, 0.3, 0.8)
    ]
    output = HDR.WeightedHDRAlgorithm().run(
        SimpleNamespace(session=None), iter(frames)
    )

    np.testing.assert_array_equal(output, np.mean(frames, axis=0))
    assert sessions and sessions[0].closed is True
    assert sessions[0].owned == []


def test_hdr_array_entrypoint_rejects_empty_iterable():
    from pixel_refine_desktop.enhance_stack.core.algorithm.HDR.HDR import (
        WeightedHDRAlgorithm,
    )

    with pytest.raises(ValueError, match="at least one frame"):
        WeightedHDRAlgorithm().run(SimpleNamespace(session=None), iter(()))


def test_hdr_path_pipeline_runs_alignment_and_fusion_through_recipe(monkeypatch, tmp_path):
    from pixel_refine_desktop.enhance_stack.core.algorithm.HDR import runtime_recipe
    from pixel_refine_desktop.enhance_stack.core.algorithm.HDR import streaming_pipeline
    from pixel_refine_desktop.enhance_stack.core.algorithm.HDR.streaming_pipeline import (
        FrameAnalysis,
    )
    from pixel_refine_desktop.enhance_stack.core.algorithm.pipeline_runtime import (
        PipelineRuntime,
    )
    from taichi_vision.taichi_algorithm import aot_api

    frames = {
        "reference.png": np.full((8, 9, 3), 0.2, dtype=np.float32),
        "support.png": np.full((8, 9, 3), 0.4, dtype=np.float32),
    }
    loaded_supports = []
    written = []

    class Session:
        def close(self):
            self.closed = True

    class RecordingRuntime(PipelineRuntime):
        def __init__(self, **kwargs):
            super().__init__(
                **kwargs,
                session_factory=lambda _engine: Session(),
            )

    class RecordingFusion:
        def __init__(self, shape, *, radiance_enabled):
            assert shape == (8, 9, 3)
            assert radiance_enabled is False
            self.frames = []

        def add_frame(self, frame, **_kwargs):
            self.frames.append(np.array(frame, copy=True))

        def finalize(self, _reference):
            return np.mean(self.frames, axis=0), None

    analyses = [
        FrameAnalysis(path, score, 0.5, (8, 9, 3), None, None, None, None)
        for path, score in (("reference.png", 0.9), ("support.png", 0.8))
    ]
    monkeypatch.setattr(streaming_pipeline, "_analyze_inputs", lambda *args, **kwargs: analyses)
    monkeypatch.setattr(streaming_pipeline, "_load_rgb", lambda path: frames[path].copy())
    monkeypatch.setattr(streaming_pipeline, "_metadata_gate", lambda _items: (False, "missing", []))
    monkeypatch.setattr(
        streaming_pipeline,
        "_write_tiff_atomic",
        lambda path, image, **kwargs: written.append((str(path), np.array(image, copy=True))),
    )
    monkeypatch.setattr(runtime_recipe, "WeightedHDRFusion", RecordingFusion)
    monkeypatch.setattr(runtime_recipe, "estimate_noise_taichi", lambda _gray, _session: 0.0)
    monkeypatch.setattr(aot_api, "align_mtb", lambda _reference, _support: (0, 0))
    monkeypatch.setattr(aot_api, "warp_affine_aot", lambda support, *_args: support.copy())
    monkeypatch.setattr(
        streaming_pipeline,
        "PipelineRuntime",
        RecordingRuntime,
    )
    original_path_source_load = runtime_recipe.HDRPathSource.load_support

    def record_support(self, index):
        loaded_supports.append(index)
        return original_path_source_load(self, index)

    monkeypatch.setattr(runtime_recipe.HDRPathSource, "load_support", record_support)

    result = streaming_pipeline.run_hdr_pipeline(
        ["reference.png", "support.png"],
        user_reference="reference.png",
        algorithm_name=streaming_pipeline.CARD_NAME,
        output_directory=tmp_path,
    )

    assert loaded_supports == [0]
    assert len(written) == 1
    np.testing.assert_array_equal(written[0][1], np.full((8, 9, 3), 0.3, np.float32))
    assert result["frame_count"] == 2


@pytest.mark.parametrize("shape,graph", [((8, 8), "estimate_noise_gray"), ((8, 8, 3), "estimate_noise")])
def test_noise_gpu_routing_respects_scalar_and_vector_graph_contract(monkeypatch, shape, graph):
    import importlib

    from taichi_vision import taichi_aot
    from taichi_vision.taichi_algorithm import aot_api

    noise = importlib.import_module("taichi_vision.taichi_algorithm.enhancement.estimate_noise")

    calls = []

    class Source:
        is_vector = False

        def __init__(self):
            self.shape = shape

        def to_numpy(self):
            raise AssertionError("noise routing must not read back the source")

        def view_as_vector(self, enabled):
            assert graph == "estimate_noise" and enabled
            calls.append("vector")
            return self

    class Statistics:
        def to_numpy(self, *, out):
            out.fill(0.0)
            return out

    monkeypatch.setattr(taichi_aot, "get_engine", lambda: object())
    monkeypatch.setattr(aot_api, "_mod", lambda name: SimpleNamespace(
        run=lambda selected_graph, **kwargs: calls.append(selected_graph)
    ))
    monkeypatch.setattr(noise, "_gpu_noise_scratch", lambda *args, **kwargs: (
        Statistics(), np.empty((1,), np.float32)
    ))
    assert noise.estimate_noise(Source()) == (0.0, 0.0)
    assert calls == (["vector", graph] if len(shape) == 3 else [graph])
