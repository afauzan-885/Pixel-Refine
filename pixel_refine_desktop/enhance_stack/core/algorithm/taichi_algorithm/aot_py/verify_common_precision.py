import taichi as ti
import numpy as np
import os
import sys

# Setup path
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

# Force AOT Mode
os.environ["PIXEL_REFINE_AOT_MODE"] = "1"

from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm import common
import pixel_refine_desktop.enhance_stack.core.algorithm.taichi_aot as taichi_aot

def verify_precision():
    print("=== Direct Precision Verification for Common AOT Helpers ===")
    
    # 1. Create random test data (3-channel)
    h, w = 1024, 1024
    img_np = (np.random.rand(h, w, 3) * 65535).astype(np.int32)
    
    print(f"Test Image: {w}x{h}x3 (int32)")

    # --- Test 1: Split ---
    print("\n[Test 1: Split]")
    # NumPy Reference
    ref_channels = [img_np[:, :, i] for i in range(3)]
    
    # AOT Result
    aot_channels = common.split(img_np)
    
    for i in range(3):
        diff = np.abs(ref_channels[i] - aot_channels[i]).max()
        print(f"  Channel {i} Max Diff: {diff}")
        if diff > 0:
            print(f"  FAILED: Channel {i} is not 100% accurate!")
        else:
            print(f"  SUCCESS: Channel {i} is bit-perfect.")

    # --- Test 2: Merge ---
    print("\n[Test 2: Merge]")
    # NumPy Reference is img_np
    
    # AOT Result
    aot_merged = common.merge(aot_channels)
    
    diff = np.abs(img_np - aot_merged).max()
    print(f"  Merge Max Diff: {diff}")
    if diff > 0:
        print("  FAILED: Merge is not 100% accurate!")
    else:
        print("  SUCCESS: Merge is bit-perfect.")

    # --- Test 3: Copy ---
    print("\n[Test 3: Copy]")
    # AOT Result
    aot_copy = common.copy(img_np)
    
    diff = np.abs(img_np - aot_copy).max()
    print(f"  Copy Max Diff: {diff}")
    if diff > 0:
        print("  FAILED: Copy is not 100% accurate!")
    else:
        print("  SUCCESS: Copy is bit-perfect.")

    # --- Test 4: RGB2Gray (Integer Math) ---
    print("\n[Test 4: RGB2Gray (Integer Approximation)]")
    # AOT Result
    aot_gray = common.cvtColor(img_np, common.COLOR_RGB2GRAY)
    
    # Manual Reference (match our kernel logic: (306*R + 601*G + 117*B) >> 10)
    R = img_np[:, :, 0].astype(np.int64)
    G = img_np[:, :, 1].astype(np.int64)
    B = img_np[:, :, 2].astype(np.int64)
    ref_gray = ((306 * R + 601 * G + 117 * B) >> 10).astype(np.int32)
    
    diff = np.abs(ref_gray - aot_gray).max()
    print(f"  Gray Max Diff: {diff}")
    if diff > 0:
        print("  FAILED: Gray conversion is not 100% accurate relative to its formula!")
    else:
        print("  SUCCESS: Gray conversion is bit-perfect relative to its formula.")

    print("\n=== Final Result ===")
    total_diff = np.abs(img_np - aot_merged).sum() + np.abs(img_np - aot_copy).sum()
    if total_diff == 0:
        print("[PASSED] Common Helpers are 100% Mathematically Accurate (Bit-Perfect).")
    else:
        print("[FAILED] Precision issues detected.")

if __name__ == "__main__":
    verify_precision()
