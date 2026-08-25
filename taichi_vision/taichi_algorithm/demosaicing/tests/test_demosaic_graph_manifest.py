"""Contract tests for the modular demosaic graph/runtime boundary.

These tests intentionally avoid loading a TCM or invoking ``aot_api``.  They
exercise the dependency-free graph manifest and the small runtime contracts
with fake buffers/dispatchers, so a graph rename cannot silently drift into a
wrapper-only selector or a broken cleanup path.
"""

from __future__ import annotations

import sys
import unittest
from collections import Counter
from pathlib import Path
import re


# Allow this file to be run directly from the repository checkout as well as
# through ``python -m unittest``.
_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from taichi_vision.taichi_algorithm.demosaicing.demosaic_graph_manifest import (
    GRAPH_MANIFEST,
    graph_specs,
    registered_graph_names,
    resolve_graph_name,
)
from taichi_vision.taichi_algorithm.demosaicing.demosaic_runtime import (
    DemosaicBufferSet,
    DemosaicGraphSpec,
    DemosaicInputs,
    DemosaicRunner,
)


class _FakeBuffer:
    def __init__(self, label: str):
        self.label = label
        self.release_count = 0

    def release(self):
        self.release_count += 1


class _FakeEngine:
    def __init__(self):
        self.sync_count = 0
        self.allocations = []

    def allocate(self, shape, **kwargs):
        buffer = _FakeBuffer(f"scratch-{len(self.allocations)}")
        self.allocations.append((shape, kwargs, buffer))
        return buffer

    def sync(self):
        self.sync_count += 1


class DemosaicGraphManifestTests(unittest.TestCase):
    def test_graph_names_are_unique_within_each_family(self):
        """A family cannot expose two variants under the same graph name.

        ``rgb_to_bgr_i32`` is deliberately shared by several family TCMs, so
        it is the only permitted duplicate across family manifests.
        """

        for family, variants in GRAPH_MANIFEST.items():
            names = tuple(variants.values())
            self.assertEqual(
                len(names),
                len(set(names)),
                f"duplicate graph name in {family}: {names}",
            )

        counts = Counter(spec.graph_name for spec in graph_specs())
        duplicates = {name for name, count in counts.items() if count > 1}
        self.assertLessEqual(duplicates, {"rgb_to_bgr_i32"})
        self.assertEqual(
            len(registered_graph_names()),
            len(set(registered_graph_names())),
        )

    def test_canonical_families_and_aliases_resolve(self):
        for family, variants in GRAPH_MANIFEST.items():
            self.assertEqual(resolve_graph_name(family), variants["default"])
            for variant, graph_name in variants.items():
                self.assertEqual(resolve_graph_name(family, variant), graph_name)

        self.assertEqual(resolve_graph_name("bilinear_demosaice"), "bilinear_demosaice")
        self.assertEqual(resolve_graph_name("hamilton_adams"), "hamilton_demosaic")
        self.assertEqual(resolve_graph_name("dcb_demosaice"), "dcb_demosaic")
        self.assertEqual(resolve_graph_name("mlri_admm_demosaice"), "mlri_admm_demosaic")
        self.assertEqual(resolve_graph_name("hamilton", "tone_map"), "hamilton_demosaic_tonemapped")

    def test_stale_dcb_and_mlri_selectors_are_rejected(self):
        stale_selectors = (
            ("dcb", "fast"),
            ("dcb", "cross"),
            ("dcb", "legacy"),
            ("mlri", "separable"),
            ("mlri", "window3"),
            ("mlri", "guided"),
        )
        for family, variant in stale_selectors:
            with self.subTest(family=family, variant=variant):
                with self.assertRaises(ValueError):
                    resolve_graph_name(family, variant)

    def test_manifest_matches_builder_graph_inventory(self):
        builder = (
            Path(__file__).resolve().parents[1] / "demosaic_aot_builder.py"
        )
        source = builder.read_text(encoding="utf-8")
        builder_names = set(
            re.findall(r'module\.add_graph\("([^"]+)"', source)
        )
        self.assertEqual(builder_names, set(registered_graph_names()))

    def test_runner_validates_and_dispatches_canonical_graph(self):
        calls = []

        def dispatcher(graph_name, values, **kwargs):
            calls.append((graph_name, values, kwargs))
            return "ok"

        spec = DemosaicGraphSpec(
            family="bilinear",
            graph_name=resolve_graph_name("bilinear"),
            required_inputs=("bayer", "cmatrix"),
        )
        runner = DemosaicRunner(spec, dispatcher)
        values = DemosaicInputs(bayer="raw", cmatrix="matrix")

        self.assertEqual(runner.run(values, backend="fake"), "ok")
        self.assertEqual(len(calls), 1)
        graph_name, resolved, kwargs = calls[0]
        self.assertEqual(graph_name, "bilinear_demosaice")
        self.assertEqual(resolved["bayer"], "raw")
        self.assertEqual(resolved["cmatrix"], "matrix")
        self.assertEqual(kwargs, {"backend": "fake"})

        with self.assertRaises(ValueError):
            runner.run({"bayer": "raw"})

    def test_buffer_set_releases_owned_buffers_and_preserves_borrowed(self):
        engine = _FakeEngine()
        borrowed = _FakeBuffer("borrowed")
        adopted = _FakeBuffer("adopted")

        with DemosaicBufferSet(runtime_engine=engine) as buffers:
            buffers.register("borrowed", borrowed)
            buffers.register("adopted", adopted, owned=True)
            scratch = buffers.scratch("temporary", (4, 4))
            detached = buffers.detach("adopted")
            self.assertIs(detached, adopted)
            self.assertIs(buffers["temporary"], scratch)

        self.assertEqual(engine.sync_count, 1)
        self.assertEqual(adopted.release_count, 0)
        self.assertEqual(borrowed.release_count, 0)
        self.assertEqual(scratch.release_count, 1)

        with self.assertRaises(RuntimeError):
            buffers.register("late", _FakeBuffer("late"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
