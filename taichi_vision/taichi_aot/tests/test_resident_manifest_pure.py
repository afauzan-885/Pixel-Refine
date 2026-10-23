"""Pure resident-manifest checks; no Taichi, native bridge, or device import."""
import importlib.util
import hashlib
import copy
import json
import tempfile
from pathlib import Path
import unittest
import warnings
import zipfile
from unittest.mock import patch


SOURCE = (
    Path(__file__).resolve().parents[2]
    / "taichi_algorithm"
    / "denoising"
    / "resident_manifest.py"
)
SPEC = importlib.util.spec_from_file_location("resident_manifest_pure", SOURCE)
manifest = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(manifest)


class ResidentManifestTests(unittest.TestCase):
    def setUp(self):
        self.target = {
            "backend": "cpu",
            "arch": "x86_64",
            "os": "windows",
            "abi": "",
            "vendor": "unknown",
            "driver": "test-driver",
            "variant": "",
            "target_id": "cpu_x86_64_windows",
        }
        self.members = {"graphs.tcb": "a" * 64}
        self.weights = b"resident-weights"
        self.metadata = {
            "format": 2,
            "backend": "cpu",
            "model_sha256": "b" * 64,
            "target_identity": dict(self.target),
            "runtime_abi": 1,
            "taichi_version": "test-taichi",
            "device_capabilities": {
                "status": "known",
                "requirements": {"backend": "cpu", "profile": "test-generic"},
            },
            "weights_sha256": hashlib.sha256(self.weights).hexdigest(),
            "opsets": {"ai.onnx": 17},
            "graph": "deno_test_f32_v1",
            "inputs": ["x"],
            "outputs": ["y"],
            "shapes": {"x": [4], "y": [4]},
            "io_schema": {
                "x": {"shape": [4], "dtype": "float32", "layout": "flat-contiguous"},
                "y": {"shape": [4], "dtype": "float32", "layout": "flat-contiguous"},
            },
            "bindings": {"x": "input_0", "y": "output_0"},
            "sizes": {"input_0": 4, "output_0": 4},
            "arguments": ["input_0", "output_0"],
            "constants": [],
            "artifact_members_sha256": dict(self.members),
        }

    def validate(self, metadata=None, **kwargs):
        call = {
            "backend": "cpu",
            "target_identity": self.target,
            "model_sha256": "b" * 64,
            "artifact_members": self.members,
            "weights_sha256": hashlib.sha256(self.weights).hexdigest(),
            "runtime_taichi_version": "test-taichi",
            "runtime_capabilities": {"backend": "cpu", "profile": "test-generic"},
        }
        call.update(kwargs)
        return manifest.validate_resident_metadata(
            self.metadata if metadata is None else metadata, **call
        )

    def test_current_identity_and_content_pass(self):
        self.assertEqual(self.validate(), "current")

    def test_model_target_abi_and_member_mismatch_fail_closed(self):
        with self.assertRaisesRegex(RuntimeError, "selected model"):
            manifest.validate_resident_metadata(
                self.metadata, backend="cpu", target_identity=self.target,
                model_sha256="c" * 64, artifact_members=self.members,
                runtime_taichi_version="test-taichi",
                runtime_capabilities=self.metadata["device_capabilities"]["requirements"],
            )
        wrong_target = dict(self.target, arch="arm64")
        with self.assertRaisesRegex(RuntimeError, "target mismatch"):
            manifest.validate_resident_metadata(
                self.metadata, backend="cpu", target_identity=wrong_target,
                model_sha256="b" * 64, artifact_members=self.members,
                runtime_taichi_version="test-taichi",
                runtime_capabilities=self.metadata["device_capabilities"]["requirements"],
            )
        with self.assertRaisesRegex(RuntimeError, "ABI mismatch"):
            manifest.validate_resident_metadata(
                self.metadata, backend="cpu", target_identity=self.target,
                model_sha256="b" * 64, runtime_abi=2, artifact_members=self.members,
                runtime_taichi_version="test-taichi",
                runtime_capabilities=self.metadata["device_capabilities"]["requirements"],
            )
        with self.assertRaisesRegex(RuntimeError, "member hash mismatch"):
            manifest.validate_resident_metadata(
                self.metadata, backend="cpu", target_identity=self.target,
                model_sha256="b" * 64, artifact_members={"graphs.tcb": "c" * 64},
                runtime_taichi_version="test-taichi",
                runtime_capabilities=self.metadata["device_capabilities"]["requirements"],
            )

    def test_runtime_version_capability_and_unknown_capability_fail_closed(self):
        with self.assertRaisesRegex(RuntimeError, "compiler/runtime version mismatch"):
            self.validate(runtime_taichi_version="different-version")
        with self.assertRaisesRegex(RuntimeError, "device capability mismatch"):
            self.validate(runtime_capabilities={"backend": "cpu", "profile": "other"})
        self.metadata["device_capabilities"] = {"status": "unknown"}
        with self.assertRaisesRegex(RuntimeError, "capability identity is unknown"):
            self.validate()

    def test_schema_shape_dtype_layout_bindings_and_opset_fail_closed(self):
        mutations = [
            ("io_schema", {"x": self.metadata["io_schema"]["x"]}),
            ("shapes", {"x": [3], "y": [4]}),
            ("dtype", None),
            ("layout", None),
            ("bindings", {"x": "missing", "y": "output_0"}),
            ("sizes", {"input_0": True, "output_0": 4}),
            ("opsets", {"ai.onnx": True}),
            ("opsets", {"": 17}),
        ]
        for field, value in mutations:
            with self.subTest(field=field, value=value):
                candidate = copy.deepcopy(self.metadata)
                if field == "dtype":
                    candidate["io_schema"]["x"]["dtype"] = "float16"
                elif field == "layout":
                    candidate["io_schema"]["x"]["layout"] = "strided"
                else:
                    candidate[field] = value
                with self.assertRaises(RuntimeError):
                    self.validate(candidate)

    def test_archive_reader_hashes_payload_and_rejects_corruption(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "resident.tcm"
            weights = b"weight-payload"
            payload = b"compiled-tcm-member"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("resident_onnx.json", json.dumps(self.metadata))
                archive.writestr("resident_weights.npz", weights)
                archive.writestr("graphs.tcb", payload)
            metadata, actual_weights, member_hashes = manifest.read_resident_archive(path)
            self.assertEqual(metadata["format"], 2)
            self.assertEqual(actual_weights, weights)
            self.assertEqual(
                member_hashes["graphs.tcb"], hashlib.sha256(payload).hexdigest()
            )

            duplicate = Path(directory) / "duplicate.tcm"
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                with zipfile.ZipFile(duplicate, "w") as archive:
                    archive.writestr("resident_onnx.json", json.dumps(self.metadata))
                    archive.writestr("resident_weights.npz", weights)
                    archive.writestr("graphs.tcb", payload)
                    archive.writestr("graphs.tcb", b"replacement")
            with self.assertRaisesRegex(RuntimeError, "corrupt resident ONNX"):
                manifest.read_resident_archive(duplicate)

            corrupt = Path(directory) / "corrupt.tcm"
            corrupt.write_bytes(b"not-a-zip")
            with self.assertRaisesRegex(RuntimeError, "corrupt resident ONNX"):
                manifest.read_resident_archive(corrupt)

            duplicate_json = Path(directory) / "duplicate-json.tcm"
            with zipfile.ZipFile(duplicate_json, "w") as archive:
                archive.writestr(
                    "resident_onnx.json", '{"format":2,"format":2}'
                )
                archive.writestr("resident_weights.npz", weights)
            with self.assertRaisesRegex(RuntimeError, "corrupt resident ONNX"):
                manifest.read_resident_archive(duplicate_json)

    def test_configured_runtime_abi_matches_engine_override_policy(self):
        with patch.dict("os.environ", {"AOT_TCM_RUNTIME_ABI": "4"}):
            self.assertEqual(manifest.configured_runtime_abi(1), 4)
        with patch.dict("os.environ", {"AOT_TCM_RUNTIME_ABI": "0"}):
            with self.assertRaisesRegex(RuntimeError, "must be positive"):
                manifest.configured_runtime_abi(1)

    def test_artifact_only_requires_identity_and_legacy_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError, "requires model_sha256"):
            manifest.validate_resident_metadata(
                self.metadata, backend="cpu", target_identity=self.target
            )
        legacy = {"format": 1, "backend": "cpu", "model_sha256": "b" * 64}
        with self.assertRaisesRegex(RuntimeError, "lacks target/ABI integrity"):
            manifest.validate_resident_metadata(
                legacy, backend="cpu", target_identity=self.target,
                artifact_only=True,
            )


if __name__ == "__main__":
    unittest.main()
