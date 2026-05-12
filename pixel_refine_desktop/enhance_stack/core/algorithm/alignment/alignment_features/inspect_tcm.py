import os
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_aot.engine import AOTEngine

def inspect():
    engine = AOTEngine()
    aot_dir = os.path.join(project_root, "pixel_refine_desktop", "ui", "data", "aot_assets")
    
    tcm_files = ["image_io.tcm", "bilinear.tcm", "compute_flow_vulkan.tcm", "warp_vulkan"]
    
    for name in tcm_files:
        path = os.path.join(aot_dir, name)
        print(f"\n--- Inspecting: {name} ---")
        try:
            mod = engine.load(path)
            # Karena engine.py kita tidak punya cara langsung buat list graphs, 
            # kita coba tebak atau lihat metadata.json jika ada di folder (untuk folder TCM)
            if os.path.isdir(path):
                metadata_path = os.path.join(path, "metadata.json")
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'r') as f:
                        print(f.read())
                else:
                    print("No metadata.json found in folder.")
            else:
                print("TCM is a single file, cannot inspect graphs directly via Python currently.")
        except Exception as e:
            print(f"Error loading {name}: {e}")

if __name__ == "__main__":
    inspect()
