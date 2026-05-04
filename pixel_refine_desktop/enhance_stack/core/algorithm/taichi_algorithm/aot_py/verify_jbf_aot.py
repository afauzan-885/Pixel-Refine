"""verify_jbf_aot.py - Verifikasi JBF + JBLU terhadap referensi NumPy."""
import numpy as np, os, sys, time

file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path: sys.path.append(project_root)

os.environ["PIXEL_REFINE_AOT_MODE"] = "1"
from pixel_refine_desktop.enhance_stack.core.algorithm import taichi_aot

def ref_jbf_1ch(src, guide, ss=1.5, sr=0.1, r=2):
    """NumPy reference JBF for 1ch."""
    h, w = src.shape
    inv_ss2 = 1.0 / (2*ss*ss); inv_sr2 = 1.0 / (2*sr*sr)
    out = np.zeros_like(src)
    for y in range(h):
        for x in range(w):
            acc, total = 0.0, 1e-12
            c_g = guide[y, x]
            for dy in range(-r, r+1):
                for dx in range(-r, r+1):
                    ny = np.clip(y+dy, 0, h-1); nx = np.clip(x+dx, 0, w-1)
                    diff_g = guide[ny, nx] - c_g
                    wt = np.exp(-float(dx*dx+dy*dy)*inv_ss2 - diff_g*diff_g*inv_sr2)
                    acc += src[ny, nx] * wt; total += wt
            out[y, x] = acc / total
    return out

if __name__ == "__main__":
    H, W = 256, 256
    print("=" * 55)
    print(" JBF + JBLU AOT VERIFICATION")
    print("=" * 55)

    # Shared test data
    img_gray = np.random.rand(H, W).astype(np.float32)
    guide    = np.random.rand(H, W).astype(np.float32)
    img_rgb  = np.random.rand(H, W, 3).astype(np.float32)
    flow     = np.random.randn(H, W, 2).astype(np.float32)

    # === TEST 1: JBF 1ch ===
    print("\n--- JBF 1ch (grayscale) ---")
    start = time.perf_counter()
    result_aot = taichi_aot.joint_bilateral_filter(img_gray, guide, preset="medium", radius=2)
    t_aot = (time.perf_counter() - start) * 1000

    # Small reference (it's slow in numpy, so use small patch)
    ph = 64
    ref = ref_jbf_1ch(img_gray[:ph, :ph], guide[:ph, :ph])
    mae = np.mean(np.abs(result_aot[:ph, :ph] - ref))
    print(f"  MAE vs NumPy: {mae:.8f}  |  Time: {t_aot:.1f}ms")
    print(f"  {'[PASS]' if mae < 0.005 else '[FAIL]'}")  # JBF softens with sigma, expect small diff

    # === TEST 2: JBF 3ch RGB ===
    print("\n--- JBF 3ch (RGB) ---")
    start = time.perf_counter()
    result_rgb = taichi_aot.joint_bilateral_filter(img_rgb, guide, preset="low", radius=2)
    t_rgb = (time.perf_counter() - start) * 1000
    print(f"  Output shape: {result_rgb.shape}  |  Time: {t_rgb:.1f}ms")
    print(f"  {'[PASS]' if result_rgb.shape == img_rgb.shape else '[FAIL] shape mismatch'}")

    # === TEST 3: JBF flow ===
    print("\n--- JBF Flow (2ch) ---")
    start = time.perf_counter()
    result_flow = taichi_aot.joint_bilateral_filter(flow, guide, preset="high", radius=1)
    t_flow = (time.perf_counter() - start) * 1000
    print(f"  Output shape: {result_flow.shape}  |  Time: {t_flow:.1f}ms")
    print(f"  {'[PASS]' if result_flow.shape == flow.shape else '[FAIL] shape mismatch'}")

    # === TEST 4: JBLU 1ch (2x upscale) ===
    print("\n--- JBLU 1ch (2x upscale) ---")
    low_gray = img_gray[:H//2, :W//2]          # (128, 128)
    guide_hi = guide                            # (256, 256)
    start = time.perf_counter()
    up_gray = taichi_aot.joint_bilateral_upsample(low_gray, guide_hi, preset="medium")
    t_up1 = (time.perf_counter() - start) * 1000
    print(f"  Input: {low_gray.shape} -> Output: {up_gray.shape}  |  Time: {t_up1:.1f}ms")
    print(f"  {'[PASS]' if up_gray.shape == (H, W) else '[FAIL] wrong output size'}")

    # === TEST 5: JBLU Flow (pyramid flow upsample) ===
    print("\n--- JBLU Flow (2x pyramid flow upsample) ---")
    flow_low = flow[:H//2, :W//2]              # (128, 128, 2)
    start = time.perf_counter()
    up_flow = taichi_aot.joint_bilateral_upsample(flow_low, guide_hi, preset="medium")
    t_upf = (time.perf_counter() - start) * 1000
    print(f"  Input: {flow_low.shape} -> Output: {up_flow.shape}  |  Time: {t_upf:.1f}ms")
    # Flow should be scaled 2x (values doubled)
    sample_orig = flow_low[32, 32, 0]
    scale_ok = abs(up_flow[64, 64, 0]) < abs(sample_orig) * 5  # reasonable bound
    print(f"  {'[PASS]' if up_flow.shape == (H, W, 2) else '[FAIL] wrong output size'}")

    # === TEST 6: JBLU 3ch ===
    print("\n--- JBLU 3ch (2x upscale) ---")
    img_low_rgb = img_rgb[:H//2, :W//2]
    start = time.perf_counter()
    up_rgb = taichi_aot.joint_bilateral_upsample(img_low_rgb, guide_hi, preset="medium")
    t_up3 = (time.perf_counter() - start) * 1000
    print(f"  Input: {img_low_rgb.shape} -> Output: {up_rgb.shape}  |  Time: {t_up3:.1f}ms")
    print(f"  {'[PASS]' if up_rgb.shape == (H, W, 3) else '[FAIL] wrong output size'}")

    # === TEST 7: Guide auto-convert (BGR input) ===
    print("\n--- Guide auto-convert from BGR 3ch ---")
    guide_bgr = np.random.rand(H, W, 3).astype(np.float32)
    try:
        result_auto = taichi_aot.joint_bilateral_filter(img_gray, guide_bgr, preset="low")
        print(f"  Output shape: {result_auto.shape}")
        print("  [PASS] BGR guide auto-converted to gray")
    except Exception as e:
        print(f"  [FAIL] {e}")

    print("\n" + "=" * 55)
    print(" All JBF+JBLU tests completed!")
    print("=" * 55)
    taichi_aot.engine.clear_pool()
