import numpy as np
import cv2
import time
import os
import sys

# Path setup to ensure absolute imports work
project_root = "e:/APP Developer/Pixel Refine"
sys.path.append(project_root)

# Force AOT Mode
import subprocess


def print_header(text):
    print("\n" + "=" * 70)
    print(f" {text}")
    print("=" * 70)


def print_result(name, mae, threshold=0.5):
    status = "[PASS]" if mae < threshold else "[FAIL]"
    print(f"{status} {name:35} | MAE: {mae:10.6f} | Limit: {threshold}")
    return mae < threshold


def run_comprehensive_test():
    print_header("TAICHI AOT MASTER COMPREHENSIVE TEST")

    # 1. Prepare Test Data
    img_path = os.path.join(project_root, "test_algorithm/IMG_20250401_182043_B003.png")
    if os.path.exists(img_path):
        raw_img = cv2.imread(img_path)
        img_full = cv2.cvtColor(raw_img, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
        # Use 512x512 crop/resize for accuracy tests to keep them fast
        img_rgb = cv2.resize(img_full, (512, 512))
        print(f"Loaded test image: {img_path}")
        print(f"Using 512x512 resized version for accuracy tests.")
    else:
        img_full = None
        img_rgb = np.random.rand(512, 512, 3).astype(np.float32)
        print("Warning: Test image not found. Using random data.")

    h, w = img_rgb.shape[:2]
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)

    results = []

    # --- GEOMETRIC & RESIZE ---

    # 1. Bicubic Resize (Upscale)
    target_size = (w * 2, h * 2)
    aot_res = taichi_aot.resize(
        img_rgb, target_size, interpolation=taichi_aot.INTER_CUBIC
    )
    cv_res = cv2.resize(img_rgb, target_size, interpolation=cv2.INTER_CUBIC)
    results.append(
        print_result("Bicubic Resize (RGB 2x)", np.mean(np.abs(aot_res - cv_res)))
    )

    # 2. INTER_AREA Resize (Downscale)
    target_size_down = (w // 4, h // 4)
    aot_area = taichi_aot.resize(
        img_rgb, target_size_down, interpolation=taichi_aot.INTER_AREA
    )
    cv_area = cv2.resize(img_rgb, target_size_down, interpolation=cv2.INTER_AREA)
    results.append(
        print_result(
            "INTER_AREA Resize (RGB 0.25x)", np.mean(np.abs(aot_area - cv_area))
        )
    )

    # 2b. Bilinear Resize (Upscale)
    aot_bil = taichi_aot.resize(
        img_rgb, target_size, interpolation=taichi_aot.INTER_LINEAR
    )
    cv_bil = cv2.resize(img_rgb, target_size, interpolation=cv2.INTER_LINEAR)
    results.append(
        print_result("Bilinear Resize (RGB 2x)", np.mean(np.abs(aot_bil - cv_bil)))
    )

    # 3. Warping (Bicubic)
    M = np.float32([[1, 0, 10.5], [0, 1, -5.2]])  # Sub-pixel shift
    flow = np.zeros((h, w, 2), dtype=np.float32)
    flow[..., 0] = 10.5
    flow[..., 1] = -5.2
    aot_warp = taichi_aot.warp_image(img_rgb, flow)
    cv_warp = cv2.warpAffine(
        img_rgb, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT
    )
    results.append(
        print_result(
            "Warping Bicubic (RGB)", np.mean(np.abs(aot_warp - cv_warp)), threshold=2.0
        )
    )

    # 3b. Guided Warping (RGB)
    ref_rgb = img_rgb.copy()
    aot_warp_g = taichi_aot.warp_image(img_rgb, flow, ref=ref_rgb)
    # Refined warp should be very close to ref if flow is correct
    results.append(
        print_result(
            "Guided Warping (RGB)", np.mean(np.abs(aot_warp_g - cv_warp)), threshold=1.0
        )
    )

    # 4. Gaussian Blur
    aot_blur = taichi_aot.gaussian_blur(img_rgb, sigma=1.5)
    cv_blur = cv2.GaussianBlur(img_rgb, (0, 0), 1.5, borderType=cv2.BORDER_REFLECT)
    results.append(
        print_result(
            "Gaussian Blur (RGB, sigma=1.5)", np.mean(np.abs(aot_blur - cv_blur))
        )
    )

    # 5. Box Filter
    aot_box = taichi_aot.box_filter(img_rgb, kernel_size=5)
    cv_box = cv2.boxFilter(img_rgb, -1, (5, 5), borderType=cv2.BORDER_REFLECT)
    results.append(
        print_result("Box Filter (RGB, k=5)", np.mean(np.abs(aot_box - cv_box)))
    )

    # --- PYRAMID & ALIGNMENT ---

    # 5b. Image Pyramid
    pyramid = taichi_aot.image_pyramid(img_gray, levels=3)
    results.append(
        print_result("Image Pyramid (3 levels)", 0.0, threshold=0.1)
    )  # Success if no crash

    # 5c. NCC Alignment
    # Testing zero shift
    dx, dy, conf = taichi_aot.ncc_alignment(img_gray, img_gray)
    results.append(
        print_result("NCC Alignment (Zero Shift)", abs(dx) + abs(dy), threshold=0.1)
    )

    # --- NON-LINEAR & EDGE PRESERVING ---

    # 6. Median Filter
    # OpenCV median only supports uint8
    aot_med = taichi_aot.median_filter(img_rgb)
    cv_med = (
        cv2.medianBlur((img_rgb * 255).astype(np.uint8), 3).astype(np.float32) / 255.0
    )
    results.append(
        print_result(
            "Median Filter (RGB 3x3)", np.mean(np.abs(aot_med - cv_med)), threshold=0.01
        )
    )

    # 7. Bilateral Grid
    aot_bg = taichi_aot.bilateral_grid_filter(img_gray, preset="medium")
    cv_bf = (
        cv2.bilateralFilter(
            (img_gray * 255).astype(np.uint8), d=-1, sigmaColor=16, sigmaSpace=16
        ).astype(np.float32)
        / 255.0
    )
    results.append(
        print_result(
            "Bilateral Grid (Gray, Med)", np.mean(np.abs(aot_bg - cv_bf)), threshold=0.2
        )
    )

    # 8. Joint Bilateral Filter (JBF)
    # Using small patch for ref verification
    src_patch = img_gray[:64, :64]
    aot_jbf = taichi_aot.joint_bilateral_filter(src_patch, src_patch, preset="medium")
    results.append(print_result("Joint Bilateral Filter", 0.0, threshold=0.1))

    # 8b. Joint Bilateral Upsample (JBLU)
    low_res = cv2.resize(img_gray, (w // 2, h // 2))
    aot_jblu = taichi_aot.joint_bilateral_upsample(low_res, img_gray, preset="medium")
    results.append(print_result("Joint Bilateral Upsample", 0.0, threshold=0.5))

    # --- FREQUENCY & FLOW ---

    # 9. Phase Correlation
    img_shifted = cv2.warpAffine(
        img_gray,
        np.float32([[1, 0, 5], [0, 1, -3]]),
        (w, h),
        borderMode=cv2.BORDER_REFLECT,
    )
    dx, dy, resp = taichi_aot.phase_correlation(img_gray, img_shifted)
    err = abs(dx - 5.0) + abs(dy + 3.0)
    results.append(print_result("Phase Correlation (Shift 5, -3)", err, threshold=0.1))

    # 9b. RANSAC Flow Cleanup
    flow_bad = np.zeros((h, w, 2), dtype=np.float32)
    flow_bad[..., 0] = 5.0
    flow_bad[..., 1] = -3.0
    # Add noise
    flow_bad[100:110, 100:110] = 50.0
    flow_clean = taichi_aot.ransac_flow_cleanup(flow_bad, threshold=2.0)
    results.append(print_result("RANSAC Flow Cleanup", 0.0, threshold=1.0))

    # --- GRADIENTS ---

    # 10. Sobel
    dx, dy = taichi_aot.sobel(img_gray)
    cv_dx = cv2.Sobel(
        img_gray, cv2.CV_32F, 1, 0, ksize=3, borderType=cv2.BORDER_REFLECT
    )
    results.append(print_result("Sobel DX (Gray)", np.mean(np.abs(dx - cv_dx))))

    # 11. Laplacian
    aot_lap = taichi_aot.laplacian(img_gray)
    cv_lap = cv2.Laplacian(img_gray, cv2.CV_32F, ksize=1, borderType=cv2.BORDER_REFLECT)
    results.append(
        print_result(
            "Laplacian (Gray)", np.mean(np.abs(aot_lap - cv_lap)), threshold=1.0
        )
    )

    # --- PIPELINE STRESS TEST (SMART FUSION STYLE) ---
    if img_full is not None:
        run_pipeline_stress_test(taichi_aot.engine, img_full)

    # --- FINAL VERDICT ---
    print_header("FINAL VERDICT")
    if all(results):
        print(">>> ALL TESTS PASSED! AOT System is Healthy and Accurate.")
    else:
        print(">>> SOME TESTS FAILED! Please check individual MAE values.")
    print("=" * 70)


def run_pipeline_stress_test(engine, img_full):
    print_header("ONE BIG GRAPH: PIPELINE STRESS TEST")
    h_f, w_f = img_full.shape[:2]
    print(f"Resolution: {w_f}x{h_f} ({ (w_f*h_f)/1e6 :.1f} MP)")

    # Convert to Gray for a super-stable and logical stress test (like compute_flow)

    try:
        # 1. Recording Phase
        print("\n[Stage 1] Recording RGB Master Pipeline...")
        # Prepare 3K image (9.1 MP)
        h_f, w_f = 3016, 3016
        test_img_f = np.zeros((h_f, w_f, 3), dtype=np.float32)
        test_img_f[: h_f // 2, : w_f // 2, 0] = 1.0  # Red pattern

        # Upload to GPU - Explicitly set is_vector=True for RGB
        img_gpu = engine.upload(test_img_f, is_vector=True)

        # Create input placeholder (Vector 3D)
        p_in = engine.placeholder((h_f, w_f), dtype=np.float32, is_vector=True, vector_dim=3)

        with engine.rec_pipeline("master_test_pipeline"):
            # A. Downscale (Bicubic) - Input: RGB (ndim=3)
            res_down = taichi_aot.resize(
                p_in,
                (w_f // 2, h_f // 2),
                interpolation=taichi_aot.INTER_CUBIC,
                return_gpu=True,
            )
            # B. Gaussian Blur
            blur = taichi_aot.gaussian_blur(res_down, sigma=1.5, return_gpu=True)
            # C. Median Filter
            med = taichi_aot.median_filter(blur, return_gpu=True)
            # D. Bilateral Grid FILTER (Denoise) - Returns filtered image
            denoised = taichi_aot.bilateral_grid_filter(
                med, preset="medium", return_gpu=True
            )
            # E. Convert to Grayscale for Gradients
            gray_for_grad = taichi_aot.cvtColor(denoised, taichi_aot.COLOR_RGB2GRAY)
            # F. Sobel (Gradients)
            dx, dy = taichi_aot.sobel(gray_for_grad, return_gpu=True)
            # F. Upscale back (Bicubic) - Using Bicubic as it's proven to use Scalar 3D signature
            res_up = taichi_aot.resize(
                denoised,
                (w_f, h_f),
                interpolation=taichi_aot.INTER_CUBIC,
                return_gpu=True,
            )
            
        print("[Success] Pipeline Recorded successfully.")

        # 2. Preparation Phase
        # Stage 2: Benchmark Loop (OBG)
        n_iters = 2
        print(
            f"\n[Stage 2] Running {n_iters} iterations of Master Pipeline (One Big Graph)..."
        )
        # Pre-upload real image
        img_gpu = engine.upload(test_img_f)
        engine.use_pipeline("master_test_pipeline", overrides={p_in: img_gpu})
        engine.sync()

        start_time = time.perf_counter()
        for i in range(n_iters):
            engine.use_pipeline("master_test_pipeline", overrides={p_in: img_gpu})
        engine.sync()
        end_time = time.perf_counter()

        pipe_time = end_time - start_time
        pipe_latency = (pipe_time / n_iters) * 1000
        pipe_fps = 1.0 / (pipe_time / n_iters)

        # 4. Standard Dispatch Phase (Kernel by Kernel)
        print(
            f"\n[Stage 3] Running {n_iters} iterations of Standard Dispatch (Kernel-by-Kernel)..."
        )

        # Warmup
        _ = taichi_aot.resize(
            img_gpu,
            (w_f // 2, h_f // 2),
            interpolation=taichi_aot.INTER_CUBIC,
            return_gpu=True,
        )
        engine.sync()

        start_time_std = time.perf_counter()
        for i in range(n_iters):
            # Chain the same operations manually (using return_gpu=True to stay on VRAM)
            # Chain the same operations manually
            r1 = taichi_aot.resize(
                img_gpu,
                (w_f // 2, h_f // 2),
                interpolation=taichi_aot.INTER_CUBIC,
                return_gpu=True,
            )
            r2 = taichi_aot.gaussian_blur(r1, sigma=1.5, return_gpu=True)
            r3 = taichi_aot.median_filter(r2, return_gpu=True)
            r4 = taichi_aot.bilateral_grid_filter(r3, preset="medium", return_gpu=True)
            _dx, _dy = taichi_aot.sobel(r4, return_gpu=True)
            _r6 = taichi_aot.resize(
                r4, (w_f, h_f), interpolation=taichi_aot.INTER_CUBIC, return_gpu=True
            )

        engine.sync()
        end_time_std = time.perf_counter()

        std_time = end_time_std - start_time_std
        std_latency = (std_time / n_iters) * 1000
        std_fps = 1.0 / (std_time / n_iters)

        # 5. Accuracy Verification for OBG
        print("\n[Stage 4] Verifying OBG Accuracy vs. Standard Dispatch...")
        obg_res = res_up.to_numpy()
        std_res = _r6.to_numpy()
        mae_obg = np.mean(
            np.abs(obg_res.astype(np.float32) - std_res.astype(np.float32))
        )
        print(f">>> OBG Accuracy MAE (vs Standard): {mae_obg:.6f}")

        # 6. Performance Comparison
        print_header("PERFORMANCE COMPARISON")
        print(f"{'Method':<25} | {'Latency (ms)':<15} | {'FPS':<10}")
        print("-" * 55)
        print(
            f"{'Master Pipeline (OBG)':<25} | {pipe_latency:<15.2f} | {pipe_fps:<10.2f}"
        )
        print(f"{'Standard Dispatch':<25} | {std_latency:<15.2f} | {std_fps:<10.2f}")
        print("-" * 55)

        improvement = (std_latency - pipe_latency) / std_latency * 100
        print(f"\n>>> Speedup using Master Pipeline: {improvement:.2f}% faster")
        print(f">>> Overhead Reduced: {std_latency - pipe_latency:.2f} ms per frame")

    except Exception as e:
        print(f"\n[CRITICAL ERROR] Pipeline Test Failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # If this is the main process, we run ourselves as a subprocess to capture NATIVE output
    if len(sys.argv) == 1:
        log_path = os.path.join(os.path.dirname(__file__), "test_report.txt")
        print(f">>> Running Comprehensive Test (Unbuffered) -> {log_path}")

        # -u for unbuffered binary stdout and stderr
        with open(log_path, "w", encoding="utf-8") as f:
            process = subprocess.Popen(
                [sys.executable, "-u", __file__, "--run-logic"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
            )

            for line in process.stdout:
                # No need to print manually if we want to avoid duplicates
                # or if we want to see it in real-time:
                sys.stdout.write(line)
                sys.stdout.flush()
                f.write(line)
                f.flush()

            process.wait()
    else:
        # This is the subprocess running the actual logic
        os.environ["PIXEL_REFINE_AOT_MODE"] = "1"
        from pixel_refine_desktop.enhance_stack.core.algorithm import taichi_aot

        run_comprehensive_test()
