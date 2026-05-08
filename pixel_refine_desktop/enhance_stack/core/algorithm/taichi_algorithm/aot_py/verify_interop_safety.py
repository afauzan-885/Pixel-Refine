import numpy as np
import ctypes
import os
import sys
import time

# Path setup
project_root = "e:/APP Developer/Pixel Refine"
sys.path.append(project_root)

os.environ["PIXEL_REFINE_AOT_MODE"] = "1"
from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_aot.engine import AOTEngine

class MockGPUDeviceMemory:
    """Simulates an external GPU object (like ONNX/PyTorch) using NumPy."""
    def __init__(self, arr):
        self.arr = np.ascontiguousarray(arr)
        self.shape = self.arr.shape
        self.dtype = self.arr.dtype
        # Mocking the CUDA interface so engine.py detects it as GPU memory
        self.__cuda_array_interface__ = {
            'data': (self.arr.ctypes.data, False),
            'shape': self.arr.shape,
            'typestr': self.arr.dtype.str,
            'version': 3
        }

def verify_interop_safety():
    engine = AOTEngine()
    print("--- INTEROP SAFETY & INTEGRITY TEST ---")
    
    # 1. Create source data (9MP Image simulation)
    size = (3000, 3000)
    src_data = np.random.rand(*size).astype(np.float32)
    mock_gpu_obj = MockGPUDeviceMemory(src_data)
    
    print(f"[Test] Data Size: {src_data.nbytes / 1024**2:.2f} MB")
    print(f"[Test] Uploading via Fast-Interop Path...")
    
    # 2. Execution
    start = time.perf_counter()
    # This triggers the _upload_fast_interop logic:
    # Map -> Memmove (CPU-to-Pinned) -> Unmap -> Copy (DMA Pinned-to-VRAM)
    gpu_buf = engine.upload(mock_gpu_obj)
    engine.sync()
    end = time.perf_counter()
    
    print(f"[Result] Fast-Interop Latency: {(end-start)*1000:.2f} ms")
    
    # 3. Verification
    print("[Test] Verifying Data Integrity (Bit-perfect check)...")
    result_data = gpu_buf.to_numpy()
    
    diff = np.abs(src_data - result_data).max()
    if diff == 0:
        print("[SUCCESS] Data integrity verified: 100% Bit-Perfect Match.")
    else:
        print(f"[FAILURE] Data mismatch detected! Max Diff: {diff}")
        sys.exit(1)

    # 4. Stress Test (Race Condition Check)
    print("\n[Test] Running Stress Test (50 iterations) to check for race conditions...")
    for i in range(50):
        # Change source data every time
        new_data = np.random.rand(*size).astype(np.float32)
        mock_gpu_obj.arr[:] = new_data[:] # Update mock memory
        
        gpu_buf = engine.upload(mock_gpu_obj)
        res = gpu_buf.to_numpy()
        
        if not np.array_equal(new_data, res):
            print(f"[CRITICAL FAILURE] Race condition or corruption at iteration {i}!")
            sys.exit(1)
            
        if i % 10 == 0: print(f"Progress: {i}/50...")
        
    print("[SUCCESS] Stress test passed. No race conditions detected.")

if __name__ == "__main__":
    verify_interop_safety()
