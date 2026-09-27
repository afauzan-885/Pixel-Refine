"""Artifact-level ABI assertions for the Hamilton demosaic graphs.

These tests read the packed ``.tcm`` archive instead of running a kernel, so
they need no backend and cannot be fooled by a stale in-memory module.  They
exist because a graph can carry arguments that no kernel reads: the Hamilton
3-channel graph used to declare a full-resolution ``wb_bayer`` scratch plane
plus an unused ``cmatrix``, and only the archive records that ABI.

Two independent checks are used, because the two artifact families encode the
graph index differently:

* CPU/CUDA archives ship a Taichi binary index (``graphs.tcb``) plus one ``.ll``
  member per compiled kernel, while graphics archives ship ``graphs.json``.
* The ZIP member list is therefore the encoding-independent, exact source of
  truth for *which kernels exist*, and the index is scanned for *argument
  names*.  The scan carries positive controls so it cannot pass vacuously.

The tests skip when the target artifact has not been compiled on this machine.
"""

from __future__ import annotations

import json
import os
import unittest
import zipfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[4]
PROJECT_TCM_ROOT = _REPO_ROOT / "taichi_vision" / "taichi_algorithm" / "aot_tcm"
TARGET_ID = os.environ.get("PIXEL_REFINE_TEST_TARGET", "cpu_x86_64_windows")
ARTIFACT = PROJECT_TCM_ROOT / TARGET_ID / f"hamilton_{TARGET_ID}.tcm"

EXPECTED_SCALARS = (
    "wb_r",
    "wb_g1",
    "wb_b",
    "wb_g2",
    "black",
    "white",
    "h",
    "w",
    "c00",
    "c01",
    "c10",
    "c11",
)

# Names that must still be present, used both as a sanity check on the scan and
# to prove the archive under test is the Hamiltonian suite and not, say, an
# empty staging artifact.
REQUIRED_KERNELS = (
    "_ha_green_direct_kernel",
    "_ha_red_blue_direct_kernel",
    "_ha_grayscale_from_green_kernel",
)

REMOVED_KERNEL = "preprocess_wb"


class HamiltonArchive:
    """Read-only view over one packed AOT archive."""

    def __init__(self, path: Path):
        self.path = path
        with zipfile.ZipFile(path, "r") as archive:
            self.members = tuple(archive.namelist())
            self.index_name = next(
                (name for name in ("graphs.json", "graphs.tcb") if name in self.members),
                None,
            )
            self.index_bytes = archive.read(self.index_name) if self.index_name else b""

    @property
    def kernel_members(self) -> tuple[str, ...]:
        return tuple(name for name in self.members if name.endswith(".ll"))

    @property
    def graph_index(self) -> dict | None:
        """Return ``{graph: {"kernels": [...], "args": [...]}}`` for a JSON index."""

        if self.index_name != "graphs.json":
            return None
        index = {}
        for entry in json.loads(self.index_bytes.decode("utf-8")):
            dispatches = entry.get("value", {}).get("dispatches", [])
            index[entry["key"]] = {
                "kernels": [item.get("kernel_name", "") for item in dispatches],
                "args": [
                    argument.get("name", "")
                    for item in dispatches
                    for argument in item.get("symbolic_args", [])
                ],
            }
        return index

    def index_contains(self, token: str) -> bool:
        return token.encode("utf-8") in self.index_bytes


class TestHamiltonArtifactAbi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not ARTIFACT.is_file():
            raise unittest.SkipTest(f"artifact not compiled: {ARTIFACT}")
        cls.archive = HamiltonArchive(ARTIFACT)
        if cls.archive.index_name is None:
            raise unittest.SkipTest(f"no graph index inside {ARTIFACT.name}")

    def test_the_archive_is_the_hamilton_suite(self):
        """Positive control: the scan must see the kernels Hamilton still needs."""

        kernels = " ".join(self.archive.kernel_members)
        for required in REQUIRED_KERNELS:
            self.assertIn(required, kernels, msg=f"missing kernel {required}")
        self.assertGreaterEqual(len(self.archive.kernel_members), 7)

    def test_the_dead_preprocess_kernel_is_gone(self):
        """The archive must not compile a kernel that only wrote a dead plane."""

        offenders = [
            name for name in self.archive.members if REMOVED_KERNEL in name
        ]
        self.assertEqual(
            offenders, [], msg=f"archive still contains {REMOVED_KERNEL}: {offenders}"
        )

    def test_no_graph_declares_a_dead_white_balance_plane(self):
        """Hamilton reads the Bayer frame directly, so nothing needs wb_bayer."""

        # Positive control first: a name that must be present, so a rename or an
        # unreadable index cannot make the real assertion pass for free.
        self.assertTrue(
            self.archive.index_contains("green"),
            msg="the graph index is not readable; the wb_bayer check would be vacuous",
        )
        self.assertFalse(
            self.archive.index_contains("wb_bayer"),
            msg="a Hamilton graph still declares the unused wb_bayer plane",
        )

    def test_three_channel_graph_has_the_minimal_contract(self):
        """Exact argument contract when the index is JSON-encoded."""

        index = self.archive.graph_index
        if index is None:
            # A binary index can still confirm the graph exists and, together
            # with the global wb_bayer check, that its contract is minimal.
            self.assertTrue(
                self.archive.index_contains("hamilton_demosaic_3channel"),
                msg="the 3-channel graph must be registered",
            )
            self.assertFalse(self.archive.index_contains("wb_bayer"))
            return

        graph = index.get("hamilton_demosaic_3channel")
        self.assertIsNotNone(graph, "the 3-channel graph must be registered")
        self.assertNotIn("wb_bayer", graph["args"])
        self.assertNotIn("cmatrix", graph["args"])
        for name in ("bayer", "green", "dst"):
            self.assertIn(name, graph["args"], msg=f"missing array argument {name}")
        for name in EXPECTED_SCALARS:
            self.assertIn(name, graph["args"], msg=f"missing scalar argument {name}")

    def test_default_graph_keeps_its_contract(self):
        """Removing the dead plane must not shrink a graph that genuinely uses it."""

        self.assertTrue(self.archive.index_contains("hamilton_demosaic"))
        index = self.archive.graph_index
        if index is None:
            return
        graph = index.get("hamilton_demosaic")
        self.assertIsNotNone(graph)
        for name in ("bayer", "green", "dst"):
            self.assertIn(name, graph["args"], msg=name)
        self.assertNotIn("wb_bayer", graph["args"])

    def test_tonemapped_graph_uses_the_colour_matrix_it_declares(self):
        index = self.archive.graph_index
        if index is None:
            return
        graph = index.get("hamilton_demosaic_tonemapped")
        self.assertIsNotNone(graph)
        self.assertIn("cmatrix", graph["args"])
        self.assertIn("dst", graph["args"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
