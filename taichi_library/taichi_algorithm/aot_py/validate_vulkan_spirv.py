"""Offline portability gate for graphics TCM SPIR-V payloads.

TCM archives contain SPIR-V rather than CPU machine code, so the shader binary
is architecture-neutral.  This validator still checks every embedded shader
with ``spirv-val`` before an artifact set is promoted to another Vulkan
profile.  Passing this gate proves binary validity for the selected Vulkan
environment; it does *not* prove driver execution on an Android device.

Example::

    python validate_vulkan_spirv.py --root \
        taichi_library/taichi_algorithm/aot_tcm/vulkan_x86_64_windows
"""

from __future__ import annotations

import argparse
import concurrent.futures
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_ROOT = ROOT / "taichi_library" / "taichi_algorithm" / "aot_tcm" / "vulkan_x86_64_windows"


def _find_validator(explicit: Path | None) -> Path:
    candidates: list[Path] = []
    if explicit:
        candidates.append(explicit)
    env_path = os.environ.get("PIXEL_REFINE_SPIRV_VAL")
    if env_path:
        candidates.append(Path(env_path))
    found = shutil.which("spirv-val")
    if found:
        candidates.append(Path(found))
    candidates.extend(
        [
            Path(r"C:\msys64\ucrt64\bin\spirv-val.exe"),
            Path(r"C:\Users\BelutGoyang\AppData\Local\ti-build-cache\vulkan-1.3.296.0\Bin\spirv-val.exe"),
        ]
    )
    for candidate in candidates:
        candidate = candidate.expanduser().resolve()
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        "spirv-val was not found; pass --spirv-val or set PIXEL_REFINE_SPIRV_VAL"
    )


def _collect(root: Path) -> list[tuple[str, str, bytes]]:
    items: list[tuple[str, str, bytes]] = []
    for archive in sorted(root.glob("*.tcm")):
        with zipfile.ZipFile(archive) as z:
            for name in sorted(z.namelist()):
                if name.endswith(".spv"):
                    items.append((archive.name, name, z.read(name)))
    return items


def _validate_one(
    item: tuple[str, str, bytes],
    index: int,
    temp_root: Path,
    validator: Path,
    target_env: str,
) -> tuple[str, str, str] | None:
    archive, name, payload = item
    shader = temp_root / f"{index:06d}.spv"
    shader.write_bytes(payload)
    result = subprocess.run(
        [str(validator), "--target-env", target_env, str(shader)],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    if result.returncode:
        detail = (result.stdout + result.stderr).strip()[-2000:]
        return archive, name, detail
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--spirv-val", type=Path, default=None)
    parser.add_argument(
        "--target-env",
        default="vulkan1.1",
        choices=(
            "vulkan1.0",
            "vulkan1.1",
            "vulkan1.2",
            "vulkan1.3",
            "opengl4.3",
            "opengl4.5",
            "spv1.3",
        ),
    )
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    root = args.root.resolve()
    if not root.is_dir():
        raise SystemExit(f"TCM target directory does not exist: {root}")
    validator = _find_validator(args.spirv_val)
    items = _collect(root)
    if args.limit > 0:
        items = items[: args.limit]
    if not items:
        raise SystemExit(f"no SPIR-V payloads found in {root}")

    workers = max(1, min(int(args.workers), 32))
    failures: list[tuple[str, str, str]] = []
    with tempfile.TemporaryDirectory(prefix="vulkan-spirv-validate-") as temp:
        temp_root = Path(temp)
        jobs = [
            (item, index + 1, temp_root, validator, args.target_env)
            for index, item in enumerate(items)
        ]
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            for result in pool.map(lambda job: _validate_one(*job), jobs):
                if result is not None:
                    failures.append(result)

    passed = len(items) - len(failures)
    print(
        f"[SPIR-V] root={root} target_env={args.target_env} validator={validator} "
        f"shaders={len(items)} pass={passed} fail={len(failures)}"
    )
    for archive, name, detail in failures[:10]:
        print(f"[FAIL] {archive}:{name}: {detail}")
    if failures:
        return 1
    print("[PASS] every embedded graphics shader passed the SPIR-V portability gate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
