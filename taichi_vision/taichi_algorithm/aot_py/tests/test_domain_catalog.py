"""Static capability inventory tests for the domain workflows."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

import numpy as np

from taichi_vision.taichi_algorithm.alignment.quality import choose_best_transform
from taichi_vision.taichi_algorithm.domain_catalog import (
    ALGORITHM_CATALOG,
    COMPOSED_AOT_LEAVES,
    audit_catalog,
)


_ROOT = Path(__file__).resolve().parents[4]


def _run_probe(code: str, *, mode: str, timeout: int = 180) -> dict:
    """Run one backend-isolated domain probe and parse its JSON result."""

    env = os.environ.copy()
    env.update(
        {
            "AOT_MODE": str(mode),
            "TAICHI_ARCH": "cpu",
            "TAICHI_ARCH": "cpu",
            "AOT_ARCH": "cpu",
            "BACKEND": "cpu",
            "AUTO_DESTROY": "0",
        }
    )
    # An older selector exported by a developer shell must not override the
    # explicit CPU route before the child imports Taichi.
    env.pop("TI_ARCH", None)
    completed = subprocess.run(
        [sys.executable, "-c", code],
        cwd=str(_ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if completed.returncode != 0:
        raise AssertionError(
            "domain probe failed:\n"
            f"stdout={completed.stdout}\n"
            f"stderr={completed.stderr}"
        )
    lines = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    payload_lines = [line for line in lines if line.startswith("{")]
    if not payload_lines:
        raise AssertionError(
            "domain probe did not emit JSON:\n"
            f"stdout={completed.stdout}\n"
            f"stderr={completed.stderr}"
        )
    return json.loads(payload_lines[-1])


class DomainCatalogTests(unittest.TestCase):
    def test_catalog_resolves_every_declared_entry(self):
        report = audit_catalog()
        self.assertEqual(report["total"], len(ALGORITHM_CATALOG))
        self.assertEqual(report["counts"].get("missing", 0), 0, report)
        backends = {entry["backend"] for entry in report["entries"]}
        self.assertIn("aot", backends)
        self.assertIn("numpy-reference", backends)

    def test_composed_aot_leaves_exist_in_compiler_registry_and_manifest(self):
        # AST/static compiler registry is intentionally imported without
        # initializing Taichi; this catches stale high-level routing names.
        from taichi_vision.taichi_algorithm.aot_py.compile_aot_backend_suite import (
            JOBS,
        )
        from taichi_vision.taichi_algorithm.aot_py.target_registry import (
            TARGET_BACKENDS,
        )

        for stage, leaves in COMPOSED_AOT_LEAVES.items():
            self.assertTrue(leaves, stage)
            for leaf in leaves:
                self.assertIn(
                    leaf, JOBS, f"{stage} references unregistered AOT leaf {leaf}"
                )
        self.assertIn("cpu_x86_64_windows", TARGET_BACKENDS)
        self.assertIn("vulkan_x86_64_windows_nvidia", TARGET_BACKENDS)

    def test_catalog_labels_keep_jit_and_aot_contracts_distinct(self):
        entries = {entry.name: entry for entry in ALGORITHM_CATALOG}
        self.assertEqual(entries["OFB_keypoints"].backend, "taichi-jit")
        self.assertIn("aot_api.ofb", entries["OFB_keypoints"].notes)
        self.assertEqual(entries["AKAZE_descriptors"].backend, "taichi-jit")
        self.assertIn("standalone descriptor", entries["AKAZE_descriptors"].notes)
        self.assertEqual(entries["Reinhard_tone_map"].backend, "taichi-jit-or-numpy")
        self.assertIn("AOT tone mapping", entries["Reinhard_tone_map"].notes)

    def test_ransac_transform_recovers_translation_with_outliers(self):
        rng = np.random.default_rng(9)
        source = np.array(
            [
                [x, y]
                for y in np.linspace(0.0, 100.0, 5)
                for x in np.linspace(0.0, 120.0, 6)
            ],
            dtype=np.float64,
        )
        target = source + np.array([7.0, -4.0], dtype=np.float64)
        outlier_rows = np.arange(0, len(target), 8)
        target[outlier_rows] = rng.uniform(-100.0, 100.0, (len(outlier_rows), 2))
        matrix, mask, quality = choose_best_transform(
            source,
            target,
            reprojection_threshold=0.5,
            iterations=80,
            seed=3,
            quality_kwargs={
                "min_inliers": 10,
                "min_inlier_ratio": 0.5,
                "min_spatial_coverage": 0.05,
            },
        )
        self.assertEqual(quality.model, "translation")
        self.assertTrue(quality.valid, quality.reason)
        self.assertEqual(int(mask.sum()), len(source) - len(outlier_rows))
        np.testing.assert_allclose(matrix[:2, 2], [7.0, -4.0], atol=1.0e-8)
        self.assertLessEqual(quality.median_error, 1.0e-12)

    def test_aot_ofb_and_akaze_facade_self_match_contract(self):
        payload = _run_probe(
            r"""
import json
import numpy as np
from taichi_vision.taichi_algorithm.aot_api import akaze, ofb

rng = np.random.default_rng(123)
rows, cols = np.indices((48, 56), dtype=np.float32)
image = np.clip(
    0.5 + 0.2 * np.sin(rows * 0.31) + 0.2 * np.cos(cols * 0.27)
    + 0.03 * rng.normal(size=(48, 56)),
    0.0,
    1.0,
).astype(np.float32)
reports = {}
for name, function, kwargs in (
    ("ofb", ofb, {"threshold": 1.0e-4}),
    ("akaze", akaze, {"threshold": 1.0e-4, "num_fed_steps": 1}),
):
    points1, points2, scores = function(
        image,
        image,
        grid_size=12,
        margin=6,
        max_keypoints=80,
        **kwargs,
    )
    assert points1 is not None and points2 is not None and scores is not None
    assert points1.shape == points2.shape and points1.shape[1] == 2
    assert scores.shape == (points1.shape[0],)
    assert 0 < points1.shape[0] <= 80
    assert np.isfinite(points1).all() and np.isfinite(points2).all()
    assert np.isfinite(scores).all()
    # The public contract is (x, y), not the row/column order used by raw
    # detector kernels.
    assert np.all((points1[:, 0] >= 0.0) & (points1[:, 0] < 56.0))
    assert np.all((points1[:, 1] >= 0.0) & (points1[:, 1] < 48.0))
    assert np.all((points2[:, 0] >= 0.0) & (points2[:, 0] < 56.0))
    assert np.all((points2[:, 1] >= 0.0) & (points2[:, 1] < 48.0))
    reports[name] = {
        "matches": int(points1.shape[0]),
        "max_self_delta": float(np.max(np.abs(points1 - points2))),
        "score_max": float(np.max(scores)),
    }
print(json.dumps(reports))
""",
            mode="1",
        )
        self.assertGreater(payload["ofb"]["matches"], 0)
        self.assertGreater(payload["akaze"]["matches"], 0)
        self.assertLessEqual(payload["ofb"]["max_self_delta"], 1.0)
        self.assertLessEqual(payload["akaze"]["max_self_delta"], 1.0e-5)


if __name__ == "__main__":
    unittest.main()
