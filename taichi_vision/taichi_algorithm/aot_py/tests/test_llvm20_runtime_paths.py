from __future__ import annotations

import tempfile
from pathlib import Path
import unittest
from unittest import mock

from taichi_vision import llvm20_runtime_paths as paths


class LLVM20RuntimePathTests(unittest.TestCase):
    def test_explicit_root_wins_and_resolves_target_tcm(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            bundle = root / "bundles" / "opengl_x86_64_windows"
            tcm = bundle / "tcm" / bundle.name
            tcm.mkdir(parents=True)
            with mock.patch.dict(
                "os.environ",
                {"PIXEL_REFINE_RUNTIME_ROOT": str(root)},
                clear=False,
            ):
                self.assertEqual(paths.runtime_root(), root.resolve())
                self.assertEqual(paths.bundle_root("opengl_x86_64_windows"), bundle.resolve())
                self.assertEqual(paths.tcm_root("opengl_x86_64_windows"), tcm.resolve())

    def test_vendor_probe_can_use_generic_graphics_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            generic = root / "bundles" / "vulkan_x86_64_windows"
            (generic / "tcm" / generic.name).mkdir(parents=True)
            with mock.patch.dict(
                "os.environ",
                {"PIXEL_REFINE_RUNTIME_ROOT": str(root)},
                clear=False,
            ):
                self.assertEqual(
                    paths.bundle_root("vulkan_x86_64_windows_nvidia"), generic.resolve()
                )
                self.assertEqual(
                    paths.tcm_root("vulkan_x86_64_windows_nvidia"),
                    (generic / "tcm" / generic.name).resolve(),
                )

    def test_invalid_explicit_root_fails_closed(self) -> None:
        with mock.patch.dict(
            "os.environ",
            {"PIXEL_REFINE_RUNTIME_ROOT": r"C:\\does-not-exist-pixel-refine"},
            clear=False,
        ):
            with self.assertRaises(RuntimeError):
                paths.runtime_root()

    def test_clean_release_is_preferred_to_development_staging(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            release = root / "release"
            (release / "bundles").mkdir(parents=True)
            (root / "bundles").mkdir(parents=True)
            with mock.patch.object(paths, "LLVM20_STAGING_ROOT", root), mock.patch.object(
                paths, "LLVM20_RELEASE_ROOT", release
            ), mock.patch.dict("os.environ", {}, clear=True):
                self.assertTrue(paths.runtime_root().samefile(release))

    def test_staging_is_fallback_when_release_is_not_ready(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "bundles").mkdir(parents=True)
            release = root / "release"
            with mock.patch.object(paths, "LLVM20_STAGING_ROOT", root), mock.patch.object(
                paths, "LLVM20_RELEASE_ROOT", release
            ), mock.patch.dict("os.environ", {}, clear=True):
                self.assertTrue(paths.runtime_root().samefile(root))


if __name__ == "__main__":
    unittest.main()
