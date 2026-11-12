"""Audit the remaining runtime coupling between taichi_vision and taichi.

Reports:
1. Python imports of ``taichi_vision.taichi_aot`` (absolute).
2. String references to ``taichi_vision/taichi_aot`` or ``taichi_vision\\taichi_aot``.
3. ``spec_from_file_location`` calls whose path targets a file scheduled for removal.
4. Imports of top-level runtime modules scheduled for removal.

Read-only. Exit code 1 when any production (non-test) reference remains, so the
script can be used as a phase gate.
"""

from __future__ import annotations

import ast
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {"venv", "__pycache__", ".git", "build", "backups", ".commandcode",
             ".goals", "artifact_implementation_plan"}

AOT_MODULES = [
    "neural", "neural_engine", "neural_adapters", "onnx_native_graph",
    "fused_mul_clip", "weightnet_gate_fusions", "device_invocation",
    "native_codec_abi", "artifact_cache", "tcm_preflight", "extended",
    "jpeg", "research", "research_pipeline", "compile_engine_native",
    "native_memory_control", "backend_config",
]
TOP_MODULES = [
    "config", "vulkan_probe", "spirv_compatibility", "release_bundle",
    "validate_native_bundle", "native_compression", "native_dng",
    "intel_vulkan_qualification", "llvm20_release_manifest",
    "benchmark_suite", "aot_experiment",
]

AOT_IMPORT_RE = re.compile(r"taichi_vision\.taichi_aot\b")
AOT_PATH_RE = re.compile(r"taichi_vision[\\/]+taichi_aot")
TOP_RE = re.compile(
    r"taichi_vision\.(?:" + "|".join(TOP_MODULES) + r")\b"
)


def iter_python_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name.endswith(".py"):
                yield os.path.join(dirpath, name)


def rel(path: str) -> str:
    return os.path.relpath(path, ROOT).replace("\\", "/")


def is_test(path: str) -> bool:
    parts = rel(path).split("/")
    return "tests" in parts or parts[-1].startswith("test_") or parts[-1].startswith("probe_")


def main() -> int:
    aot_imports: list[tuple[str, int]] = []
    aot_paths: list[tuple[str, int]] = []
    top_imports: list[tuple[str, int]] = []
    spec_targets: list[tuple[str, int, str]] = []

    for path in iter_python_files():
        try:
            source = open(path, "r", encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        try:
            tree = ast.parse(source)
        except SyntaxError:
            tree = None

        if tree is not None:
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    if AOT_IMPORT_RE.search(module):
                        aot_imports.append((rel(path), node.lineno))
                    if TOP_RE.search(module):
                        top_imports.append((rel(path), node.lineno))
                    if node.level == 0 and module == "taichi_vision":
                        for alias in node.names:
                            if alias.name in TOP_MODULES:
                                top_imports.append((rel(path), node.lineno))
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if AOT_IMPORT_RE.search(alias.name):
                            aot_imports.append((rel(path), node.lineno))
                        if TOP_RE.search(alias.name):
                            top_imports.append((rel(path), node.lineno))
                elif isinstance(node, ast.Call):
                    func = node.func
                    name = getattr(func, "attr", None) or getattr(func, "id", None)
                    if name == "spec_from_file_location" and len(node.args) >= 2:
                        literal = node.args[1]
                        if isinstance(literal, ast.Constant) and isinstance(literal.value, str):
                            spec_targets.append((rel(path), node.lineno, literal.value))

        is_audit_tool = rel(path) == "tools/audit_taichi_vision_runtime.py"
        for index, line in enumerate(source.splitlines(), 1):
            if not is_audit_tool and AOT_PATH_RE.search(line):
                aot_paths.append((rel(path), index))

    def production(rows):
        return [row for row in rows if not is_test(row[0])]

    print("== taichi_vision.taichi_aot imports ==")
    print(f"total={len(aot_imports)} production={len(production(aot_imports))}")
    for file, line in production(aot_imports):
        print(f"  {file}:{line}")

    print("== taichi_vision/taichi_aot paths ==")
    print(f"total={len(aot_paths)} production={len(production(aot_paths))}")
    for file, line in production(aot_paths):
        print(f"  {file}:{line}")

    print("== top-level runtime imports ==")
    print(f"total={len(top_imports)} production={len(production(top_imports))}")
    for file, line in production(top_imports):
        print(f"  {file}:{line}")

    print("== spec_from_file_location targets ==")
    for file, line, target in spec_targets:
        if AOT_PATH_RE.search(target) or "aot_artifact" in target or "block.py" in target or "memory.py" in target:
            print(f"  {file}:{line} -> {target}")

    remaining = len(production(aot_imports)) + len(production(aot_paths)) + len(production(top_imports))
    print(f"\nproduction runtime references remaining: {remaining}")
    return 1 if remaining else 0


if __name__ == "__main__":
    sys.exit(main())
