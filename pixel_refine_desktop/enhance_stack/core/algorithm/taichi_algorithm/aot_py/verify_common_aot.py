import numpy as np
import os
import sys
import time

# Path setup
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

# Force AOT Mode
os.environ["PIXEL_REFINE_AOT_MODE"] = "1"
from pixel_refine_desktop.enhance_stack.core.algorithm import taichi_aot

def test_common_aot():
    print("=== COMMON UTILITIES AOT VERIFICATION ===")
    
    h, w = 512, 512
    # 1. Test Split & Merge
    img = np.random.randint(0, 255, (h, w, 3)).astype(np.float32)
    img_gpu = taichi_aot.upload(img, is_vector=True)
    
    # Split
    start = time.perf_counter()
    channels = taichi_aot.split_3ch(img_gpu)
    print(f"Split 3ch (AOT): {(time.perf_counter()-start)*1000:.2f}ms")
    
    # Merge
    start = time.perf_counter()
    merged_gpu = taichi_aot.merge_3ch(channels[0], channels[1], channels[2])
    print(f"Merge 3ch (AOT): {(time.perf_counter()-start)*1000:.2f}ms")
    
    merged_np = merged_gpu.to_numpy()
    parity = np.allclose(img, merged_np, atol=1e-5)
    print(f"Split-Merge Parity: {'[PASS]' if parity else '[FAIL]'}")
    
    # 2. Test cvtColor (RGB2GRAY)
    start = time.perf_counter()
    gray_gpu = taichi_aot.cvtColor(img_gpu, 7) # RGB2GRAY
    print(f"cvtColor RGB2GRAY (AOT): {(time.perf_counter()-start)*1000:.2f}ms")
    
    gray_np = gray_gpu.to_numpy()
    # Reference
    ref_gray = 0.299 * img[:,:,0] + 0.587 * img[:,:,1] + 0.114 * img[:,:,2]
    parity = np.allclose(ref_gray, gray_np, atol=1e-5)
    print(f"cvtColor Parity: {'[PASS]' if parity else '[FAIL]'}")
    
    # 3. Test insert_channel
    new_ch = np.zeros((h, w), dtype=np.float32)
    new_ch_gpu = taichi_aot.upload(new_ch)
    
    taichi_aot.insert_channel(new_ch_gpu, merged_gpu, 1) # Insert zeros into Green
    modified_np = merged_gpu.to_numpy()
    parity = np.all(modified_np[:,:,1] == 0)
    print(f"insert_channel Parity: {'[PASS]' if parity else '[FAIL]'}")

    # 4. Test absdiff
    img2 = np.random.randint(0, 255, (h, w, 3)).astype(np.float32)
    img2_gpu = taichi_aot.upload(img2)
    start = time.perf_counter()
    diff_gpu = taichi_aot.absdiff(img_gpu, img2_gpu)
    print(f"absdiff (AOT): {(time.perf_counter()-start)*1000:.2f}ms")
    
    diff_np = diff_gpu.to_numpy()
    ref_diff = np.abs(img - img2)
    parity = np.allclose(ref_diff, diff_np, atol=1e-5)
    print(f"absdiff Parity: {'[PASS]' if parity else '[FAIL]'}")

    taichi_aot.engine.clear_pool()

if __name__ == "__main__":
    test_common_aot()
