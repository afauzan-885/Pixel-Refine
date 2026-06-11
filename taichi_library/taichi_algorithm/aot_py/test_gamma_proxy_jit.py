import taichi as ti
import numpy as np
import os
import sys

# Add project root to sys.path
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

import taichi_library.alignment.alignment_tile.aot.gamma_proxy_kernels as kernels

def to_gamma_proxy_python(linear_img, scale=1.0, gamma_pow=2.22, slope=4.5, cutoff=0.018):
    x = linear_img * scale
    x_mapped = x / np.sqrt(1.0 + x * x)
    res = np.power(np.clip(x_mapped, 0.0, 1.0), 1.0 / gamma_pow)
    return res.astype(np.float32)

def test_parity():
    ti.init(arch=ti.cpu)
    print("\n" + "="*60)
    print(" GAMMA PROXY JIT PARITY TEST")
    print("="*60)
    
    # 1. Create Test Data
    h, w = 512, 512
    # Create a gradient with edge cases (0, 1, and values near cutoff)
    x = np.linspace(0, 1, w, dtype=np.float32)
    y = np.linspace(0, 1, h, dtype=np.float32)
    xv, yv = np.meshgrid(x, y)
    
    # RGB Data
    img_linear = np.stack([xv, yv, 1.0 - xv], axis=-1).astype(np.float32)
    
    scale = 1.2
    gamma_pow = 2.22
    slope = 4.5
    cutoff = 0.018
    
    # 2. Python Reference
    ref_out = to_gamma_proxy_python(img_linear, scale, gamma_pow, slope, cutoff)
    
    # 3. Taichi Implementation
    dst_taichi = np.zeros_like(img_linear)
    
    # Run Taichi Kernel
    kernels.gamma_proxy_rgb_kernel(
        img_linear, dst_taichi,
        scale, gamma_pow, slope, cutoff
    )
    
    # 4. Compare
    diff = np.abs(ref_out - dst_taichi)
    max_err = np.max(diff)
    mae = np.mean(diff)
    
    print(f"Scale: {scale}, Gamma: {gamma_pow}, Slope: {slope}, Cutoff: {cutoff}")
    print(f"Mean Absolute Error: {mae:.10f}")
    print(f"Max Absolute Error : {max_err:.10f}")
    
    # Tolerance 0.00001% = 1e-7
    tolerance = 1e-7
    
    if max_err <= tolerance:
        print("\n>>> [SUCCESS] Math Parity Achieved! (within 1e-7)")
    else:
        print(f"\n>>> [FAILURE] Math Mismatch! Max Err: {max_err:.10f} > {tolerance:.10f}")
        # Find where it failed
        idx = np.unravel_index(np.argmax(diff), diff.shape)
        print(f"Peak failure at {idx}: Ref={ref_out[idx]:.10f}, Taichi={dst_taichi[idx]:.10f}")

if __name__ == "__main__":
    test_parity()
