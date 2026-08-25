"""Edge-case coverage for backend capability and dispatch policy.

These tests are metadata-only: they do not claim that a backend is physically
available.  They pin the fail-closed decisions used before native resources
are created, including vendor aliases and unsupported CUDA targets.
"""

from __future__ import annotations

import os
import unittest

from taichi_vision.taichi_aot.capabilities import backend_candidates, classify_device


class BackendCapabilityEdgeTests(unittest.TestCase):
    def test_vendor_aliases_do_not_drop_nvidia_policy(self):
        for key in ("vendor_name", "manufacturer"):
            with self.subTest(key=key):
                self.assertEqual(
                    backend_candidates(
                        {"name": "Generic Compute Adapter", key: "NVIDIA Corporation"}
                    ),
                    ["vulkan", "opengl", "cpu"],
                )

    def test_amd_never_advertises_cuda_with_auto_fallback(self):
        previous = os.environ.get("PIXEL_REFINE_AOT_AUTO_FALLBACK")
        os.environ["PIXEL_REFINE_AOT_AUTO_FALLBACK"] = "1"
        try:
            device = {"name": "Radeon Pro Test", "vendor": "AMD"}
            self.assertNotIn("cuda", backend_candidates(device))
            capability = classify_device(device, "cuda")
            self.assertFalse(capability.safe)
            self.assertIn("NVIDIA", capability.reason)
        finally:
            if previous is None:
                os.environ.pop("PIXEL_REFINE_AOT_AUTO_FALLBACK", None)
            else:
                os.environ["PIXEL_REFINE_AOT_AUTO_FALLBACK"] = previous

    def test_nvidia_auto_fallback_can_opt_in_to_cuda(self):
        previous = os.environ.get("PIXEL_REFINE_AOT_AUTO_FALLBACK")
        os.environ["PIXEL_REFINE_AOT_AUTO_FALLBACK"] = "1"
        try:
            self.assertEqual(
                backend_candidates({"name": "GeForce MX150", "vendor": "NVIDIA"}),
                ["cuda", "vulkan", "opengl", "cpu"],
            )
        finally:
            if previous is None:
                os.environ.pop("PIXEL_REFINE_AOT_AUTO_FALLBACK", None)
            else:
                os.environ["PIXEL_REFINE_AOT_AUTO_FALLBACK"] = previous

    def test_unqualified_ada_metadata_is_fail_closed(self):
        capability = classify_device(
            {
                "name": "NVIDIA GeForce RTX Test",
                "vendor": "NVIDIA",
                "compute_capability": "8.9",
            },
            "cuda",
        )
        self.assertFalse(capability.safe)
        self.assertIn("outside the current LLVM20 TCM-lowering candidate set", capability.reason)


if __name__ == "__main__":
    unittest.main()
