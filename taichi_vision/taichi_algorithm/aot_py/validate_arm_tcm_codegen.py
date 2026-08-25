"""Validate ARM CPU TCM kernels through real AArch64 object code generation.

The normal ARM retarget step parses textual LLVM with the Android NDK.  This
companion check goes one step further: LLVM's ``llc`` must lower every kernel
to an AArch64 object file.  It is intentionally a host-side validation; it
does not claim that the Taichi runtime has executed on an ARM device.

Example::

    python validate_arm_tcm_codegen.py --target cpu_arm64_android

The LLVM 20 toolchain is used as the offline validator and must match the
runtime bitcode major. Legacy LLVM14/NDK artifacts are rejected by the ARM
runtime build scripts.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[3]
TCM_ROOT = ROOT / "taichi_vision" / "taichi_algorithm" / "aot_tcm"
TRIPLES = {
    "cpu_arm64_android": "aarch64-unknown-linux-android26",
    "cpu_arm64_linux": "aarch64-unknown-linux-gnu",
}


def _find_llc(explicit: Path | None) -> Path:
    candidates = []
    if explicit:
        candidates.append(explicit)
    env_path = os.environ.get("ARM_LLVM_LLC")
    if env_path:
        candidates.append(Path(env_path))
    # Prefer the repository-pinned LLVM20 toolchain before the historical
    # MSYS2 fallback.  This keeps the offline ARM gate reproducible after
    # MSYS2 is removed from a VS2022-only workstation.
    candidates.append(
        ROOT
        / "test_algorithm"
        / "llvm_msvc_dev_extract"
        / "clang+llvm-20.1.5-x86_64-pc-windows-msvc"
        / "bin"
        / "llc.exe"
    )
    found = shutil.which("llc")
    if found:
        candidates.append(Path(found))
    # Require an explicit LLVM20 path or the pinned repository toolchain on
    # other machines; do not depend on MSYS2 PATH state.
    for candidate in candidates:
        candidate = candidate.expanduser().resolve()
        if candidate.exists():
            return candidate
    raise FileNotFoundError("llc was not found; pass --llc or set ARM_LLVM_LLC")


def _collect(root: Path):
    items = []
    for archive in sorted(root.glob("*.tcm")):
        with zipfile.ZipFile(archive) as z:
            for name in sorted(z.namelist()):
                if name.endswith(".ll"):
                    items.append((archive.name, name, z.read(name)))
    return items


def _validate_arm_ir_metadata(payload: bytes, triple: str) -> None:
    """Reject a retargeted archive that still carries host-only CPU metadata.

    ``llc`` can sometimes lower a module despite stale x86 attributes, which
    would make a green codegen result misleading.  Check the identity before
    lowering so the static gate proves both the target triple and the absence
    of accidental x86/SSE requirements.  AArch64 NEON is baseline, therefore
    an IR module may omit the feature attribute; when it is present it must be
    the retargeted ``+neon`` form.
    """

    text = payload.decode("utf-8", errors="strict")
    if f'target triple = "{triple}"' not in text:
        raise ValueError(f"missing exact ARM target triple {triple!r}")
    if 'target triple = "x86' in text or 'target triple = "i686' in text:
        raise ValueError("host x86 target triple remains in ARM archive")
    lowered = text.lower()
    forbidden = ('"target-cpu"="x86', '"target-cpu"="haswell', "+sse", "+avx")
    if any(token in lowered for token in forbidden):
        raise ValueError("host x86/SSE/AVX CPU feature remains in ARM archive")
    if '"target-features"=' in text and '"target-features"="+neon"' not in text:
        raise ValueError("ARM target-features must be +neon when present")


def _codegen(
    item,
    index: int,
    temp_root: Path,
    llc: Path,
    triple: str,
    opt_level: str,
):
    archive, name, payload = item
    stem = f"{index:05d}"
    ir_path = temp_root / f"{stem}.ll"
    object_path = temp_root / f"{stem}.o"
    try:
        _validate_arm_ir_metadata(payload, triple)
    except Exception as exc:
        return archive, name, -2, str(exc)
    ir_path.write_bytes(payload)
    command = [
        str(llc),
        str(ir_path),
        "-mtriple=" + triple,
        "-O" + opt_level,
        "-filetype=obj",
        "-o",
        str(object_path),
    ]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except Exception as exc:  # pragma: no cover - environment-specific
        return archive, name, -1, repr(exc)
    if result.returncode or not object_path.exists():
        return archive, name, result.returncode, (result.stdout + result.stderr)[-2000:]
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target", choices=sorted(TRIPLES), default="cpu_arm64_android"
    )
    parser.add_argument("--root", type=Path, default=None, help="TCM target directory")
    parser.add_argument("--llc", type=Path, default=None, help="LLVM llc executable")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument(
        "--opt-level",
        choices=("0", "1", "2", "3"),
        default="2",
        help="LLVM lowering optimization level used for validation (default: O2)",
    )
    args = parser.parse_args()

    target_root = (args.root or TCM_ROOT / args.target).resolve()
    if not target_root.is_dir():
        raise SystemExit(f"target directory does not exist: {target_root}")
    llc = _find_llc(args.llc)
    items = _collect(target_root)
    if args.limit > 0:
        items = items[: args.limit]
    if not items:
        raise SystemExit(f"no LLVM kernels found in {target_root}")

    triple = TRIPLES[args.target]
    workers = max(1, min(int(args.workers), 32))
    failures = []
    with tempfile.TemporaryDirectory(prefix="arm-tcm-codegen-") as temp:
        temp_root = Path(temp)
        jobs = [
            (item, index + 1, temp_root, llc, triple, args.opt_level)
            for index, item in enumerate(items)
        ]
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            for result in pool.map(lambda job: _codegen(*job), jobs):
                if result is not None:
                    failures.append(result)

    passed = len(items) - len(failures)
    print(
        f"[ARM codegen] target={args.target} triple={triple} "
        f"llc={llc} kernels={len(items)} pass={passed} fail={len(failures)}"
    )
    for archive, name, code, detail in failures[:10]:
        print(f"[FAIL] {archive}:{name} exit={code}: {detail.strip()}")
    if failures:
        return 1
    print("[PASS] every ARM TCM kernel lowered to an AArch64 object")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
