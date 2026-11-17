"""Routing tests for resident factory/provider lifecycle through the session."""

from types import SimpleNamespace

import numpy as np

from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.pipeline_process.aligners import (
    factory,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.pipeline_process.raw_pipeline import (
    provider as provider_module,
)


class _RecordingSession:
    """Records the session API the pipeline actually calls."""

    def __init__(self):
        self.calls = []

    def managed_api(self, api):
        self.calls.append(("managed_api", api))
        return ("managed", api)

    def _track(self, result):
        self.calls.append(("_track", result))
        return result

    def view(self, shape, **kwargs):
        buffer = SimpleNamespace(shape=shape, kwargs=kwargs)
        self.calls.append(("view", buffer))
        return buffer

    def borrow(self, resource, *, from_session=None):
        self.calls.append(("borrow", resource))
        return resource

    def release(self, resource=None, *, to=None, retain=False, keep=()):
        self.calls.append(("release", resource, retain))
        return 1

    def release_tree(self, resource):
        self.calls.append(("release_tree", resource))


class _RecordingRuntime:
    def __init__(self, session):
        self.buffer_session = session
        self.session = session

    @property
    def managed_api(self):
        return self.session.managed_api

    def ensure_session(self):
        return self.session

    def own(self, resource, releaser=None):
        return self.session.borrow(resource)


def test_factory_helpers_route_ownership_through_runtime_session(monkeypatch):
    session = _RecordingSession()
    runtime = _RecordingRuntime(session)
    monkeypatch.setattr(factory, "current_pipeline_runtime", lambda: runtime)

    api = object()
    result = object()
    component = object()
    exported = object()

    assert factory._managed_api(api) == ("managed", api)
    assert factory._track_gpu_result(result) is result
    assert factory._own_component(component) is component
    assert factory._export_result(exported) is exported

    assert [call[0] for call in session.calls] == [
        "managed_api",
        "_track",
        "borrow",
        "borrow",
        "release",
    ]
    export_release = session.calls[-1]
    assert export_release[1] is exported
    assert export_release[2] is True


def test_factory_cleanup_releases_work_item_without_protected_carrier(monkeypatch):
    session = _RecordingSession()
    runtime = _RecordingRuntime(session)
    monkeypatch.setattr(factory, "current_pipeline_runtime", lambda: runtime)
    first, shared, repeated = object(), object(), object()

    factory._destroy_work_item((first, shared))
    factory._destroy_work_item_except((first, shared, repeated, repeated), shared)

    released = [call[1] for call in session.calls if call[0] == "release"]
    assert released[0] == (first, shared)
    assert released[1] == (first, repeated)


def test_raw_provider_releases_cfa_workspace_via_active_runtime(monkeypatch):
    from pixel_refine_desktop.enhance_stack.core.algorithm import pipeline_runtime

    session = _RecordingSession()
    runtime = _RecordingRuntime(session)
    monkeypatch.setattr(pipeline_runtime, "current_pipeline_runtime", lambda: runtime)

    provider = provider_module.RawPipelineProvider(["reference.dng", "support.dng"])
    provider._engine = object()
    frame = SimpleNamespace(
        samples=np.zeros((8, 12), dtype=np.float32),
        phase_origin=(0, 0),
    )
    provider._ensure_cfa_workspace(frame)
    buffers = tuple(provider._cfa_planes_gpu)

    assert len(buffers) == 4
    assert all(call[0] == "view" for call in session.calls)
    assert not hasattr(provider, "_cfa_buffer_session")

    provider.close()

    released = [call[1] for call in session.calls if call[0] == "release"]
    assert released == list(buffers)
    assert provider._cfa_planes_gpu is None
