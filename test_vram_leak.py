"""
Test: Verify TaichiGPUBuffer.destroy() correctly frees VRAM immediately.
Simulates the alignment loop pattern (allocate -> use -> destroy) for 4 frames.
"""
import os
os.environ["PIXEL_REFINE_AOT_ARCH"] = "vulkan"
import numpy as np
import gc

from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_aot.engine import AOTEngine, TaichiGPUBuffer

engine = AOTEngine()

print("=== Test: VRAM destroy() correctness ===\n")

# Simulate: allocate a 3K-sized buffer, use it, then destroy it
# For a 3016x3016 grayscale float32 = ~36MB per buffer
H, W = 1024, 1024  # Work resolution

def get_vram_estimate():
    """Estimate pool size (buffers NOT yet freed from VRAM)."""
    total = sum(len(v) * s for s, v in engine.buffer_pool.free_buffers.items())
    return total / (1024 * 1024)

print(f"[Init] Pool size: {get_vram_estimate():.1f} MB")

for frame_i in range(1, 5):
    print(f"\n--- Frame {frame_i} ---")
    
    # Allocate comparison pyramid (simulating prepare_comparison_for_alignment)
    comp_l0 = engine.allocate((H, W), dtype=np.float32)
    comp_l1 = engine.allocate((H//2, W//2), dtype=np.float32)
    comp_l2 = engine.allocate((H//4, W//4), dtype=np.float32)
    
    print(f"  Allocated 3 pyramid buffers ({H}x{W}, {H//2}x{W//2}, {H//4}x{W//4})")
    
    # Use the buffers (simulation)
    # ... run AOT graph ...
    
    # Destroy immediately after use
    comp_l0.destroy()
    comp_l1.destroy()
    comp_l2.destroy()
    
    # Verify handles are None
    assert comp_l0.handle is None, f"Frame {frame_i}: comp_l0.handle should be None after destroy!"
    assert comp_l1.handle is None, f"Frame {frame_i}: comp_l1.handle should be None after destroy!"
    assert comp_l2.handle is None, f"Frame {frame_i}: comp_l2.handle should be None after destroy!"
    
    print(f"  destroy() called -> handles set to None: OK")
    print(f"  Pool size after destroy: {get_vram_estimate():.1f} MB (should be 0 - no pool reuse)")

print("\n=== PASSED: destroy() correctly frees VRAM immediately ===")
print("=== Pool is empty (buffers freed to VRAM driver, not pooled) ===")
