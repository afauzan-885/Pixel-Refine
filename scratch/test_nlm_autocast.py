"""
NLM AOT Auto-Cast Test: uint8/uint16/float32 input
===================================================
Verifies that NLM correctly auto-casts integer inputs
and returns the same dtype.
"""
import os, sys, time, numpy as np
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
os.environ["AOT_MODE"] = "1"
from taichi_library import taichi_aot
from skimage.metrics import structural_similarity as ssim

def gen(h=128, w=128, seed=42):
    rng = np.random.RandomState(seed)
    img = np.zeros((h,w), dtype=np.float32)
    yy, xx = np.mgrid[0:h, 0:w]
    img += 0.3*np.sin(2*np.pi*xx/w) + 0.2*np.cos(2*np.pi*yy/h)
    img[h//4:3*h//4, w//4:3*w//4] += 0.4
    cx,cy = w//3, h//3
    r = min(h,w)//6
    img[((xx-cx)**2+(yy-cy)**2) < r**2] += 0.3
    return np.clip(img, 0, 1)

def noise(img, s=0.1, seed=123):
    rng = np.random.RandomState(seed)
    return np.clip(img + rng.normal(0,s,img.shape).astype(np.float32), 0, 1)

gt = gen(128, 128)
noisy_f32 = noise(gt, 0.10)

configs = [
    ("float32 grayscale", noisy_f32.astype(np.float32)),
    ("uint8 grayscale",   (noisy_f32 * 255).astype(np.uint8)),
    ("uint16 grayscale",  (noisy_f32 * 65535).astype(np.uint16)),
    ("float32 RGB",       np.stack([noisy_f32]*3, axis=-1).astype(np.float32)),
    ("uint8 RGB",         (np.stack([noisy_f32]*3, axis=-1) * 255).astype(np.uint8)),
    ("uint16 RGB",        (np.stack([noisy_f32]*3, axis=-1) * 65535).astype(np.uint16)),
]

print("=" * 75)
print("  NLM AOT Auto-Cast Test: dtype preservation")
print("=" * 75)
print(f"{'Input Type':<25} {'InDtype':<12} {'OutDtype':<12} {'SSIM':>7} {'PSNR':>8} {'Time':>8} {'PASS':>5}")
print("-" * 75)

all_pass = True
for label, img in configs:
    in_dtype = img.dtype
    t0 = time.perf_counter()
    result = taichi_aot.non_local_means(img, h_param=10.0, search_window=5, patch_size=2, return_gpu=False)
    t1 = time.perf_counter()
    out_dtype = result.dtype

    # SSIM comparison (normalize to float32 [0,1])
    if result.dtype == np.uint8:
        result_f = result.astype(np.float32) / 255.0
        gt_f = gt
    elif result.dtype == np.uint16:
        result_f = result.astype(np.float32) / 65535.0
        gt_f = gt
    else:
        result_f = result.astype(np.float32)
        gt_f = gt

    s = ssim(gt_f, result_f, data_range=1.0)
    mse = np.mean((gt_f - result_f) ** 2)
    p = 10 * np.log10(1.0 / max(mse, 1e-10))

    dtype_ok = (out_dtype == in_dtype)
    marker = "  OK" if dtype_ok else "  FAIL"
    if not dtype_ok:
        all_pass = False

    print(f"{label:<25} {str(in_dtype):<12} {str(out_dtype):<12} {s:>7.4f} {p:>7.2f}dB {(t1-t0)*1000:>6.1f}ms{marker}")

print("-" * 75)
print(f"\n  RESULT: {'ALL PASS' if all_pass else 'SOME FAILURES'}")
