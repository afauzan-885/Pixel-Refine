import os
import sys
import numpy as np

# Setup path
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../"))
if project_root not in sys.path:
    sys.path.append(project_root)

import pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature as gf

test_path = "E:/Photo_Editor/HDR Bracketing/RAW/Untuk Training/IMG_20250401_182043_B001.dng"
print(f"Testing gf._prepare_image_array_from_raw with path: {test_path}")

try:
    res = gf._prepare_image_array_from_raw(test_path, linear_mode=True, generate_ref_proxy=True)
    if isinstance(res, tuple):
        print(f"Success! Returned tuple of shapes: {res[0].shape}, {res[1].shape}")
    else:
        print(f"Success! Returned shape: {res.shape}")
except Exception as e:
    import traceback
    traceback.print_exc()
