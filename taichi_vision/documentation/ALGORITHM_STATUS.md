# Algorithm Status

Snapshot: 2026-09-06; primary scope is Windows desktop x86-64.

The labels below are intentionally conservative. An algorithm without complete
runtime evidence is not described as 100% production-ready.

| Family | Status | Notes |
|---|---|---|
| Resize (bicubic/bilinear/area/nearest) | **QUALIFIED** | Qualified only on the documented desktop smoke/parity targets |
| Gaussian, gradients, Canny | **QUALIFIED** | Fast hardware gate 5/5 on the documented devices; other drivers require their own gate |
| Bilinear, DCB, Hamilton, ARM demosaic | **EXPERIMENTAL** | Artifacts and focused evidence exist, but the full target/device matrix is not complete |
| MLRI-ADMM demosaic | **EXPERIMENTAL** | Portable Vulkan reconstruction was corrected; broader parity and lifecycle evidence remains required |
| Remap, perspective warp, affine warp | **QUALIFIED** | Qualified only for the recorded desktop paths and shapes |
| Optical flow and block matching | **EXPERIMENTAL** | Native implementations and recovery paths exist; fused/block variants remain target-gated |
| RANSAC/homography, OFB, AKAZE | **EXPERIMENTAL** | CPU/native graph work is present; cross-backend runtime evidence is incomplete |
| Box, median, bilateral, guided, NLM, BM3D | **EXPERIMENTAL** | CPU/reference parity exists; native graphics paths retain per-operation guards |
| FFT, phase correlation, NCC/ZNCC | **EXPERIMENTAL** | Focused CPU evidence exists; universal backend support is not established |
| HDR, tone mapping, inpaint, SFM/MVS | **EXPERIMENTAL** | Research artifacts and CPU evidence exist; target/device qualification remains incomplete |
| Compression and RAW pipeline | **EXPERIMENTAL** | Artifacts and focused pipeline evidence exist; complete native matrix is pending |

The label applies to the family as a whole. A narrower operation/backend gate
may still be **QUALIFIED** when its evidence explicitly names the backend,
device, shape, dtype, command, metric, lifecycle, and memory result.

## Current Native Evidence (2026-09-05)

The latest recorded native desktop evidence is limited to the devices and
commands that were actually run:

- CPU Windows x86-64: fast hardware matrix 5/5.
- NVIDIA GeForce MX150 CUDA: fast hardware matrix 5/5.
- NVIDIA GeForce MX150 native OpenGL ICD: fast hardware matrix 5/5 and
  comprehensive native OpenGL gate 29/29.
- Intel UHD Graphics 620 native Vulkan API 1.3.215, driver 101.2115:
  75/75 target-qualified TCM loads, 940/940 SPIR-V shader validations,
  28/28 algorithm checks, and lifecycle/graph parity MAE
  `3.7529832752625225e-07`.
- Intel UHD Graphics 620 native `ig11icd64.dll` OpenGL ICD, driver 101.2115:
  29/29 comprehensive checks and the recorded 8122x2966 float32 stress gate.

These are qualification records for exact device/driver combinations, not a
universal claim for all Intel/NVIDIA driver versions. Dozen/D3D12 translation
adapters are excluded from production selection, and no CPU fallback was used
for these native records.

## Historical Qualification Evidence (2026-08-30)

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

### Historical TCM Artifact Coverage

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
