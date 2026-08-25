"""Promote validated desktop Vulkan TCM archives to the ARM64 Android profile.

Vulkan TCM archives contain SPIR-V plus graph metadata and no CPU machine
code.  After ``validate_vulkan_spirv.py`` passes, the same payload is a valid
architecture-neutral candidate for Android Vulkan.  This tool deliberately
does not claim device compatibility: the target manifest remains
``device_execution_pending`` until a real ARM64 Vulkan runtime executes the
artifacts.

Existing files are preserved by default.  Use ``--overwrite`` only after a
new desktop artifact set has passed the SPIR-V gate.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys
import tempfile
import zipfile

try:
    from .validate_vulkan_spirv import _collect, _find_validator, _validate_one
except ImportError:  # direct script execution
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from validate_vulkan_spirv import _collect, _find_validator, _validate_one


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SOURCE = ROOT / "taichi_vision" / "taichi_algorithm" / "aot_tcm" / "vulkan_x86_64_windows"
DEFAULT_OUTPUT = ROOT / "taichi_vision" / "taichi_algorithm" / "aot_tcm" / "vulkan_arm64_android"
REQUIRED_ENTRIES = {"__content__", "__version__", "metadata.json", "graphs.json"}


def _validate_archive_shape(path: Path) -> None:
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
    if not REQUIRED_ENTRIES.issubset(names):
        missing = sorted(REQUIRED_ENTRIES - names)
        raise ValueError(f"{path.name} is missing TCM metadata: {missing}")
    unexpected = [
        name
        for name in names
        if name not in REQUIRED_ENTRIES and not name.endswith(".spv")
    ]
    if unexpected:
        raise ValueError(f"{path.name} contains non-portable payloads: {unexpected[:5]}")
    if not any(name.endswith(".spv") for name in names):
        raise ValueError(f"{path.name} contains no SPIR-V shaders")


def _promote(source: Path, output: Path, overwrite: bool) -> tuple[int, int]:
    output.mkdir(parents=True, exist_ok=True)
    copied = skipped = 0
    for archive in sorted(source.glob("*.tcm")):
        _validate_archive_shape(archive)
        suffix = "_vulkan_x86_64_windows"
        if suffix not in archive.stem:
            raise ValueError(f"unexpected Vulkan source filename: {archive.name}")
        destination = output / (
            archive.stem.rsplit(suffix, 1)[0] + "_vulkan_arm64_android.tcm"
        )
        if destination.exists() and not overwrite:
            skipped += 1
            continue
        with tempfile.NamedTemporaryFile(
            prefix=destination.stem + ".", suffix=".staging.tcm", dir=output, delete=False
        ) as staging:
            staging_path = Path(staging.name)
        try:
            shutil.copyfile(archive, staging_path)
            staging_path.replace(destination)
        finally:
            staging_path.unlink(missing_ok=True)
        copied += 1
    return copied, skipped


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--spirv-val", type=Path, default=None)
    parser.add_argument("--target-env", choices=("vulkan1.0", "vulkan1.1", "vulkan1.2", "vulkan1.3"), default="vulkan1.1")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    source = args.source.resolve()
    output = args.output.resolve()
    if not source.is_dir():
        raise SystemExit(f"Vulkan source directory does not exist: {source}")
    validator = _find_validator(args.spirv_val)
    shaders = _collect(source)
    if not shaders:
        raise SystemExit(f"no SPIR-V shaders found in {source}")

    workers = max(1, min(int(args.workers), 32))
    failures = []
    with tempfile.TemporaryDirectory(prefix="vulkan-promote-validate-") as temp:
        temp_root = Path(temp)
        jobs = [
            (item, index + 1, temp_root, validator, args.target_env)
            for index, item in enumerate(shaders)
        ]
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            for result in pool.map(lambda job: _validate_one(*job), jobs):
                if result is not None:
                    failures.append(result)
    if failures:
        print(f"[FAIL] SPIR-V gate failed for {len(failures)} shader(s)")
        for archive, name, detail in failures[:10]:
            print(f"  {archive}:{name}: {detail}")
        return 1

    copied, skipped = _promote(source, output, args.overwrite)
    print(
        f"[PASS] SPIR-V gate shaders={len(shaders)}; target={output.name}; "
        f"copied={copied} skipped_existing={skipped}; device_execution_pending"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
