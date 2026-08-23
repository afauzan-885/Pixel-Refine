"""Create a deterministic checksum manifest for the isolated LLVM20 bundles.

This is a release/checkpoint tool, not a runtime import.  It inventories only
the four Windows target bundles and the isolated LLVM20 venv; build
intermediates remain outside the release payload.  The manifest is used before
cutover and again after extraction to prove that no TCM, bridge, or Python
extension changed silently.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any
import zipfile


DEFAULT_ROOT = Path(r"D:\development_build\taichi_runtime_llvm20")
TARGETS = (
    "cpu_x86_64_windows",
    "cuda_x86_64_windows_nvidia",
    "vulkan_x86_64_windows",
    "opengl_x86_64_windows",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _file_record(root: Path, path: Path) -> dict[str, Any]:
    return {
        "path": path.relative_to(root).as_posix(),
        "size": path.stat().st_size,
        "sha256": _sha256(path),
    }


def _load_build_manifest(root: Path, target: str) -> dict[str, Any]:
    path = root / "manifests" / f"{target}_build.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing target build manifest: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("toolchain", {}).get("llvm") != "20.1.5":
        raise ValueError(f"target {target} is not marked LLVM20.1.5")
    if payload.get("validation", {}).get("llvm15_marker") is not False:
        raise ValueError(f"target {target} has an LLVM15 marker")
    return payload


def build_manifest(
    root: Path = DEFAULT_ROOT,
    *,
    include_venv: bool = True,
    bundle_root: Path | None = None,
    record_root: Path | None = None,
) -> dict[str, Any]:
    root = root.expanduser().resolve()
    bundle_root = (bundle_root or (root / "bundles")).expanduser().resolve()
    record_root = (record_root or root).expanduser().resolve()
    if not record_root.is_dir():
        raise FileNotFoundError(f"manifest record root does not exist: {record_root}")
    bundles: list[dict[str, Any]] = []
    for target in TARGETS:
        bundle = bundle_root / target
        if not bundle.is_dir():
            raise FileNotFoundError(f"missing LLVM20 target bundle: {bundle}")
        build = _load_build_manifest(root, target)
        files = sorted((p for p in bundle.rglob("*") if p.is_file()), key=lambda p: p.as_posix())
        tcm = [p for p in files if p.suffix.lower() == ".tcm"]
        if len(tcm) != 69:
            raise ValueError(f"{target}: expected 69 TCM archives, found {len(tcm)}")
        manifests: list[Path] = []
        for path in tcm:
            with zipfile.ZipFile(path) as archive:
                if "tcm_manifest.json" in archive.namelist():
                    manifests.append(path)
        if len(manifests) != len(tcm):
            raise ValueError(f"{target}: one or more TCM archives lack tcm_manifest.json")
        bundles.append(
            {
                "target": target,
                "status": build.get("status"),
                "toolchain": build.get("toolchain", {}),
                "validation": build.get("validation", {}),
                "file_count": len(files),
                "tcm_count": len(tcm),
                "files": [_file_record(record_root, path) for path in files],
            }
        )

    venv = root / "venv_llvm20"
    venv_files = (
        sorted((p for p in venv.rglob("*") if p.is_file()), key=lambda p: p.as_posix())
        if include_venv and venv.is_dir()
        else []
    )
    return {
        "schema_version": 1,
        "runtime": "taichi_runtime_llvm20",
        "scope": "runtime_payload" if not include_venv else "staging_inventory",
        "record_root": record_root.as_posix(),
        "toolchain": "LLVM 20.1.5 / VS2022 / Python 3.12",
        "status": "production_candidate",
        "llvm15_active": False,
        "target_count": len(bundles),
        "tcm_total": sum(item["tcm_count"] for item in bundles),
        "bundles": bundles,
        "venv_llvm20": {
            "present": bool(venv_files),
            "file_count": len(venv_files),
        "files": [_file_record(record_root, path) for path in venv_files],
        },
        "open_gates": [
            "GUI Average + Block Matching cancellation/window-close behavior",
            "bilateral-grid native tiled qualification; local denoising tiles are qualified",
            "GPU board-power telemetry qualification; bounded peak-memory and concurrency passed",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--payload-only",
        action="store_true",
        help="exclude the candidate venv from the runtime payload manifest",
    )
    parser.add_argument(
        "--bundle-root",
        type=Path,
        help="bundle directory to inventory; defaults to <root>/bundles",
    )
    parser.add_argument(
        "--record-root",
        type=Path,
        help="root used for recorded paths; defaults to --root",
    )
    args = parser.parse_args()
    bundle_root = args.bundle_root
    if bundle_root is not None and not bundle_root.is_absolute():
        bundle_root = args.root / bundle_root
    record_root = args.record_root
    if record_root is not None and not record_root.is_absolute():
        record_root = args.root / record_root
    payload = build_manifest(
        args.root,
        include_venv=not args.payload_only,
        bundle_root=bundle_root,
        record_root=record_root,
    )
    output = args.output or args.root / "RELEASE_MANIFEST.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output.resolve()), "targets": payload["target_count"], "tcm_total": payload["tcm_total"], "venv_files": payload["venv_llvm20"]["file_count"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
