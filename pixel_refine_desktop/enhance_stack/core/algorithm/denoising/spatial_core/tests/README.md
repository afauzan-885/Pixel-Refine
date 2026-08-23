# Spatial block parity evidence

The production block gate is intentionally fail-closed in
`spatial_fusion.py`.  `test_spatial_native_parity.py` is the integration
harness for a real same-backend comparison:

```powershell
$env:AOT_MODE = "1"
$env:PIXEL_REFINE_AOT_ARCH = "cpu"       # or cuda/vulkan/opengl
$env:PIXEL_REFINE_RUN_SPATIAL_NATIVE_PARITY = "1"
venv\Scripts\python.exe -m pytest -q `
  pixel_refine_desktop\enhance_stack\core\algorithm\denoising\spatial_core\tests\test_spatial_native_parity.py -s
```

The full-frame and block runs must use the same runtime context, device,
shape, dtype, parameters, and spatial TCM.  The report checks image sum,
weight sum, processed-frame count, shape, dtype, finite values, maximum
absolute error, mean absolute error, RMSE, and relative-L1 loss.  The
top-level `loss_score` is the larger relative-L1 loss of the image and weight
planes, so candidate configurations can be ranked by the lowest measured
loss even when a strict promotion tolerance is not met.  `quality_passed`
records whether the measured relative loss is within the relaxed quality
budget; it is intentionally separate from strict `passed` (maximum absolute
error).  A passing probe is evidence only for the exact configuration tested;
it does not automatically set
`SPATIAL_BLOCK_PARITY_CERTIFIED` or promote the block path.  Run the matrix
for every supported desktop backend before changing that gate.

If the active engine reports a quarantined TCM, repair/rebuild that artifact
first.  A failed module load is not spatial parity evidence.
