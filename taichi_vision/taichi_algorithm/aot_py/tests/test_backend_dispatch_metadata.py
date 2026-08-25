"""Regression tests for metadata-backed backend dispatch."""

from __future__ import annotations

import unittest

from taichi_vision.taichi_aot.backend_manager import BackendManager
from taichi_vision.taichi_aot.capabilities import (
    backend_candidates,
    classify_device,
)


class BackendDispatchMetadataTests(unittest.TestCase):
    def test_mapping_device_selects_nvidia_order_without_attribute_error(self):
        device = {"name": "Generic Compute Adapter", "vendor": "NVIDIA"}
        self.assertEqual(
            backend_candidates(device),
            ["vulkan", "opengl", "cpu"],
        )

    def test_mapping_vendor_is_used_by_cuda_capability_classification(self):
        capability = classify_device(
            {"name": "Generic Compute Adapter", "vendor": "NVIDIA"},
            "cuda",
        )
        self.assertTrue(capability.safe)
        self.assertEqual(capability.vendor, "nvidia")
        self.assertEqual(capability.device, "Generic Compute Adapter")

    def test_backend_manager_accepts_probe_metadata(self):
        decision = BackendManager(
            device={"name": "Generic Compute Adapter", "vendor": "NVIDIA"},
            validated={"vulkan": "validated", "opengl": "validated"},
        ).decide("auto")
        self.assertEqual(decision.selected, "vulkan")
        self.assertEqual(decision.candidates, ["vulkan", "opengl", "cpu"])


if __name__ == "__main__":
    unittest.main()
