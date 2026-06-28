import numpy as np
import os
import sys

# Setup path
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

# Enable AOT Mode
os.environ["AOT_MODE"] = "1"

import taichi_library.taichi_aot as taichi_aot
from taichi_library.taichi_aot.engine import AOTEngine

def test_remap_with_flow_f32_2d():
    print("\n--- Testing F32 2D (Grayscale) ---")
    h_src, w_src = 512, 512
    h_dst, w_dst = 1024, 1024
    h_flow, w_flow = 64, 64

    # Create dummy data
    np.random.seed(42)
    src_np = np.random.rand(h_src, w_src).astype(np.float32)
    flow_np = (np.random.rand(h_flow, w_flow, 2).astype(np.float32) - 0.5) * 10.0

    # Upload flow (Bypass engine.upload auto-detect bug)
    engine = AOTEngine()
    flow_gpu = engine.allocate(flow_np.shape, dtype=np.float32, is_vector=False, host_accessible=True)
    from taichi_library.taichi_aot.engine import _LIB, _RUNTIME
    _LIB.write_to_gpu_buffer(_RUNTIME, flow_gpu.handle, flow_np.ctypes.data, flow_gpu.nbytes)

    # 1. Legacy Way
    print("Running Legacy remap...")
    map_x_gpu, map_y_gpu = taichi_aot.build_flow_maps(flow_gpu, h_dst, w_dst)
    legacy_res = taichi_aot.remap(src_np, map_x_gpu, map_y_gpu, return_gpu=False)

    # 2. Optimized Fused Way
    print("Running Fused remap_with_flow...")
    opt_res = taichi_aot.remap_with_flow(src_np, flow_gpu, h_dst, w_dst, return_gpu=False)

    # Validate
    mae = np.mean(np.abs(legacy_res - opt_res))
    print(f"MAE: {mae}")
    assert mae < 1e-4, f"F32 2D MAE too high: {mae}"
    print("SUCCESS: F32 2D matches Legacy!")

    # Cleanup
    map_x_gpu.destroy()
    map_y_gpu.destroy()
    flow_gpu.destroy()


def test_remap_with_flow_f32_3d():
    print("\n--- Testing F32 3D (Color/RGB) ---")
    h_src, w_src = 512, 512
    h_dst, w_dst = 1024, 1024
    h_flow, w_flow = 64, 64

    # Create dummy data
    np.random.seed(42)
    src_np = np.random.rand(h_src, w_src, 3).astype(np.float32)
    flow_np = (np.random.rand(h_flow, w_flow, 2).astype(np.float32) - 0.5) * 10.0

    # Upload flow (Bypass engine.upload auto-detect bug)
    engine = AOTEngine()
    flow_gpu = engine.allocate(flow_np.shape, dtype=np.float32, is_vector=False, host_accessible=True)
    from taichi_library.taichi_aot.engine import _LIB, _RUNTIME
    _LIB.write_to_gpu_buffer(_RUNTIME, flow_gpu.handle, flow_np.ctypes.data, flow_gpu.nbytes)

    # 1. Legacy Way
    print("Running Legacy remap...")
    map_x_gpu, map_y_gpu = taichi_aot.build_flow_maps(flow_gpu, h_dst, w_dst)
    legacy_res = taichi_aot.remap(src_np, map_x_gpu, map_y_gpu, return_gpu=False)

    # 2. Optimized Fused Way
    print("Running Fused remap_with_flow...")
    opt_res = taichi_aot.remap_with_flow(src_np, flow_gpu, h_dst, w_dst, return_gpu=False)

    # Validate
    mae = np.mean(np.abs(legacy_res - opt_res))
    print(f"MAE: {mae}")
    assert mae < 1e-4, f"F32 3D MAE too high: {mae}"
    print("SUCCESS: F32 3D matches Legacy!")

    # Cleanup
    map_x_gpu.destroy()
    map_y_gpu.destroy()
    flow_gpu.destroy()


def test_remap_with_flow_u16_3d():
    print("\n--- Testing U16 3D (Color/RGB) ---")
    h_src, w_src = 512, 512
    h_dst, w_dst = 1024, 1024
    h_flow, w_flow = 64, 64

    # Create dummy data (u16 values in [0, 65535])
    np.random.seed(42)
    src_np = (np.random.rand(h_src, w_src, 3) * 65535.0).astype(np.uint16)
    flow_np = (np.random.rand(h_flow, w_flow, 2).astype(np.float32) - 0.5) * 10.0

    # Upload flow (Bypass engine.upload auto-detect bug)
    engine = AOTEngine()
    flow_gpu = engine.allocate(flow_np.shape, dtype=np.float32, is_vector=False, host_accessible=True)
    from taichi_library.taichi_aot.engine import _LIB, _RUNTIME
    _LIB.write_to_gpu_buffer(_RUNTIME, flow_gpu.handle, flow_np.ctypes.data, flow_gpu.nbytes)

    # 1. Legacy Way
    # Note: Legacy remap will internally cast src to float32, perform bilinear interpolation,
    # and then cast the output back to uint16 (which we specified).
    print("Running Legacy remap...")
    map_x_gpu, map_y_gpu = taichi_aot.build_flow_maps(flow_gpu, h_dst, w_dst)
    legacy_res = taichi_aot.remap(src_np, map_x_gpu, map_y_gpu, return_gpu=False)

    # 2. Optimized Fused Way (return GPU buffer first so we can inspect it)
    print("Running Fused remap_with_flow...")
    opt_gpu = taichi_aot.remap_with_flow(src_np, flow_gpu, h_dst, w_dst, return_gpu=True)
    
    # Download float32 results directly
    opt_f32_np = opt_gpu.to_numpy()
    print(f"Opt F32 GPU Download Range: min={opt_f32_np.min()}, max={opt_f32_np.max()}, mean={opt_f32_np.mean()}")
    
    # Cast to uint16
    opt_res = opt_f32_np.astype(np.uint16)
    opt_gpu.destroy()

    # Validate
    print(f"Legacy Range: min={legacy_res.min()}, max={legacy_res.max()}, mean={legacy_res.mean()}")
    print(f"Opt Range: min={opt_res.min()}, max={opt_res.max()}, mean={opt_res.mean()}")
    mae = np.mean(np.abs(legacy_res.astype(np.float32) - opt_res.astype(np.float32)))
    print(f"MAE: {mae}")
    assert mae < 1.0, f"U16 3D MAE too high: {mae}"
    print("SUCCESS: U16 3D matches Legacy within sub-pixel rounding error!")

    # Cleanup
    map_x_gpu.destroy()
    map_y_gpu.destroy()
    flow_gpu.destroy()


if __name__ == "__main__":
    test_remap_with_flow_f32_2d()
    test_remap_with_flow_f32_3d()
    test_remap_with_flow_u16_3d()
    print("\nALL TESTS PASSED SUCCESSFULLY!")
