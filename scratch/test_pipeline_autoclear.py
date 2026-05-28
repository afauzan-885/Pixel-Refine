import os
import sys
import numpy as np

# Path setup to ensure absolute imports work
project_root = "e:/APP Developer/Pixel Refine"
sys.path.append(project_root)

os.environ["PIXEL_REFINE_AOT_MODE"] = "1"
from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_aot.engine import AOTEngine, TaichiGPUBuffer
import pixel_refine_desktop.enhance_stack.core.algorithm.taichi_aot as taichi_aot

def test_autoclear():
    print("=" * 60)
    print(" TESTING PIPELINE AUTO-CLEAR ON BUFFER DESTRUCTION")
    print("=" * 60)

    engine = AOTEngine()
    
    # 1. Prepare simple inputs
    p_in = engine.placeholder((100, 100), dtype=np.float32)
    in_val = np.random.rand(100, 100).astype(np.float32)
    in_gpu = engine.upload(in_val)
    
    # 2. Record pipeline
    pipeline_name = "test_autoclear_pipeline"
    print(f"\n[Step 1] Recording pipeline '{pipeline_name}'...")
    
    # Allocate a buffer that will act as intermediate
    with engine.rec_pipeline(pipeline_name):
        # resize will allocate an intermediate output buffer
        res = taichi_aot.resize(p_in, (50, 50), interpolation=taichi_aot.INTER_LINEAR, return_gpu=True)
    
    print("Pipeline recorded successfully.")
    print(f"Recorded pipelines: {engine.recorded_pipelines}")
    print(f"Intermediate buffers in pipeline: {engine._pipeline_intermediates.get(pipeline_name)}")
    
    # Ensure the intermediate is tracked and associated with the pipeline
    assert pipeline_name in engine.recorded_pipelines, "Pipeline should be in recorded_pipelines set"
    intermediates = engine._pipeline_intermediates.get(pipeline_name, [])
    assert len(intermediates) > 0, "Should have tracked the intermediate buffer"
    intermediate_buf = intermediates[0]
    assert pipeline_name in intermediate_buf.associated_pipelines, "Buffer should be associated with the pipeline"

    # 3. Test execution (should succeed)
    print(f"\n[Step 2] Executing pipeline before buffer destruction...")
    engine.use_pipeline(pipeline_name, overrides={p_in: in_gpu})
    engine.sync()
    print("Pipeline executed successfully without errors.")

    # 4. Destroy the intermediate buffer explicitly
    print(f"\n[Step 3] Destroying intermediate buffer explicitly...")
    intermediate_buf.destroy()
    
    # Verify the pipeline is automatically cleared/invalidated
    print(f"Recorded pipelines after destruction: {engine.recorded_pipelines}")
    print(f"Pipeline intermediates after destruction: {engine._pipeline_intermediates.get(pipeline_name)}")
    
    assert pipeline_name not in engine.recorded_pipelines, "Pipeline should have been removed from recorded_pipelines"
    assert pipeline_name not in engine._pipeline_intermediates, "Pipeline entry in intermediates should have been deleted"
    print("[SUCCESS] Pipeline was automatically cleared from Python and C++ engine maps!")

    # 5. Try to use the pipeline again (should warn and skip safely)
    print(f"\n[Step 4] Attempting to use the invalidated pipeline (should warn and skip safely)...")
    engine.use_pipeline(pipeline_name, overrides={p_in: in_gpu})
    print("[SUCCESS] use_pipeline skipped execution safely without crashing.")

    # Cleanup
    in_gpu.destroy()
    print("\n" + "=" * 60)
    print(" ALL AUTO-CLEAR TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    test_autoclear()
