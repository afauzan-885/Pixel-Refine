from types import SimpleNamespace

import numpy as np


def test_hdr_mask_fusion_selects_unsaturated_samples_and_tracks_radiance():
    from pixel_refine_desktop.enhance_stack.core.algorithm.HDR.hdr_mask_pipeline import (
        HDRMaskFusion,
    )

    fusion = HDRMaskFusion((2, 2, 3), radiance_enabled=True)
    first = np.asarray(
        [
            [[0.4, 0.3, 0.3], [0.1, 0.1, 0.1]],
            [[0.99, 0.99, 0.99], [0.2, 0.2, 0.2]],
        ],
        dtype=np.float32,
    )
    second = np.asarray(
        [
            [[1.0, 1.0, 1.0], [0.2, 0.2, 0.2]],
            [[1.0, 1.0, 1.0], [0.8, 0.8, 0.8]],
        ],
        dtype=np.float32,
    )
    valid = np.asarray([[True, True], [True, False]])

    fusion.add_frame(first, valid_mask=valid)
    fusion.add_frame(second, exposure_scale=2.0, valid_mask=valid)
    ldr, radiance = fusion.finalize(first)

    np.testing.assert_array_equal(fusion.source_map, [[0, 1], [0, -1]])
    np.testing.assert_allclose(ldr[0, 0], first[0, 0])
    np.testing.assert_allclose(ldr[0, 1], second[0, 1])
    np.testing.assert_allclose(radiance[0, 1], second[0, 1] / 2.0)
    np.testing.assert_allclose(ldr[1, 1], first[1, 1])


def test_hdr_mask_algorithm_runs_through_array_recipe_without_noise_estimation(
    monkeypatch,
):
    from pixel_refine_desktop.enhance_stack.core.algorithm import catalog
    from pixel_refine_desktop.enhance_stack.core.algorithm.HDR import runtime_recipe
    from pixel_refine_desktop.enhance_stack.core.algorithm.pipeline_runtime import (
        PipelineRuntime,
    )

    sessions = []

    class Session:
        def close(self):
            self.closed = True

    class RecordingRuntime(PipelineRuntime):
        def __init__(self, **kwargs):
            super().__init__(
                **kwargs,
                session_factory=lambda _engine: sessions.append(Session())
                or sessions[-1],
            )

    monkeypatch.setattr(
        "pixel_refine_desktop.enhance_stack.core.algorithm.pipeline_runtime.PipelineRuntime",
        RecordingRuntime,
    )
    monkeypatch.setattr(
        runtime_recipe,
        "estimate_noise_taichi",
        lambda *_args: (_ for _ in ()).throw(
            AssertionError("HDR Mask must not invoke noise estimation")
        ),
    )

    algorithm = catalog.get_spec("hdr", "mask").create()
    frames = [
        np.full((8, 8, 3), value, dtype=np.float32)
        for value in (0.2, 0.6)
    ]
    result = algorithm.run(SimpleNamespace(session=None), iter(frames))

    np.testing.assert_array_equal(result, frames[1])
    assert algorithm.NAME == "HDR Mask"
    assert sessions and sessions[0].closed is True


def test_hdr_mask_batch_pipeline_selects_support_pixels(monkeypatch, tmp_path):
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
        "reference.png": np.full((8, 9, 3), 0.25, dtype=np.float32),
        "support.png": np.full((8, 9, 3), 0.65, dtype=np.float32),
    }
    written = []

    class Session:
        def close(self):
            self.closed = True

    class RecordingRuntime(PipelineRuntime):
        def __init__(self, **kwargs):
            super().__init__(**kwargs, session_factory=lambda _engine: Session())

    analyses = [
        FrameAnalysis(path, score, 0.5, (8, 9, 3), None, None, None, None)
        for path, score in (("reference.png", 0.9), ("support.png", 0.8))
    ]
    monkeypatch.setattr(
        streaming_pipeline, "_analyze_inputs", lambda *args, **kwargs: analyses
    )
    monkeypatch.setattr(
        streaming_pipeline, "_load_rgb", lambda path: frames[path].copy()
    )
    monkeypatch.setattr(
        streaming_pipeline, "_metadata_gate", lambda _items: (False, "missing", [])
    )
    monkeypatch.setattr(
        streaming_pipeline,
        "_write_tiff_atomic",
        lambda path, image, **kwargs: written.append(
            (str(path), np.array(image, copy=True))
        ),
    )
    monkeypatch.setattr(aot_api, "align_mtb", lambda _reference, _support: (0, 0))
    monkeypatch.setattr(
        aot_api, "warp_affine_aot", lambda support, *_args: support.copy()
    )
    monkeypatch.setattr(
        "pixel_refine_desktop.enhance_stack.core.algorithm.pipeline_runtime.PipelineRuntime",
        RecordingRuntime,
    )
    monkeypatch.setattr(
        runtime_recipe,
        "estimate_noise_taichi",
        lambda *_args: (_ for _ in ()).throw(
            AssertionError("HDR Mask must not invoke noise estimation")
        ),
    )

    result = streaming_pipeline.run_hdr_pipeline(
        ["reference.png", "support.png"],
        user_reference="reference.png",
        algorithm_name="HDR Mask",
        output_directory=tmp_path,
    )

    assert result["algorithm"] == "HDR Mask"
    assert result["ldr_path"].endswith("_hdr_mask_ldr.tif")
    assert len(written) == 1
    np.testing.assert_array_equal(
        written[0][1], np.full((8, 9, 3), 0.65, dtype=np.float32)
    )

