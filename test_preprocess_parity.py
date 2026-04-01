import os
import numpy as np
import taichi as ti

from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_tile.alignment_tile_taichi import (
    AlignmentTileTaichiAOT,
    AlignmentTileTaichiJIT,
)

# Set backend to PRODUCTION for AOT testing
os.environ["PIXEL_REFINE_BACKEND"] = "PRODUCTION"


def test_preprocess_parity():
    print("[Test] Starting Preprocess Parity Test...")

    import cv2
    img_path = r"save_align_image\IMG_20250330_160424_EXP1_2_3_4_5.jpg"
    img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        print(f"[Test] FAILED: Could not load image at {img_path}")
        return
        
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
    print(f"[Test] Loaded image: {img.shape}, dtype={img.dtype}")
    h, w = img.shape[:2]
    work_h, work_w = h // 4, w // 4  # scale down for parity test

    # 2. Initialize Backends
    try:
        aot = AlignmentTileTaichiAOT()
        jit = AlignmentTileTaichiJIT()
    except Exception as e:
        print(f"[Test] FAILED: Could not initialize backends. {e}")
        print("[Test] Note: You must compile the DLL first!")
        return

    # 3. Running Preprocess on Both
    # Case A: is_linear=True (Should apply gamma)
    print("\n[Case A] Preprocessing with is_linear=True...")
    aot.set_reference(img, work_h, work_w, is_linear=True)
    jit.set_reference(img, work_h, work_w, is_linear=True)

    aot_res = aot.ref_work_res.to_numpy()
    jit_res = jit.ref_work_res.to_numpy()

    diff = np.abs(aot_res - jit_res)
    mean_err = np.mean(diff)
    max_err = np.max(diff)

    print(f"  Mean Error: {mean_err:.6e}")
    print(f"  Max Error:  {max_err:.6e}")

    if mean_err < 1e-4:
        print("  [PASS] Case A Parity OK.")
    else:
        print("  [FAIL] Case A Parity Error too high!")

    # Case B: is_linear=False (Should skip gamma)
    print("\n[Case B] Preprocessing with is_linear=False...")
    aot.set_reference(img, work_h, work_w, is_linear=False)
    jit.set_reference(img, work_h, work_w, is_linear=False)

    aot_res_b = aot.ref_work_res.to_numpy()
    jit_res_b = jit.ref_work_res.to_numpy()

    diff_b = np.abs(aot_res_b - jit_res_b)
    mean_err_b = np.mean(diff_b)

    print(f"  Mean Error: {mean_err_b:.6e}")

    if mean_err_b < 1e-6:
        print("  [PASS] Case B Parity OK.")
    else:
        print("  [FAIL] Case B Parity Error too high!")

    # Case C: Quality Parity check (Ensure no double gamma)
    # If is_linear=False, mean should be different from Case A
    if np.mean(aot_res) != np.mean(aot_res_b):
        print("\n[Test] SUCCESS: Gamma logic is correctly conditional.")
    else:
        print(
            "\n[Test] FAILED: Preprocess output is identical for both linear cases (logic error)."
        )


if __name__ == "__main__":
    test_preprocess_parity()
