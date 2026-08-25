"""Lifecycle tests for segmented automatic AOT recording.

The recorder is replaced with a tiny in-memory fake so these tests exercise
scope ownership, cleanup, and same-backend replay without requiring a GPU
driver or claiming queue overlap.  Run with ``BACKEND=cpu``;
other backends are skipped because this suite intentionally never probes them.
"""

from __future__ import annotations

import os
from pathlib import Path
import sys
import unittest

try:
    from taichi_vision.taichi_aot.auto_pipeline import GraphSpec
except ModuleNotFoundError:  # direct ``python path/to/test_*.py`` invocation
    sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
    from taichi_vision.taichi_aot.auto_pipeline import GraphSpec


class _FakeModule:
    def __init__(self):
        self.calls = []

    def run(self, name, **kwargs):
        self.calls.append((str(name), dict(kwargs)))


class _CancelledError(Exception):
    pass


class _FakeRecorder:
    def __init__(self, owner, name):
        self.owner = owner
        self.name = str(name)

    def __enter__(self):
        owner = self.owner
        owner.current_pipeline = self.name
        owner.recorded_pipelines.add(self.name)
        owner._pipeline_recordings[self.name] = {
            "active": True,
            "owner_thread": None,
            "generation": owner._generation,
        }
        return self

    def __exit__(self, exc_type, _exc_value, _traceback):
        owner = self.owner
        record = owner._pipeline_recordings.get(self.name)
        owns_record = (
            record is not None and record.get("generation") == owner._generation
        )
        if owns_record:
            record["active"] = False
            if owner.current_pipeline == self.name:
                owner.current_pipeline = None
            if exc_type is not None:
                owner.recorded_pipelines.discard(self.name)
        elif owner.current_pipeline == self.name:
            owner.current_pipeline = None
        return False


class SegmentedPipelineLifecycleTests(unittest.TestCase):
    """Use a fake recorder while retaining the real engine state machine."""

    def setUp(self):
        if os.environ.get("BACKEND", "").lower() not in {
            "cpu",
            "cpu_x86_64_windows",
        }:
            self.skipTest("set BACKEND=cpu for lifecycle tests")
        from taichi_vision.taichi_aot.engine import engine as engine_handle

        self.engine = engine_handle._live()
        self._original = {
            name: self.engine.__dict__.get(name, None)
            for name in (
                "rec_pipeline",
                "sync",
                "use_pipeline",
                "_drop_pipeline_recording",
            )
        }
        self._had_instance_attr = {
            name: name in self.engine.__dict__ for name in self._original
        }
        self._old_generation = self.engine._generation
        self._had_test_attrs = {
            name: name in self.engine.__dict__
            for name in ("_test_fail_submit", "_test_use")
        }
        self.engine._pipeline_recordings.clear()
        self.engine._pipeline_intermediates.clear()
        self.engine.recorded_pipelines.clear()
        self.engine.current_pipeline = None
        self.engine._generation = 0
        self.engine._test_fail_submit = False
        self.engine._test_use = []

        self.engine.rec_pipeline = lambda name, **_kwargs: _FakeRecorder(
            self.engine, name
        )
        self.engine.sync = lambda: None

        def drop(name, *, destroy_intermediates=False):
            del destroy_intermediates
            name = str(name)
            self.engine.recorded_pipelines.discard(name)
            self.engine._pipeline_recordings.pop(name, None)
            self.engine._pipeline_intermediates.pop(name, None)
            if self.engine.current_pipeline == name:
                self.engine.current_pipeline = None

        def use(name, overrides=None):
            del overrides
            name = str(name)
            self.engine._test_use.append(name)
            record = self.engine._pipeline_recordings.get(name)
            if self.engine._test_fail_submit:
                raise RuntimeError("injected segmented submit failure")
            if (
                record is not None
                and record.get("generation") != self.engine._generation
            ):
                drop(name)

        self.engine._drop_pipeline_recording = drop
        self.engine.use_pipeline = use

        self.specs = (
            GraphSpec("a1", 64, module_key="module_a"),
            GraphSpec("a2", 64, module_key="module_a"),
            GraphSpec("b1", 64, module_key="module_b"),
            GraphSpec("b2", 64, module_key="module_b"),
        )

    def tearDown(self):
        self.engine.current_pipeline = None
        self.engine.recorded_pipelines.clear()
        self.engine._pipeline_recordings.clear()
        self.engine._pipeline_intermediates.clear()
        self.engine._generation = self._old_generation
        for name, existed in self._had_test_attrs.items():
            if not existed:
                self.engine.__dict__.pop(name, None)
        for name, value in self._original.items():
            if self._had_instance_attr[name]:
                setattr(self.engine, name, value)
            else:
                self.engine.__dict__.pop(name, None)

    def _dispatch_scope(self, module, *, names=None, error=None, name="lifecycle"):
        names = tuple(names or ("a1", "a2", "b1", "b2"))
        with self.engine.auto_pipeline(self.specs, name=name) as plan:
            self.assertEqual(plan.mode, "segmented")
            for graph_name in names:
                self.engine._auto_pipeline_before_run(graph_name, {"value": 1})
                if self.engine.current_pipeline:
                    self.engine._auto_pipeline_capture_call(
                        module, graph_name, {"value": 1}
                    )
            if error is not None:
                raise error

    def test_repeated_recording_and_submit_failure_replay(self):
        module = _FakeModule()
        self._dispatch_scope(module)
        self._dispatch_scope(module)
        self.assertEqual(len(self.engine._test_use), 4)
        self.assertFalse(self.engine.recorded_pipelines)
        self.assertFalse(self.engine._pipeline_recordings)

        self.engine._test_fail_submit = True
        module = _FakeModule()
        self._dispatch_scope(module, name="submit_failure")
        self.assertEqual(len(module.calls), 4)
        self.assertFalse(self.engine.recorded_pipelines)
        self.assertFalse(self.engine._pipeline_recordings)

    def test_exception_and_cancellation_cleanup(self):
        module = _FakeModule()
        with self.assertRaises(ValueError):
            self._dispatch_scope(module, names=("a1", "a2"), error=ValueError("stop"))
        # The first segment has already submitted; only the active failing
        # segment is replayed, preserving exception semantics.
        self.assertEqual(len(module.calls), 2)
        self.assertFalse(self.engine.recorded_pipelines)
        self.assertFalse(self.engine._pipeline_recordings)

        module = _FakeModule()
        with self.assertRaises(_CancelledError):
            self._dispatch_scope(
                module,
                names=("a1", "a2"),
                error=_CancelledError("cancelled"),
                name="cancelled",
            )
        self.assertEqual(module.calls, [])
        self.assertFalse(self.engine.recorded_pipelines)
        self.assertFalse(self.engine._pipeline_recordings)

    def test_stale_generation_is_rejected_without_replay(self):
        module = _FakeModule()
        with self.assertRaisesRegex(RuntimeError, "invalidated"):
            with self.engine.auto_pipeline(self.specs, name="stale") as plan:
                self.assertEqual(plan.mode, "segmented")
                for graph_name in ("a1", "a2"):
                    self.engine._auto_pipeline_before_run(graph_name, {"value": 1})
                    if self.engine.current_pipeline:
                        self.engine._auto_pipeline_capture_call(
                            module, graph_name, {"value": 1}
                        )
                # Simulate a runtime reinitialization while the recorder is
                # open.  Old handles are not replayable and must be dropped.
                self.engine._generation = 1
        self.assertEqual(module.calls, [])
        self.assertFalse(self.engine.recorded_pipelines)
        self.assertFalse(self.engine._pipeline_recordings)


if __name__ == "__main__":
    unittest.main()
