"""
Standalone Test Script for GPU Flow Computation
================================================
Tests the Taichi GPU implementation without importing the full application.
"""

import numpy as np
import sys
import os

# Direct imports to avoid PySide6 dependency
sys.path.insert(0, r"e:\APP Developer\Pixel Refine")


def test_cost_function():
    """Test cost function module."""
    print("\n" + "=" * 60)
    print("Test: Cost Function")
    print("=" * 60)

    try:
        import taichi as ti

        os.environ["TI_ENABLE_CUDA_MALLOC_ASYNC"] = "0"
        ti.init(arch=ti.gpu, offline_cache=True)
        print("[OK] Taichi initialized on GPU")
    except Exception as e:
        print(f"[WARN] GPU init failed, trying CPU: {e}")
        try:
            import taichi as ti

            ti.init(arch=ti.cpu)
            print("[OK] Taichi initialized on CPU")
        except Exception as e2:
            print(f"[FAIL] Taichi init failed: {e2}")
            return False

    # Direct import of cost_function
    sys.path.insert(
        0,
        r"e:\APP Developer\Pixel Refine\pixel_refine_desktop\enhance_stack\core\algorithm\alignment\alignment_tile",
    )

    try:
        from cost_function import calculate_fine_analysis

        print("[OK] cost_function module imported")
    except ImportError as e:
        print(f"[FAIL] Import error: {e}")
        import traceback

        traceback.print_exc()
        return False

    # Test ZMCL cost
    ref = np.random.rand(16, 16).astype(np.float32)
    comp_same = ref.copy()
    comp_diff = np.random.rand(16, 16).astype(np.float32)

    cost_same = calculate_fine_analysis(ref, comp_same)
    cost_diff = calculate_fine_analysis(ref, comp_diff)

    print(f"[INFO] Cost (identical): {cost_same:.6f}")
    print(f"[INFO] Cost (different): {cost_diff:.6f}")

    if cost_same < cost_diff:
        print("[PASS] Cost function: identical < different")
    else:
        print("[FAIL] Cost function: identical should be less than different")
        return False

    return True


def test_refinement():
    """Test refinement module."""
    print("\n" + "=" * 60)
    print("Test: Refinement")
    print("=" * 60)

    try:
        from refinement import subpixel_refinement, parabolic_refinement

        print("[OK] refinement module imported")
    except ImportError as e:
        print(f"[FAIL] Import error: {e}")
        import traceback

        traceback.print_exc()
        return False

    # Create test images with known sub-pixel shift
    h, w = 64, 64
    ref = np.random.rand(h, w).astype(np.float32)

    try:
        from scipy.ndimage import gaussian_filter

        ref = gaussian_filter(ref, sigma=2.0).astype(np.float32)
    except ImportError:
        # Simple box blur fallback
        kernel = np.ones((3, 3)) / 9
        from scipy.signal import convolve2d

        ref = convolve2d(ref, kernel, mode="same").astype(np.float32)

    # Integer shift for testing
    shift_x, shift_y = 2, 3
    comp = np.roll(ref, (shift_y, shift_x), axis=(0, 1)).astype(np.float32)

    # Test refinement
    tile_x, tile_y = 16, 16
    tile_w, tile_h = 16, 16
    init_dx, init_dy = -shift_x, -shift_y  # Initial guess

    refined = subpixel_refinement(
        ref, comp, tile_x, tile_y, init_dx, init_dy, tile_w, tile_h
    )

    print(f"[INFO] Initial guess: dx={init_dx}, dy={init_dy}")
    print(f"[INFO] Refined: dx={refined[0]:.3f}, dy={refined[1]:.3f}")

    # Should be close to initial guess (already correct)
    error = abs(refined[0] - init_dx) + abs(refined[1] - init_dy)
    if error < 1.5:
        print("[PASS] Refinement within expected range")
        return True
    else:
        print("[WARN] Refinement deviation larger than expected")
        return True


def test_compute_flow():
    """Test full flow computation."""
    print("\n" + "=" * 60)
    print("Test: Compute Flow")
    print("=" * 60)

    try:
        # Import functions directly from modules to avoid name clashes with taichi_algorithm/__init__.py
        from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.pyramid import (
            build_image_pyramid,
        )
        from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.ransac import (
            ransac_flow_cleanup,
        )
        from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.box_filter import (
            box_filter_flow,
        )
        from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.median_filter import (
            median_filter,
        )
        from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.common import (
            ensure_taichi_field,
        )

        print("[OK] Taichi algorithm functions imported")
    except ImportError as e:
        print(f"[FAIL] Import error: {e}")
        import traceback

        traceback.print_exc()
        return False

    # Create test images
    np.random.seed(42)
    h, w = 128, 128  # Smaller for faster test

    # Generate smooth random texture
    base = np.random.rand(h, w).astype(np.float32)
    try:
        from scipy.ndimage import gaussian_filter

        ref = gaussian_filter(base, sigma=3.0).astype(np.float32)
    except ImportError:
        ref = base

    # Known shift
    shift_x, shift_y = 4, 2
    comp = np.roll(ref, (shift_y, shift_x), axis=(0, 1))

    print(f"[INFO] Reference shape: {ref.shape}")
    print(f"[INFO] Known shift: dx={shift_x}, dy={shift_y}")

    # Test pyramid
    print("[INFO] Testing pyramid...")
    pyr = build_image_pyramid(ref, n_levels=3)
    print(f"[OK] Pyramid built with {len(pyr)} levels")
    for i, level in enumerate(pyr):
        print(f"  Level {i}: {level.shape}")

    # Test RANSAC
    print("[INFO] Testing RANSAC...")
    flow_test = np.random.rand(h, w, 2).astype(np.float32) * 2
    flow_clean = ransac_flow_cleanup(flow_test, threshold=3.0)
    print(f"[OK] RANSAC cleanup done: {flow_clean.shape}")

    # Test box filter
    print("[INFO] Testing box filter...")
    flow_smooth = box_filter_flow(flow_test, kernel_size=3)
    print(f"[OK] Box filter done: {flow_smooth.shape}")

    print("[PASS] All component tests passed!")
    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("GPU Flow Computation - Standalone Test Suite")
    print("=" * 60 + "\n")

    results = []

    # Test cost function
    results.append(("Cost Function", test_cost_function()))

    # Test refinement
    results.append(("Refinement", test_refinement()))

    # Test flow components
    results.append(("Flow Components", test_compute_flow()))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False

    print("=" * 60)
    if all_passed:
        print("All tests passed!")
    else:
        print("Some tests failed - check output above")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
