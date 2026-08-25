"""Pure-Python invariants for adaptive memory decisions."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest
from collections import UserDict


ROOT = Path(__file__).resolve().parents[4]
_SPEC = importlib.util.spec_from_file_location(
    "pixel_refine_memory_contract",
    ROOT / "taichi_vision" / "taichi_aot" / "memory.py",
)
assert _SPEC is not None and _SPEC.loader is not None
MEMORY = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = MEMORY
_SPEC.loader.exec_module(MEMORY)


class MemoryContractTests(unittest.TestCase):
    def test_block_size_pressure_caps_are_monotonic(self):
        """Pressure must never admit a larger tile than a healthier state."""

        target = 2 * MEMORY.GIB
        shared = 4 * MEMORY.GIB
        sizes = [
            MEMORY._choose_block_size(
                target,
                pressure=pressure,
                shared_budget=shared,
                channels=3,
                sample_bytes=4,
                live_buffers=4,
            )
            for pressure in MEMORY.MemoryPressure
        ]
        self.assertEqual(sizes, [2048, 1536, 1024, 512, 256])
        self.assertEqual(sizes, sorted(sizes, reverse=True))

    def test_shape_aware_recommendation_uses_dtype_and_channel_budget(self):
        """Small grayscale/f16 work may use the safe cap without over-admitting RGB-f32."""

        target = 128 * 1024**2
        shared = 2 * MEMORY.GIB
        rgb_f32 = MEMORY._choose_block_size(
            target,
            pressure=MEMORY.MemoryPressure.HEALTHY,
            shared_budget=shared,
            channels=3,
            sample_bytes=4,
            live_buffers=4,
        )
        gray_f16 = MEMORY._choose_block_size(
            target,
            pressure=MEMORY.MemoryPressure.HEALTHY,
            shared_budget=shared,
            channels=1,
            sample_bytes=2,
            live_buffers=2,
        )
        self.assertEqual(rgb_f32, 1536)
        self.assertEqual(gray_f16, 2048)

    def test_zero_budget_remains_fail_closed_under_critical_pressure(self):
        """No shared budget must select the smallest bounded tile, never zero."""

        for pressure in (MEMORY.MemoryPressure.CRITICAL, MEMORY.MemoryPressure.EMERGENCY):
            self.assertEqual(
                MEMORY._choose_block_size(
                    0,
                    pressure=pressure,
                    shared_budget=0,
                    channels=3,
                    sample_bytes=4,
                    live_buffers=4,
                ),
                256,
            )

    def test_governor_decision_is_structurally_valid(self):
        snapshot = MEMORY.MemorySnapshot(16 * MEMORY.GIB, 8 * MEMORY.GIB, 1.0)
        decision = MEMORY.MemoryDecision(
            pressure=MEMORY.MemoryPressure.HEALTHY,
            host_cache_budget=512 * 1024**2,
            shared_device_budget=2 * MEMORY.GIB,
            device_pool_budget=256 * 1024**2,
            pipeline_resident_limit=1024 * 1024**2,
            target_chunk_bytes=512 * 1024**2,
            recommended_block_size=1024,
            system_reserve_bytes=4 * MEMORY.GIB,
            device_heap_budget=0,
            device_heap_usage=0,
            device_heap_available=0,
            device_budget_source="system_memory",
            allow_cache=True,
            allow_pinned_spill=True,
            allow_prefetch=True,
            max_concurrency=4,
            snapshot=snapshot,
            staging_pool_budget=128 * 1024**2,
            retired_buffer_budget=128 * 1024**2,
        )
        report = MEMORY.validate_memory_decision(decision)
        self.assertTrue(report["valid"], report)

    def test_inconsistent_budget_fails_closed_diagnostics(self):
        report = MEMORY.validate_memory_decision(
            {
                "shared_device_budget": 256,
                "pipeline_resident_limit": 512,
                "device_pool_budget": 512,
                "target_chunk_bytes": 1024,
                "recommended_block_size": 64,
            }
        )
        self.assertFalse(report["valid"])
        self.assertIn("pipeline_resident_limit exceeds shared_device_budget", report["issues"])
        self.assertIn("device_pool_budget exceeds shared_device_budget", report["issues"])
        self.assertIn("recommended_block_size is outside the 256..2048 contract", report["issues"])

    def test_invalid_input_is_reported_without_raising(self):
        report = MEMORY.validate_memory_decision(object())
        self.assertFalse(report["valid"])
        self.assertTrue(report["issues"])

    def test_device_heap_sample_above_budget_fails_closed(self):
        report = MEMORY.validate_memory_decision(
            {
                "shared_device_budget": 4096,
                "pipeline_resident_limit": 2048,
                "target_chunk_bytes": 1024,
                "recommended_block_size": 512,
                "device_heap_budget": 1000,
                "device_heap_usage": 1001,
                "device_heap_available": 1002,
            }
        )
        self.assertFalse(report["valid"])
        self.assertIn("device_heap_usage exceeds device_heap_budget", report["issues"])
        self.assertIn("device_heap_available exceeds device_heap_budget", report["issues"])

    def test_unknown_heap_budget_keeps_advisory_counters_compatible(self):
        report = MEMORY.validate_memory_decision(
            {
                "shared_device_budget": 4096,
                "pipeline_resident_limit": 2048,
                "target_chunk_bytes": 1024,
                "recommended_block_size": 512,
                "device_heap_budget": 0,
                "device_heap_usage": 1001,
                "device_heap_available": 1002,
            }
        )
        self.assertTrue(report["valid"], report)

    def test_fractional_and_boolean_budget_metadata_fails_closed(self):
        report = MEMORY.validate_memory_decision(
            {
                "shared_device_budget": 4096.5,
                "pipeline_resident_limit": True,
                "target_chunk_bytes": 1024,
                "recommended_block_size": 512,
            }
        )
        self.assertFalse(report["valid"])
        self.assertIn("shared_device_budget must be an integer", report["issues"])
        self.assertIn("pipeline_resident_limit must be an integer", report["issues"])

    def test_impossible_snapshot_fails_closed(self):
        report = MEMORY.validate_memory_decision(
            {
                "shared_device_budget": 4096,
                "pipeline_resident_limit": 2048,
                "target_chunk_bytes": 1024,
                "recommended_block_size": 512,
                "snapshot": {"total_bytes": 100, "available_bytes": 101},
            }
        )
        self.assertFalse(report["valid"])
        self.assertIn(
            "snapshot.available_bytes exceeds snapshot.total_bytes",
            report["issues"],
        )

    def test_malformed_snapshot_type_fails_closed(self):
        """A present but undecodable snapshot must not be ignored."""

        report = MEMORY.validate_memory_decision(
            {
                "shared_device_budget": 4096,
                "pipeline_resident_limit": 2048,
                "target_chunk_bytes": 1024,
                "recommended_block_size": 512,
                "snapshot": object(),
            }
        )
        self.assertFalse(report["valid"])
        self.assertIn(
            "snapshot must be MemorySnapshot or mapping when provided",
            report["issues"],
        )

    def test_non_finite_snapshot_timestamp_fails_closed(self):
        """Freshness telemetry must not accept NaN or infinity."""

        for timestamp in (float("nan"), float("inf"), float("-inf"), "not-a-time", True):
            report = MEMORY.validate_memory_decision(
                {
                    "shared_device_budget": 4096,
                    "pipeline_resident_limit": 2048,
                    "target_chunk_bytes": 1024,
                    "recommended_block_size": 512,
                    "snapshot": MEMORY.MemorySnapshot(8192, 4096, timestamp),
                }
            )
            self.assertFalse(report["valid"], timestamp)
            self.assertIn(
                "snapshot.timestamp must be finite when provided",
                report["issues"],
            )

    def test_legacy_snapshot_mapping_without_timestamp_remains_compatible(self):
        """Old JSON snapshots may omit optional freshness metadata."""

        report = MEMORY.validate_memory_decision(
            {
                "shared_device_budget": 4096,
                "pipeline_resident_limit": 2048,
                "target_chunk_bytes": 1024,
                "recommended_block_size": 512,
                "snapshot": {"total_bytes": 8192, "available_bytes": 4096},
            }
        )
        self.assertTrue(report["valid"], report)

    def test_mapping_adapters_are_accepted_without_dict_coercion(self):
        """JSON adapters exposing Mapping must retain the public contract."""

        report = MEMORY.validate_memory_decision(
            UserDict(
                {
                    "shared_device_budget": 4096,
                    "pipeline_resident_limit": 2048,
                    "target_chunk_bytes": 1024,
                    "recommended_block_size": 512,
                    "snapshot": UserDict(
                        {"total_bytes": 8192, "available_bytes": 4096}
                    ),
                }
            )
        )
        self.assertTrue(report["valid"], report)


if __name__ == "__main__":
    unittest.main()
