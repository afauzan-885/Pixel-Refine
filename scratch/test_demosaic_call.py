import os
import sys
import numpy as np

# Setup path
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../"))
if project_root not in sys.path:
    sys.path.append(project_root)

import pixel_refine_desktop.enhance_stack.core.algorithm.taichi_aot as ta_aot

test_path = "E:/Photo_Editor/HDR Bracketing/RAW/Untuk Training/IMG_20250401_182043_B001.dng"
if not os.path.exists(test_path):
    # Fallback to the other one
    test_path = "test_algorithm/IMG_20250401_182043_B003.png"

print(f"Testing path: {test_path}")
print(f"Exists? {os.path.exists(test_path)}")

try:
    res = ta_aot.demosaic(test_path, method="hamilton", return_gpu=False)
    print(f"Success! Output shape: {res.shape}")
except Exception as e:
    import traceback
    traceback.print_exc()
