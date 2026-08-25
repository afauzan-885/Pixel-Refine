"""Regression tests for the lazy ``compute_block`` adapter bridge."""

from __future__ import annotations

from types import SimpleNamespace
import unittest

import numpy as np

from taichi_vision.taichi_aot.block import lookup_block_adapter
from taichi_vision.taichi_aot.compute_block import compute_block


class _FakeCpuRuntime:
    arch = "cpu"

    def __init__(self):
        self.last = {}

    def plan_generic_blocks(self, operation, shape, nbytes, **kwargs):
        del operation, shape, nbytes, kwargs
        return SimpleNamespace(block_height=8, block_width=8)

    def set_last_block_execution(self, payload):
        self.last = dict(payload)


class _FakeCudaRuntime(_FakeCpuRuntime):
    arch = "cuda"


class ComputeBlockLazyAdapterTests(unittest.TestCase):
    def test_explicit_operation_registers_and_dispatches_lazily(self):
        runtime = _FakeCpuRuntime()

        @compute_block(
            operation="copy",
            mode="force",
            block_size=8,
            runtime=runtime,
        )
        def copy_operation(image):
            raise AssertionError("same-backend fallback should not be used")

        source = np.arange(33 * 37, dtype=np.float32).reshape(33, 37)
        result = copy_operation(source)

        self.assertTrue(np.array_equal(result, source))
        self.assertIsNotNone(lookup_block_adapter("copy"))
        self.assertTrue(runtime.last.get("selected"))
        self.assertEqual(runtime.last.get("backend"), "cpu")

    def test_unknown_operation_uses_original_same_backend_function(self):
        runtime = _FakeCpuRuntime()

        @compute_block(
            operation="operation_that_does_not_exist",
            mode="force",
            runtime=runtime,
            fallback="full_frame",
        )
        def unknown_operation(image):
            return np.asarray(image) + 1.0

        source = np.zeros((9, 11), dtype=np.float32)
        result = unknown_operation(source)

        self.assertTrue(np.array_equal(result, np.ones_like(source)))
        self.assertFalse(runtime.last.get("selected", False))

    def test_demosaic_configuration_arrays_stay_out_of_image_inputs(self):
        runtime = _FakeCpuRuntime()

        @compute_block(
            operation="mlri_admm_demosaic",
            mode="force",
            block_size=8,
            runtime=runtime,
        )
        def demosaic_operation(image, **kwargs):
            raise AssertionError("bounded adapter should handle the call")

        source = np.arange(16 * 18, dtype=np.float32).reshape(16, 18)
        result = demosaic_operation(
            source,
            iterations=0,
            wb=(1.0, 1.0, 1.0, 1.0),
            levels=(0.0, 1023.0),
            cfa=(0, 1, 2, 3),
            cmatrix=np.eye(3, dtype=np.float32),
        )

        self.assertEqual(result.shape, (16, 18, 3))
        self.assertTrue(np.isfinite(result).all())
        self.assertTrue(runtime.last.get("selected"))

    def test_unsupported_graphics_adapter_recovers_to_same_backend_full_frame(self):
        runtime = _FakeCudaRuntime()

        @compute_block(
            operation="dcb_demosaic",
            mode="force",
            block_size=8,
            runtime=runtime,
            adapter_params={
                "wb": (1.0, 1.0, 1.0, 1.0),
                "levels": (0.0, 1023.0),
                "cfa": (0, 1, 2, 3),
            },
        )
        def dcb_operation(image):
            # This models the native CUDA full-frame route.  The current DCB
            # adapter is CPU-qualified only, so the decorator must not return
            # None or substitute CPU; it must call this original function.
            return np.asarray(image)[..., None] * np.ones((1, 1, 3), dtype=np.float32)

        source = np.arange(16 * 18, dtype=np.float32).reshape(16, 18)
        result = dcb_operation(source)

        self.assertEqual(result.shape, (16, 18, 3))
        self.assertTrue(np.isfinite(result).all())
        self.assertFalse(runtime.last.get("selected", False))


if __name__ == "__main__":
    unittest.main()
