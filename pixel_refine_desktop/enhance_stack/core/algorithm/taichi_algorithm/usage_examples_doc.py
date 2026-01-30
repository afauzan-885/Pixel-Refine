"""
Taichi Algorithm Usage Examples & Documentation
===============================================
This script demonstrates how to use the refactored Taichi Algorithm API.
It covers:
1. Basic Filters (Median, Gaussian, Box)
2. Gradients & Warping (Sobel, Laplacian, Warping)
3. Image Pyramid Construction
4. RANSAC (Optical Flow Outlier Removal)
5. Bilateral Grid (Edge-Preserving Smoothing)
6. Efficient Interpolation (Linear, Nearest, Cubic)

The examples use a unified, OpenCV-like API provided by `taichi_algorithm`.
"""

import os
import sys
import numpy as np
import time

# Ensure the project root is in sys.path for direct execution
project_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../../..")
)
if project_root not in sys.path:
    print(f"[Setup] Added project root to sys.path: {project_root}")
    sys.path.insert(0, project_root)

try:
    import pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm as ta
except ImportError as e:
    print(f"[Error] Could not import taichi_algorithm: {e}")
    sys.exit(1)

import taichi as ti


def benchmark(label, func, *args, **kwargs):
    """
    Run function, print time and FPS.
    Args:
        label: Description of the benchmark.
        func: The function to execute.
        *args, **kwargs: Arguments for the function.
    Returns:
        The result of the function call.
    """
    # Ensure any previous GPU work is done
    try:
        ti.sync()
    except Exception:
        pass

    t0 = time.perf_counter()
    res = func(*args, **kwargs)

    # Sync to correct timer for GPU operations (implicit in to_numpy usually, but explicit is safer for timing)
    try:
        ti.sync()
    except Exception:
        pass
    t1 = time.perf_counter()

    dt = t1 - t0
    fps = 1.0 / dt if dt > 0 else 0.0
    print(f"-> {label:<35}: {dt*1000:7.2f} ms | {fps:7.2f} FPS")
    return res


def example_filters():
    """
    1. Filters
    ==========
    - median: Remove salt-and-pepper noise.
    - gaussian: Smooth images.
    - box: Fast averaging.
    - resize: Resize images (Linear, Nearest, Cubic).
    """
    print("\n===============================================================")
    print(" 1. Basic Filters (RGB & Grayscale)")
    print("===============================================================")

    # Create dummy image (H, W, 3) float32 0..1
    image_rgb = np.random.rand(512, 512, 3).astype(np.float32)
    print(f"Input RGB: {image_rgb.shape}")

    # Median Filter
    benchmark("Median Filter (3x3)", ta.median, image_rgb, ksize=3)

    # Median Filter (Grayscale)
    image_gray = np.random.rand(512, 512).astype(np.float32)
    print(f"\nInput Gray: {image_gray.shape}")
    benchmark("Median Filter (Gray)", ta.median, image_gray, ksize=3)

    # Gaussian Blur
    benchmark("Gaussian Blur (3x3)", ta.gaussian, image_rgb, ksize=(3, 3), sigmaX=2.0)

    # Box Filter (Grayscale)
    benchmark("Box Filter (Gray, k=5)", ta.box, image_gray, ksize=5)


def example_resize_modes():
    """
    Demonstrate resize with different interpolation modes.
    """
    print("\n===============================================================")
    print(" 2. Resize Modes")
    print("===============================================================")

    img = np.random.rand(100, 100, 3).astype(np.float32)
    target_size = (200, 200)
    print(f"Input: {img.shape} -> Target: {target_size}")

    # Linear
    benchmark(
        "Resize (Linear)", ta.resize, img, target_size, interpolation=ta.INTER_LINEAR
    )

    # Nearest
    benchmark(
        "Resize (Nearest)", ta.resize, img, target_size, interpolation=ta.INTER_NEAREST
    )

    # Cubic
    benchmark(
        "Resize (Cubic)", ta.resize, img, target_size, interpolation=ta.INTER_CUBIC
    )


def example_point_sampling():
    """
    Demonstrate point-wise sampling with bicubic and bilinear.
    """
    print("\n===============================================================")
    print(" 3. Point-wise Sampling (Bicubic & Bilinear)")
    print("===============================================================")

    # Create test image
    img_gray = np.random.rand(100, 100).astype(np.float32)
    img_rgb = np.random.rand(100, 100, 3).astype(np.float32)

    print("Scenario: Sample at fractional coordinates")

    # Bicubic sampling (high quality)
    print("\n→ Bicubic Sampling (High Quality):")
    value_bicubic = ta.sample_at_bicubic(img_gray, x=10.5, y=20.3)
    print(f"   Grayscale sample at (10.5, 20.3): {value_bicubic:.4f}")

    green_bicubic = ta.sample_at_bicubic(img_rgb, x=10.5, y=20.3, channel=1)
    print(f"   Green channel sample at (10.5, 20.3): {green_bicubic:.4f}")

    # Bilinear sampling (faster)
    print("\n→ Bilinear Sampling (Faster):")
    value_bilinear = ta.sample_at_bilinear(img_gray, x=10.5, y=20.3)
    print(f"   Grayscale sample at (10.5, 20.3): {value_bilinear:.4f}")

    green_bilinear = ta.sample_at_bilinear(img_rgb, x=10.5, y=20.3, channel=1)
    print(f"   Green channel sample at (10.5, 20.3): {green_bilinear:.4f}")

    print("\nUse Cases:")
    print("   ✓ Bicubic: High-quality warping, subpixel alignment")
    print("   ✓ Bilinear: Real-time processing, fast transforms")


def example_channel_manipulation():
    """
    Demonstrate processing specific channels.
    """
    print("\n===============================================================")
    print(" 3. Channel Manipulation Scenarios")
    print("===============================================================")

    img = np.random.rand(512, 512, 3).astype(np.float32)

    print("Scenario: Edge Detection on GREEN channel only")
    # Extract Green (Index 1) -- simulating manual extraction if API didn't support it,
    # but here we show how to combine results.
    green = img[:, :, 1]

    edges_green = benchmark("Sobel (Green Channel)", ta.sobel, green, 1, 0)
    print(f"   Green Edges X: {edges_green.shape}")

    print("Scenario: Denoise RED channel only")
    red = img[:, :, 0]
    denoised_red = benchmark("Median (Red Channel)", ta.median, red, ksize=3)

    # Recombine (Manual for demo)
    img_processed = img.copy()
    img_processed[:, :, 0] = denoised_red
    print(f"   Combined Image: {img_processed.shape}")


def example_advanced_algorithms():
    """
    Advanced algorithms: Bilateral Grid, RANSAC.
    """
    print("\n===============================================================")
    print(" 4. Advanced Algorithms")
    print("===============================================================")

    # Bilateral Grid
    img = np.random.rand(512, 512, 3).astype(np.float32)
    print("-> Bilateral Filter (Edge-Preserving Smoothing)")
    res_bil = benchmark(
        "Bilateral Grid", ta.bilateral, img, d=16, sigmaColor=0.5, sigmaSpace=2.0
    )
    print(f"   Output: {res_bil.shape}")

    # RANSAC (2-channel flow)
    flow = np.random.randn(256, 256, 2).astype(np.float32)
    # Add some outliers
    flow[100:110, 100:110] += 50.0

    print("\n-> RANSAC (Optical Flow Outlier Removal)")
    print(f"   Input Flow: {flow.shape}")

    # Note: RANSAC might not benefit from simple benchmarking if it's very fast or data dependency
    res_ransac = benchmark("RANSAC Flow", ta.ransac, flow, threshold=2.0)
    print(f"   Output Flow: {res_ransac.shape}")


def run_all_examples():
    """Run all examples to verify functionality."""
    print("Running Taichi Algorithm Usage Examples with Performance Benchmarking...")

    try:
        # Init Taichi once
        import taichi as ti

        ti.init(arch=ti.gpu)  # Auto-detect GPU backend (CUDA/Vulkan/Metal)
    except Exception as e:
        print(f"[Warning] GPU Init failed: {e}. Fallback to CPU.")
        ti.init(arch=ti.cpu)

    print(f"[Taichi] Backend: {ti.cfg.arch}")

    examples = [
        example_filters,
        example_resize_modes,
        example_point_sampling,
        example_channel_manipulation,
        example_advanced_algorithms,
    ]

    for ex in examples:
        try:
            ex()
        except Exception as e:
            print(f"\n[ERROR] {ex.__name__} Failed: {e}")
            import traceback

            traceback.print_exc()

    print("\nExamples run finished.")


if __name__ == "__main__":
    run_all_examples()
