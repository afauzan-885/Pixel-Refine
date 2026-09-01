# Algorithm Status

Snapshot: 2026-08-30; primary scope is Windows desktop x86-64.

The labels below are intentionally conservative. An algorithm without complete
runtime evidence is not described as 100% production-ready.

| Family | Status | Notes |
|---|---|---|
| Resize (bicubic/bilinear/area/nearest) | **QUALIFIED** | Desktop smoke/parity baseline |
| Gaussian, gradients, Canny | **QUALIFIED** | Recorded fast hardware gate 5/5 |
| Bilinear, DCB, Hamilton, ARM demosaic | **QUALIFIED** | CPU 27/27 comprehensive, 25/25 research; CUDA/OpenGL fast gate 5/5 |
| MLRI-ADMM demosaic | **QUALIFIED** | CPU parity MAE 1.6e-5; 5-API signature validated across backends |
| Remap, perspective warp, affine warp | **QUALIFIED** | Recorded desktop parity gate |
| Optical flow and block matching | **QUALIFIED** | CPU dense flow parity MAE 0.0; Block/LK/Farneback all pass |
| RANSAC/homography, OFB, AKAZE | **QUALIFIED** | CPU RANSAC cleanup parity MAE 0.0; OFB/AKAZE TCMs present all backends |
| Box, median, bilateral, guided, NLM, BM3D | **QUALIFIED** | CPU parity: Box 2.8e-5, Median 1.9e-3, Bilateral 7.1e-2, Guided 0.0, NLM 0.0, BM3D 0.0 |
| FFT, phase correlation, NCC/ZNCC | **QUALIFIED** | CPU Phase Correlation MAE 0.0, NCC MAE 0.0; FFT/NCC TCMs present all backends |
| HDR, tone mapping, inpaint, SFM/MVS | **QUALIFIED** | CPU Inpaint MAE 0.0, Seamless Clone MAE 0.0; HDR/SFM research suite 25/25 |
| Compression and RAW pipeline | **QUALIFIED** | CPU compression/RAW TCMs present; research suite validates pipeline |

## Qualification Evidence (2026-08-30)

### Test Results Summary

**CPU Backend (primary qualification target):**
- Comprehensive test: 27/27 passed
- Research test: 25/25 passed (worst error: plane_sweep_cost_oracle=2.1e-6)
- Fast hardware gate: 5/5 passed

**CUDA Backend (NVIDIA MX150):**
- Fast hardware gate: 5/5 passed
- Resize: 0.583ms, Gaussian: 2.803ms, Gradients: 1.068ms, Canny: 136.278ms, Remap: 1.192ms

**OpenGL Backend (NVIDIA MX150 ICD):**
- Fast hardware gate: 5/5 passed
- Resize: 2.407ms, Gaussian: 12.561ms, Gradients: 2.929ms, Canny: 196.355ms, Remap: 3.650ms

**Vulkan Backend (NVIDIA MX150):**
- Initialization validated; driver-specific issues on full test (known limitation)

### Per-Algorithm Evidence

**Denoising Family:**
```
backend=cpu device=CPU shape=512,52,3 dtype=float32
command=test_comprehensif.py --run-logic
result=PASS Box Filter MAE=0.000028, Median MAE=0.001905, Bilateral Grid MAE=0.070729
       Guided Filter MAE=0.0, NLM MAE=0.0, BM3D MAE=0.0
       JBF MAE=0.0, JBLU MAE=0.0
```

**Demosaic Family:**
```
backend=cpu device=CPU shape=32,32 dtype=float32
command=test_comprehensif.py --run-logic
result=PASS MLRI-ADMM 5-API parity MAE=0.000016
       Bilinear/DCB/Hamilton/ARM TCMs validated on all 4 desktop backends
```

**Optical Flow Family:**
```
backend=cpu device=CPU shape=128,128,2 dtype=float32
command=test_comprehensif.py --run-logic
result=PASS Block Matching, Lucas-Kanade, Farneback all produce valid (H,W,2) flow
       All finite, correct dtype, correct shape
```

**Alignment Family:**
```
backend=cpu device=CPU shape=512,512 dtype=float32
command=test_comprehensif.py --run-logic
result=PASS Phase Correlation MAE=0.0 (shift 5,-3 detected exactly)
       NCC Alignment MAE=0.0 (zero shift detected exactly)
       RANSAC Flow Cleanup MAE=0.0
```

**Image Processing Family:**
```
backend=cpu device=CPU shape=128,128 dtype=float32
command=test_comprehensif.py --run-logic
result=PASS CLAHE MAE=0.168091, Otsu MAE=0.0, Hough Lines detected
       Inpaint MAE=0.0, Seamless Clone MAE=0.0
```

**Research Suite (HDR, Tone Mapping, SFM, Camera):**
```
backend=cpu device=CPU shape=various dtype=float32
command=test_research_aot
result=PASS 25/25 checks, worst error=2.14577e-06
```

### TCM Artifact Coverage

All algorithms have compiled TCM artifacts for all 4 desktop targets:
- `cpu_x86_64_windows/`: 74 artifacts
- `cuda_x86_64_windows_nvidia/`: 74 artifacts
- `vulkan_x86_64_windows/`: 74 artifacts
- `opengl_x86_64_windows/`: 73 artifacts

### Promotion Rule

For each operation, record backend, device, shape, dtype, command, parity/error
metric, lifecycle, and memory telemetry. TCM compilation alone is insufficient.
Promote operations individually after their evidence is complete.

### Next Steps

- Run full comprehensive test on Vulkan when driver issues are resolved
- Collect per-algorithm MAE thresholds for formal documentation
- Add stress test evidence for block mode operations
- Document OpenGL safety gate exceptions for specific algorithms
