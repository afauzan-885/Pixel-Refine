"""Focused tests for strict graphics capability qualification."""

from __future__ import annotations

import unittest

from taichi_vision.taichi_aot.gfx_capabilities import (
    classify_desktop_opengl,
    classify_gles,
    classify_vulkan,
)


class GraphicsCapabilityTests(unittest.TestCase):
    def test_vulkan_requires_compute_and_storage_buffer(self):
        missing_ssbo = classify_vulkan(
            "1.3", features={"compute": True}
        )
        self.assertEqual(missing_ssbo.status, "unsupported")
        self.assertIn("ssbo", missing_ssbo.reason)

        qualified = classify_vulkan(
            "1.3",
            features={"compute": True, "storage_buffer": True},
        )
        self.assertEqual(qualified.status, "native_candidate")

    def test_vulkan_feature_aliases_are_normalized(self):
        qualified = classify_vulkan(
            "1.2",
            features={
                "compute_queue": True,
                "shader-storage-buffer-object": True,
            },
            required_spirv="1.3",
        )
        self.assertEqual(qualified.status, "native_candidate")

    def test_vulkan_custom_feature_floor_remains_available(self):
        # Some non-TCM diagnostic callers only need to ask about a compute
        # queue.  The explicit override preserves that use without weakening
        # the default TCM graphics gate.
        decision = classify_vulkan(
            "1.1",
            features={"compute": True},
            required_features=("compute",),
        )
        self.assertEqual(decision.status, "native_candidate")

    def test_gles_policy_still_requires_ssbo(self):
        decision = classify_gles(
            "3.1",
            compute_shader=True,
            ssbo=False,
        )
        self.assertEqual(decision.status, "unsupported")

    def test_desktop_opengl_legacy_floor_is_fail_closed(self):
        decision = classify_desktop_opengl("2.0")
        self.assertEqual(decision.status, "legacy_render")
        self.assertFalse(decision.usable)

        qualified = classify_desktop_opengl("4.3")
        self.assertEqual(qualified.status, "native_candidate")

    def test_graphics_future_versions_are_not_silently_qualified(self):
        self.assertEqual(
            classify_desktop_opengl("4.7").status,
            "unsupported",
        )
        self.assertEqual(classify_gles("3.3").status, "unsupported")
        self.assertEqual(
            classify_vulkan("1.5", features={"compute": True, "ssbo": True}).status,
            "unsupported",
        )

    def test_vulkan_spirv_future_version_is_fail_closed(self):
        decision = classify_vulkan(
            "1.4",
            features={"compute": True, "ssbo": True},
            required_spirv="1.7",
        )
        self.assertEqual(decision.status, "unsupported")

    def test_driver_version_spellings_are_normalized(self):
        for value in ("1.3.280", "VK_API_VERSION_1_3", "Vulkan-1-3"):
            decision = classify_vulkan(
                value,
                features={"compute": True, "ssbo": True},
                required_spirv="1.3",
            )
            self.assertEqual(decision.status, "native_candidate", value)

    def test_opengl_arb_ssbo_extension_is_recognized(self):
        decision = classify_desktop_opengl(
            "4.2",
            extensions=("GL_ARB_compute_shader", "GL_ARB_shader_storage_buffer_object"),
        )
        # The extension is detected, but the native TCM policy still requires
        # the core 4.3 profile and therefore remains legacy-render only.
        self.assertEqual(decision.status, "legacy_render")


if __name__ == "__main__":
    unittest.main()
