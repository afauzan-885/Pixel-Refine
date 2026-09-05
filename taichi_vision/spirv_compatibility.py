"""Static portability audit for packed Taichi Vulkan AOT artifacts.

This module is deliberately independent of ``taichi_vision.taichi_aot`` so
it can inspect artifacts without constructing a native runtime. It validates
every embedded SPIR-V module, extracts its declared capabilities/extensions,
and audits graph descriptor pressure before a driver is allowed to dispatch.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import tempfile
import zipfile


AUDIT_SCHEMA = 2
_CAPABILITY_FEATURES = {
    "Float64": "shaderFloat64",
    "Int64": "shaderInt64",
    "Int16": "shaderInt16",
}
_CAPABILITY_RE = re.compile(r"\bOpCapability\s+(\S+)")
_EXTENSION_RE = re.compile(r'\bOpExtension\s+"([^"]+)"')
_LOCAL_SIZE_RE = re.compile(
    r"\bOpExecutionMode\s+\S+\s+LocalSize\s+(\d+)\s+(\d+)\s+(\d+)"
)
_BINDING_RE = re.compile(r"\bOpDecorate\s+(\S+)\s+Binding\s+(\d+)")
_SET_RE = re.compile(r"\bOpDecorate\s+(\S+)\s+DescriptorSet\s+(\d+)")
_VARIABLE_RE = re.compile(
    r"^\s*(\S+)\s*=\s*OpVariable\s+\S+\s+(\S+)(?:\s|$)",
    re.MULTILINE,
)


def _tool(name):
    env_names = {
        "spirv-val": ("SPIRV_VAL", "PIXEL_REFINE_SPIRV_VAL"),
        "spirv-dis": ("SPIRV_DIS", "PIXEL_REFINE_SPIRV_DIS"),
    }.get(name, ())
    candidates = [os.environ.get(env_name) for env_name in env_names]
    candidates.append(shutil.which(name))
    candidates.append(
        str(
            Path(__file__).resolve().parent
            / "taichi_algorithm"
            / "aot_py"
            / "aot_dll"
            / "vulkan"
            / f"{name}.exe"
        )
    )
    vulkan_sdk = os.environ.get("VULKAN_SDK")
    if vulkan_sdk:
        candidates.append(str(Path(vulkan_sdk) / "Bin" / f"{name}.exe"))
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return str(Path(candidate).resolve())
    hint = "/".join(env_names) if env_names else "PATH"
    raise FileNotFoundError(
        f"{name} is required for the Vulkan artifact portability audit; "
        f"set {hint} or install it through the Vulkan SDK"
    )


def _spirv_version(payload):
    if len(payload) < 20:
        raise ValueError("SPIR-V payload is shorter than its five-word header")
    magic, version = struct.unpack_from("<II", payload)
    if magic != 0x07230203:
        raise ValueError(f"Invalid SPIR-V magic 0x{magic:08x}")
    return {
        "word": version,
        "major": (version >> 16) & 0xFF,
        "minor": (version >> 8) & 0xFF,
        "text": f"{(version >> 16) & 0xFF}.{(version >> 8) & 0xFF}",
    }


def _run_tool(command):
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        creationflags=flags,
        check=False,
    )


def _graph_pressure(archive):
    try:
        graphs = json.loads(archive.read("graphs.json"))
    except KeyError:
        return {
            "graph_count": 0,
            "max_ndarray_args": 0,
            "max_total_args": 0,
            "graphs": {},
        }
    details = {}
    max_ndarrays = 0
    max_args = 0
    for entry in graphs:
        name = str(entry.get("key", ""))
        graph_max_ndarrays = 0
        graph_max_args = 0
        for dispatch in entry.get("value", {}).get("dispatches", []):
            args = dispatch.get("symbolic_args", [])
            graph_max_args = max(graph_max_args, len(args))
            graph_max_ndarrays = max(
                graph_max_ndarrays,
                sum(int(arg.get("tag", -1)) == 2 for arg in args),
            )
        details[name] = {
            "max_ndarray_args": graph_max_ndarrays,
            "max_total_args": graph_max_args,
        }
        max_ndarrays = max(max_ndarrays, graph_max_ndarrays)
        max_args = max(max_args, graph_max_args)
    return {
        "graph_count": len(details),
        "max_ndarray_args": max_ndarrays,
        "max_total_args": max_args,
        "graphs": details,
    }


def audit_tcm(path, target_env="vulkan1.1"):
    """Audit one packed module and return a JSON-safe compatibility report."""
    artifact = Path(path).resolve()
    validator = _tool("spirv-val")
    disassembler = _tool("spirv-dis")
    capabilities = set()
    extensions = set()
    versions = set()
    local_sizes = set()
    bindings = set()
    descriptor_sets = set()
    shader_reports = []
    errors = []

    with zipfile.ZipFile(artifact) as archive:
        graph_pressure = _graph_pressure(archive)
        shader_names = sorted(
            name for name in archive.namelist() if name.lower().endswith(".spv")
        )
        with tempfile.TemporaryDirectory(prefix="pixel_refine_spirv_") as temp:
            temp_root = Path(temp)
            for index, name in enumerate(shader_names):
                payload = archive.read(name)
                version = _spirv_version(payload)
                versions.add(version["text"])
                shader_path = temp_root / f"{index}.spv"
                shader_path.write_bytes(payload)
                validation = _run_tool(
                    [validator, "--target-env", target_env, str(shader_path)]
                )
                disassembly = _run_tool([disassembler, str(shader_path)])
                shader_errors = []
                if validation.returncode != 0:
                    shader_errors.append(
                        (validation.stderr or validation.stdout).strip()
                    )
                if disassembly.returncode != 0:
                    shader_errors.append(
                        (disassembly.stderr or disassembly.stdout).strip()
                    )
                    text = ""
                else:
                    text = disassembly.stdout
                shader_caps = sorted(set(_CAPABILITY_RE.findall(text)))
                shader_exts = sorted(set(_EXTENSION_RE.findall(text)))
                shader_local = [
                    tuple(int(value) for value in match)
                    for match in _LOCAL_SIZE_RE.findall(text)
                ]
                binding_map = {
                    symbol: int(value)
                    for symbol, value in _BINDING_RE.findall(text)
                }
                variable_storage = dict(_VARIABLE_RE.findall(text))
                shader_bindings = list(binding_map.values())
                storage_bindings = {
                    binding
                    for symbol, binding in binding_map.items()
                    if variable_storage.get(symbol) == "StorageBuffer"
                }
                uniform_bindings = {
                    binding
                    for symbol, binding in binding_map.items()
                    if variable_storage.get(symbol) == "Uniform"
                }
                uniform_constant_bindings = {
                    binding
                    for symbol, binding in binding_map.items()
                    if variable_storage.get(symbol) == "UniformConstant"
                }
                shader_sets = [
                    int(value) for _symbol, value in _SET_RE.findall(text)
                ]
                capabilities.update(shader_caps)
                extensions.update(shader_exts)
                local_sizes.update(shader_local)
                bindings.update(shader_bindings)
                descriptor_sets.update(shader_sets)
                errors.extend(
                    f"{name}: {message}" for message in shader_errors if message
                )
                shader_reports.append(
                    {
                        "name": name,
                        "spirv_version": version["text"],
                        "capabilities": shader_caps,
                        "extensions": shader_exts,
                        "local_sizes": shader_local,
                        "max_binding": (
                            max(shader_bindings) if shader_bindings else -1
                        ),
                        "binding_count": len(set(shader_bindings)),
                        "storage_buffer_binding_count": len(storage_bindings),
                        "uniform_binding_count": len(uniform_bindings),
                        "uniform_constant_binding_count": len(
                            uniform_constant_bindings
                        ),
                        "descriptor_sets": sorted(set(shader_sets)),
                        "valid": not shader_errors,
                    }
                )

    max_local_invocations = max(
        (x * y * z for x, y, z in local_sizes), default=0
    )
    return {
        "schema": AUDIT_SCHEMA,
        "artifact": artifact.name,
        "target_env": target_env,
        "valid": not errors and bool(shader_reports),
        "shader_count": len(shader_reports),
        "spirv_versions": sorted(versions),
        "capabilities": sorted(capabilities),
        "extensions": sorted(extensions),
        "local_sizes": [list(size) for size in sorted(local_sizes)],
        "max_local_invocations": max_local_invocations,
        "max_binding": max(bindings) if bindings else -1,
        "max_shader_binding_count": max(
            (
                shader["binding_count"]
                for shader in shader_reports
            ),
            default=0,
        ),
        "max_storage_buffer_bindings": max(
            (
                shader["storage_buffer_binding_count"]
                for shader in shader_reports
            ),
            default=0,
        ),
        "max_uniform_bindings": max(
            (shader["uniform_binding_count"] for shader in shader_reports),
            default=0,
        ),
        "descriptor_sets": sorted(descriptor_sets),
        "graph_pressure": graph_pressure,
        "errors": errors,
        "shaders": shader_reports,
    }


def audit_vulkan_inventory(project_root=None, target_env="vulkan1.1"):
    root = Path(project_root or Path(__file__).resolve().parent.parent).resolve()
    artifact_root = (
        root / "taichi_vision" / "taichi_algorithm" / "aot_tcm"
    )
    target_root = artifact_root / "vulkan_x86_64_windows"
    reports = [
        audit_tcm(path, target_env=target_env)
        for path in sorted(
            target_root.glob("*_vulkan_x86_64_windows.tcm"),
            key=lambda item: item.name,
        )
    ]
    capability_counts = Counter(
        capability
        for report in reports
        for capability in report["capabilities"]
    )
    extension_counts = Counter(
        extension
        for report in reports
        for extension in report["extensions"]
    )
    return {
        "schema": AUDIT_SCHEMA,
        "target_env": target_env,
        "valid": bool(reports) and all(report["valid"] for report in reports),
        "artifact_count": len(reports),
        "shader_count": sum(report["shader_count"] for report in reports),
        "spirv_versions": sorted(
            {
                version
                for report in reports
                for version in report["spirv_versions"]
            }
        ),
        "capabilities": dict(sorted(capability_counts.items())),
        "extensions": dict(sorted(extension_counts.items())),
        "max_local_invocations": max(
            (report["max_local_invocations"] for report in reports),
            default=0,
        ),
        "max_binding": max(
            (report["max_binding"] for report in reports), default=-1
        ),
        "max_shader_binding_count": max(
            (
                report["max_shader_binding_count"]
                for report in reports
            ),
            default=0,
        ),
        "max_storage_buffer_bindings": max(
            (
                report["max_storage_buffer_bindings"]
                for report in reports
            ),
            default=0,
        ),
        "max_uniform_bindings": max(
            (report["max_uniform_bindings"] for report in reports),
            default=0,
        ),
        "max_ndarray_args": max(
            (
                report["graph_pressure"]["max_ndarray_args"]
                for report in reports
            ),
            default=0,
        ),
        "errors": [
            error for report in reports for error in report["errors"]
        ],
        "artifacts": reports,
    }


def evaluate_device_compatibility(device, audit, device_capabilities=None):
    """Evaluate static requirements before any AOT pipeline is constructed."""
    reasons = []
    api_text = str((device or {}).get("api_version") or "0.0")
    try:
        api_parts = tuple(int(part) for part in api_text.split(".")[:2])
    except ValueError:
        api_parts = (0, 0)
    if api_parts < (1, 1):
        reasons.append(
            f"Vulkan {api_text} is below the required Vulkan 1.1"
        )
    if not audit.get("valid"):
        reasons.append("SPIR-V inventory validation failed")
    if audit.get("max_local_invocations", 0) > 128:
        # 128 is the Vulkan 1.1 minimum for compute workgroup invocations.
        reasons.append(
            "artifact local size exceeds the portable Vulkan 1.1 minimum"
        )

    device_capabilities = device_capabilities or {}
    features = device_capabilities.get("features", {})
    limits = device_capabilities.get("limits", {})
    required_features = sorted(
        {
            _CAPABILITY_FEATURES[capability]
            for capability in audit.get("capabilities", {})
            if capability in _CAPABILITY_FEATURES
        }
    )
    for feature in required_features:
        if not features.get(feature, False):
            reasons.append(f"device feature {feature} is required but unavailable")
    required_ssbo = int(audit.get("max_storage_buffer_bindings", 0))
    available_ssbo = int(
        limits.get("maxPerStageDescriptorStorageBuffers", 0)
    )
    available_set_ssbo = int(
        limits.get("maxDescriptorSetStorageBuffers", 0)
    )
    if available_ssbo and required_ssbo > available_ssbo:
        reasons.append(
            f"artifact requires {required_ssbo} storage buffers per shader, "
            f"device exposes {available_ssbo}"
        )
    if available_set_ssbo and required_ssbo > available_set_ssbo:
        reasons.append(
            f"artifact requires {required_ssbo} storage buffers per set, "
            f"device exposes {available_set_ssbo}"
        )
    required_invocations = int(audit.get("max_local_invocations", 0))
    available_invocations = int(
        limits.get("maxComputeWorkGroupInvocations", 0)
    )
    if available_invocations and required_invocations > available_invocations:
        reasons.append(
            f"artifact requires {required_invocations} workgroup invocations, "
            f"device exposes {available_invocations}"
        )

    return {
        "compatible": not reasons,
        "reasons": reasons,
        "minimum_vulkan": "1.1",
        "required_features": required_features,
        "max_local_invocations": int(
            audit.get("max_local_invocations", 0)
        ),
        "max_shader_binding_count": int(
            audit.get("max_shader_binding_count", 0)
        ),
        "max_storage_buffer_bindings": int(
            audit.get("max_storage_buffer_bindings", 0)
        ),
        "device_max_storage_buffer_bindings": available_ssbo,
        "device_max_descriptor_set_storage_buffers": available_set_ssbo,
        "device_max_compute_workgroup_invocations": available_invocations,
        "device_max_storage_buffer_range": int(
            limits.get("maxStorageBufferRange", 0)
        ),
        "max_ndarray_args": int(audit.get("max_ndarray_args", 0)),
    }


def _parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root")
    parser.add_argument("--target-env", default="vulkan1.1")
    parser.add_argument("--summary", action="store_true")
    return parser


def main(argv=None):
    args = _parser().parse_args(argv)
    report = audit_vulkan_inventory(
        project_root=args.project_root, target_env=args.target_env
    )
    if args.summary:
        report = {key: value for key, value in report.items() if key != "artifacts"}
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
