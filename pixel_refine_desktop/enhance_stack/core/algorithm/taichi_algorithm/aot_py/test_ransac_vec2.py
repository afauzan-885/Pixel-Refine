import os
import sys
import numpy as np

# Set Device 2 (NVIDIA)
os.environ["PIXEL_REFINE_AOT_DEVICE"] = "2"

file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

from pixel_refine_desktop.enhance_stack.core.algorithm import taichi_aot

print("Engine initialized on Device 2")
devices = taichi_aot.engine.get_vulkan_devices()
print("Available Devices:")
for i, d in enumerate(devices):
    print(f"[{i}] {d}")

# Test RANSAC
flow = np.zeros((64, 64, 2), dtype=np.float32)
flow_gpu = taichi_aot.engine.upload(flow, is_vec2=True)
print("Upload successful")

cleaned = taichi_aot.ransac_flow_cleanup(flow_gpu, threshold=1.0, n_iterations=1, return_gpu=True)
print("RANSAC run successful")
print("Result shape:", cleaned.shape)
