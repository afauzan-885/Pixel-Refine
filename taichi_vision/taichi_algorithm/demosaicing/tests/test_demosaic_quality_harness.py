"""Correctness tests for the demosaic quality harness.

A metric that is wrong is worse than no metric, so each detector is validated
against a construction with a known answer: a perfect reconstruction must score
zero, blur must not trip the halo detector, and an alternating residual must
trip the zipper detector.

The harness is loaded by file path rather than through the ``taichi_vision``
package.  Importing the package boots the native AOT engine, which these pure
NumPy metrics neither need nor should depend on; the same pattern is already
used by ``aot_py/audit_aot_matrix.py`` for the pure target registry.

The white-balance model in these tests is physical: the sensor measures
``scene / gain`` and the demosaic multiplies the gain back, so a perfect
reconstruction reproduces the scene.  Building the mosaic without that division
compares two different domains and produces a large phantom error.
"""

from __future__ import annotations

import importlib.util
import os
import sys
import unittest
from pathlib import Path

import numpy as np
from scipy import ndimage

_HARNESS_PATH = Path(__file__).resolve().parent / "demosaic_quality_harness.py"
_SPEC = importlib.util.spec_from_file_location(
    "pixel_refine_demosaic_quality_harness_under_test", _HARNESS_PATH
)
if _SPEC is None or _SPEC.loader is None:  # pragma: no cover - repository invariant
    raise ImportError(f"cannot load the quality harness: {_HARNESS_PATH}")
harness = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = harness
_SPEC.loader.exec_module(harness)

CFA_PATTERNS = harness.CFA_PATTERNS
SensorModel = harness.SensorModel
apply_lateral_ca = harness.apply_lateral_ca
cfa_halo_overshoot = harness.cfa_halo_overshoot
cfa_checkerboard_chroma = harness.cfa_checkerboard_chroma
chroma_highpass_energy = harness.chroma_highpass_energy
compare_scene_metrics = harness.compare_scene_metrics
direction_of = harness.direction_of
gain_vector = harness.gain_vector
ground_truth_free_bundle = harness.ground_truth_free_bundle
invert_output_transfer = harness.invert_output_transfer
make_color_edges = harness.make_color_edges
make_contrast_edges = harness.make_contrast_edges
make_neutral_chart = harness.make_neutral_chart
metric_bundle = harness.metric_bundle
output_transfer = harness.output_transfer
render_frame = harness.render_frame
rgb_to_cfa = harness.rgb_to_cfa
run_full_frame = harness.run_full_frame
sample_site_fidelity = harness.sample_site_fidelity
simulate_sensor = harness.simulate_sensor

_COLOUR_TO_CHANNEL = {0: 0, 1: 1, 2: 2, 3: 1}
_BLOCK = ((0, 1), (3, 2))  # RGGB colour codes


def _step_edge(size: int = 96, low: float = 0.15, high: float = 0.75) -> np.ndarray:
    """Achromatic vertical step edge, the canonical halo/zipper stimulus."""

    x = np.indices((size, size), dtype=np.float32)[1]
    level = np.where(x < size / 2, low, high).astype(np.float32)
    return np.repeat(level[:, :, None], 3, axis=2)


def _achromatic(values: np.ndarray) -> np.ndarray:
    """Broadcast a 1-D value ramp into an (n, 1, 3) achromatic image."""

    value = np.asarray(values, dtype=np.float32).reshape(-1, 1, 1)
    return np.repeat(value, 3, axis=2)


class TestHarnessIsBackendFree(unittest.TestCase):
    def test_harness_source_has_no_backend_dependency(self):
        """The metric library must stay usable without a Taichi backend.

        This is asserted against the source rather than ``sys.modules`` because
        the test runner's own environment may import unrelated packages; what
        matters is that this module never grows a Taichi or engine dependency.
        """

        source = _HARNESS_PATH.read_text(encoding="utf-8")
        self.assertNotIn("import taichi", source)
        self.assertNotIn("taichi_vision", source)


class TestTransfers(unittest.TestCase):
    def test_invert_round_trip_below_clipping(self):
        rgb = _achromatic(np.linspace(0.0, 0.6, 64))
        self.assertTrue(np.allclose(invert_output_transfer(output_transfer(rgb)), rgb, atol=1e-4))

    def test_transfer_is_monotonic_along_the_value_axis(self):
        rgb = _achromatic(np.linspace(0.0, 3.0, 128))
        compressed = output_transfer(rgb)[:, 0, 0]
        self.assertTrue(np.all(np.diff(compressed) > 0.0))


class TestMosaicAndSensor(unittest.TestCase):
    def test_mosaic_is_exact_at_sampled_sites(self):
        scene = make_contrast_edges(64)
        bayer = rgb_to_cfa(scene, CFA_PATTERNS["RGGB"])
        self.assertEqual(bayer.shape, scene.shape[:2])
        for row in range(2):
            for col in range(2):
                channel = _COLOUR_TO_CHANNEL[_BLOCK[row][col]]
                self.assertTrue(
                    np.allclose(
                        bayer[row::2, col::2], scene[row::2, col::2, channel], atol=1e-6
                    )
                )

    def test_all_four_layouts_place_colours_correctly(self):
        checks = {
            "RGGB": ((0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 2)),
            "GRBG": ((0, 0, 1), (0, 1, 0), (1, 0, 2), (1, 1, 1)),
            "GBRG": ((0, 0, 1), (0, 1, 2), (1, 0, 0), (1, 1, 1)),
            "BGGR": ((0, 0, 2), (0, 1, 1), (1, 0, 1), (1, 1, 0)),
        }
        scene = make_contrast_edges(48)
        for name, placements in checks.items():
            bayer = rgb_to_cfa(scene, CFA_PATTERNS[name])
            for row, col, channel in placements:
                self.assertTrue(
                    np.allclose(
                        bayer[row::2, col::2], scene[row::2, col::2, channel], atol=1e-6
                    ),
                    msg=f"{name} position ({row},{col})",
                )

    def test_noiseless_sensor_reproduces_the_mosaic(self):
        scene = make_color_edges(64)
        model = SensorModel(psf_sigma=0.0, ca_strength=0.0, full_well=0.0, read_noise_e=-1.0)
        bayer = simulate_sensor(scene, model)
        self.assertTrue(np.allclose(bayer, rgb_to_cfa(scene, CFA_PATTERNS["RGGB"]), atol=1e-6))

    def test_noise_is_seeded_bounded_and_nonzero(self):
        scene = make_color_edges(64)
        model = SensorModel(psf_sigma=0.0, ca_strength=0.0, noise_seed=11)
        first = simulate_sensor(scene, model)
        second = simulate_sensor(scene, model)
        self.assertTrue(np.array_equal(first, second))
        self.assertGreaterEqual(float(first.min()), 0.0)
        self.assertLessEqual(float(first.max()), 1.0)
        clean = rgb_to_cfa(scene, CFA_PATTERNS["RGGB"])
        self.assertGreater(float(np.std(first - clean)), 0.0)

    def test_lateral_ca_moves_red_and_blue_but_not_green(self):
        x = np.indices((96, 96), dtype=np.float32)[1]
        scene = np.repeat((0.5 + 0.4 * np.cos(x * 0.5))[:, :, None], 3, axis=2)
        shifted = apply_lateral_ca(scene, 0.02)
        self.assertGreater(float(np.mean(np.abs(shifted[..., 0] - scene[..., 0]))), 0.0)
        self.assertGreater(float(np.mean(np.abs(shifted[..., 2] - scene[..., 2]))), 0.0)
        self.assertTrue(np.allclose(shifted[..., 1], scene[..., 1], atol=1e-6))


class TestGroundTruthMetrics(unittest.TestCase):
    def test_perfect_reconstruction_scores_zero(self):
        reference = make_contrast_edges(96)
        bundle = metric_bundle(reference, reference, achromatic=True)
        for metric in (
            "mae",
            "p99_abs",
            "false_pixel_rate",
            "edge_mae",
            "halo_energy",
            "halo_rate",
            "zipper_score",
            "fringing_score",
            "chroma_error_mean",
            "chroma_error_p99",
            "edge_chroma_error",
            "false_chroma_mean",
            "edge_false_chroma",
        ):
            self.assertAlmostEqual(bundle[metric], 0.0, places=6, msg=metric)

    def test_false_chroma_is_reported_only_for_achromatic_scenes(self):
        """Chroma of a coloured scene is not an artifact, so it must not be scored as one."""

        reference = make_color_edges(96)
        colored = metric_bundle(reference, reference, achromatic=False)
        achromatic = metric_bundle(reference, reference, achromatic=True)

        for metric in ("chroma_error_mean", "chroma_error_p99", "edge_chroma_error"):
            self.assertIn(metric, colored)
            self.assertAlmostEqual(colored[metric], 0.0, places=6)
        for metric in ("false_chroma_mean", "false_chroma_p99", "edge_false_chroma"):
            self.assertNotIn(metric, colored)
            self.assertIn(metric, achromatic)
        # The scene genuinely carries colour, which is exactly why it cannot be
        # reported as false colour.
        self.assertGreater(achromatic["false_chroma_mean"], 0.05)

    def test_halo_magnitude_separates_ringing_from_blur(self):
        """The halo detector must be scale invariant, not tuned to one contrast.

        Measured on this stimulus, blur stays at 4.9--8.8 percent of the step
        amplitude while ringing reaches 78--82 percent, so the separation is
        9.4--16.1x in p99 across amplitudes 0.20, 0.60 and 0.93.  The assertions
        are therefore expressed as a fraction of the step amplitude and checked
        at two contrasts, which is what makes them a real invariant.
        """

        for low, high in ((0.10, 0.30), (0.15, 0.75)):
            amplitude = high - low
            reference = _step_edge(low=low, high=high)
            blurred = ndimage.gaussian_filter(reference, 1.2, mode="nearest")
            ringing = reference + 2.5 * (reference - blurred)

            blur_halo = metric_bundle(reference, blurred, achromatic=True)
            ring_halo = metric_bundle(reference, ringing, achromatic=True)

            self.assertLess(
                blur_halo["halo_p99"],
                0.15 * amplitude,
                msg=f"blur must stay near the step amplitude: {blur_halo}",
            )
            self.assertGreater(
                ring_halo["halo_p99"],
                0.40 * amplitude,
                msg=f"ringing must exceed the step amplitude: {ring_halo}",
            )
            self.assertGreater(ring_halo["halo_p99"], 5.0 * max(blur_halo["halo_p99"], 1e-9))
            self.assertGreater(
                ring_halo["halo_energy"], 4.0 * max(blur_halo["halo_energy"], 1e-9)
            )
            # Blur is a genuine error, so it must still be visible to MAE.
            self.assertGreater(blur_halo["mae"], 0.0)

    def test_zipper_detector_sees_alternation_not_bias(self):
        reference = _step_edge()
        biased = reference + 0.02

        columns = np.arange(reference.shape[1])[None, :]
        sign = np.where((columns % 2) == 0, 1.0, -1.0).astype(np.float32)
        alternating = np.broadcast_to((0.02 * sign)[:, :, None], reference.shape)
        zippered = reference + alternating

        bias = metric_bundle(reference, biased, achromatic=True)
        zipper = metric_bundle(reference, zippered, achromatic=True)

        self.assertLess(bias["zipper_score"], 1e-4)
        self.assertGreater(zipper["zipper_score"], 0.03)
        self.assertGreater(zipper["zipper_score"], 10.0 * max(bias["zipper_score"], 1e-6))

    def test_fringing_detector_sees_chroma_not_luma(self):
        reference = _step_edge()
        middle = reference.shape[1] // 2
        luma_only = np.clip(reference + 0.03, 0.0, 1.0)

        fringed = luma_only.copy()
        fringed[:, middle:, 0] = np.clip(fringed[:, middle:, 0] + 0.04, 0.0, 1.0)
        fringed[:, middle:, 2] = np.clip(fringed[:, middle:, 2] - 0.04, 0.0, 1.0)

        clean = metric_bundle(reference, luma_only, achromatic=True)
        colored = metric_bundle(reference, fringed, achromatic=True)

        self.assertLess(clean["fringing_score"], 1e-6)
        self.assertGreater(colored["fringing_score"], 0.005)
        self.assertGreater(colored["false_chroma_mean"], clean["false_chroma_mean"])

    def test_shape_mismatch_is_rejected(self):
        with self.assertRaises(ValueError):
            metric_bundle(
                make_contrast_edges(64),
                np.zeros((32, 32, 3), dtype=np.float32),
                achromatic=True,
            )


class TestGroundTruthFreeMetrics(unittest.TestCase):
    """Fidelity and CFA halo must be exact on a physically consistent fixture.

    The fixture is a step edge, not a ramp: a ramp's same-colour samples already
    span a wide range, which would hide a small ringing overshoot and make the
    detector look broken when it is only being asked the wrong question.  Levels
    stay below the highlight-recovery knee so ``invert_output_transfer`` is exact.
    """

    SIZE = 96
    GAINS = (1.6, 1.0, 1.4, 1.02)

    def _fixture(self):
        """Return scene, physical Bayer frame, CFA, and a perfect reconstruction."""

        x = np.indices((self.SIZE, self.SIZE), dtype=np.float32)[1]
        level = np.where(x < self.SIZE / 2, 0.10, 0.30).astype(np.float32)
        scene = np.repeat(level[:, :, None], 3, axis=2)

        cfa = CFA_PATTERNS["RGGB"]
        table = gain_vector(cfa, self.GAINS)
        sensor = np.empty_like(scene)
        for row in range(2):
            for col in range(2):
                colour = _BLOCK[row][col]
                channel = _COLOUR_TO_CHANNEL[colour]
                sensor[row::2, col::2, channel] = (
                    scene[row::2, col::2, channel] / table[colour]
                )

        bayer = rgb_to_cfa(sensor, cfa)
        return scene, bayer, cfa, output_transfer(scene)

    def test_measured_site_fidelity_is_zero_for_an_exact_reconstruction(self):
        _, bayer, cfa, perfect = self._fixture()
        report = sample_site_fidelity(bayer, perfect, cfa, self.GAINS)
        self.assertLess(
            report["sample_site_fidelity_max"],
            1e-4,
            msg=f"an exact reconstruction must reproduce every measured sample: {report}",
        )

    def test_measured_site_fidelity_catches_a_perturbed_site(self):
        _, bayer, cfa, perfect = self._fixture()
        perturbed = perfect.copy()
        perturbed[10::16, 10::16, :] = np.clip(perturbed[10::16, 10::16, :] + 0.05, 0.0, 1.0)
        clean = sample_site_fidelity(bayer, perfect, cfa, self.GAINS)
        broken = sample_site_fidelity(bayer, perturbed, cfa, self.GAINS)
        self.assertGreater(broken["sample_site_fidelity_max"], 0.01)
        self.assertGreater(broken["sample_site_fidelity_max"], clean["sample_site_fidelity_max"])

    def test_highlight_gate_is_evaluated_before_white_balance(self):
        """A sample below the highlight knee stays usable even if its gain lifts it above.

        The graph's highlight recovery acts on the pre-gain sample, so a gate on
        the post-gain value would silently drop every bright red site on a frame
        whose red gain exceeds one.  The perturbation below lands exactly in that
        regime: measured 0.30, post-gain 0.60.
        """

        size = 64
        gains = (2.0, 1.0, 1.0, 1.0)
        cfa = CFA_PATTERNS["RGGB"]
        table = gain_vector(cfa, gains)

        scene = np.empty((size, size, 3), dtype=np.float32)
        scene[..., 0] = 0.60
        scene[..., 1] = 0.30
        scene[..., 2] = 0.30

        sensor = np.empty_like(scene)
        for row in range(2):
            for col in range(2):
                colour = _BLOCK[row][col]
                channel = _COLOUR_TO_CHANNEL[colour]
                sensor[row::2, col::2, channel] = (
                    scene[row::2, col::2, channel] / table[colour]
                )
        bayer = rgb_to_cfa(sensor, cfa)

        red_measured = bayer[0::2, 0::2]
        self.assertLess(float(red_measured.max()), 0.5, msg="R sites must sit below the knee")
        self.assertGreater(
            float(red_measured.max() * gains[0]), 0.5, msg="...yet above it after white balance"
        )

        candidate = output_transfer(scene)
        clean = sample_site_fidelity(bayer, candidate, cfa, gains)

        perturbed = candidate.copy()
        perturbed[0::2, 0::2, :] = np.clip(perturbed[0::2, 0::2, :] + 0.05, 0.0, 1.0)
        broken = sample_site_fidelity(bayer, perturbed, cfa, gains)

        self.assertGreater(
            broken["sample_site_fidelity_max"],
            clean["sample_site_fidelity_max"] + 0.01,
            msg=f"R sites must remain usable and measurable: clean={clean} broken={broken}",
        )

    def test_cfa_halo_detector_is_quiet_on_a_perfect_reconstruction(self):
        _, bayer, cfa, perfect = self._fixture()
        report = cfa_halo_overshoot(bayer, perfect, cfa, self.GAINS)
        self.assertLess(
            report["cfa_halo_energy"],
            1e-4,
            msg=f"a reconstruction that equals the samples cannot overshoot them: {report}",
        )

    def test_cfa_halo_detector_sees_overshoot_without_ground_truth(self):
        _, bayer, cfa, perfect = self._fixture()
        ringing = np.clip(
            perfect + 2.5 * (perfect - ndimage.gaussian_filter(perfect, 1.5, mode="nearest")), 0.0, 1.0
        )
        clean = cfa_halo_overshoot(bayer, perfect, cfa, self.GAINS)
        ring = cfa_halo_overshoot(bayer, ringing, cfa, self.GAINS)
        self.assertGreater(ring["cfa_halo_energy"], 1e-3)
        self.assertGreater(ring["cfa_halo_energy"], clean["cfa_halo_energy"])
        self.assertGreater(ring["cfa_halo_rate"], clean["cfa_halo_rate"])

    def test_neutral_chart_reference_is_achromatic(self):
        scene = make_neutral_chart(96)
        chroma = np.max(scene, axis=2) - np.min(scene, axis=2)
        self.assertLess(float(np.max(chroma)), 1e-6)


class TestRenderFrame(unittest.TestCase):
    """The scoring reference must be the optical image, not the sharp scene."""

    def test_ideal_sensor_makes_the_optical_image_equal_the_scene(self):
        scene = make_contrast_edges(64)
        ideal = SensorModel(psf_sigma=0.0, ca_strength=0.0, full_well=0.0, read_noise_e=-1.0)
        frame = render_frame(scene, ideal)
        self.assertTrue(np.allclose(frame.optical, scene, atol=1e-6))
        self.assertTrue(
            np.allclose(frame.bayer, simulate_sensor(scene, ideal), atol=1e-9),
            msg="render_frame and simulate_sensor must agree on the mosaic",
        )

    def test_lens_blur_separates_the_optical_image_from_the_scene(self):
        scene = make_contrast_edges(64)
        softened = SensorModel(psf_sigma=1.0, ca_strength=0.0, full_well=0.0, read_noise_e=-1.0)
        frame = render_frame(scene, softened)
        self.assertGreater(float(np.mean(np.abs(frame.optical - scene))), 0.01)
        # The mosaic must be sampled from the optical image, not from the scene.
        self.assertTrue(
            np.allclose(
                frame.bayer, rgb_to_cfa(frame.optical, CFA_PATTERNS["RGGB"]), atol=1e-6
            )
        )
        self.assertFalse(
            np.allclose(frame.bayer, rgb_to_cfa(scene, CFA_PATTERNS["RGGB"]), atol=1e-3)
        )


class TestComparativeMetrics(unittest.TestCase):
    """Real-capture metrics are comparative; they must still separate signal."""

    @staticmethod
    def _constant_chroma(size: int = 64) -> np.ndarray:
        x = np.indices((size, size), dtype=np.float32)[1]
        level = 0.2 + 0.3 * (x / size)
        cube = np.empty((size, size, 3), dtype=np.float32)
        cube[..., 0] = 0.5 + level
        cube[..., 1] = 0.3 + level
        cube[..., 2] = 0.2 + level
        return cube

    @staticmethod
    def _checker_chroma(cube: np.ndarray, amplitude: float = 0.1) -> np.ndarray:
        y, x = np.indices(cube.shape[:2])
        sign = np.where((y + x) % 2 == 0, 1.0, -1.0).astype(np.float32)
        out = cube.copy()
        out[..., 2] = cube[..., 2] - amplitude * sign
        return out

    def test_chroma_highpass_is_quiet_for_constant_chroma(self):
        report = chroma_highpass_energy(self._constant_chroma())
        self.assertLess(report["chroma_hp_energy"], 1e-9)
        self.assertLess(report["chroma_hp_p99"], 1e-6)

    def test_chroma_highpass_sees_checkerboard_chroma(self):
        quiet = chroma_highpass_energy(self._constant_chroma())
        loud = chroma_highpass_energy(self._checker_chroma(self._constant_chroma()))
        self.assertGreater(loud["chroma_hp_energy"], 1e-3)
        self.assertGreater(loud["chroma_hp_energy"], quiet["chroma_hp_energy"] * 100.0)

    def test_cfa_checkerboard_metric_is_quiet_for_constant_chroma(self):
        report = cfa_checkerboard_chroma(self._constant_chroma())
        self.assertLess(report["cfa_checkerboard_chroma"], 1e-6)

    def test_cfa_checkerboard_metric_sees_cfa_locked_chroma(self):
        report = cfa_checkerboard_chroma(self._checker_chroma(self._constant_chroma()))
        self.assertAlmostEqual(report["cfa_checkerboard_chroma"], 0.1, places=2)

    def test_ground_truth_free_bundle_reports_every_group(self):
        scene = make_contrast_edges(64)
        ideal = SensorModel(psf_sigma=0.0, ca_strength=0.0, full_well=0.0, read_noise_e=-1.0)
        frame = render_frame(scene, ideal)
        report = ground_truth_free_bundle(
            frame.bayer, output_transfer(scene), CFA_PATTERNS["RGGB"], (1.0, 1.0, 1.0, 1.0)
        )
        for key in (
            "sample_site_fidelity_max",
            "cfa_halo_energy",
            "chroma_hp_energy",
            "cfa_checkerboard_chroma",
        ):
            self.assertIn(key, report)
            self.assertTrue(np.isfinite(report[key]), msg=key)


class _FakeBuffer:
    def __init__(self, array):
        self.array = array
        self.released = 0

    def release(self):
        self.released += 1

    def to_numpy(self):
        return self.array


class _FakeApi:
    """Stand-in for the ``taichi_aot`` facade so timing is testable backend-free."""

    def __init__(self, output):
        self.output = output
        self.calls = 0
        self.uploads = []

    def upload(self, array):
        buffer = _FakeBuffer(array)
        self.uploads.append(buffer)
        return buffer

    def hamilton(self, bayer, *args, return_gpu=False):
        self.calls += 1
        return _FakeBuffer(self.output)


class TestRunFullFrame(unittest.TestCase):
    def test_uploads_once_and_releases_every_buffer(self):
        expected = np.arange(48, dtype=np.float32).reshape(4, 4, 3)
        api = _FakeApi(expected)
        scalars = (1.0, 1.0, 1.0, 1.0, np.eye(3, dtype=np.float32), 0.0, 1.0, 0, 1, 1, 2)

        output, timing = run_full_frame(
            api, "hamilton", np.zeros((4, 4), dtype=np.float32), scalars, runs=2
        )

        self.assertTrue(np.array_equal(output, expected))
        self.assertEqual(api.calls, 3, "one warm-up plus the requested runs")
        self.assertEqual(len(api.uploads), 1, "a resident input is uploaded once")
        self.assertEqual(api.uploads[0].released, 1, "the resident input is released")
        self.assertEqual(timing["runs"], 2)
        self.assertEqual(timing["input_mode"], "resident")
        self.assertIn("dispatch_median_ms", timing)
        self.assertEqual(len(timing["end_to_end_runs_ms"]), 2)

    def test_host_input_is_neither_uploaded_nor_released(self):
        api = _FakeApi(np.zeros((4, 4, 3), dtype=np.float32))
        _, timing = run_full_frame(
            api,
            "hamilton",
            np.zeros((4, 4), dtype=np.float32),
            (1.0,) * 4,
            runs=1,
            resident=False,
        )
        self.assertEqual(api.uploads, [])
        self.assertEqual(timing["input_mode"], "host")


class TestGateComparison(unittest.TestCase):
    def test_psnr_direction_is_higher_is_better(self):
        self.assertEqual(direction_of("psnr_db"), "higher")
        self.assertEqual(direction_of("mae"), "lower")

    def test_regression_detection_respects_direction(self):
        baseline = {"mae": 0.01, "psnr_db": 30.0}
        better = {"mae": 0.009, "psnr_db": 31.0}
        worse = {"mae": 0.011, "psnr_db": 29.0}
        self.assertEqual(compare_scene_metrics(baseline, better), [])
        regressions = {item["metric"] for item in compare_scene_metrics(baseline, worse)}
        self.assertEqual(regressions, {"mae", "psnr_db"})

    def test_improved_psnr_is_not_flagged_as_regression(self):
        self.assertEqual(compare_scene_metrics({"psnr_db": 20.0}, {"psnr_db": 26.0}), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
