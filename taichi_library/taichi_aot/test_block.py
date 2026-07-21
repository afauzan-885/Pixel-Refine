import importlib.util
from pathlib import Path
import sys
import threading
import types
import unittest

import numpy as np
import cv2


MODULE_PATH = Path(__file__).with_name("block.py")
SPEC = importlib.util.spec_from_file_location("pixel_refine_block_test", MODULE_PATH)
block = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = block
SPEC.loader.exec_module(block)

MEMORY_PATH = MODULE_PATH.with_name("memory.py")
MEMORY_SPEC = importlib.util.spec_from_file_location("pixel_refine_memory_test", MEMORY_PATH)
memory_policy = importlib.util.module_from_spec(MEMORY_SPEC)
sys.modules[MEMORY_SPEC.name] = memory_policy
MEMORY_SPEC.loader.exec_module(memory_policy)

RESIDENCY_PATH = MODULE_PATH.with_name("residency.py")
RESIDENCY_SPEC = importlib.util.spec_from_file_location("pixel_refine_residency_test", RESIDENCY_PATH)
residency = importlib.util.module_from_spec(RESIDENCY_SPEC)
sys.modules[RESIDENCY_SPEC.name] = residency
RESIDENCY_SPEC.loader.exec_module(residency)


class BlockGridTest(unittest.TestCase):
    def test_grid_covers_image_once(self):
        grid = block.BlockGrid((600, 700, 3), size=256)
        self.assertEqual(len(grid), 9)
        coverage = np.zeros((600, 700), dtype=np.uint8)
        for spec in grid:
            coverage[spec.write_slice] += 1
        self.assertTrue(np.all(coverage == 1))

    def test_halo_is_clamped_and_core_is_relative(self):
        first = next(iter(block.BlockGrid((300, 300), size=256, halo=12)))
        self.assertEqual(first.read_shape, (268, 268))
        self.assertEqual(first.core_slice, (slice(0, 256), slice(0, 256)))
        last = list(block.BlockGrid((300, 300), size=256, halo=12))[-1]
        self.assertEqual(last.shape, (44, 44))
        self.assertEqual(last.core_slice, (slice(12, 56), slice(12, 56)))

    def test_block_id_changes_with_operation_parameters(self):
        spec = next(iter(block.BlockGrid((32, 32), size=16)))
        first = spec.make_id("frame-1", "copy", {"dtype": "float32"})
        self.assertEqual(first, spec.make_id("frame-1", "copy", {"dtype": "float32"}))
        self.assertNotEqual(first, spec.make_id("frame-1", "copy", {"dtype": "float16"}))


class BlockCacheTest(unittest.TestCase):
    def test_collect_keeps_dirty_and_pinned_records(self):
        cache = block.BlockCache(max_entries=2)
        cache.put(block.BlockRecord("dirty", state=block.BlockState.DIRTY, data=1, dirty=True))
        cache.put(block.BlockRecord("pinned", state=block.BlockState.READY, data=2, pinned=True))
        cache.put(block.BlockRecord("free", state=block.BlockState.READY, data=3))
        self.assertEqual(len(cache), 2)
        self.assertIsNone(cache.get("free"))
        self.assertIsNotNone(cache.get("dirty"))
        self.assertIsNotNone(cache.get("pinned"))

    def test_checksum_detects_changed_data(self):
        data = np.zeros((4, 4), dtype=np.float32)
        first = block.checksum(data)
        data[0, 0] = 1.0
        self.assertNotEqual(first, block.checksum(data))

    def test_byte_budget_evicts_lru_and_rejects_oversized_entry(self):
        cache = block.BlockCache(max_entries=10, max_bytes=96)
        cache.put(block.BlockRecord("first", state=block.BlockState.READY,
                                    data=np.zeros(16, dtype=np.float32)))
        cache.put(block.BlockRecord("second", state=block.BlockState.READY,
                                    data=np.ones(16, dtype=np.float32)))
        self.assertIsNone(cache.get("first"))
        self.assertIsNotNone(cache.get("second"))
        self.assertEqual(cache.size_bytes, 64)

        rejected = block.BlockCache(max_entries=10, max_bytes=32)
        rejected.put(block.BlockRecord("large", state=block.BlockState.READY,
                                       data=np.zeros(16, dtype=np.float32)))
        self.assertEqual(len(rejected), 0)
        self.assertEqual(rejected.size_bytes, 0)

    def test_automatic_owner_quota_reclaims_borrowed_capacity(self):
        cache = block.BlockCache(max_entries=20, max_bytes=100)
        for index in range(3):
            cache.put(block.BlockRecord(
                f"a{index}", owner="algorithm_a", state=block.BlockState.READY,
                data=np.zeros(30, dtype=np.uint8),
            ))
        cache.put(block.BlockRecord(
            "b0", owner="algorithm_b", state=block.BlockState.READY,
            data=np.zeros(30, dtype=np.uint8),
        ))
        self.assertIsNotNone(cache.get("b0"))
        self.assertEqual(cache.owner_bytes["algorithm_a"], 60)
        self.assertEqual(cache.owner_bytes["algorithm_b"], 30)
        self.assertLessEqual(cache.size_bytes, 100)


class MemoryGovernorTest(unittest.TestCase):
    def test_realtime_pressure_disables_and_recovers_cache_admission(self):
        gib = 1024 ** 3
        state = {"available": 8 * gib}

        def provider():
            return memory_policy.MemorySnapshot(16 * gib, state["available"], 0.0)

        governor = memory_policy.MemoryGovernor(
            provider=provider, configured_max_bytes=2 * gib, sample_interval=0.05
        )
        healthy = governor.refresh(force=True)
        self.assertEqual(healthy.pressure, memory_policy.MemoryPressure.HEALTHY)
        self.assertTrue(healthy.allow_cache)
        self.assertGreater(healthy.host_cache_budget, 0)

        state["available"] = 2 * gib
        low = governor.refresh(force=True)
        self.assertEqual(low.pressure, memory_policy.MemoryPressure.LOW)
        self.assertFalse(low.allow_cache)
        self.assertEqual(low.host_cache_budget, 0)
        self.assertEqual(low.max_concurrency, 1)

        state["available"] = 5 * gib
        recovered = governor.refresh(force=True)
        self.assertEqual(recovered.pressure, memory_policy.MemoryPressure.HEALTHY)
        self.assertTrue(recovered.allow_cache)


class DeviceResidencyCacheTest(unittest.TestCase):
    def test_borrowed_blocks_are_reclaimed_and_leases_prevent_eviction(self):
        disposed = []
        cache = residency.DeviceResidencyCache(max_bytes=100)
        cache.configure_owner("a", soft_bytes=30, hard_bytes=100)
        cache.configure_owner("b", soft_bytes=30, hard_bytes=100)
        cache.put("a1", "a", object(), 40, dispose=lambda _buffer: disposed.append("a1"))
        cache.put("a2", "a", object(), 40, dispose=lambda _buffer: disposed.append("a2"))

        with cache.lease("a2") as leased:
            self.assertIsNotNone(leased)
            cache.put("b1", "b", object(), 50, dispose=lambda _buffer: disposed.append("b1"))
            self.assertIsNone(cache.get("a1"))
            self.assertIsNotNone(cache.get("a2"))
            self.assertIsNotNone(cache.get("b1"))
        self.assertIn("a1", disposed)
        self.assertLessEqual(cache.size_bytes, 100)

    def test_hard_owner_limit_rejects_admission(self):
        cache = residency.DeviceResidencyCache(max_bytes=256)
        cache.configure_owner("limited", soft_bytes=32, hard_bytes=64)
        self.assertIsNotNone(cache.put("one", "limited", object(), 48))
        self.assertIsNone(cache.put("two", "limited", object(), 32))
        self.assertEqual(cache.stats()["owner_bytes"]["limited"], 48)


class BlockPolicyTest(unittest.TestCase):
    def test_policy_is_conservative(self):
        config = block.BlockConfig(enabled=True, threshold_bytes=16)
        self.assertTrue(block.should_use_blocks("copy", 16, config))
        self.assertTrue(block.should_use_blocks("remap", 16, config))
        self.assertFalse(block.should_use_blocks("fft", 16, config))

    def test_policy_rejects_invalid_cache_and_threshold(self):
        with self.assertRaises(ValueError):
            block.BlockConfig(cache_entries=0)
        with self.assertRaises(ValueError):
            block.BlockConfig(threshold_bytes=-1)


class EngineBlockIntegrationTest(unittest.TestCase):
    def test_engine_plans_only_safe_opted_in_operations(self):
        package_name = "taichi_library.taichi_aot"
        package = types.ModuleType(package_name)
        package.__path__ = [str(MODULE_PATH.parent)]
        sys.modules[package_name] = package

        engine_path = MODULE_PATH.with_name("engine.py")
        engine_spec = importlib.util.spec_from_file_location(
            f"{package_name}.engine_test", engine_path
        )
        engine_module = importlib.util.module_from_spec(engine_spec)
        sys.modules[engine_spec.name] = engine_module
        engine_spec.loader.exec_module(engine_module)

        engine = object.__new__(engine_module.AOTEngine)
        engine._lock = threading.RLock()
        engine._block_config = block.BlockConfig()
        engine._block_cache = block.BlockCache(engine._block_config.cache_entries)

        config = engine.configure_blocks(enabled=True, size=128, threshold_bytes=16)
        self.assertEqual(config.normalized_size(), (128, 128))
        self.assertEqual(len(engine.plan_blocks("copy", (300, 300), 16)), 9)
        self.assertEqual(len(engine.plan_blocks("remap", (300, 300), 16)), 9)
        self.assertEqual(engine.configure_blocks(cache_bytes=1024).cache_bytes, 1024)
        self.assertEqual(engine.configure_blocks(enabled=True).cache_bytes, 1024)
        self.assertIsNone(engine.configure_blocks(cache_bytes=None).cache_bytes)


class CommonCopyBlockTest(unittest.TestCase):
    def setUp(self):
        from taichi_library import taichi_aot

        self.aot = taichi_aot
        self.previous = taichi_aot.get_block_config()
        taichi_aot.set_block_mode(
            enabled=True,
            size=16,
            threshold_bytes=1,
            cache_entries=32,
        )
        taichi_aot.engine.clear_block_cache()

    def test_low_ram_pressure_falls_back_to_uncached_block_compute(self):
        governor = self.aot.engine._memory_governor
        original_provider = governor.provider
        gib = 1024 ** 3
        try:
            governor.provider = lambda: memory_policy.MemorySnapshot(16 * gib, 2 * gib, 0.0)
            governor._decision = None
            self.aot.set_block_mode(
                enabled=True, size=16, threshold_bytes=0, cache_entries=64,
                cache_bytes=64 * 1024 ** 2, adaptive_memory=True,
                device_cache_enabled=True, device_cache_bytes=32 * 1024 ** 2,
            )
            self.aot.engine.clear_block_cache()
            source = np.arange(32 * 32, dtype=np.float32).reshape(32, 32)
            result = self.aot.copy(source)
            np.testing.assert_array_equal(result, source)
            self.assertEqual(len(self.aot.engine.get_block_cache()), 0)
            self.assertEqual(self.aot.engine.get_device_block_cache().max_bytes, 0)
            self.assertEqual(self.aot.get_memory_status(True)["pressure"], "low")
        finally:
            governor.provider = original_provider
            governor._decision = None
            governor._pressure = memory_policy.MemoryPressure.HEALTHY
            self.aot.engine._refresh_memory_policy(force=True)

    def test_cached_first_ordering_avoids_partial_working_set_thrashing(self):
        self.aot.set_block_mode(
            enabled=True, size=16, threshold_bytes=0, cache_entries=64,
            cache_bytes=8 * 1024, adaptive_memory=True,
        )
        self.aot.engine.clear_block_cache()
        source = np.arange(64 * 64, dtype=np.float32).reshape(64, 64)
        expected = self.aot.copy(source)
        before = self.aot.get_block_cache_stats()
        actual = self.aot.copy(source)
        after = self.aot.get_block_cache_stats()
        np.testing.assert_array_equal(actual, expected)
        self.assertGreater(after["hits"] - before["hits"], 0)

    def test_native_vram_residency_restores_host_evicted_tiles(self):
        self.aot.set_block_mode(
            enabled=True, size=16, threshold_bytes=0, cache_entries=1,
            cache_bytes=1024, adaptive_memory=False,
            device_cache_enabled=True, device_cache_bytes=1024 * 1024,
        )
        self.aot.engine.clear_block_cache()
        source = np.arange(64 * 64, dtype=np.float32).reshape(64, 64)
        expected = self.aot.copy(source)
        before = self.aot.get_block_cache_stats()["device"]
        actual = self.aot.copy(source)
        after = self.aot.get_block_cache_stats()["device"]

        np.testing.assert_array_equal(actual, expected)
        self.assertEqual(after["hits"] - before["hits"], 15)
        self.assertEqual(after["entries"], 16)

    def tearDown(self):
        self.aot.engine.configure_blocks(
            enabled=self.previous.enabled,
            size=self.previous.size,
            threshold_bytes=self.previous.threshold_bytes,
            cache_entries=self.previous.cache_entries,
            cache_bytes=self.previous.cache_bytes,
            adaptive_memory=self.previous.adaptive_memory,
            device_cache_enabled=self.previous.device_cache_enabled,
            device_cache_bytes=self.previous.device_cache_bytes,
        )

    def test_large_copy_uses_common_aot_graph_per_block(self):
        source = np.arange(96 * 80, dtype=np.float32).reshape(96, 80)
        result = self.aot.copy(source)
        np.testing.assert_array_equal(result, source)

    def test_corrupt_cached_tile_is_recomputed(self):
        source = np.arange(64 * 64, dtype=np.float32).reshape(64, 64)
        self.aot.copy(source)
        record = next(iter(self.aot.engine.get_block_cache()._records.values()))
        record.data.flat[0] += 1.0

        np.testing.assert_array_equal(self.aot.copy(source), source)

    def test_transient_tile_failure_retries_from_source(self):
        source = np.arange(48 * 48, dtype=np.float32).reshape(48, 48)
        original_copy_tile = self.aot._copy_tile
        calls = 0

        def fail_once(tile):
            nonlocal calls
            calls += 1
            if calls == 1:
                raise RuntimeError("injected transient tile failure")
            return original_copy_tile(tile)

        self.aot._copy_tile = fail_once
        try:
            result = self.aot.copy(source)
        finally:
            self.aot._copy_tile = original_copy_tile

        self.assertGreaterEqual(calls, 2)
        np.testing.assert_array_equal(result, source)

    def test_absdiff_matches_full_frame_execution(self):
        first = np.arange(64 * 48, dtype=np.float32).reshape(64, 48)
        second = first[::-1].copy()

        self.aot.set_block_mode(enabled=False)
        expected = self.aot.absdiff(first, second)
        self.aot.set_block_mode(enabled=True, size=16, threshold_bytes=1)
        self.aot.engine.clear_block_cache()

        np.testing.assert_array_equal(self.aot.absdiff(first, second), expected)

    def test_rgb2gray_matches_full_frame_execution(self):
        source = np.arange(48 * 64 * 3, dtype=np.float32).reshape(48, 64, 3)

        self.aot.set_block_mode(enabled=False)
        expected = self.aot.rgb2gray(source)
        self.aot.set_block_mode(enabled=True, size=16, threshold_bytes=1)
        self.aot.engine.clear_block_cache()

        np.testing.assert_array_equal(self.aot.rgb2gray(source), expected)

    def test_gaussian_blur_halo_matches_full_frame_execution(self):
        source = np.arange(64 * 80, dtype=np.float32).reshape(64, 80) / 255.0

        self.aot.set_block_mode(enabled=False)
        expected = self.aot.gaussian_blur(source, sigma=1.0, kernel_size=5)
        self.aot.set_block_mode(enabled=True, size=16, threshold_bytes=1)
        self.aot.engine.clear_block_cache()

        np.testing.assert_allclose(
            self.aot.gaussian_blur(source, sigma=1.0, kernel_size=5),
            expected,
            rtol=0,
            atol=1e-6,
        )

    def test_box_filter_halo_matches_full_frame_execution(self):
        source = np.arange(64 * 80, dtype=np.float32).reshape(64, 80) / 255.0

        self.aot.set_block_mode(enabled=False)
        expected = self.aot.box_filter(source, kernel_size=5)
        self.aot.set_block_mode(enabled=True, size=16, threshold_bytes=1)
        self.aot.engine.clear_block_cache()

        np.testing.assert_allclose(
            self.aot.box_filter(source, kernel_size=5),
            expected,
            rtol=0,
            atol=1e-6,
        )

    def test_median_filter_halo_matches_full_frame_execution(self):
        source = (np.arange(64 * 80, dtype=np.float32).reshape(64, 80) % 31) / 31.0

        self.aot.set_block_mode(enabled=False)
        expected = self.aot.median_filter(source)
        self.aot.set_block_mode(enabled=True, size=16, threshold_bytes=1)
        self.aot.engine.clear_block_cache()

        np.testing.assert_array_equal(self.aot.median_filter(source), expected)

    def test_laplacian_halo_matches_full_frame_execution(self):
        source = np.arange(64 * 80, dtype=np.float32).reshape(64, 80) / 255.0

        self.aot.set_block_mode(enabled=False)
        expected = self.aot.laplacian(source)
        self.aot.set_block_mode(enabled=True, size=16, threshold_bytes=1)
        self.aot.engine.clear_block_cache()

        np.testing.assert_allclose(
            self.aot.laplacian(source), expected, rtol=0, atol=1e-6
        )

    def test_sobel_halo_matches_full_frame_execution(self):
        source = np.arange(64 * 80, dtype=np.float32).reshape(64, 80) / 255.0

        self.aot.set_block_mode(enabled=False)
        expected_dx, expected_dy = self.aot.sobel(source)
        self.aot.set_block_mode(enabled=True, size=16, threshold_bytes=1)
        self.aot.engine.clear_block_cache()
        actual_dx, actual_dy = self.aot.sobel(source)

        np.testing.assert_allclose(actual_dx, expected_dx, rtol=0, atol=1e-6)
        np.testing.assert_allclose(actual_dy, expected_dy, rtol=0, atol=1e-6)

    def test_nlm_halo_matches_full_frame_execution_and_reuses_cache(self):
        source = (np.arange(48 * 48, dtype=np.float32).reshape(48, 48) % 29) / 29.0

        self.aot.set_block_mode(enabled=False)
        expected = self.aot.non_local_means(
            source, h_param=0.1, search_window=3, patch_size=1
        )
        self.aot.set_block_mode(
            enabled=True, size=16, threshold_bytes=1, cache_entries=32
        )
        self.aot.engine.clear_block_cache()

        original_tile = self.aot._non_local_means_tile
        calls = 0

        def count_tile(*args):
            nonlocal calls
            calls += 1
            return original_tile(*args)

        self.aot._non_local_means_tile = count_tile
        try:
            first = self.aot.non_local_means(
                source, h_param=0.1, search_window=3, patch_size=1
            )
            first_pass_calls = calls
            second = self.aot.non_local_means(
                source, h_param=0.1, search_window=3, patch_size=1
            )
        finally:
            self.aot._non_local_means_tile = original_tile

        self.assertGreater(first_pass_calls, 0)
        self.assertEqual(calls, first_pass_calls)
        np.testing.assert_allclose(first, expected, rtol=0, atol=1e-6)
        np.testing.assert_array_equal(second, first)

    def test_smooth_flow_halo_matches_full_frame_execution(self):
        flow = np.stack(
            [
                np.arange(48 * 64, dtype=np.float32).reshape(48, 64) / 100.0,
                np.arange(48 * 64, dtype=np.float32).reshape(48, 64) / 200.0,
            ],
            axis=-1,
        )

        self.aot.set_block_mode(enabled=False)
        expected = self.aot.smooth_flow_gpu(flow, sigma=1.0, kernel_size=5)
        self.aot.set_block_mode(enabled=True, size=16, threshold_bytes=1)
        self.aot.engine.clear_block_cache()

        np.testing.assert_allclose(
            self.aot.smooth_flow_gpu(flow, sigma=1.0, kernel_size=5),
            expected,
            rtol=0,
            atol=1e-6,
        )

    def test_joint_bilateral_halo_matches_full_frame_execution(self):
        source = np.arange(48 * 64, dtype=np.float32).reshape(48, 64) / 255.0
        guide = source[::-1].copy()

        self.aot.set_block_mode(enabled=False)
        expected = self.aot.joint_bilateral_filter(source, guide, radius=2)
        self.aot.set_block_mode(enabled=True, size=16, threshold_bytes=1)
        self.aot.engine.clear_block_cache()

        np.testing.assert_allclose(
            self.aot.joint_bilateral_filter(source, guide, radius=2),
            expected,
            rtol=0,
            atol=1e-6,
        )

    def test_guided_filter_halo_matches_full_frame_execution(self):
        guide = np.arange(48 * 64, dtype=np.float32).reshape(48, 64) / 255.0
        source = (guide * 0.7 + 0.1).astype(np.float32)

        self.aot.set_block_mode(enabled=False)
        expected = self.aot.guided_filter_aot(guide, source, radius=2)
        self.aot.set_block_mode(enabled=True, size=16, threshold_bytes=1)
        self.aot.engine.clear_block_cache()

        np.testing.assert_allclose(
            self.aot.guided_filter_aot(guide, source, radius=2),
            expected,
            rtol=0,
            atol=1e-6,
        )

    def test_channel_operations_match_full_frame_execution(self):
        source = np.arange(48 * 64 * 3, dtype=np.float32).reshape(48, 64, 3)
        destination = np.full_like(source, -1.0)

        self.aot.set_block_mode(enabled=False)
        expected_split = self.aot.split_3ch(source)
        expected_extract = self.aot.extract_channel(source, 1)
        expected_merge = self.aot.merge_3ch(*expected_split)
        expected_insert = destination.copy()
        self.aot.insert_channel(expected_extract, expected_insert, 2)

        self.aot.set_block_mode(enabled=True, size=16, threshold_bytes=1)
        self.aot.engine.clear_block_cache()
        actual_split = self.aot.split_3ch(source)
        actual_extract = self.aot.extract_channel(source, 1)
        actual_merge = self.aot.merge_3ch(*actual_split)
        actual_insert = destination.copy()
        returned = self.aot.insert_channel(actual_extract, actual_insert, 2)

        for actual, expected in zip(actual_split, expected_split):
            np.testing.assert_array_equal(actual, expected)
        np.testing.assert_array_equal(actual_extract, expected_extract)
        np.testing.assert_array_equal(actual_merge, expected_merge)
        self.assertIs(returned, actual_insert)
        np.testing.assert_array_equal(actual_insert, expected_insert)

    def test_enhance_grayscale_matches_full_frame_execution(self):
        source = np.arange(48 * 64, dtype=np.float32).reshape(48, 64) / 255.0
        blurred = source[::-1].copy()
        lut = np.linspace(0.0, 1.0, 256, dtype=np.float32)

        self.aot.set_block_mode(enabled=False)
        expected = self.aot.enhance_grayscale(source, blurred, lut, clarity=0.25)
        self.aot.set_block_mode(enabled=True, size=16, threshold_bytes=1)
        self.aot.engine.clear_block_cache()

        np.testing.assert_allclose(
            self.aot.enhance_grayscale(source, blurred, lut, clarity=0.25),
            expected,
            rtol=0,
            atol=1e-6,
        )

    def test_remap_matches_full_frame_execution(self):
        source = np.arange(53 * 71, dtype=np.float32).reshape(53, 71) / 255.0
        yy, xx = np.mgrid[:59, :67].astype(np.float32)
        map_x = xx + 1.25 * np.sin(yy / 7.0)
        map_y = yy + 0.75 * np.cos(xx / 9.0)

        self.aot.set_block_mode(enabled=False)
        expected_remap = self.aot.remap(source, map_x, map_y)
        self.aot.set_block_mode(enabled=True, size=17, threshold_bytes=1)

        np.testing.assert_allclose(self.aot.remap(source, map_x, map_y), expected_remap, rtol=0, atol=1e-6)

    def test_coordinate_mapped_operations_match_full_frame_and_opencv(self):
        rng = np.random.default_rng(42)
        source = rng.random((53, 71), dtype=np.float32)
        flow = np.zeros((27, 36, 2), dtype=np.float32)
        flow[..., 0], flow[..., 1] = 0.35, -0.2
        matrix = np.array(
            [[1.0, 0.02, 2.0], [-0.01, 1.0, 3.0], [0.0001, 0.0002, 1.0]],
            dtype=np.float32,
        )

        self.aot.set_block_mode(enabled=False)
        full_linear = self.aot.resize(source, (89, 61), self.aot.INTER_LINEAR)
        full_cubic = self.aot.resize(source, (89, 61), self.aot.INTER_CUBIC)
        full_area = self.aot.resize(source, (31, 23), self.aot.INTER_AREA)
        full_pyramid = self.aot.image_pyramid(source, levels=2)
        full_flow = self.aot.remap_with_flow(source, flow, 59, 67)
        full_warp = self.aot.warp_perspective(source, matrix, (67, 59))

        self.aot.set_block_mode(enabled=True, size=17, threshold_bytes=1)
        np.testing.assert_allclose(self.aot.resize(source, (89, 61), self.aot.INTER_LINEAR), full_linear, rtol=0, atol=1e-6)
        np.testing.assert_allclose(self.aot.resize(source, (89, 61), self.aot.INTER_CUBIC), full_cubic, rtol=0, atol=2e-6)
        np.testing.assert_allclose(self.aot.resize(source, (31, 23), self.aot.INTER_AREA), full_area, rtol=0, atol=1e-6)
        np.testing.assert_allclose(self.aot.image_pyramid(source, levels=2), full_pyramid, rtol=0, atol=1e-6)
        np.testing.assert_allclose(self.aot.remap_with_flow(source, flow, 59, 67), full_flow, rtol=0, atol=1e-6)
        np.testing.assert_allclose(self.aot.warp_perspective(source, matrix, (67, 59)), full_warp, rtol=0, atol=1e-6)

        cv_linear = cv2.resize(source, (89, 61), interpolation=cv2.INTER_LINEAR)
        cv_pyramid = cv2.pyrDown(source, dstsize=(35, 26), borderType=cv2.BORDER_REFLECT_101)
        cv_warp = cv2.warpPerspective(source, matrix, (67, 59), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
        np.testing.assert_allclose(full_linear, cv_linear, rtol=0, atol=1e-5)
        np.testing.assert_allclose(self.aot.image_pyramid(source, levels=1), cv_pyramid, rtol=0, atol=1e-6)
        np.testing.assert_allclose(full_warp, cv_warp, rtol=0, atol=2e-2)

    def test_coordinate_mapped_rgb_block_paths(self):
        rng = np.random.default_rng(84)
        source = rng.random((37, 49, 3), dtype=np.float32)
        flow = np.zeros((19, 25, 2), dtype=np.float32)
        matrix = np.array([[1.0, 0.01, 1.0], [-0.02, 1.0, 2.0], [0.0001, 0.0, 1.0]], dtype=np.float32)

        self.aot.set_block_mode(enabled=False)
        expected = (
            self.aot.resize(source, (61, 43), self.aot.INTER_LINEAR),
            self.aot.image_pyramid(source, 2),
            self.aot.remap_with_flow(source, flow, 41, 55),
            self.aot.warp_perspective(source, matrix, (55, 41)),
        )
        self.aot.set_block_mode(enabled=True, size=11, threshold_bytes=1)
        actual = (
            self.aot.resize(source, (61, 43), self.aot.INTER_LINEAR),
            self.aot.image_pyramid(source, 2),
            self.aot.remap_with_flow(source, flow, 41, 55),
            self.aot.warp_perspective(source, matrix, (55, 41)),
        )
        for result, reference in zip(actual, expected):
            np.testing.assert_allclose(result, reference, rtol=0, atol=1e-6)

    def test_output_tile_cache_reuses_across_algorithms_and_isolates_corruption(self):
        rng = np.random.default_rng(1234)
        source = rng.random((48, 64), dtype=np.float32)
        flow = np.zeros((24, 32, 2), dtype=np.float32)
        matrix = np.array([[1.0, 0.01, 1.0], [-0.005, 1.0, 2.0], [0.0001, 0.0, 1.0]], dtype=np.float32)
        self.aot.set_block_mode(enabled=True, size=16, threshold_bytes=1, cache_entries=128)
        self.aot.engine.clear_block_cache()
        operations = {
            "resize": lambda: self.aot.resize(source, (73, 55), self.aot.INTER_CUBIC),
            "warp": lambda: self.aot.warp_perspective(source, matrix, (73, 55)),
            "flow": lambda: self.aot.remap_with_flow(source, flow, 55, 73),
            "pyramid": lambda: self.aot.image_pyramid(source, 2),
        }

        key_sets = {}
        previous_keys = set()
        for name, operation in operations.items():
            operation()
            current_keys = set(self.aot.engine.get_block_cache()._records)
            key_sets[name] = current_keys - previous_keys
            previous_keys = current_keys
        names = list(key_sets)
        for index, name in enumerate(names):
            for other in names[index + 1:]:
                self.assertTrue(key_sets[name].isdisjoint(key_sets[other]))

        original_put = self.aot._put_cached_output_tile
        put_calls = 0
        def count_put(*args, **kwargs):
            nonlocal put_calls
            put_calls += 1
            return original_put(*args, **kwargs)
        self.aot._put_cached_output_tile = count_put
        try:
            for name in ("flow", "resize", "pyramid", "warp"):
                operations[name]()
        finally:
            self.aot._put_cached_output_tile = original_put
        self.assertEqual(put_calls, 0)

        resize_record = self.aot.engine.get_block_cache()._records[next(iter(key_sets["resize"]))]
        resize_record.data.flat[0] = np.nan
        put_calls = 0
        self.aot._put_cached_output_tile = count_put
        try:
            operations["warp"]()
            self.assertEqual(put_calls, 0)
            recovered = operations["resize"]()
        finally:
            self.aot._put_cached_output_tile = original_put
        # The intact VRAM tier repairs the corrupted RAM tile without recompute.
        self.assertEqual(put_calls, 0)
        self.assertTrue(np.isfinite(recovered).all())

    def test_demosaic_and_dense_flow_block_paths_match_full_frame(self):
        rng = np.random.default_rng(207)
        raw = rng.random((96, 128), dtype=np.float32)
        cmatrix = np.eye(3, dtype=np.float32)
        demosaic_args = (1.7, 1.0, 1.4, 1.0, cmatrix, 0.0, 1.0, 0, 1, 1, 2)
        y, x = np.mgrid[:128, :128]
        prev = (127.0 + 60.0 * np.sin(x * 0.09) + 50.0 * np.cos(y * 0.07)).astype(np.float32)
        next_frame = np.roll(np.roll(prev, 2, axis=0), 3, axis=1)

        self.aot.set_block_mode(enabled=False)
        hamilton = self.aot.hamilton_demosaic(raw, *demosaic_args)
        arm = self.aot.arm_demosaic(raw, *demosaic_args)
        lk = self.aot.lucasKanade(prev, next_frame, maxLevel=1, grid_step=16, winSize=(9, 9))
        bm = self.aot.blockMatching(prev, next_frame, maxLevel=1, grid_step=16, winSize=(9, 9))
        farneback = self.aot.farneback_flow(prev, next_frame, num_levels=2, num_iters=2, win_size=9)

        self.aot.set_block_mode(enabled=True, size=64, threshold_bytes=1, cache_entries=128)
        np.testing.assert_array_equal(self.aot.hamilton_demosaic(raw, *demosaic_args), hamilton)
        np.testing.assert_array_equal(self.aot.arm_demosaic(raw, *demosaic_args), arm)
        np.testing.assert_allclose(
            self.aot.lucasKanade(prev, next_frame, maxLevel=1, grid_step=16, winSize=(9, 9)),
            lk, rtol=0, atol=2e-5,
        )
        np.testing.assert_array_equal(
            self.aot.blockMatching(prev, next_frame, maxLevel=1, grid_step=16, winSize=(9, 9)), bm
        )
        np.testing.assert_allclose(
            self.aot.farneback_flow(prev, next_frame, num_levels=2, num_iters=2, win_size=9),
            farneback, rtol=0, atol=3e-6,
        )

        self.aot.engine.clear_block_cache()
        self.aot.farneback_flow(prev, next_frame, num_levels=2, num_iters=2, win_size=9)
        records = self.aot.engine.get_block_cache()._records
        next(iter(records.values())).data.flat[0] = np.nan
        recovered = self.aot.farneback_flow(prev, next_frame, num_levels=2, num_iters=2, win_size=9)
        self.assertTrue(np.isfinite(recovered).all())

    def test_all_demosaic_variants_are_block_native(self):
        rng = np.random.default_rng(411)
        raw = rng.random((101, 133), dtype=np.float32)
        cmatrix = np.array(
            [[1.02, -0.01, -0.01], [-0.02, 1.04, -0.02], [0.0, -0.03, 1.03]],
            dtype=np.float32,
        )
        wb = (1.6, 1.0, 1.35, 0.98)
        levels = (0.01, 0.99)
        cfa = (2, 1, 1, 0)
        cases = (
            ("hamilton_demosaic_1channel", (*wb, *levels, *cfa)),
            ("hamilton_demosaic_half_res", (*wb, *levels, *cfa)),
            ("hamilton_demosaic_rgb_half_res", (*wb, cmatrix, *levels, *cfa)),
            ("hamilton_demosaic_3channel", (*wb, cmatrix, *levels, *cfa)),
            ("arm_demosaic_1channel", (*wb, *levels, *cfa)),
            ("arm_demosaic_half_res", (*wb, *levels, *cfa)),
            ("arm_demosaic_rgb_half_res", (*wb, cmatrix, *levels, *cfa)),
            ("pure_arm_demosaic", (*levels, *cfa)),
        )
        for name, arguments in cases:
            function = getattr(self.aot, name)
            self.aot.set_block_mode(enabled=False)
            expected = function(raw, *arguments)
            self.aot.set_block_mode(enabled=True, size=32, threshold_bytes=1, cache_entries=128)
            actual = function(raw, *arguments)
            np.testing.assert_array_equal(actual, expected, err_msg=name)

        self.aot.set_block_mode(enabled=False)
        expected = self.aot.demosaic(
            raw, *wb, cmatrix, *levels, *cfa, method="hamilton-rgb-half-res"
        )
        self.aot.set_block_mode(enabled=True, size=32, threshold_bytes=1)
        actual = self.aot.demosaic(
            raw, *wb, cmatrix, *levels, *cfa, method="hamilton-rgb-half-res"
        )
        np.testing.assert_array_equal(actual, expected)

        self.aot.engine.clear_block_cache()
        expected = self.aot.arm_demosaic_half_res(raw, *wb, *levels, *cfa)
        record = next(iter(self.aot.engine.get_block_cache()._records.values()))
        record.data.flat[0] = np.nan
        recovered = self.aot.arm_demosaic_half_res(raw, *wb, *levels, *cfa)
        np.testing.assert_array_equal(recovered, expected)
        self.assertTrue(np.isfinite(recovered).all())


if __name__ == "__main__":
    unittest.main()
