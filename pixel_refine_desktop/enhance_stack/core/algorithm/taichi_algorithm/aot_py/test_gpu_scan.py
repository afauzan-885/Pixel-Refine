import os
import sys

# Add project root to sys.path
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

from pixel_refine_desktop.enhance_stack.core.algorithm import taichi_aot

def test_devices():
    engine = taichi_aot.engine
    devices = engine.get_vulkan_devices()
    print("\nAvailable Vulkan Devices:")
    for i, name in enumerate(devices):
        print(f"[{i}] {name}")
    
    if devices:
        print(f"\nCurrent active device index: {os.environ.get('PIXEL_REFINE_AOT_DEVICE', '0')}")

if __name__ == "__main__":
    # Add project root to sys.path
    file_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
    if project_root not in sys.path:
        sys.path.append(project_root)
        
    test_devices()
