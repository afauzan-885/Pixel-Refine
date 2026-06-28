import taichi as ti
import numpy as np
import os
import sys

# Add project root to sys.path
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

import taichi_library.taichi_algorithm.image_io_kernels as kernels

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

def test_normalize_jit():
    ti.init(arch=ti.cpu)
    print("\n" + "="*60)
    print(" IMAGE NORMALIZATION JIT PARITY TEST")
    print("="*60)
    
    h, w = 512, 512
    tolerance = 1e-7 # 0.00001% (as requested by USER)
    
    test_cases = [
        ("Uint8 Gray",  np.uint8,   False),
        ("Uint8 RGB",   np.uint8,   True),
        ("Uint16 Gray", np.uint16,  False),
        ("Uint16 RGB",  np.uint16,  True),
    ]
    
    for name, dtype, is_rgb in test_cases:
        print(f"\n[Case] {name}")
        
        # 1. Create Data
        if is_rgb:
            img = np.random.randint(0, np.iinfo(dtype).max + 1, (h, w, 3), dtype=dtype)
        else:
            img = np.random.randint(0, np.iinfo(dtype).max + 1, (h, w), dtype=dtype)
            
        # 2. Reference
        ref_out = normalize_image_ref(img, dtype)
        
        # 3. Taichi JIT
        dst_ti = np.zeros((h, w, 3), dtype=np.float32)
        
        if not is_rgb:
            if dtype == np.uint8:
                kernels.normalize_u8_to_vec3_kernel(img, dst_ti)
            else:
                kernels.normalize_u16_to_vec3_kernel(img, dst_ti)
        else:
            if dtype == np.uint8:
                kernels.normalize_vec3_u8_to_vec3_f32_kernel(img, dst_ti)
            else:
                kernels.normalize_vec3_u16_to_vec3_f32_kernel(img, dst_ti)
                
        # 4. Compare
        diff = np.abs(ref_out - dst_ti)
        mae = np.mean(diff)
        max_err = np.max(diff)
        
        print(f"  MAE: {mae:.12f}")
        print(f"  Max: {max_err:.12f}")
        
        if max_err <= tolerance:
            print("  >>> [SUCCESS] Math Parity Achieved!")
        else:
            print(f"  >>> [FAILURE] Math Mismatch! Max Err: {max_err:.12f}")
            idx = np.unravel_index(np.argmax(diff), diff.shape)
            print(f"      Peak Error at {idx}: Ref={ref_out[idx]:.10f}, JIT={dst_ti[idx]:.10f}")

    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    test_normalize_jit()
