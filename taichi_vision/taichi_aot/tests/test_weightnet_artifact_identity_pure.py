"""Pure model provenance selection for resident WeightNet loader callers."""
import importlib.util
import hashlib
import ast
from pathlib import Path
import tempfile
import unittest
import zipfile


SOURCE = (
    Path(__file__).resolve().parents[2]
    / "taichi_algorithm"
    / "denoising"
    / "weightnet_artifact_identity.py"
)
SPEC = importlib.util.spec_from_file_location("weightnet_identity_pure", SOURCE)
identity = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(identity)


class WeightNetIdentityTests(unittest.TestCase):
    def test_model_bytes_choose_exact_model_bound_hash(self):
        payload = b"selected-weightnet-model"
        self.assertEqual(
            identity.resident_weightnet_load_kwargs(payload),
            {"model_sha256": hashlib.sha256(payload).hexdigest()},
        )

    def test_explicit_artifact_only_has_no_model_provenance(self):
        self.assertEqual(identity.resident_weightnet_load_kwargs(), {"artifact_only": True})

    def test_model_path_and_bundle_member_are_resolved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            model_bytes = b"onnx-payload"
            model = root / "model.onnx"
            model.write_bytes(model_bytes)
            self.assertEqual(
                identity.selected_weightnet_model_bytes(model, 512), model_bytes
            )

            bundle = root / "weightnet_master.bundle"
            with zipfile.ZipFile(bundle, "w") as archive:
                archive.writestr("weightnet_512_gpu_1c_fp32.onnx", model_bytes)
            self.assertEqual(
                identity.selected_weightnet_model_bytes(root, 512, [root]), model_bytes
            )

    def test_existing_bundle_without_selected_profile_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bundle = root / "weightnet_master.bundle"
            with zipfile.ZipFile(bundle, "w") as archive:
                archive.writestr("other.onnx", b"not-the-selected-profile")
            with self.assertRaisesRegex(FileNotFoundError, "model member"):
                identity.selected_weightnet_model_bytes(root, 512, [root])

    def test_missing_explicit_model_source_does_not_downgrade_to_artifact_only(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "selected.onnx"
            with self.assertRaisesRegex(FileNotFoundError, "Selected WeightNet ONNX"):
                identity.selected_weightnet_model_bytes(missing, 512)

    def test_production_residentweightnet_callers_select_identity_mode(self):
        source = (
            Path(__file__).resolve().parents[3]
            / "pixel_refine_desktop"
            / "enhance_stack"
            / "core"
            / "algorithm"
            / "denoising"
            / "fusionet_engine"
            / "weightnet_inference.py"
        )
        tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        calls = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "ResidentWeightNet"
        ]
        self.assertEqual(len(calls), 4)
        for call in calls:
            identity_kwargs = [
                keyword.value for keyword in call.keywords
                if keyword.arg is None
            ]
            self.assertEqual(len(identity_kwargs), 1)
            self.assertIsInstance(identity_kwargs[0], ast.Call)
            self.assertEqual(
                getattr(identity_kwargs[0].func, "id", None),
                "resident_weightnet_load_kwargs",
            )


if __name__ == "__main__":
    unittest.main()
