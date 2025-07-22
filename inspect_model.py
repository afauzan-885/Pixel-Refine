import onnxruntime as ort
import os

def describe_onnx_io(onnx_path):
    if not os.path.exists(onnx_path):
        print(f"File not found: {onnx_path}")
        return

    sess = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
    print(f"=== MODEL: {onnx_path} ===")

    # INPUTS
    print("\n=== INPUTS ===")
    for inp in sess.get_inputs():
        shape = [d if isinstance(d, int) else 0 for d in inp.shape]
        print(f"{inp.name}: {shape}")

    # OUTPUTS
    print("\n=== OUTPUTS ===")
    for out in sess.get_outputs():
        shape = [d if isinstance(d, int) else 0 for d in out.shape]
        print(f"{out.name}: {shape}")

# Ganti path sesuai file Anda
onnx_path = "database/Learning_Model/disk_lightglue_pipeline.ort.onnx"
describe_onnx_io(onnx_path)
