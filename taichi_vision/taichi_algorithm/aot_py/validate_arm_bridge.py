"""Validate ARM64 AOT bridge ABI and instruction selection without a device.

This is a static gate, not an Android/Linux runtime claim.  It verifies that
the cross-compiled bridge is an AArch64 ELF, exports the stable C ABI consumed
by :mod:`taichi_aot.engine`, and contains the ARMv8 NEON instructions used by
``ti_cast_buffer``.  Device execution still belongs to the Android/Linux CI
matrix when an ARM runner is available.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[3]
BRIDGE_ROOT = ROOT / "taichi_vision" / "taichi_algorithm" / "aot_py" / "aot_dll"
DEFAULT_TARGETS = (
    "cpu_arm64_android",
    "cpu_arm64_linux",
    "vulkan_arm64_android",
    "gles_arm64_android",
    "opengl_arm64_linux",
    "gles_arm64_linux",
)
REQUIRED_SYMBOLS = {
    "init_aot_engine",
    "destroy_aot_engine",
    "load_aot_module",
    "ti_cast_buffer",
}
NEON_MNEMONICS = re.compile(
    r"\b(?:fmla|fmls|fmul|fcvt(?:zs|zu|as)|sqxtun(?:2)?|uqxtn(?:2)?|ld1|st1)\b",
    re.IGNORECASE,
)
# This module performs ELF/ABI/codegen checks only.  Keep the qualification
# explicit so callers cannot accidentally treat a static pass as device proof.
STATIC_QUALIFICATION = "compile_only"


def _tool(name: str) -> Path:
    from shutil import which

    # The repository-pinned LLVM20 utilities are sufficient for the ELF/ABI
    # checks and are preferred over the historical MSYS2 installation.  This
    # makes MSYS2 optional when the native build is driven by VS2022.
    candidate = (
        ROOT
        / "test_algorithm"
        / "llvm_msvc_dev_extract"
        / "clang+llvm-20.1.5-x86_64-pc-windows-msvc"
        / "bin"
        / f"{name}.exe"
    )
    if candidate.is_file():
        return candidate
    found = which(name)
    if not found:
        raise RuntimeError(f"required LLVM tool not found: {name}")
    return Path(found)


def _run(command: list[str]) -> str:
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    output = result.stdout + result.stderr
    if result.returncode:
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(command)}\n{output}")
    return output


def validate(target: str) -> dict[str, object]:
    bridge = BRIDGE_ROOT / target / "taichi_aot_engine.so"
    if not bridge.is_file():
        raise RuntimeError(f"missing ARM bridge: {bridge}")
    readobj = _tool("llvm-readobj")
    nm = _tool("llvm-nm")
    objdump = _tool("llvm-objdump")

    header = _run([str(readobj), "--file-header", str(bridge)])
    if "elf64-littleaarch64" not in header or "EM_AARCH64" not in header:
        raise RuntimeError(f"{target}: bridge is not ELF AArch64")
    symbols_text = _run([str(nm), "--defined-only", str(bridge)])
    symbols = {
        line.rsplit(" ", 1)[-1].strip()
        for line in symbols_text.splitlines()
        if line.strip()
    }
    missing = sorted(REQUIRED_SYMBOLS - symbols)
    if missing:
        raise RuntimeError(f"{target}: missing exported ABI symbols: {', '.join(missing)}")
    c_api = bridge.parent / "libtaichi_c_api.so"
    c_api_linked = False
    # Android and the cross-built Linux profile both package the matching
    # C-API runtime beside the bridge.  Older Linux bridges were intentionally
    # relocatable, so inspect the ELF NEEDED entry instead of assuming that
    # profile remains external.
    if target.endswith("_android") or target.endswith("_linux"):
        if not c_api.is_file():
            raise RuntimeError(f"{target}: sibling libtaichi_c_api.so is missing")
        c_api_header = _run([str(readobj), "--file-header", str(c_api)])
        if "elf64-littleaarch64" not in c_api_header or "EM_AARCH64" not in c_api_header:
            raise RuntimeError(f"{target}: sibling C API is not ELF AArch64")
        c_api_symbols = _run([str(nm), "-D", "--defined-only", str(c_api)])
        if "ti_get_version" not in c_api_symbols or "ti_create_runtime" not in c_api_symbols:
            raise RuntimeError(f"{target}: sibling C API does not export the stable runtime ABI")
        if target.endswith("_linux"):
            c_api_needed = _run([str(readobj), "--needed-libs", str(c_api)])
            if "libX11" in c_api_needed:
                raise RuntimeError(f"{target}: headless ARM Linux runtime unexpectedly depends on X11")
        dynamic = _run([str(_tool("llvm-objdump")), "-p", str(bridge)])
        if "NEEDED       libtaichi_c_api.so" not in dynamic:
            raise RuntimeError(f"{target}: bridge does not declare libtaichi_c_api.so")
        c_api_linked = True
    disassembly = _run(
        [str(objdump), "-d", "--disassemble-symbols=ti_cast_buffer", str(bridge)]
    )
    neon_hits = sorted(set(NEON_MNEMONICS.findall(disassembly.lower())))
    if not neon_hits:
        raise RuntimeError(f"{target}: ti_cast_buffer has no detectable NEON instructions")
    return {
        "target": target,
        "bridge": str(bridge),
        "bytes": bridge.stat().st_size,
        "symbols": sorted(REQUIRED_SYMBOLS),
        "neon_mnemonics": neon_hits,
        "c_api_linked": c_api_linked,
        # This validator only inspects cross-compiled ELF/ABI properties.  A
        # successful result must never be consumed as proof of execution on
        # an ARM device or driver.
        "qualification": STATIC_QUALIFICATION,
        "native_runtime": False,
        "runtime_evidence_required": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", action="append", choices=DEFAULT_TARGETS)
    args = parser.parse_args()
    targets = tuple(args.target or DEFAULT_TARGETS)
    for target in targets:
        result = validate(target)
        print(
            f"[PASS] {target}: ELF AArch64, {result['bytes']} bytes, "
            f"ABI={len(result['symbols'])}/{len(REQUIRED_SYMBOLS)}, "
            f"NEON={','.join(result['neon_mnemonics'])}, "
            f"C_API={'linked' if result['c_api_linked'] else 'external'}, "
            f"qualification={result['qualification']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
