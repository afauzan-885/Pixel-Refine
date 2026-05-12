import numpy as np
import os
import sys
import cv2
import time

# Add project root to sys.path
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features import taichi_bridge

def normalize_image_ref(image, dtype):
    if np.issubdtype(dtype, np.integer):
        scale = np.float32(np.iinfo(dtype).max)
    elif np.issubdtype(dtype, np.floating):
        scale = 1.0
    else:
        raise TypeError(f"Unsupported dtype for normalization: {dtype}")
    img_float = image.astype(np.float32, copy=False)
    if scale > 1e-6:
        img_float = img_float / scale
    if img_float.ndim == 2:
        img_float = np.stack((img_float, img_float, img_float), axis=-1)
    return img_float

def verify_normalize_aot():
    from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_aot.engine import AOTEngine
    engine = AOTEngine()
    
    print("\n" + "="*60)
    print(f" IMAGE NORMALIZATION AOT PARITY VERIFICATION ({getattr(engine, '_active_arch', 'vulkan')})")
    print("="*60)
    
    # 1. Load Real Image
    img_path = os.path.join(project_root, "test_algorithm/IMG_20160202_015247.png")
    img_u8 = cv2.imread(img_path)
    if img_u8 is None:
        print("[Error] Image not found.")
        return
        
    print(f"[Input] {os.path.basename(img_path)} ({img_u8.shape}, {img_u8.dtype})")
    
    # Test Cases
    test_cases = [
        ("Uint8 RGB",  img_u8, np.uint8, True),
        ("Uint8 Gray", cv2.cvtColor(img_u8, cv2.COLOR_BGR2GRAY), np.uint8, False),
    ]
    
    # Add Uint16 case if available (simulated)
    img_u16 = (img_u8.astype(np.float32) * 257).astype(np.uint16)
    test_cases.append(("Uint16 RGB", img_u16, np.uint16, True))
    test_cases.append(("Uint16 Gray", cv2.cvtColor(img_u16, cv2.COLOR_BGR2GRAY), np.uint16, False))

    tolerance = 1e-8 # 0.000001%
    
    for name, img, dtype, is_rgb in test_cases:
        print(f"\n--- Testing {name} ---")
        
        # 2. Python Reference
        ref_out = normalize_image_ref(img, dtype)
        
        # 3. AOT Implementation
        img_gpu = engine.upload(img, is_vector=is_rgb)
        
        t0 = time.perf_counter()
        aot_gpu = taichi_bridge.normalize_image_gpu(img_gpu, dtype)
        engine.sync()
        aot_time = (time.perf_counter()-t0)*1000
        
        aot_out = aot_gpu.to_numpy()
        print(f"[AOT] Computed in {aot_time:.2f} ms")
        
        # 4. Compare
        diff = np.abs(ref_out - aot_out)
        mae = np.mean(diff)
        max_err = np.max(diff)
        
        print(f"MAE: {mae:.12f}")
        print(f"Max: {max_err:.12f}")
        
        if max_err <= tolerance:
            print(">>> [SUCCESS] Parity Achieved!")
        else:
            print(">>> [FAILURE] Precision Mismatch!")
            idx = np.unravel_index(np.argmax(diff), diff.shape)
            print(f"    Sample Error at {idx}: Ref={ref_out[idx]:.10f}, AOT={aot_out[idx]:.10f}")

    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    verify_normalize_aot()
