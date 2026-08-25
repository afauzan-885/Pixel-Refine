import numpy as np
import cv2
import time
import os
import sys
from pathlib import Path

# Path setup
project_root = str(Path(__file__).resolve().parents[4])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

os.environ["AOT_MODE"] = "1"
from taichi_vision import taichi_aot
from taichi_vision.taichi_aot.engine import AOTEngine, TaichiGPUBuffer

def extreme_stress_test():
    engine = AOTEngine()
    img_path = os.path.join(project_root, "test_algorithm/IMG_20160202_015247.png")
    output_dir = os.path.join(project_root, "taichi_vision/taichi_algorithm/aot_py/test_output")
    os.makedirs(output_dir, exist_ok=True)

    print(f"--- EXTREME STRESS TEST (GRAYSCALE) ---")
    print(f"Image: {img_path}")

    # 1. Pipeline Test (Grayscale)
    print("\n[Test] Recording Stress Pipeline (Grayscale)...")
    # Grayscale: (3000, 3000)
    p_in = engine.placeholder((3000, 3000), dtype=np.float32)

    with engine.rec_pipeline("stress_chain_gray"):
        # Chain 1: Resize to 1500x1500x1
        res = taichi_aot.resize(p_in, (1500, 1500), interpolation=taichi_aot.INTER_LINEAR, return_gpu=True)
        # Chain 2: Blur
        blur = taichi_aot.gaussian_blur(res, sigma=1.5, return_gpu=True)
        # Chain 3: Sobel
        dx, dy = taichi_aot.sobel(blur, return_gpu=True)

    print("[Success] Pipeline Recorded.")

    # Prepare Input
    img_raw = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    img_f32 = cv2.resize(img_raw, (3000, 3000)).astype(np.float32) / 255.0
    img_gpu = engine.upload(img_f32)

    print(f"\n[Running] 100 iterations of recorded pipeline...")
    start = time.time()
    for i in range(100):
        engine.use_pipeline("stress_chain_gray", overrides={p_in: img_gpu})
        if i % 20 == 0:
            print(f"Progress: {i}/100...")

    engine.sync()
    end = time.time()

    print(f"\n[Result] Total Time: {end-start:.4f} s")
    print(f"[Result] Avg Latency: {(end-start)/100*1000:.2f} ms")
    print(f"[Result] FPS: {100/(end-start):.2f}")

if __name__ == "__main__":
    extreme_stress_test()
