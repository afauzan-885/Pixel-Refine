"""Semantic parity gates for the built-in low-risk block adapters."""

from __future__ import annotations

import unittest

import numpy as np

from taichi_vision.taichi_aot.block import (
    BlockCache,
    BlockGrid,
    block_coverage_report,
    can_auto_block,
    can_partition_block,
    can_auto_partition_dispatch,
    operation_contract,
    registered_block_adapters,
)
from taichi_vision.taichi_aot.generic_block import BlockComputeSpec, GenericBlockExecutor
from taichi_vision.taichi_aot.block_adapters import (
    LOW_RISK_ADAPTER_OPERATIONS,
    ACCUMULATOR_ADAPTER_OPERATIONS,
    COORDINATE_ADAPTER_OPERATIONS,
    NCC_ADAPTER_OPERATIONS,
    STITCH_ADAPTER_OPERATIONS,
    OUTPUT_DOMAIN_ADAPTER_OPERATIONS,
    register_low_risk_block_adapters,
    register_map_reduce_block_adapters,
    register_accumulator_block_adapters,
    register_coordinate_block_adapters,
    register_output_domain_adapters,
    run_adapter_map_reduce,
    verify_adapter_parity,
    verify_map_reduce_parity,
    verify_output_domain_parity,
)


class LowRiskAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adapters = register_low_risk_block_adapters()
        cls.map_adapters = register_map_reduce_block_adapters()
        cls.accumulator_adapters = register_accumulator_block_adapters()
        cls.coordinate_adapters = register_coordinate_block_adapters()
        cls.output_adapters = register_output_domain_adapters()

    def test_registration_is_complete_and_gpu_fail_closed(self):
        self.assertEqual(
            set(LOW_RISK_ADAPTER_OPERATIONS),
            {
                "copy",
                "absdiff",
                "rgb2gray",
                "split_3ch",
                "merge_3ch",
                "extract_channel",
                "insert_channel",
                "cvtColor",
                "enhance_grayscale",
            },
        )
        self.assertTrue(set(LOW_RISK_ADAPTER_OPERATIONS).issubset(self.adapters))
        for name in LOW_RISK_ADAPTER_OPERATIONS:
            adapter = registered_block_adapters()[name]
            self.assertTrue(adapter.partition_ready)
            self.assertTrue(can_auto_partition_dispatch(name, "cpu"))
            self.assertFalse(can_auto_partition_dispatch(name, "vulkan"))
            self.assertFalse(can_auto_partition_dispatch(name, "opengl"))
            # The richer adapter contract must not mutate the existing strict
            # operation table or its legacy automatic flag.
            self.assertTrue(can_auto_block(name, "cpu"))

    def test_full_frame_and_tiled_semantic_parity(self):
        rng = np.random.default_rng(20260810)
        rgb = rng.random((65, 71, 3), dtype=np.float32)
        cases = (
            ("copy", (rgb,), {}),
            ("absdiff", (rgb, rgb * np.float32(0.7)), {}),
            ("rgb2gray", (rgb,), {}),
            ("split_3ch", (rgb,), {}),
            ("merge_3ch", tuple(rgb[..., index] for index in range(3)), {}),
            ("extract_channel", (rgb,), {"channel": 1}),
            ("insert_channel", (rgb[..., 1], rgb), {"channel": 1}),
            ("cvtColor", (rgb,), {"code": 7}),
        )
        for name, inputs, params in cases:
            with self.subTest(operation=name):
                report = verify_adapter_parity(
                    name, inputs, block_size=(17, 19), params=params
                )
                self.assertTrue(report["passed"], report)
                self.assertEqual(report["max_abs_error"], 0.0)
                self.assertEqual(report["backend"], "cpu")
                self.assertFalse(report["native_runtime"])

    def test_tuple_output_arity_and_shapes_are_explicit(self):
        """Tuple-valued local adapters retain exact output contracts."""

        rng = np.random.default_rng(20260813)
        rgb = rng.random((37, 43, 3), dtype=np.float32)
        split = verify_adapter_parity(
            "split_3ch", (rgb,), block_size=(11, 13)
        )
        self.assertTrue(split["passed"], split)
        self.assertEqual(split["output_arity"], 3)
        self.assertEqual(split["expected_output_arity"], 3)
        self.assertEqual(split["output_shapes"], [[37, 43]] * 3)
        self.assertEqual(split["expected_output_shapes"], [[37, 43]] * 3)

        merge = verify_adapter_parity(
            "merge_3ch", tuple(rgb[..., index] for index in range(3)),
            block_size=(11, 13),
        )
        self.assertTrue(merge["passed"], merge)
        self.assertEqual(merge["output_arity"], 1)
        self.assertEqual(merge["expected_output_arity"], 1)
        self.assertEqual(merge["output_shapes"], [[37, 43, 3]])
        self.assertEqual(merge["expected_output_shapes"], [[37, 43, 3]])

    def test_enhance_grayscale_semantic_parity(self):
        rng = np.random.default_rng(9)
        source = rng.random((33, 37), dtype=np.float32)
        blurred = rng.random((33, 37), dtype=np.float32)
        lut = np.linspace(0.0, 1.0, 256, dtype=np.float32)
        report = verify_adapter_parity(
            "enhance_grayscale",
            (source, blurred),
            block_size=11,
            params={
                "lut": lut,
                "micro_contrast": 2.1,
                "clarity": 0.3,
                "noise_coring": 0.05,
            },
        )
        self.assertTrue(report["passed"], report)
        self.assertEqual(report["max_abs_error"], 0.0)

    def test_adapter_callbacks_fit_generic_executor_protocol(self):
        """The registry callbacks can be passed through the generic planner."""

        class Runtime:
            arch = "cpu"
            target_id = "test"
            gpu_name = "cpu"
            _generation = 1

            def __init__(self):
                self.cache = BlockCache(max_entries=32)
                self.quarantine = {}

            def get_block_cache(self):
                return self.cache

            def restore_resident_block(self, *_args):
                return None

            def put_block_record(self, record):
                return self.cache.put(record)

            def get_device_block_cache(self):
                return self.cache

            def quarantine_block_operation(self, operation, reason):
                self.quarantine[str(operation)] = str(reason)

            def plan_generic_blocks(self, operation, shape, nbytes, **kwargs):
                del operation, nbytes
                return BlockGrid(
                    shape,
                    size=kwargs.get("block_size") or 2,
                    halo=kwargs.get("halo", 0),
                )

            def set_last_block_execution(self, _report):
                return None

        adapter = self.adapters["copy"]
        source = np.arange(35, dtype=np.float32).reshape(5, 7)
        spec = BlockComputeSpec(
            "copy",
            adapter.runner,
            output_shape=source.shape,
            output_dtype=source.dtype,
            input_reader=adapter.reader,
            validate_tile=adapter.validator,
            merge_tile=adapter.merger,
            contract=adapter.contract,
            metadata={
                "backend_capability": {"cpu": {"supported": True, "parity": True}},
                "params": {},
            },
            block_size=2,
            mode="auto",
            automatic=True,
            threshold_bytes=1,
            fallback="error",
        )
        result = GenericBlockExecutor(Runtime()).run((source,), spec)
        np.testing.assert_array_equal(result, source)

    def test_map_reduce_histogram_and_otsu_semantic_parity(self):
        rng = np.random.default_rng(20260810)
        image = rng.integers(0, 256, size=(67, 73), dtype=np.uint8)
        histogram = verify_map_reduce_parity(
            "histogram",
            (image,),
            block_size=(19, 23),
            params={"bins": 256, "range_min": 0.0, "range_max": 256.0},
        )
        self.assertTrue(histogram["passed"], histogram)
        self.assertEqual(histogram["max_abs_error"], 0.0)
        self.assertFalse(histogram["native_runtime"])

        otsu = verify_map_reduce_parity(
            "otsu_threshold",
            (image.astype(np.float32),),
            block_size=17,
            params={"bins": 256, "max_val": 255.0, "thresh_type": 0},
        )
        self.assertTrue(otsu["passed"], otsu)
        self.assertEqual(otsu["max_abs_error"], 0.0)
        self.assertFalse(otsu["native_runtime"])

        for name in ("histogram", "otsu_threshold"):
            adapter = self.map_adapters[name]
            self.assertEqual(adapter.metadata["partition_kind"], "map_reduce")
            self.assertTrue(adapter.partition_ready)

    def test_ssim_halo_map_reduce_non_multiple_and_fail_closed(self):
        """SSIM uses a dynamic halo and never promotes native dispatch."""

        rng = np.random.default_rng(20260810)
        first = rng.random((29, 37), dtype=np.float32)
        second = np.clip(
            first + rng.normal(0.0, 0.02, size=first.shape).astype(np.float32),
            0.0,
            1.0,
        )
        adapter = self.map_adapters["ssim_aot"]
        self.assertEqual(adapter.metadata["partition_kind"], "map_reduce")
        self.assertTrue(adapter.metadata["deterministic_merge"])
        self.assertEqual(adapter.metadata["merge_order"], "row-major_block_index")
        self.assertTrue(adapter.partition_ready)
        self.assertEqual(adapter.contract.halo_policy.value, "dynamic")
        self.assertEqual(adapter.contract.border_policy.value, "clamp")
        self.assertTrue(can_partition_block("ssim_aot", "cpu"))
        self.assertFalse(can_auto_block("ssim_aot", "cpu"))
        self.assertFalse(can_auto_partition_dispatch("ssim_aot", "cpu"))
        for window_size, block_size in ((1, (7, 11)), (5, (8, 9)), (11, (13, 10)), (21, (17, 19))):
            with self.subTest(window_size=window_size, block_size=block_size):
                report = verify_map_reduce_parity(
                    "ssim_aot",
                    (first, second),
                    block_size=block_size,
                    params={"window_size": window_size, "data_range": 1.0},
                )
                self.assertTrue(report["passed"], report)
                self.assertLessEqual(report["max_abs_error"], 1.0e-12)
                self.assertEqual(report["halo"], window_size // 2)
                self.assertFalse(report["native_runtime"])

        # A 3-channel path exercises the same halo and reduction contract for
        # all channels without requiring a second adapter implementation.
        first_rgb = np.stack((first, first * 0.5, first * 0.2), axis=-1)
        second_rgb = np.stack((second, second * 0.5, second * 0.2), axis=-1)
        report = verify_map_reduce_parity(
            "ssim_aot",
            (first_rgb, second_rgb),
            block_size=(9, 12),
            params={"window_size": 7, "data_range": 1.0},
        )
        self.assertTrue(report["passed"], report)
        self.assertLessEqual(report["max_abs_error"], 1.0e-12)

    def test_ncc_output_domain_map_reduce_non_multiple_and_fail_closed(self):
        """ZNCC tiles the derived search surface, not the source frame."""

        rng = np.random.default_rng(20260810)
        image = rng.random((31, 43), dtype=np.float32)
        template = np.ascontiguousarray(image[9:16, 13:22])
        self.assertEqual(set(NCC_ADAPTER_OPERATIONS), {"zncc", "ncc_alignment"})
        for operation in NCC_ADAPTER_OPERATIONS:
            with self.subTest(operation=operation):
                adapter = self.map_adapters[operation]
                self.assertTrue(adapter.partition_ready)
                self.assertTrue(adapter.metadata["output_grid"])
                self.assertEqual(
                    adapter.metadata["coordinate_contract"]["kind"],
                    "sliding_window",
                )
                self.assertEqual(adapter.contract.halo_policy.value, "dynamic")
                self.assertEqual(adapter.contract.shape_transform.value, "changing" if operation == "zncc" else "reduce")
                self.assertTrue(can_partition_block(operation, "cpu"))
                self.assertFalse(can_auto_block(operation, "cpu"))
                self.assertFalse(can_auto_partition_dispatch(operation, "cpu"))

        # Both dimensions are deliberately non-multiples of every block size;
        # stride also exercises the output-coordinate mapping and source halo.
        for stride, block_size in ((1, (8, 11)), (2, (7, 9)), (3, (5, 6))):
            with self.subTest(stride=stride, block_size=block_size):
                surface = verify_map_reduce_parity(
                    "zncc",
                    (image, template),
                    block_size=block_size,
                    params={"stride": stride},
                )
                self.assertTrue(surface["passed"], surface)
                self.assertEqual(surface["max_abs_error"], 0.0)
                self.assertEqual(surface["output_shape"], list(((31 - 7) // stride + 1, (43 - 9) // stride + 1)))
                self.assertEqual(surface["source_halo"], (6, 8))

                alignment = verify_map_reduce_parity(
                    "ncc_alignment",
                    (image, template),
                    block_size=block_size,
                    params={"stride": stride},
                )
                self.assertTrue(alignment["passed"], alignment)
                self.assertLessEqual(alignment["max_abs_error"], 1.0e-12)

        # A constant surface has many equal maxima.  The reducer must retain
        # the first row-major candidate, exactly as np.argmax(full_surface).
        constant = np.ones((17, 19), dtype=np.float32)
        constant_template = np.ones((5, 7), dtype=np.float32)
        full_surface = run_adapter_map_reduce(
            "zncc",
            (constant, constant_template),
            block_size=(4, 6),
            params={"stride": 2},
        )
        first_alignment = run_adapter_map_reduce(
            "ncc_alignment",
            (constant, constant_template),
            block_size=(4, 6),
            params={"stride": 2},
        )
        self.assertEqual(tuple(np.unravel_index(int(np.argmax(full_surface)), full_surface.shape)), (0, 0))
        self.assertEqual(first_alignment[:2], (0.0, 0.0))

    def test_stitch_sequence_map_reduce_overlap_order_and_non_multiple(self):
        """Stitch reductions preserve overlap semantics and canonical order."""

        rng = np.random.default_rng(20260810)
        tile_count, tile_h, tile_w = 7, 4, 5
        frame_shape = (13, 17)
        tiles = rng.random((tile_count, tile_h, tile_w), dtype=np.float32)
        # Per-tile weights exercise the batch form; the hanning window is
        # intentionally non-uniform so overlap and ordering are observable.
        tile_weights = rng.random((tile_count, tile_h, tile_w), dtype=np.float32)
        hanning = np.linspace(
            0.2, 1.0, tile_h * tile_w, dtype=np.float32
        ).reshape(tile_h, tile_w)
        accum = rng.random(frame_shape, dtype=np.float32)
        weight_accum = rng.random(frame_shape, dtype=np.float32)
        y0s = np.asarray([7, 0, 3, 2, 8, 4, 9], dtype=np.int32)
        x0s = np.asarray([2, 10, 3, 0, 9, 6, 11], dtype=np.int32)
        inputs = (tiles, tile_weights, hanning, accum, weight_accum, y0s, x0s)

        self.assertEqual(
            set(STITCH_ADAPTER_OPERATIONS),
            {"stitch_tile", "stitch_tile_normalized"},
        )
        for operation in STITCH_ADAPTER_OPERATIONS:
            with self.subTest(operation=operation):
                adapter = self.map_adapters[operation]
                self.assertTrue(adapter.partition_ready)
                self.assertTrue(adapter.metadata["sequence_domain"])
                self.assertEqual(
                    adapter.metadata["sequence_contract"]["order"],
                    "row_major_origin_then_input_index",
                )
                self.assertTrue(adapter.metadata["sequence_contract"]["overlap"] == "allowed")
                self.assertTrue(can_partition_block(operation, "cpu"))
                self.assertFalse(can_auto_block(operation, "cpu"))
                self.assertFalse(can_auto_partition_dispatch(operation, "cpu"))

                for chunk in (2, 3, 4):
                    report = verify_map_reduce_parity(
                        operation,
                        inputs,
                        block_size=(chunk, 1),
                    )
                    self.assertTrue(report["passed"], report)
                    self.assertEqual(report["max_abs_error"], 0.0)

                # Reordering the input stack must not change the result: the
                # adapter sorts by origin and uses the original index only as
                # a stable tie-break for identical origins.
                permutation = np.asarray([4, 0, 6, 2, 5, 1, 3])
                permuted_inputs = (
                    tiles[permutation],
                    tile_weights[permutation],
                    hanning,
                    accum,
                    weight_accum,
                    y0s[permutation],
                    x0s[permutation],
                )
                canonical = run_adapter_map_reduce(
                    operation, inputs, block_size=(3, 1)
                )
                permuted = run_adapter_map_reduce(
                    operation, permuted_inputs, block_size=(3, 1)
                )
                for left, right in zip(canonical, permuted):
                    np.testing.assert_array_equal(left, right)

    def test_accumulator_adapters_are_semantic_cpu_only(self):
        self.assertEqual(
            set(ACCUMULATOR_ADAPTER_OPERATIONS),
            {"mean_division", "normalize_accumulator"},
        )
        self.assertTrue(
            set(ACCUMULATOR_ADAPTER_OPERATIONS).issubset(
                self.accumulator_adapters
            )
        )
        for name in ACCUMULATOR_ADAPTER_OPERATIONS:
            adapter = registered_block_adapters()[name]
            self.assertTrue(adapter.partition_ready)
            self.assertTrue(adapter.metadata["semantic_only"])
            self.assertTrue(adapter.metadata["legacy_global_operation"])
            self.assertEqual(adapter.metadata["source_path"], "global")
            # The local adapter contract is usable by explicit CPU partition
            # helpers, but the maintained operation remains global and has no
            # legacy executor/native evidence for automatic dispatch.
            self.assertTrue(can_partition_block(name, "cpu"))
            self.assertFalse(can_auto_block(name, "cpu"))
            self.assertFalse(can_auto_partition_dispatch(name, "cpu"))
            self.assertEqual(operation_contract(name).reduction.value, "global")
            self.assertFalse(operation_contract(name).automatic_safe)

    def test_accumulator_full_frame_and_tiled_parity(self):
        rng = np.random.default_rng(20260810)
        sum_img = rng.random((67, 73), dtype=np.float32)
        weights = rng.random((67, 73), dtype=np.float32)
        # Exercise both the guarded fallback and ordinary division branches.
        weights[::5, ::7] = 0.0
        weights[1::11, 2::13] = 1.0e-7
        reference = rng.random((67, 73), dtype=np.float32)

        mean = verify_adapter_parity(
            "mean_division",
            (sum_img, weights, reference),
            block_size=(19, 23),
        )
        self.assertTrue(mean["passed"], mean)
        self.assertEqual(mean["max_abs_error"], 0.0)
        self.assertFalse(mean["native_runtime"])

        normalized = verify_adapter_parity(
            "normalize_accumulator",
            (sum_img, weights),
            block_size=(19, 23),
        )
        self.assertTrue(normalized["passed"], normalized)
        self.assertEqual(normalized["max_abs_error"], 0.0)
        self.assertFalse(normalized["native_runtime"])

    def test_accumulator_vector_and_zero_weight_semantics(self):
        rng = np.random.default_rng(91)
        sum_img = rng.random((23, 29, 3), dtype=np.float32)
        weights = rng.random((23, 29), dtype=np.float32)
        weights[0, :] = 0.0
        weights[1, 1] = -2.0
        reference = rng.random((23, 29, 3), dtype=np.float32)

        mean = verify_adapter_parity(
            "mean_division",
            (sum_img, weights, reference),
            block_size=7,
        )
        self.assertTrue(mean["passed"], mean)
        self.assertEqual(mean["max_abs_error"], 0.0)

        normalized = verify_adapter_parity(
            "normalize_accumulator",
            (sum_img, weights),
            block_size=7,
        )
        self.assertTrue(normalized["passed"], normalized)
        self.assertEqual(normalized["max_abs_error"], 0.0)

    def test_accumulator_contract_rejects_nonfinite_and_complex_inputs(self):
        """Partitioning must not claim deterministic parity for invalid lanes."""

        sum_img = np.ones((5, 7), dtype=np.float32)
        weights = np.ones((5, 7), dtype=np.float32)
        reference = np.zeros_like(sum_img)
        cases = (
            ((sum_img.copy(), weights.copy(), reference.copy()), {"epsilon": np.nan}),
            ((sum_img.copy(), weights.copy(), reference.copy()), {"epsilon": np.inf}),
        )
        for inputs, params in cases:
            with self.subTest(params=params):
                with self.assertRaises(ValueError):
                    verify_adapter_parity(
                        "mean_division", inputs, block_size=3, params=params
                    )

        nonfinite = sum_img.copy()
        nonfinite[2, 3] = np.nan
        with self.assertRaises(ValueError):
            verify_adapter_parity(
                "mean_division",
                (nonfinite, weights, reference),
                block_size=3,
            )

        complex_weights = weights.astype(np.complex64)
        with self.assertRaises(TypeError):
            verify_adapter_parity(
                "normalize_accumulator",
                (sum_img, complex_weights),
                block_size=3,
            )

    def test_coordinate_adapters_are_semantic_cpu_only_and_fail_closed(self):
        self.assertEqual(
            set(COORDINATE_ADAPTER_OPERATIONS),
            {"tone_map_srgb", "naturalTonemapping", "to_gamma_proxy", "rotate_by_flip"},
        )
        self.assertTrue(set(COORDINATE_ADAPTER_OPERATIONS).issubset(self.coordinate_adapters))
        for name in COORDINATE_ADAPTER_OPERATIONS:
            adapter = registered_block_adapters()[name]
            self.assertTrue(adapter.partition_ready)
            self.assertTrue(adapter.metadata["semantic_only"])
            self.assertFalse(can_auto_partition_dispatch(name, "cpu"))
            self.assertFalse(can_auto_partition_dispatch(name, "vulkan"))
            self.assertFalse(can_auto_block(name, "cpu"))
        coverage = block_coverage_report("cpu")
        self.assertTrue(
            set(COORDINATE_ADAPTER_OPERATIONS).issubset(
                set(coverage["adapter_operations"])
            )
        )
        self.assertEqual(coverage["strict_auto_safe"], 48)

    def test_coordinate_semantic_parity_edge_shapes_and_dtypes(self):
        rng = np.random.default_rng(20260810)
        rgb = rng.random((33, 37, 3), dtype=np.float32)
        raw_u16 = rng.integers(0, 65536, size=(33, 37), dtype=np.uint16)
        gamma_f16 = rng.random((33, 37), dtype=np.float32).astype(np.float16)

        cases = (
            (
                "tone_map_srgb",
                (rgb,),
                {"exposure": 1.25, "shoulder": 2.2, "gamma": 1.4, "saturation": 1.1},
            ),
            (
                "naturalTonemapping",
                (raw_u16,),
                {"exposure": 1.35, "shoulder": 2.5, "gamma": 1.6, "texture_amount": 0.0},
            ),
            ("to_gamma_proxy", (gamma_f16,), {"scale": 0.85}),
        )
        for name, inputs, params in cases:
            with self.subTest(operation=name):
                report = verify_adapter_parity(
                    name, inputs, block_size=(11, 13), params=params
                )
                self.assertTrue(report["passed"], report)
                self.assertEqual(report["max_abs_error"], 0.0)
                self.assertFalse(report["native_runtime"])

        with self.assertRaisesRegex(ValueError, "texture_amount=0"):
            verify_adapter_parity(
                "naturalTonemapping",
                (rgb,),
                block_size=11,
                params={"texture_amount": 0.2},
            )

    def test_rotate_by_flip_coordinate_mapping_same_shape(self):
        rng = np.random.default_rng(20260810)
        image = rng.integers(0, 65536, size=(33, 37, 3), dtype=np.uint16)
        for flip in (0, 1, 2, 3):
            with self.subTest(flip=flip):
                report = verify_adapter_parity(
                    "rotate_by_flip",
                    (image,),
                    block_size=(11, 13),
                    params={"flip": flip},
                )
                self.assertTrue(report["passed"], report)
                self.assertEqual(report["max_abs_error"], 0.0)
        with self.assertRaisesRegex(ValueError, "only flip values 0..3"):
            verify_adapter_parity(
                "rotate_by_flip",
                (image,),
                block_size=11,
                params={"flip": 5},
            )

    def test_output_domain_coordinate_adapters_edge_shapes(self):
        self.assertEqual(
            set(OUTPUT_DOMAIN_ADAPTER_OPERATIONS),
            {"generate_hanning_window_2d", "gaussian_window_aot"},
        )
        self.assertTrue(set(OUTPUT_DOMAIN_ADAPTER_OPERATIONS).issubset(self.output_adapters))
        for name in OUTPUT_DOMAIN_ADAPTER_OPERATIONS:
            adapter = registered_block_adapters()[name]
            self.assertTrue(adapter.partition_ready)
            self.assertTrue(adapter.metadata["output_domain"])
            self.assertTrue(adapter.metadata["semantic_only"])
            self.assertFalse(can_auto_partition_dispatch(name, "cpu"))
            self.assertFalse(can_auto_partition_dispatch(name, "vulkan"))

        cases = (
            (
                "generate_hanning_window_2d",
                {"shape": (33, 37), "exclude_boundary": False, "dtype": np.float32},
            ),
            (
                "generate_hanning_window_2d",
                {"shape": (33, 37), "exclude_boundary": True, "dtype": np.float16},
            ),
            (
                "gaussian_window_aot",
                {"shape": (33, 37), "sigma": 4.25},
            ),
        )
        for name, params in cases:
            with self.subTest(operation=name, params=params):
                report = verify_output_domain_parity(
                    name, params=params, block_size=(11, 13)
                )
                self.assertTrue(report["passed"], report)
                self.assertEqual(report["max_abs_error"], 0.0)
                self.assertFalse(report["native_runtime"])


if __name__ == "__main__":
    unittest.main()
