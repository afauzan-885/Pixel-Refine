"""Backend-neutral contract and EWMA planner tests (no native device needed)."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest
import numpy as np


ROOT = Path(__file__).resolve().parents[4]


def _load(relative: str, name: str):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BLOCK = _load("taichi_vision/taichi_aot/block.py", "pixel_refine_contract_block")
PIPELINE = _load(
    "taichi_vision/taichi_aot/auto_pipeline.py",
    "pixel_refine_contract_pipeline",
)
RESIDENCY = _load(
    "taichi_vision/taichi_aot/residency.py",
    "pixel_refine_contract_residency",
)


class ContractTests(unittest.TestCase):
    def test_aliases_resolve_without_changing_capabilities(self):
        self.assertEqual(
            BLOCK.canonical_operation_name("guided_filter_aot"),
            "guided_filter",
        )
        self.assertEqual(
            BLOCK.canonical_operation_name("lucasKanade"),
            "lucas_kanade",
        )
        self.assertEqual(BLOCK.canonical_operation_name("unknown"), "unknown")
        self.assertFalse(BLOCK.can_auto_block("lucasKanade", "cpu"))

    def test_adapter_registration_is_diagnostic_only(self):
        name = "_contract_test_adapter"
        adapter = BLOCK.register_block_adapter(
            name,
            runner=lambda context: context,
            metadata={"source": "unit-test"},
        )
        self.assertEqual(adapter.operation, name)
        self.assertTrue(adapter.ready)
        self.assertFalse(adapter.partition_ready)
        self.assertIs(BLOCK.lookup_block_adapter(name), adapter)
        self.assertIs(BLOCK.get_block_adapter(name), adapter)
        # Registering an adapter must not mutate the strict operation tables.
        self.assertFalse(BLOCK.can_auto_block(name, "cpu"))
        self.assertFalse(BLOCK.can_partition_block(name, "cpu"))
        self.assertIn(name, BLOCK.block_coverage_report("cpu")["adapter_operations"])

    def test_partition_strategy_metadata_is_descriptive_only(self):
        self.assertEqual(
            BLOCK.operation_contract("copy").partition_strategy,
            BLOCK.PartitionStrategy.LOCAL,
        )
        self.assertEqual(
            BLOCK.operation_contract("gaussian_blur").partition_strategy,
            BLOCK.PartitionStrategy.STENCIL,
        )
        self.assertEqual(
            BLOCK.operation_contract("resize").partition_strategy,
            BLOCK.PartitionStrategy.COORDINATE,
        )
        self.assertEqual(
            BLOCK.operation_contract("histogram").partition_strategy,
            BLOCK.PartitionStrategy.MAP_REDUCE,
        )
        # Existing strict contracts are not promoted by metadata alone.
        self.assertFalse(BLOCK.operation_contract("copy").allows_partitioned_block)
        self.assertFalse(BLOCK.can_partition_block("copy", "cpu"))
        invalid = BLOCK.OperationContract(
            "_invalid_partition_strategy",
            partition_strategy="not-a-strategy",
            partition_qualified=True,
        )
        self.assertIsNone(invalid.partition_strategy)
        self.assertFalse(invalid.allows_partitioned_block)

    def test_partition_gate_requires_qualified_adapter_and_parity(self):
        name = "_partition_contract_test"
        contract = BLOCK.OperationContract(
            name,
            shape_transform=BLOCK.ShapeTransform.CHANGING,
            partition_strategy=BLOCK.PartitionStrategy.COORDINATE,
            partition_qualified=True,
            backend_capability={
                "cpu": {"supported": True, "parity": True},
            },
            automatic_safe=False,
            parity_qualified=False,
        )
        BLOCK.register_operation_contract(contract)
        try:
            # A contract can be inspected independently, but runtime
            # partitioning remains fail-closed until a complete adapter exists.
            self.assertTrue(BLOCK.can_partition_block(name, "cpu", require_adapter=False))
            self.assertFalse(BLOCK.can_partition_block(name, "cpu"))

            runner = lambda context: context
            validator = lambda context, result: True
            merger = lambda output, result, block: output
            adapter = BLOCK.register_block_adapter(
                name,
                reader=lambda context, block: context,
                runner=runner,
                validator=validator,
                merger=merger,
                contract=contract,
            )
            self.assertTrue(adapter.partition_ready)
            self.assertTrue(adapter.contract_allows_partition("cpu"))
            self.assertTrue(BLOCK.can_partition_block(name, "cpu"))
            self.assertFalse(BLOCK.can_partition_block(name, "vulkan"))
            # The legacy strict gate remains false for the shape-changing op.
            self.assertFalse(BLOCK.can_auto_block(name, "cpu"))
        finally:
            BLOCK.OPERATION_CONTRACTS.pop(name, None)
            with BLOCK._BLOCK_ADAPTERS_LOCK:
                BLOCK._BLOCK_ADAPTERS.pop(name, None)

    def test_legacy_partition_evidence_only_lists_real_executor_families(self):
        copy_evidence = BLOCK.legacy_partition_evidence("copy", "cpu")
        self.assertEqual(copy_evidence["executor"], "_run_blockwise")
        self.assertEqual(copy_evidence["status"], "executor_only")
        self.assertFalse(copy_evidence["backend_supported"])
        self.assertFalse(copy_evidence["backend_parity_qualified"])

        resize_evidence = BLOCK.legacy_partition_evidence("resize")
        self.assertTrue(resize_evidence["specialized"])
        self.assertEqual(resize_evidence["strategy"], "coordinate")
        self.assertEqual(
            BLOCK.legacy_partition_evidence("dcb_demosaic")["executor"],
            "_demosaic_blockwise",
        )

        # These wrappers currently call a full-frame DCB graph and must not be
        # represented as legacy block evidence merely because they are listed
        # in OPERATION_PATHS.
        self.assertIsNone(BLOCK.legacy_partition_evidence("dcb_demosaic_half_res"))
        self.assertFalse(BLOCK.can_auto_partition_dispatch("dcb_demosaic_half_res", "cpu"))

        snapshot = BLOCK.legacy_partition_evidence()
        self.assertIn("copy", snapshot)
        self.assertIn("lucas_kanade", snapshot)
        self.assertGreaterEqual(len(snapshot), 30)

    def test_legacy_dispatch_requires_fake_full_frame_parity_evidence(self):
        name = "copy"
        contract = BLOCK.OperationContract(
            name,
            partition_strategy=BLOCK.PartitionStrategy.LOCAL,
            partition_qualified=True,
            backend_capability={
                "cpu": {"supported": True, "parity": True},
            },
        )
        source = np.arange(16, dtype="float32").reshape(4, 4)
        full_frame = lambda array: array + 1.0
        tile_runner = lambda tile: tile + 1.0
        adapter = BLOCK.register_block_adapter(
            name,
            reader=lambda context, block: context,
            runner=tile_runner,
            validator=lambda context, result: True,
            merger=lambda output, result, block: output,
            contract=contract,
            backend_capability={"cpu": {"supported": True, "parity": True}},
            metadata={
                "legacy_executor": "_run_blockwise",
                "parity_evidence": {"cpu": True},
            },
        )
        try:
            # The fake tile callback and the full-frame oracle agree, which is
            # the parity evidence represented by the adapter metadata.
            np.testing.assert_array_equal(tile_runner(source), full_frame(source))
            self.assertTrue(adapter.partition_ready)
            self.assertTrue(BLOCK.can_partition_block(name, "cpu"))
            self.assertTrue(BLOCK.can_auto_partition_dispatch(name, "cpu"))
            # An explicit negative proof must override metadata and remain
            # fail-closed.
            self.assertFalse(
                BLOCK.can_auto_partition_dispatch(name, "cpu", parity_evidence=False)
            )
            # Existing automatic behavior is not redirected through this new
            # diagnostic gate.
            self.assertTrue(BLOCK.can_auto_block(name, "cpu"))
        finally:
            with BLOCK._BLOCK_ADAPTERS_LOCK:
                BLOCK._BLOCK_ADAPTERS.pop(name, None)

    def test_coverage_report_exposes_current_baseline_and_target(self):
        report = BLOCK.block_coverage_report("cpu")
        self.assertEqual(report["total_operations"], 109)
        self.assertEqual(report["strict_auto_safe"], 48)
        self.assertEqual(report["target_95_operations"], 104)
        self.assertEqual(report["remaining_to_95"], 56)
        self.assertEqual(report["path_counts"]["global"], 25)
        self.assertEqual(report["path_counts"]["custom"], 15)
        self.assertEqual(report["alias_count"], 15)
        self.assertIn("partition_qualified_operations", report)
        self.assertIn("partition_safe_operations", report)
        self.assertEqual(report["partition_safe_operations"], 0)
        self.assertEqual(report["partition_remaining_to_95"], 104)

    def test_local_contract_is_automatic_safe(self):
        contract = BLOCK.operation_contract("gaussian_blur")
        self.assertTrue(contract.allows_automatic_block)
        self.assertTrue(BLOCK.can_auto_block("gaussian_blur", "vulkan"))

    def test_global_and_shape_changing_contracts_fail_closed(self):
        self.assertFalse(BLOCK.can_auto_block("histogram", "cpu"))
        self.assertFalse(BLOCK.can_auto_block("resize", "cpu"))
        self.assertFalse(BLOCK.can_auto_block("new_operation", "cpu"))

    def test_planner_exposes_bounded_tuning_without_overlap_claim(self):
        telemetry = {"pipeline_resident_limit": 1024, "residency_depth": 3}
        planner = PIPELINE.AutoPipelinePlanner("cpu", lambda: telemetry)
        plan = planner.plan([
            PIPELINE.GraphSpec("a", resident_bytes=100),
            PIPELINE.GraphSpec("b", resident_bytes=100),
        ])
        self.assertEqual(plan.mode, "recorded")
        self.assertGreaterEqual(plan.recommended_block_size, 128)
        self.assertFalse(plan.overlap_verified)
        self.assertEqual(plan.pipeline_depth, 1)

    def test_autotune_pressure_thresholds_remain_ordered(self):
        config = PIPELINE.AutoTuneConfig(
            pressure_reduce_at=0.80,
            pressure_critical_at=0.20,
        )
        self.assertEqual(config.pressure_reduce_at, 0.80)
        self.assertEqual(config.pressure_critical_at, 0.80)

    def test_autotune_block_candidates_are_sorted_and_bounded(self):
        config = PIPELINE.AutoTuneConfig(
            min_block_size=256,
            max_block_size=1024,
            default_block_size=512,
            block_candidates=(4096, 128, 512, 512, 256),
        )
        self.assertEqual(config.block_candidates, (256, 512, 1024))
        self.assertGreaterEqual(config.default_block_size, config.min_block_size)
        self.assertLessEqual(config.default_block_size, config.max_block_size)

    def test_autotune_recommendation_validator_accepts_planner_output(self):
        config = PIPELINE.AutoTuneConfig(
            min_block_size=256, max_block_size=1024, default_block_size=512
        )
        recommendation = PIPELINE.AutoTuneRecommendation(
            block_size=512, pipeline_depth=1, confidence=0.5, samples=3,
            overlap_verified=False,
        )
        report = PIPELINE.validate_autotune_recommendation(recommendation, config)
        self.assertTrue(report["valid"], report)
        self.assertEqual(len(report["checked_fields"]), 5)

    def test_autotune_recommendation_validator_rejects_untrusted_mapping(self):
        config = PIPELINE.AutoTuneConfig(
            min_block_size=256, max_block_size=1024, default_block_size=512
        )
        report = PIPELINE.validate_autotune_recommendation(
            {
                "block_size": 2048,
                "pipeline_depth": 0,
                "confidence": float("nan"),
                "samples": -1,
                "overlap_verified": "yes",
            },
            config,
        )
        self.assertFalse(report["valid"])
        self.assertIn("block_size is not an allowed autotune candidate", report["issues"])
        self.assertIn("pipeline_depth is outside configured bounds", report["issues"])
        self.assertIn("confidence must be finite and in [0, 1]", report["issues"])
        self.assertIn("samples must be non-negative", report["issues"])
        self.assertIn("overlap_verified must be boolean", report["issues"])

    def test_plan_report_explains_segment_residency_and_headroom(self):
        planner = PIPELINE.AutoPipelinePlanner(
            "cpu", lambda: {"pipeline_resident_limit": 150}
        )
        plan = planner.plan([
            PIPELINE.GraphSpec("a", resident_bytes=100),
            PIPELINE.GraphSpec("b", resident_bytes=100),
        ])
        report = plan.as_dict()
        self.assertEqual(report["segment_graph_counts"], [1, 1])
        self.assertEqual(report["segment_resident_bytes"], [100, 100])
        self.assertEqual(report["resident_headroom_bytes"], -50)
        self.assertFalse(report["fits_resident_limit"])

    def test_shape_contract_forces_pipeline_boundary(self):
        planner = PIPELINE.AutoPipelinePlanner("cpu", lambda: {"pipeline_resident_limit": 4096})
        resize = BLOCK.operation_contract("resize")
        plan = planner.plan([
            PIPELINE.GraphSpec("resize", 10, contract=resize),
            PIPELINE.GraphSpec("copy", 10),
        ])
        self.assertEqual(plan.mode, "segmented")
        self.assertEqual(len(plan.segments), 2)

    def test_implicit_graph_names_do_not_record_without_footprint(self):
        planner = PIPELINE.AutoPipelinePlanner("cpu", lambda: {"pipeline_resident_limit": 4096})
        plan = planner.plan(["unknown_graph"])
        self.assertEqual(plan.mode, "direct")
        self.assertIn("metadata is incomplete", plan.reason)

    def test_zero_footprint_graphs_are_segmented(self):
        planner = PIPELINE.AutoPipelinePlanner("cpu", lambda: {"pipeline_resident_limit": 4096})
        plan = planner.plan([PIPELINE.GraphSpec("a"), PIPELINE.GraphSpec("b")])
        self.assertEqual(plan.mode, "segmented")
        self.assertEqual(len(plan.segments), 2)

    def test_resident_fence_blocks_consumer_until_signalled(self):
        ready = [False]
        cache = RESIDENCY.DeviceResidencyCache(1024)
        cache.put("tile", "op", object(), 16, fence_ready=lambda: ready[0])
        with cache.lease("tile") as entry:
            self.assertIsNone(entry)
        ready[0] = True
        with cache.lease("tile") as entry:
            self.assertIsNotNone(entry)

    def test_fence_exception_fails_closed_for_maintenance(self):
        disposed = []

        def fence_raises():
            raise RuntimeError("queue is being torn down")

        cache = RESIDENCY.DeviceResidencyCache(64)
        self.assertIsNotNone(
            cache.put(
                "tile",
                "op",
                object(),
                16,
                dispose=lambda buffer: disposed.append(buffer),
                fence_ready=fence_raises,
            )
        )
        # Fence exceptions must not escape put/clear/invalidate_owner and must
        # never dispose the potentially in-flight native buffer.
        self.assertIsNone(cache.put("replacement", "other", object(), 49))
        self.assertFalse(cache.invalidate("tile"))
        cache.clear()
        self.assertEqual(cache.invalidate_owner("op"), 1)
        self.assertEqual(disposed, [])
        self.assertIsNotNone(cache.peek("tile"))

    def test_residency_invalid_budget_is_fail_closed(self):
        cache = RESIDENCY.DeviceResidencyCache(64)
        self.assertEqual(cache.set_budget(-1), None)
        self.assertEqual(cache.max_bytes, 0)
        self.assertIsNone(cache.put("tile", "op", object(), 1))


if __name__ == "__main__":
    unittest.main()
