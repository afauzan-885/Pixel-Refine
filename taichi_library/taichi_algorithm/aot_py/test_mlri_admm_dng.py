"""Test MLRI-ADMM Demosaicing - DNG to JPG Output"""
import os
import sys
import time
import numpy as np
import cv2

# Setup project root
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Force AOT mode
os.environ["AOT_MODE"] = "1"
os.environ["PIXEL_REFINE_AOT_DEVICE"] = "0"

from taichi_library import taichi_aot


def test_mlri_admm_dng():
    print("=" * 60)
    print(" MLRI-ADMM Demosaicing Test - DNG to JPG Output")
    print("=" * 60)

    dng_path = os.path.join(project_root, "test_algorithm", "IMG_test.dng")
    output_dir = os.path.join(project_root, "test_algorithm")
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(dng_path):
        print(f"ERROR: DNG file not found: {dng_path}")
        return

    print(f"Input:  {dng_path}")
    print(f"Output: {output_dir}")

    # --- Load RAW ---
    import rawpy
    print("\nLoading RAW file...")
    raw = rawpy.imread(dng_path)
    print(f"  Shape: {raw.raw_image.shape}")
    print(f"  White level: {raw.white_level}")
    print(f"  Black levels: {raw.black_level_per_channel}")

    # --- Run MLRI-ADMM Demosaic ---
    print("\nRunning MLRI-ADMM demosaicing via unified API...")
    t0 = time.perf_counter()
    result = taichi_aot.demosaic(raw, method="mlri-admm")
    elapsed = (time.perf_counter() - t0) * 1000
    print(f"  Completed in {elapsed:.2f} ms")
    print(f"  Output shape: {result.shape}")
    print(f"  Output dtype: {result.dtype}")
    print(f"  Value range: [{result.min():.4f}, {result.max():.4f}]")

    raw.close()

    # --- Convert to uint8 BGR for saving ---
    result_clipped = np.clip(result, 0.0, 1.0)
    result_uint8 = (result_clipped * 255.0 + 0.5).astype(np.uint8)
    result_bgr = cv2.cvtColor(result_uint8, cv2.COLOR_RGB2BGR)

    # --- Save JPG ---
    output_path = os.path.join(output_dir, "mlri_admm_result.jpg")
    cv2.imwrite(output_path, result_bgr, [cv2.IMWRITE_JPEG_QUALITY, 95])
    print(f"\nSaved: {output_path}")
    print(f"  File size: {os.path.getsize(output_path) / 1024:.1f} KB")

    print("\n" + "=" * 60)
    print(" TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    test_mlri_admm_dng()
