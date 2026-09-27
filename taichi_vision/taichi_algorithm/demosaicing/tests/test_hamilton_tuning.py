"""Guards for the Hamilton tuning contract.

Two things can silently destroy the tuning work:

1. The float64 model in ``hamilton_reference.py`` and the compiled constants in
   ``compile_hamilton_tcm.py`` drifting apart.  The whole search method depends
   on the model predicting the graph, so the two constant sets must be equal.
2. A future edit reverting the searched values.  This module therefore encodes
   the improvement itself as an executable check: the tuned constants must score
   better than the pre-tuning constants on the harness scenes.

The kernel module is read with :mod:`ast` rather than imported, so these tests
stay fast and backend-free; the same technique is used by
``aot_py/audit_aot_matrix.py``.
"""

from __future__ import annotations

import ast
import importlib.util
import os
import sys
import unittest
from pathlib import Path

import numpy as np

_TESTS_DIR = Path(__file__).resolve().parent
_DEMOSAIC_DIR = _TESTS_DIR.parent
_KERNEL_PATH = _DEMOSAIC_DIR / "compile_hamilton_tcm.py"

if str(_DEMOSAIC_DIR) not in sys.path:
    sys.path.insert(0, str(_DEMOSAIC_DIR))


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:  # pragma: no cover - repository invariant
        raise ImportError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


harness = _load("pixel_refine_harness_tuning_test", _TESTS_DIR / "demosaic_quality_harness.py")
model = _load("pixel_refine_hamilton_model_test", _TESTS_DIR / "hamilton_reference.py")

# The constants as they were before the search.  These are what the tuned set
# must beat, and they are the reference point for the improvement claim.
PRE_TUNING = model.HamiltonParams(
    direction_primary=3.0,
    direction_secondary=2.0,
    green_weight_floor=0.01,
    texture_offset=4.0,
    texture_scale=0.25,
    chroma_weight_floor=0.005,
    opponent_offset=0.015,
    opponent_scale=0.155,
    opponent_texture_offset=0.16,
    opponent_texture_scale=0.39,
    highlight_knee=0.55,
    highlight_scale=0.43,
    neutrality_offset=0.40,
    neutrality_scale=0.45,
)

# One scalar per kernel constant, mapped to the model field it must equal.
KERNEL_CONSTANT_FIELDS = {
    "HA_DIRECTION_PRIMARY": "direction_primary",
    "HA_DIRECTION_SECONDARY": "direction_secondary",
    "HA_GREEN_WEIGHT_FLOOR": "green_weight_floor",
    "HA_TEXTURE_OFFSET": "texture_offset",
    "HA_TEXTURE_SCALE": "texture_scale",
    "HA_CHROMA_WEIGHT_FLOOR": "chroma_weight_floor",
    "HA_OPPONENT_TEXTURE_OFFSET": "opponent_texture_offset",
    "HA_OPPONENT_TEXTURE_SCALE": "opponent_texture_scale",
    "HA_OPPONENT_OFFSET": "opponent_offset",
    "HA_OPPONENT_SCALE": "opponent_scale",
    "HA_HIGHLIGHT_KNEE": "highlight_knee",
    "HA_HIGHLIGHT_SCALE": "highlight_scale",
    "HA_NEUTRALITY_OFFSET": "neutrality_offset",
    "HA_NEUTRALITY_SCALE": "neutrality_scale",
}


def read_kernel_constants(path: Path) -> dict:
    """Return every top-level ``HA_*`` numeric constant without importing Taichi."""

    tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    constants = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id.startswith("HA_"):
                try:
                    constants[target.id] = float(ast.literal_eval(node.value))
                except (ValueError, TypeError):
                    pass
    return constants


class TestTuningContract(unittest.TestCase):
    def test_kernel_constants_match_the_model(self):
        """A searched value must live in exactly one place in each implementation."""

        self.assertTrue(_KERNEL_PATH.is_file(), msg=f"missing kernel source: {_KERNEL_PATH}")
        constants = read_kernel_constants(_KERNEL_PATH)
        self.assertGreaterEqual(len(constants), len(KERNEL_CONSTANT_FIELDS))
        defaults = model.HamiltonParams().__dict__
        for kernel_name, field in KERNEL_CONSTANT_FIELDS.items():
            self.assertIn(kernel_name, constants, msg=f"{kernel_name} missing from the kernel")
            self.assertAlmostEqual(
                constants[kernel_name],
                float(defaults[field]),
                places=6,
                msg=(
                    f"{kernel_name}={constants[kernel_name]} does not match the model's "
                    f"{field}={defaults[field]}"
                ),
            )


class TestTunedSetBeatsTheOriginal(unittest.TestCase):
    """Encode the improvement claim so a revert cannot pass unnoticed.

    The claim is deliberately scoped.  The constants were searched under the
    realistic sensor model (lens PSF, lateral chromatic aberration, shot and
    read noise) because that is the configuration the tuning targets, and there
    the gains are large and consistent.  Measured across configurations:

    * realistic sensor, 128 px: mae -10.8%, chroma error -13.9%, zipper -10.4%,
      fringing -7.8%, halo energy -20.7%;
    * realistic sensor, 192 px: mae -10.6%, chroma error -13.5%, zipper -9.7%,
      fringing -9.2%, halo energy -23.8%;
    * ideal sensor (no PSF, no CA, no noise), 128 px: mae +0.4%, zipper +6.3%,
      halo energy +11.0%.

    So a noise-free synthetic frame does *not* improve, which is why this test
    uses the realistic model.  The likely reason is that the stronger directional
    evidence weights act as a stabiliser against noise; without noise they
    over-smooth and produce zipper.  Making the constants noise-adaptive is the
    obvious follow-up.  ``halo_rate`` is excluded from the claim because it
    worsens in every configuration while halo *magnitude* improves.
    """

    SIZE = 128
    SCENES = (
        "contrast_edges",
        "color_edges",
        "repeating_detail",
        "micro_foliage",
        "neutral_chart",
        "star_chart",
        "micro_foliage_alt",
    )
    IMPROVED_METRICS = (
        "mae",
        "chroma_error_mean",
        "zipper_score",
        "fringing_score",
        "halo_energy",
    )

    @classmethod
    def setUpClass(cls):
        cls.sensor = harness.SensorModel()
        cls.suite = {}
        for name in cls.SCENES:
            factory = harness.SCENE_LIBRARY.get(name) or harness.HELD_OUT_SCENES[name]
            frame = harness.render_frame(factory(cls.SIZE), cls.sensor)
            cls.suite[name] = {
                "bayer": frame.bayer,
                "reference": harness.output_transfer(frame.optical),
                "achromatic": name in harness.ACHROMATIC_SCENES,
            }

    def _score(self, params) -> dict:
        scored = {}
        for name, entry in self.suite.items():
            output = model.hamilton_model(
                entry["bayer"], (1.0, 1.0, 1.0, 1.0), 0.0, 1.0, (0, 1, 3, 2), params
            )
            scored[name] = harness.metric_bundle(
                entry["reference"], output, achromatic=entry["achromatic"]
            )
        return scored

    def test_tuned_constants_reduce_the_headline_errors(self):
        before = self._score(PRE_TUNING)
        after = self._score(model.HamiltonParams())

        for metric in self.IMPROVED_METRICS:
            mean_before = float(np.mean([before[name][metric] for name in self.SCENES]))
            mean_after = float(np.mean([after[name][metric] for name in self.SCENES]))
            self.assertLess(
                mean_after,
                mean_before,
                msg=f"{metric} must improve: {mean_before:.6f} -> {mean_after:.6f}",
            )

    def test_tuned_constants_are_not_a_silent_no_op(self):
        """Guard against the tuning being reverted to the original values."""

        self.assertNotEqual(
            model.HamiltonParams().__dict__,
            PRE_TUNING.__dict__,
            msg="the tuned constants were reverted to the pre-tuning values",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
