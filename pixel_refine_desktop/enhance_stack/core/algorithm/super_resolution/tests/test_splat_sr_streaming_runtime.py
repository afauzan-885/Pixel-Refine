from __future__ import annotations

import os
import tempfile
import threading
import time

import numpy as np

from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.splat_sr import (
    SplatSRAOTEngine,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.splat_sr.streaming_pipeline import (
    ImagePathSource,
    SplatSRRecipe,
    _RefinementBacking,
    _ReferenceState,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.pipeline_runtime import (
    PipelineCancelledError,
    PipelineRuntime,
)


def test_existing_splat_sr_import_facade_remains_available():
    from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.SplatSR import (
        SplatSRAlgorithm,
        main,
        running_splatting_sr,
        run_splat_sr_pipeline,
    )

    assert SplatSRAlgorithm is not None
    assert callable(main)
    assert callable(running_splatting_sr)
    assert callable(run_splat_sr_pipeline)
    assert SplatSRAOTEngine is not None


def test_worker_entrypoint_calls_canonical_streaming_pipeline(monkeypatch, tmp_path):
    from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution import (
        SplatSR,
        splat_SR,
    )
    from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.splat_sr import (
        legacy,
    )

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SPLATSR_USE_WEIGHTNET", "0")
    monkeypatch.setenv("SPLATSR_REFINEMENT_ITERATIONS", "0")
    paths = ["reference.dng", "support.dng"]
    calls = []
    progress = []

    class BatchAlgorithm:
        def __init__(self, db_path):
            assert db_path == "session.db"

        def get_all_image_paths_for_batch_process(self, batch_id):
            assert batch_id == 4
            return paths

    def run_pipeline(image_paths, **kwargs):
        calls.append((image_paths, kwargs))
        return kwargs["output_path"]

    def report(percent, message):
        progress.append((percent, message))

    def stop_requested():
        return False

    monkeypatch.setattr(legacy, "SplatSRAlgorithm", BatchAlgorithm)
    monkeypatch.setattr(splat_SR, "run_splat_sr_pipeline", run_pipeline)

    SplatSR.running_splatting_sr(
        db_path="session.db",
        batch_id=4,
        progress_callback=report,
        stop_callback=stop_requested,
    )

    assert len(calls) == 1
    image_paths, options = calls[0]
    assert image_paths is paths
    assert options["weight_source"] == "compute_spatial"
    assert options["progress_callback"] is report
    assert options["stop_event"] is stop_requested
    assert options["output_path"] == os.path.join(
        "database/stack", "reference_splattingSR.tif"
    )
    assert progress[-1] == (
        100,
        "Process finished successfully: reference_splattingSR.tif",
    )


def test_path_source_decodes_only_requested_indices(monkeypatch):
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.fusionet_engine import (
        weightnet_inference,
    )

    decoded = []

    def load(path):
        decoded.append(os.fspath(path))
        shape = (12, 16) if path.endswith("ref") else (6, 8)
        return np.full((*shape, 3), 0.25, dtype=np.float32)

    monkeypatch.setattr(weightnet_inference, "load_rgb_linear_image", load)
    source = ImagePathSource(["ref", "support-a", "support-b"])
    assert decoded == []

    reference = source.load_reference()
    assert reference.shape == (12, 16, 3)
    assert decoded == ["ref"]

    support = source.load_support(2)
    assert support.shape == reference.shape
    assert decoded == ["ref", "support-b"]


def test_recipe_processes_one_support_and_inverts_flow_in_place(monkeypatch):
    from taichi_vision import taichi_aot

    monkeypatch.setattr(
        taichi_aot,
        "AutoEnhance",
        lambda image, params=None: np.array(image, dtype=np.float32, copy=True),
    )

    class FakeSession:
        def __init__(self):
            self.reset_count = 0
            self.scratch = {}

        def acquire_host(self, shape, *, dtype, tag):
            if tag not in self.scratch:
                self.scratch[tag] = np.empty(shape, dtype=dtype)
            return self.scratch[tag]

        def reset_ring(self):
            self.reset_count += 1

    class FakeContext:
        def __init__(self):
            self.session = FakeSession()
            self.progress = []
            self.progress_callback = None

        def check_cancelled(self):
            return None

        def is_cancelled(self):
            return False

        def report(self, *args, **kwargs):
            self.progress.append((args, kwargs))

    class FakeAlgorithm:
        def __init__(self, flow):
            self.flow = flow

        def _estimate_alignment_pair(self, **kwargs):
            return self.flow

    class FakeProvider:
        def __init__(self):
            self.device_map = object()

        def generate_device(self, reference, support, *, session):
            assert reference.shape == support.shape == (8, 10)
            assert session is not None
            return self.device_map

    class FakeAccumulator:
        def __init__(self):
            self.arguments = None

        def add_frame(self, frame, flow, confidence):
            self.arguments = (frame, flow.copy(), confidence)

    reference = np.full((8, 10, 3), 0.2, dtype=np.float32)
    support = np.full((8, 10, 3), 0.3, dtype=np.float32)
    flow = np.zeros((8, 10, 2), dtype=np.float32)
    flow[..., 0] = 1.25
    provider = FakeProvider()
    state = _ReferenceState(
        reference_rgb=reference,
        reference_gray=np.full((8, 10), 0.2, dtype=np.float32),
        reference_carrier_gray=np.full((8, 10), 0.2, dtype=np.float32),
        analysis_params={},
        analysis_reference_rgb=None,
        accumulator=FakeAccumulator(),
        provider=provider,
        algorithm=FakeAlgorithm(flow),
        use_farneback=True,
        farneback_config={},
        matcher=None,
        bm_config=None,
        flow_proxy_scale=1.0,
        exposure_normalization=False,
        refinement=None,
        count=2,
    )
    context = FakeContext()
    recipe = SplatSRRecipe(["ref", "support"], exposure_normalization=False)

    recipe.process_support(1, support, state, context)

    assert state.accumulator.arguments[0] is support
    assert np.all(state.accumulator.arguments[1][..., 0] == -1.25)
    assert state.accumulator.arguments[2] is provider.device_map
    assert state.processed == 1
    assert context.session.reset_count == 1


def test_refinement_backing_closes_all_temporary_files(tmp_path, monkeypatch):
    make_temp_directory = tempfile.TemporaryDirectory
    monkeypatch.setattr(
        "pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.splat_sr.streaming_pipeline.tempfile.TemporaryDirectory",
        lambda prefix: make_temp_directory(prefix=prefix, dir=tmp_path),
    )
    backing = _RefinementBacking(2, 4, 6)
    paths = [backing.frames.filename, backing.flows.filename, backing.confidence.filename]
    backing.frames[0] = 1.0
    backing.flows[0] = 0.0
    backing.confidence[0] = 1.0

    backing.close()

    assert all(not os.path.exists(path) for path in paths)
    backing.close()  # idempotent for BufferSession teardown


def test_refinement_frame_view_does_not_materialize_memmap(tmp_path):
    from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.splat_sr.spatial_splat_sr import (
        _as_float_frames,
    )

    path = tmp_path / "frames.f32"
    source = np.memmap(path, mode="w+", dtype=np.float32, shape=(2, 3, 4))
    source[:] = 0.5
    result, squeezed = _as_float_frames(source)

    assert squeezed
    assert result.shape == (2, 3, 4, 1)
    assert np.shares_memory(result, source)
    source._mmap.close()


class _RuntimeTestSession:
    def __init__(self):
        self.resources = {}
        self.closed = False

    def own(self, resource, releaser=None):
        self.resources[id(resource)] = (resource, releaser)
        return resource

    def release_buffer(self, resource):
        entry = self.resources.pop(id(resource), None)
        if entry is not None and entry[1] is not None:
            entry[1](resource)

    def close(self):
        for resource, releaser in tuple(self.resources.values()):
            if releaser is not None:
                releaser(resource)
        self.resources.clear()
        self.closed = True


class _RuntimeTestSource:
    def __init__(self):
        self.loaded = []
        self.session = None

    def load_reference(self):
        return "reference"

    def load_support(self, index):
        self.loaded.append(index)
        return np.asarray([index], dtype=np.int32)


class _RuntimeTestRecipe:
    def __init__(self, *, delay=0.0, cancel_event=None, fail_at=None):
        self.delay = delay
        self.cancel_event = cancel_event
        self.fail_at = fail_at
        self.processed = []
        self.active = 0
        self.max_active = 0
        self.session = None
        self.max_owned_supports = 0

    def prepare_reference(self, reference, context):
        self.session = context.session
        return reference

    def process_support(self, index, support, reference_state, context):
        self.active += 1
        self.max_active = max(self.max_active, self.active)
        owned_supports = sum(
            1
            for resource, _ in self.session.resources.values()
            if isinstance(resource, np.ndarray)
        )
        self.max_owned_supports = max(self.max_owned_supports, owned_supports)
        try:
            self.processed.append(index)
            if self.delay:
                time.sleep(self.delay)
            if self.cancel_event is not None and index == 1:
                self.cancel_event.set()
            if self.fail_at == index:
                raise ValueError("injected support failure")
        finally:
            self.active -= 1

    def finalize(self, reference_state, context):
        return tuple(self.processed)


def test_pipeline_runtime_prefetch_is_bounded_and_ordered():
    source = _RuntimeTestSource()
    session = _RuntimeTestSession()
    recipe = _RuntimeTestRecipe(delay=0.04)
    runtime = PipelineRuntime(
        prefetch_depth=2,
        session_factory=lambda _engine: session,
    )

    result = runtime.execute(source, recipe, range(1, 8))

    assert result == tuple(range(1, 8))
    assert source.loaded == list(range(1, 8))
    assert recipe.max_active == 1
    assert recipe.max_owned_supports <= 3  # queued depth 2 + active support 1
    assert session.closed


def test_pipeline_runtime_depth_zero_loads_immediately_before_each_support():
    events = []

    class Source(_RuntimeTestSource):
        def load_support(self, index):
            events.append(("load", index))
            return super().load_support(index)

    class Recipe(_RuntimeTestRecipe):
        def process_support(self, index, support, reference_state, context):
            events.append(("process", index))
            super().process_support(index, support, reference_state, context)

    session = _RuntimeTestSession()
    runtime = PipelineRuntime(
        prefetch_depth=0,
        session_factory=lambda _engine: session,
    )
    recipe = Recipe()
    runtime.execute(Source(), recipe, range(1, 4))

    assert events == [
        ("load", 1),
        ("process", 1),
        ("load", 2),
        ("process", 2),
        ("load", 3),
        ("process", 3),
    ]
    assert session.closed


def test_pipeline_runtime_cancel_and_exception_close_session():
    cancel = threading.Event()
    session = _RuntimeTestSession()
    runtime = PipelineRuntime(
        prefetch_depth=2,
        stop_event=cancel,
        session_factory=lambda _engine: session,
    )
    with np.testing.assert_raises(PipelineCancelledError):
        runtime.execute(
            _RuntimeTestSource(),
            _RuntimeTestRecipe(cancel_event=cancel),
            range(1, 20),
        )
    assert session.closed

    session = _RuntimeTestSession()
    runtime = PipelineRuntime(
        prefetch_depth=2,
        session_factory=lambda _engine: session,
    )
    with np.testing.assert_raises_regex(ValueError, "injected support failure"):
        runtime.execute(
            _RuntimeTestSource(),
            _RuntimeTestRecipe(fail_at=2),
            range(1, 20),
        )
    assert session.closed
