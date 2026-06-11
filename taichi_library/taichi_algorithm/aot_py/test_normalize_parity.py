import numpy as np
import taichi as ti
import os
import sys

# Add project root to sys.path
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

from taichi_library.taichi_aot.engine import AOTEngine

def normalize_image_ref(image, dtype, out=None):
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
    if out is not None:
        if out.shape != img_float.shape or out.dtype != np.float32:
            out.resize(img_float.shape, refcheck=False)
            out[:] = np.zeros_like(img_float, dtype=np.float32)
        np.copyto(out, img_float, casting="unsafe")
        return out
    return img_float

def test_normalize_parity():
    # Use CPU for JIT precision testing
    ti.init(arch=ti.cpu)
    engine = AOTEngine()
    
    print("\n" + "="*60)
    print(" NORMALIZE IMAGE PARITY TEST (CPU vs GPU JIT)")
    print("="*60)
    
    h, w = 512, 512
    
    test_cases = [
        ("Uint8 Gray", np.uint8, False),
        ("Uint8 RGB",  np.uint8, True),
        ("Uint16 Gray", np.uint16, False),
        ("Uint16 RGB",  np.uint16, True),
    ]
    
    tolerance = 1e-8 # 0.000001%
    
    for name, dtype, is_rgb in test_cases:
        print(f"\n[Case] {name}")
        
        # 1. Create Test Data
        if is_rgb:
            img = np.random.randint(0, np.iinfo(dtype).max + 1, (h, w, 3), dtype=dtype)
        else:
            img = np.random.randint(0, np.iinfo(dtype).max + 1, (h, w), dtype=dtype)
            
        # 2. Python Reference
        ref_out = normalize_image_ref(img, dtype)
        
        # 3. GPU Implementation (via JIT fallback in taichi_bridge)
        from taichi_library.alignment.alignment_features.taichi_bridge import normalize_image_gpu
        img_gpu = engine.upload(img, is_vector=is_rgb)
        aot_gpu = normalize_image_gpu(img_gpu, dtype)
        aot_out = aot_gpu.to_numpy()
        
        # 4. Compare
        diff = np.abs(ref_out - aot_out)
        mae = np.mean(diff)
        max_err = np.max(diff)
        
        print(f"  MAE: {mae:.12f}")
        print(f"  Max: {max_err:.12f}")
        
        if max_err <= tolerance:
            print(f"  >>> [SUCCESS] Case {name} passed.")
        else:
            print(f"  >>> [FAILURE] Case {name} failed! Max Err: {max_err:.12f} > {tolerance:.12f}")
            # Find a failing pixel
            idx = np.unravel_index(np.argmax(diff), diff.shape)
            print(f"      Ref: {ref_out[idx]:.12f}, AOT: {aot_out[idx]:.12f}")

    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    test_normalize_parity()
