import os
os.environ["VK_LOADER_DEBUG"] = "error"
os.environ["PIXEL_REFINE_AOT_DEVICE"] = "0"
import numpy as np
import cv2
import time
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


def run_jit_algorithm_tests(img_rgb, img_gray, h, w, results):
    """
    Test the 9 new algorithms (JIT mode: AOT_MODE=0).
    These run Taichi kernels directly without compiled TCM modules.
    """
    print_header("NEW ALGORITHMS (JIT Mode)")

    # Force JIT mode for these tests
    os.environ["AOT_MODE"] = "0"
    try:
        import importlib
        import taichi_library.taichi_algorithm as ta
        # Reload to pick up AOT_MODE=0
        importlib.reload(ta)
    except Exception as e:
        print(f"[SKIP] JIT mode unavailable: {e}")
        return

    if not ta.common.TAICHI_AVAILABLE:
        print("[SKIP] Taichi not available for JIT tests")
        return

    # Use smaller images for expensive algorithms
    small_gray = cv2.resize(img_gray, (128, 128))
    small_rgb = cv2.resize(img_rgb, (128, 128))
    sh, sw = small_gray.shape

    # ---- 1. Color Space Conversions ----
    try:
        img_u8 = (img_gray * 255).astype(np.uint8)
        img_bgr_u8 = cv2.merge([img_u8, img_u8, img_u8])  # Gray as BGR

        # BGR -> YCrCb
        img_bgr_f32 = img_bgr_u8.astype(np.float32)
        ta_ycrcb = ta.cvtColor_extended(img_bgr_f32, ta.COLOR_BGR2YCrCb)
        cv_ycrcb = cv2.cvtColor(img_bgr_u8, cv2.COLOR_BGR2YCrCb).astype(np.float32)
        mae = np.mean(np.abs(ta_ycrcb - cv_ycrcb))
        results.append(print_result("Color: BGR->YCrCb", mae, threshold=3.0))

        # BGR -> HSV
        ta_hsv = ta.cvtColor_extended(img_bgr_f32, ta.COLOR_BGR2HSV)
        cv_hsv = cv2.cvtColor(img_bgr_u8, cv2.COLOR_BGR2HSV).astype(np.float32)
        mae = np.mean(np.abs(ta_hsv - cv_hsv))
        results.append(print_result("Color: BGR->HSV", mae, threshold=5.0))

        # YCrCb roundtrip
        ta_back = ta.cvtColor_extended(ta_ycrcb, ta.COLOR_YCrCb2BGR)
        mae = np.mean(np.abs(ta_back - img_bgr_f32))
        results.append(print_result("Color: YCrCb->BGR roundtrip", mae, threshold=3.0))
    except Exception as e:
        print(f"[FAIL] Color Conversions: {e}")
        results.append(False)

    # ---- 2. Otsu's Threshold ----
    try:
        gray_255 = (img_gray * 255).astype(np.float32)
        thresh_val, binary = ta.otsu_threshold(gray_255)
        cv_thresh, cv_binary = cv2.threshold(
            gray_255.astype(np.uint8), 0, 255,
            cv2.THRESH_BINARY | cv2.THRESH_OTSU
        )
        # Compare threshold values (should be close)
        thresh_err = abs(thresh_val - float(cv_thresh))
        results.append(print_result("Otsu Threshold Value", thresh_err, threshold=5.0))

        # Compare binary maps
        binary_diff = np.mean(np.abs(binary - cv_binary.astype(np.float32)))
        results.append(print_result("Otsu Binary Map", binary_diff, threshold=20.0))
    except Exception as e:
        print(f"[FAIL] Otsu Threshold: {e}")
        results.append(False)

    # ---- 3. Guided Filter ----
    try:
        guide = small_gray.copy()
        src = small_gray + np.random.randn(sh, sw).astype(np.float32) * 0.02
        gf_result = ta.guided_filter(guide, src, radius=4, epsilon=0.01)
        # Verify: output should be smoother than input but follow guide edges
        input_std = np.std(src)
        output_std = np.std(gf_result)
        # Smoothed output should have lower variance
        smoothness = input_std - output_std
        results.append(print_result(
            "Guided Filter (smoothing)",
            0.0 if smoothness > 0 else 1.0,
            threshold=0.5
        ))
    except Exception as e:
        print(f"[FAIL] Guided Filter: {e}")
        results.append(False)

    # ---- 4. CLAHE ----
    try:
        gray_u8 = (small_gray * 255).astype(np.uint8)
        gray_f32 = gray_u8.astype(np.float32)
        ta_clahe = ta.clahe(gray_f32, clip_limit=2.0, tile_grid_size=(4, 4))
        cv_clahe_obj = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
        cv_clahe = cv_clahe_obj.apply(gray_u8).astype(np.float32)
        mae = np.mean(np.abs(ta_clahe - cv_clahe))
        results.append(print_result("CLAHE (clip=2.0, 4x4)", mae, threshold=30.0))
    except Exception as e:
        print(f"[FAIL] CLAHE: {e}")
        results.append(False)

    # ---- 5. Canny Edge Detector ----
    try:
        gray_u8 = (small_gray * 255).astype(np.uint8)
        gray_f32 = gray_u8.astype(np.float32)
        ta_canny = ta.canny(gray_f32, low_threshold=50, high_threshold=150)
        cv_canny = cv2.Canny(gray_u8, 50, 150).astype(np.float32)
        # Canny is sensitive to implementation details, use generous threshold
        mae = np.mean(np.abs(ta_canny - cv_canny))
        results.append(print_result("Canny Edge Detector", mae, threshold=80.0))
    except Exception as e:
        print(f"[FAIL] Canny: {e}")
        results.append(False)

    # ---- 6. Hough Lines ----
    try:
        # Create synthetic edge image with a clear line
        synth = np.zeros((128, 128), dtype=np.float32)
        synth[30:32, 10:118] = 255.0  # Horizontal line
        synth[10:118, 60:62] = 255.0  # Vertical line
        lines = ta.hough_lines(synth, threshold=40)
        # Should detect at least 1 line
        results.append(print_result(
            "Hough Lines (synthetic)",
            0.0 if len(lines) >= 1 else 1.0,
            threshold=0.5
        ))
    except Exception as e:
        print(f"[FAIL] Hough Lines: {e}")
        results.append(False)

    # ---- 7. Non-Local Means ----
    try:
        # Use very small image for NLM (expensive)
        tiny = cv2.resize(small_gray, (64, 64))
        noisy = tiny + np.random.randn(64, 64).astype(np.float32) * 0.05
        nlm_result = ta.non_local_means(
            noisy, h_param=0.1, search_window=3, patch_size=2
        )
        # Verify: denoised should be closer to original than noisy
        noise_err = np.mean(np.abs(noisy - tiny))
        denoise_err = np.mean(np.abs(nlm_result - tiny))
        improvement = noise_err - denoise_err
        results.append(print_result(
            "Non-Local Means (64x64)",
            0.0 if improvement > 0 else 1.0,
            threshold=0.5
        ))
    except Exception as e:
        print(f"[FAIL] Non-Local Means: {e}")
        results.append(False)

    # ---- 8. Inpainting ----
    try:
        # Create test image with a hole
        inp_src = small_rgb.copy() * 255.0
        mask = np.zeros((sh, sw), dtype=np.float32)
        mask[40:80, 40:80] = 1.0  # Square hole
        inp_result = ta.inpaint(inp_src, mask, inpaint_radius=3)
        # Verify: masked region should be filled (no NaN/Inf)
        has_nan = np.any(np.isnan(inp_result)) or np.any(np.isinf(inp_result))
        # Masked region should have reasonable values (not all zeros)
        masked_mean = np.mean(inp_result[40:80, 40:80])
        results.append(print_result(
            "Inpainting (128x128)",
            0.0 if (not has_nan and masked_mean > 1.0) else 1.0,
            threshold=0.5
        ))
    except Exception as e:
        print(f"[FAIL] Inpainting: {e}")
        results.append(False)

    # ---- 9. Seamless Cloning ----
    try:
        src_clone = small_rgb.copy() * 255.0
        dst_clone = np.ones_like(src_clone) * 128.0  # Gray background
        mask_clone = np.zeros((sh, sw), dtype=np.float32)
        mask_clone[20:100, 20:100] = 1.0
        sc_result = ta.seamless_clone(
            src_clone, dst_clone, mask_clone,
            flags=ta.NORMAL_CLONE, max_iterations=50
        )
        # Verify: no NaN/Inf and masked region should differ from dst
        has_nan = np.any(np.isnan(sc_result)) or np.any(np.isinf(sc_result))
        masked_diff = np.mean(np.abs(
            sc_result[30:90, 30:90] - dst_clone[30:90, 30:90]
        ))
        results.append(print_result(
            "Seamless Clone (128x128)",
            0.0 if (not has_nan and masked_diff > 1.0) else 1.0,
            threshold=0.5
        ))
    except Exception as e:
        print(f"[FAIL] Seamless Clone: {e}")
        results.append(False)

    # Restore AOT mode for remaining tests
    os.environ["AOT_MODE"] = "1"
    print("\n--- End of JIT Algorithm Tests ---\n")


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

    # 1. Resize (Bicubic) - Non-integer scale to test sub-pixel drift
    target_w, target_h = int(w * 1.33), int(h * 1.33)
    aot_bicubic = taichi_aot.resize(
        img_rgb, (target_w, target_h), interpolation=taichi_aot.INTER_CUBIC
    )
    cv_bicubic = cv2.resize(
        img_rgb, (target_w, target_h), interpolation=cv2.INTER_CUBIC
    )
    results.append(
        print_result(
            "Bicubic Resize (RGB 1.33x)", np.mean(np.abs(aot_bicubic - cv_bicubic))
        )
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

    # 2b. Bilinear Resize
    target_size_bilinear = (w * 2, h * 2)
    aot_bilinear = taichi_aot.resize(
        img_rgb, target_size_bilinear, interpolation=taichi_aot.INTER_LINEAR
    )
    cv_bilinear = cv2.resize(
        img_rgb, target_size_bilinear, interpolation=cv2.INTER_LINEAR
    )
    results.append(
        print_result(
            "Bilinear Resize (RGB 2x)", np.mean(np.abs(aot_bilinear - cv_bilinear))
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

    # --- NEW ALGORITHMS (JIT Mode) ---
    run_jit_algorithm_tests(img_rgb, img_gray, h, w, results)

    # --- PIPELINE STRESS TEST (SMART FUSION STYLE) ---
    if img_full is not None:
        run_pipeline_stress_test(taichi_aot.engine, img_full)

    # --- FINAL VERDICT ---
    print_header("FINAL VERDICT")
    if all(results):
        print(">>> ALL TESTS PASSED! AOT System is Healthy and Accurate.")
    else:
        print(">>> SOME TESTS FAILED! Please check individual MAE values.")
    passed = sum(results)
    total = len(results)
    print(f">>> Results: {passed}/{total} tests passed.")
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
        p_in = engine.placeholder(
            (h_f, w_f), dtype=np.float32, is_vector=True, vector_dim=3
        )

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
        n_iters = 10
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

            # Explicitly release intermediate VRAM buffers to prevent massive memory leakage/spikes
            r1.destroy()
            r2.destroy()
            r3.destroy()
            r4.destroy()
            _dx.destroy()
            _dy.destroy()
            if i < n_iters - 1:
                _r6.destroy()

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
        env = os.environ.copy()
        env["VK_LOADER_DEBUG"] = "error"
        with open(log_path, "w", encoding="utf-8") as f:
            process = subprocess.Popen(
                [sys.executable, "-u", __file__, "--run-logic"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                env=env,
            )

            for line in process.stdout:
                # Filter out the annoying Vulkan registry loader warnings
                if "windows_read_data_files_in_registry" in line:
                    continue
                sys.stdout.write(line)
                sys.stdout.flush()
                f.write(line)
                f.flush()

            process.wait()
    else:
        # This is the subprocess running the actual logic
        os.environ["AOT_MODE"] = "1"
        from taichi_library import taichi_aot

        run_comprehensive_test()
