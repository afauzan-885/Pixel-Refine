"""
Script kompilasi otomatis taichi_aot menjadi Native C++ Package DLL/PYD menggunakan Nuitka.
Mendukung relative imports antar modul (block.py, memory.py, engine.py, dll.)
"""

import os
import sys
import shutil
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PYTHON_EXE = sys.executable
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "build_native_aot")
TARGET_DIR = os.path.join(PROJECT_ROOT, "taichi_vision", "taichi_aot")

def compile_package_pyd():
    print(f"===========================================================")
    print(f"[AOT NATIVE] MEMULAI KOMPILASI PAKET TAICHI AOT -> NATIVE DLL (.pyd)")
    print(f"Project Root      : {PROJECT_ROOT}")
    print(f"Python Executable : {PYTHON_EXE}")
    print(f"Target Directory  : {TARGET_DIR}")
    print(f"===========================================================\n")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    cmd = [
        PYTHON_EXE,
        "-m", "nuitka",
        "--mode=package",
        "--lto=yes",
        "--output-dir=" + OUTPUT_DIR,
        "--no-pyi-file",
        "--remove-output",
        TARGET_DIR
    ]

    print("Executing command:\n", " ".join(cmd))
    res = subprocess.run(cmd, cwd=PROJECT_ROOT)
    
    if res.returncode != 0:
        print("\n[ERROR] Gagal mengompilasi taichi_aot dengan Nuitka!")
        sys.exit(res.returncode)

    # File hasil build berupa folder taichi_aot.dist atau taichi_aot.cp312-win_amd64.pyd
    for item in os.listdir(OUTPUT_DIR):
        src = os.path.join(OUTPUT_DIR, item)
        if item.endswith((".pyd", ".so")):
            dst = os.path.join(TARGET_DIR, item)
            shutil.copy2(src, dst)
            print(f"[SUCCESS] Berhasil menyalin binary: {dst}")

    print("\n[DONE] KOMPILASI PAKET NATIVE DLL BERHASIL!")

if __name__ == "__main__":
    compile_package_pyd()
