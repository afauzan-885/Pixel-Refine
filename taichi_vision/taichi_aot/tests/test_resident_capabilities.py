"""Pure checks for resident capability identity; no Taichi/device import."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path

SOURCE = (
    Path(__file__).resolve().parents[2]
    / "taichi_algorithm"
    / "denoising"
    / "resident_capabilities.py"
)
SPEC = importlib.util.spec_from_file_location("resident_capabilities_pure", SOURCE)
caps = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(caps)

_POLICY = "taichi_vision.taichi_aot.capabilities"


class ResidentCapabilitiesTests(unittest.TestCase):
    def test_identity_is_known_and_equals_requirements(self):
        for backend in ("cpu", "cuda", "vulkan", "opengl"):
            ident = caps.capability_identity(backend)
            self.assertEqual(ident["status"], "known")
            self.assertEqual(ident["requirements"], caps.required_capabilities(backend))
            self.assertEqual(ident["requirements"]["backend"], backend)

    def test_backend_names_are_not_interchangeable(self):
        self.assertNotEqual(
            caps.required_capabilities("cuda"), caps.required_capabilities("vulkan")
        )

    def test_runtime_matches_only_when_device_is_admitted(self):
        fake = types.ModuleType(_POLICY)

        class Caps:
            def __init__(self, safe):
                self.safe, self.fp32 = safe, True

        fake.classify_device = lambda device, backend, driver="unknown": Caps(
            safe=device != "quarantined"
        )
        original = sys.modules.get(_POLICY)
        sys.modules[_POLICY] = fake
        try:
            admitted = caps.runtime_capabilities("vulkan", "good-gpu")
            quarantined = caps.runtime_capabilities("vulkan", "quarantined")
        finally:
            if original is not None:
                sys.modules[_POLICY] = original
            else:
                del sys.modules[_POLICY]
        self.assertEqual(admitted, caps.required_capabilities("vulkan"))
        self.assertNotEqual(quarantined, caps.required_capabilities("vulkan"))

    def test_cuda_empty_device_name_defaults_to_nvidia_like_target_detector(self):
        self.assertEqual(
            caps.runtime_capabilities("cuda", ""),
            caps.required_capabilities("cuda"),
        )


if __name__ == "__main__":
    unittest.main()

