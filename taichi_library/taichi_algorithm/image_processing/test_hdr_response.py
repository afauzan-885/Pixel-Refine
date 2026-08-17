"""Known-value checks for HDR response calibration and weighted merge."""

from __future__ import annotations

import unittest

import numpy as np

from .hdr_response import (
    _debevec_system_taichi,
    estimate_response_curve,
    estimate_response_curve_robertson,
    merge_radiance,
    merge_radiance_weighted,
    response_weight,
)


class HDRResponseTests(unittest.TestCase):
    def setUp(self) -> None:
        yy, xx = np.indices((20, 24), dtype=np.float32)
        radiance = 0.05 + 0.45 * (0.35 * xx / 23.0 + 0.65 * yy / 19.0)
        self.radiance = radiance.astype(np.float32)
        self.times = np.array([0.5, 1.0, 2.0], dtype=np.float64)
        self.images = [np.clip(self.radiance * time, 0.0, 1.0).astype(np.float32) for time in self.times]

    def test_response_calibration_and_merge(self) -> None:
        calibration = estimate_response_curve(
            self.images,
            self.times,
            levels=64,
            sample_count=128,
            smooth_lambda=5.0,
            reference_value=0.4,
            backend="numpy",
        )
        self.assertEqual(calibration.curve.shape, (64, 1))
        self.assertTrue(np.isfinite(calibration.curve).all())
        merged = merge_radiance(self.images, self.times, calibration=calibration, backend="numpy")
        self.assertEqual(merged.shape, self.radiance.shape)
        self.assertTrue(np.isfinite(merged).all())
        self.assertLess(float(np.mean(np.abs(merged - self.radiance))), 0.03)

    def test_linear_weighted_merge_and_backend_contract(self) -> None:
        merged = merge_radiance_weighted(self.images, self.times, backend="numpy")
        self.assertLess(float(np.mean(np.abs(merged - self.radiance))), 0.02)
        self.assertEqual(response_weight(np.array([0.0, 0.5, 1.0]), levels=64).shape, (3,))
        try:
            aot_merge = merge_radiance(self.images, self.times, backend="aot")
        except NotImplementedError as exc:
            self.skipTest(str(exc))
        np.testing.assert_allclose(aot_merge, merged, atol=2e-6, rtol=2e-6)
        with self.assertRaises(ValueError):
            estimate_response_curve(self.images, [1.0], backend="numpy")

    def test_taichi_weight_and_linear_merge_parity(self) -> None:
        values = np.linspace(0.0, 1.0, 97, dtype=np.float32)
        numpy_weights = response_weight(values, levels=64, backend="numpy")
        taichi_weights = response_weight(values, levels=64, backend="taichi")
        np.testing.assert_array_equal(taichi_weights, numpy_weights)

        numpy_merge = merge_radiance(self.images, self.times, backend="numpy")
        taichi_merge = merge_radiance(self.images, self.times, backend="taichi")
        np.testing.assert_allclose(taichi_merge, numpy_merge, atol=2e-6, rtol=2e-6)

    def test_taichi_calibrated_merge_parity_and_hybrid_solver_boundary(self) -> None:
        numpy_calibration = estimate_response_curve(
            self.images,
            self.times,
            levels=64,
            sample_count=128,
            smooth_lambda=5.0,
            reference_value=0.4,
            backend="numpy",
        )
        taichi_calibration = estimate_response_curve(
            self.images,
            self.times,
            levels=64,
            sample_count=128,
            smooth_lambda=5.0,
            reference_value=0.4,
            backend="taichi",
        )
        self.assertEqual(taichi_calibration.backend, "taichi")
        self.assertEqual(taichi_calibration.solver_backend, "taichi-quantize+numpy-lstsq")
        np.testing.assert_array_equal(taichi_calibration.curve, numpy_calibration.curve)
        numpy_merge = merge_radiance(
            self.images,
            self.times,
            calibration=numpy_calibration,
            method="log",
            backend="numpy",
        )
        taichi_merge = merge_radiance(
            self.images,
            self.times,
            calibration=taichi_calibration,
            method="log",
            backend="taichi",
        )
        np.testing.assert_allclose(taichi_merge, numpy_merge, atol=2e-6, rtol=2e-6)

    def test_taichi_response_quantisation_matches_numpy_for_random_samples(self) -> None:
        rng = np.random.default_rng(1234)
        values = rng.uniform(-0.1, 1.1, size=(3, 257)).astype(np.float32)
        # Include exact half-bin values because nearest-even behaviour is part
        # of the response LUT contract.
        values[0, :8] = np.array(
            [0.5, 1.5, 2.5, 3.5, 10.5, 31.5, 63.5, 127.5],
            dtype=np.float32,
        ) / 255.0
        expected = np.rint(np.clip(values, 0.0, 1.0) * 255.0).astype(np.int32)
        taichi_calibration = estimate_response_curve(
            self.images,
            self.times,
            levels=64,
            sample_count=64,
            backend="taichi",
        )
        # The public response-weight API exercises the same quantiser and is a
        # useful bounded parity oracle for values not consumed by calibration.
        from .hdr_response import _response_quantise_taichi

        np.testing.assert_array_equal(_response_quantise_taichi(values, 256), expected)
        self.assertTrue(np.isfinite(taichi_calibration.curve).all())

    def test_taichi_debevec_system_assembly_parity_and_memory_guard(self) -> None:
        quantised = np.array(
            [[1, 8, 31, 63], [2, 12, 28, 60], [4, 16, 24, 56]],
            dtype=np.int32,
        )
        log_times = np.log(np.array([0.5, 1.0, 2.0], dtype=np.float64))
        levels = 64
        smooth_lambda = 5.0
        reference_value = 0.4
        matrix, rhs = _debevec_system_taichi(
            quantised,
            log_times,
            levels=levels,
            smooth_lambda=smooth_lambda,
            reference_value=reference_value,
        )
        rows = quantised.shape[0] * quantised.shape[1] + levels - 2 + 1
        cols = levels + quantised.shape[1]
        expected_matrix = np.zeros((rows, cols), dtype=np.float64)
        expected_rhs = np.zeros(rows, dtype=np.float64)
        row = 0
        for sample in range(quantised.shape[1]):
            for frame in range(quantised.shape[0]):
                code = int(quantised[frame, sample])
                weight = float(min(code, levels - 1 - code))
                if weight > 0.0:
                    expected_matrix[row, code] = weight
                    expected_matrix[row, levels + sample] = weight
                    expected_rhs[row] = weight * log_times[frame]
                row += 1
        for code in range(1, levels - 1):
            weight = smooth_lambda * float(min(code, levels - 1 - code))
            expected_matrix[row, code - 1] = weight
            expected_matrix[row, code] = -2.0 * weight
            expected_matrix[row, code + 1] = weight
            row += 1
        expected_matrix[row, int(round((levels - 1) * reference_value))] = 1.0
        expected_rhs[row] = np.log(reference_value)
        np.testing.assert_array_equal(matrix, expected_matrix)
        np.testing.assert_array_equal(rhs, expected_rhs)
        with self.assertRaises(MemoryError):
            estimate_response_curve(
                [np.zeros((1, 1), dtype=np.float32)] * 2,
                [0.5, 1.0],
                levels=4096,
                sample_count=4096,
                max_working_bytes=16 * 1024 * 1024,
                backend="taichi",
            )

    def test_taichi_rgb_merge_shape_and_parity(self) -> None:
        rgb_radiance = np.stack(
            [self.radiance, np.clip(self.radiance * 0.8, 0.0, 1.0), np.clip(self.radiance * 1.1, 0.0, 1.0)],
            axis=-1,
        ).astype(np.float32)
        rgb_images = [np.clip(rgb_radiance * time, 0.0, 1.0).astype(np.float32) for time in self.times]
        numpy_merge = merge_radiance(rgb_images, self.times, backend="numpy")
        taichi_merge = merge_radiance(rgb_images, self.times, backend="taichi")
        self.assertEqual(taichi_merge.shape, rgb_radiance.shape)
        np.testing.assert_allclose(taichi_merge, numpy_merge, atol=2e-6, rtol=2e-6)

    def test_robertson_curve_and_merge_are_bounded_and_monotone(self) -> None:
        calibration = estimate_response_curve_robertson(
            self.images,
            self.times,
            levels=64,
            sample_count=128,
            smooth_lambda=5.0,
            reference_value=0.4,
            iterations=12,
            backend="numpy",
        )
        self.assertEqual(calibration.method, "robertson")
        self.assertEqual(calibration.solver_backend, "numpy-robertson")
        self.assertEqual(calibration.curve.shape, (64, 1))
        self.assertTrue(np.isfinite(calibration.curve).all())
        self.assertTrue(np.all(np.diff(calibration.curve[:, 0]) >= -1e-6))
        merged = merge_radiance(
            self.images,
            self.times,
            calibration=calibration,
            method="log",
            backend="numpy",
        )
        self.assertLess(float(np.mean(np.abs(merged - self.radiance))), 0.05)

    def test_robertson_taichi_quantisation_parity_and_explicit_backend(self) -> None:
        numpy_calibration = estimate_response_curve_robertson(
            self.images,
            self.times,
            levels=64,
            sample_count=128,
            smooth_lambda=5.0,
            reference_value=0.4,
            iterations=12,
            backend="numpy",
        )
        taichi_calibration = estimate_response_curve(
            self.images,
            self.times,
            levels=64,
            sample_count=128,
            smooth_lambda=5.0,
            reference_value=0.4,
            iterations=12,
            method="robertson",
            backend="taichi",
        )
        self.assertEqual(taichi_calibration.method, "robertson")
        self.assertEqual(taichi_calibration.solver_backend, "taichi-quantize+numpy-robertson")
        np.testing.assert_array_equal(taichi_calibration.curve, numpy_calibration.curve)
        taichi_merge = merge_radiance(
            self.images,
            self.times,
            calibration=taichi_calibration,
            method="log",
            backend="taichi",
        )
        numpy_merge = merge_radiance(
            self.images,
            self.times,
            calibration=numpy_calibration,
            method="log",
            backend="numpy",
        )
        np.testing.assert_allclose(taichi_merge, numpy_merge, atol=2e-6, rtol=2e-6)

    def test_robertson_method_and_pressure_guards(self) -> None:
        with self.assertRaises(ValueError):
            estimate_response_curve(self.images, self.times, method="unknown")
        try:
            aot_calibration = estimate_response_curve_robertson(
                self.images,
                self.times,
                levels=64,
                sample_count=64,
                backend="aot",
            )
        except NotImplementedError as exc:
            self.skipTest(str(exc))
        self.assertEqual(aot_calibration.solver_backend, "aot-quantize+numpy-robertson")
        self.assertTrue(np.isfinite(aot_calibration.curve).all())
        with self.assertRaises(ValueError):
            estimate_response_curve_robertson(self.images, self.times, iterations=0)
        with self.assertRaises(MemoryError):
            estimate_response_curve_robertson(
                [np.zeros((32, 32), dtype=np.float32)] * 3,
                [0.5, 1.0, 2.0],
                levels=4096,
                sample_count=4096,
                max_working_bytes=1024,
            )


if __name__ == "__main__":
    unittest.main()
