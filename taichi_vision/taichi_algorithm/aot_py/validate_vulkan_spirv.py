"""Offline portability gate for graphics TCM SPIR-V payloads.

TCM archives contain SPIR-V rather than CPU machine code, so the shader binary
is architecture-neutral.  This validator still checks every embedded shader
with ``spirv-val`` before an artifact set is promoted to another Vulkan
profile.  Passing this gate proves binary validity for the selected Vulkan
environment; it does *not* prove driver execution on an Android device.

Example::

    python validate_vulkan_spirv.py --root \
        taichi_vision/taichi_algorithm/aot_tcm/vulkan_x86_64_windows
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
DEFAULT_ROOT = (
    ROOT / "taichi_vision" / "taichi_algorithm" / "aot_tcm" / "vulkan_x86_64_windows"
)


def default_target_env(root: Path) -> str:
    """Select the portable SPIR-V environment from a target directory name.

    OpenGL/GLES payloads in this project are emitted as SPIR-V 1.3; asking
    ``spirv-val`` for ``opengl4.3`` would incorrectly require SPIR-V 1.0.
    An explicit CLI value always overrides this inference.
    """

    name = root.name.lower()
    if name.startswith(("opengl_", "gles_")):
        return "spv1.3"
    if name.startswith("vulkan_"):
        return "vulkan1.1"
    return "vulkan1.1"


def _find_validator(explicit: Path | None) -> Path:
    candidates: list[Path] = []
    if explicit:
        candidates.append(explicit)
    # Keep the historical project variable as an alias while preferring the
    # shorter generic name for new invocations.
    for env_name in ("SPIRV_VAL", "PIXEL_REFINE_SPIRV_VAL"):
        env_path = os.environ.get(env_name)
        if env_path:
            candidates.append(Path(env_path))
    found = shutil.which("spirv-val")
    if found:
        candidates.append(Path(found))
    # Vulkan SDK/cache is the supported Windows validator.  Do not fall back
    # to MSYS2: release validation must be reproducible independently of a
    # Unix compatibility environment.
    candidates.append(
        Path(
            r"C:\Users\BelutGoyang\AppData\Local\ti-build-cache\vulkan-1.3.296.0\Bin\spirv-val.exe"
        )
    )
    for candidate in candidates:
        candidate = candidate.expanduser().resolve()
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        "spirv-val was not found; pass --spirv-val or set SPIRV_VAL "
        "(PIXEL_REFINE_SPIRV_VAL is also supported)"
    )


def _collect(root: Path) -> list[tuple[str, str, bytes]]:
    items: list[tuple[str, str, bytes]] = []
    for archive in sorted(root.glob("*.tcm")):
        with zipfile.ZipFile(archive) as z:
            for name in sorted(z.namelist()):
                # Match the resolver's case-insensitive graphics payload
                # gate.  A TCM producer may preserve an upper-case extension;
                # silently skipping it would under-report the validation set.
                if name.lower().endswith(".spv"):
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
        default=None,
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
    target_env = args.target_env or default_target_env(root)
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
            (item, index + 1, temp_root, validator, target_env)
            for index, item in enumerate(items)
        ]
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            for result in pool.map(lambda job: _validate_one(*job), jobs):
                if result is not None:
                    failures.append(result)

    passed = len(items) - len(failures)
    print(
        f"[SPIR-V] root={root} target_env={target_env} validator={validator} "
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
