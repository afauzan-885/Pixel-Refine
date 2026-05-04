import os
import numpy as np
import time

# Force AOT Mode
os.environ["PIXEL_REFINE_AOT_MODE"] = "1"

# Import common after setting env
from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm import common
import pixel_refine_desktop.enhance_stack.core.algorithm.taichi_aot as taichi_aot

def test_common_aot():
    print("Testing Common Helper AOT Dispatch...")
    
    # 1. Test split/merge
    img = (np.random.rand(1000, 1000, 3) * 65535).astype(np.int32)
    
    t0 = time.time()
    channels = common.split(img)
    t1 = time.time()
    print(f"Split (AOT) Time: {(t1-t0)*1000:.2f}ms")
    print(f"Split Channel 0[:2, :2]:\n{channels[0][:2, :2]}")

    t0 = time.time()
    merged = common.merge(channels)
    t1 = time.time()
    print(f"Merge (AOT) Time: {(t1-t0)*1000:.2f}ms")

    print(f"Original img[:2, :2, 0]:\n{img[:2, :2, 0]}")
    print(f"Merged res[:2, :2, 0]:\n{merged[:2, :2, 0]}")
    
    diff = np.abs(img.astype(np.float32) - merged.astype(np.float32)).max()
    print(f"Merge Diff: {diff}")
    
    # 1.5 Test Copy 3D
    t0 = time.time()
    img_copy = common.copy(img)
    t1 = time.time()
    print(f"Copy 3D (AOT) Time: {(t1-t0)*1000:.2f}ms")
    copy_diff = np.abs(img.astype(np.float32) - img_copy.astype(np.float32)).max()
    print(f"Copy 3D Diff: {copy_diff}")
    
    # 2. Test cvtColor
    t0 = time.time()
    gray = common.cvtColor(img, common.COLOR_RGB2GRAY)
    t1 = time.time()
    print(f"cvtColor (AOT) Time: {(t1-t0)*1000:.2f}ms")
    
    # 3. Test GPU Buffer persistence
    img_gpu = taichi_aot.upload(img)
    t0 = time.time()
    ch1_gpu = common.extract_channel(img_gpu, 1)
    t1 = time.time()
    print(f"extract_channel (GPU-to-GPU AOT) Time: {(t1-t0)*1000:.2f}ms")
    
    print("\n[SUCCESS] Common AOT Helper Integration Verified!")

if __name__ == "__main__":
    test_common_aot()
