# Algorithm Status

Snapshot: 2026-08-17; primary scope is Windows desktop x86-64.

The labels below are intentionally conservative. An algorithm without complete
runtime evidence is not described as 100% production-ready.

| Family | Status | Notes |
|---|---|---|
| Resize (bicubic/bilinear/area/nearest) | **QUALIFIED** | Desktop smoke/parity baseline |
| Gaussian, gradients, Canny | **QUALIFIED** | Recorded fast hardware gate 5/5 |
| Bilinear, DCB, Hamilton, ARM demosaic | **EXPERIMENTAL** | AOT APIs exist; full dtype/backend matrix is unfinished |
| MLRI-ADMM demosaic | **EXPERIMENTAL** | CPU signatures validated; cross-backend matrix remains |
| Remap, perspective warp, affine warp | **QUALIFIED** | Recorded desktop parity gate |
| Optical flow and block matching | **EXPERIMENTAL** | Some native/tile paths qualified, not every driver combination |
| RANSAC/homography, OFB, AKAZE | **EXPERIMENTAL** | AOT APIs exist; device/stress coverage is not universal |
| Box, median, bilateral, guided, NLM, BM3D | **EXPERIMENTAL** | Some OpenGL cases use a safety/reference path |
| FFT, phase correlation, NCC/ZNCC | **EXPERIMENTAL** | APIs exist; target-specific evidence is incomplete |
| HDR, tone mapping, inpaint, SFM/MVS | **EXPERIMENTAL** | Source and dispatch exist; qualification is incomplete |
| Compression and RAW pipeline | **EXPERIMENTAL** | Codec parity/production gates are tracked separately |

## Pending or quarantined

- ARM CPU/GLES/Vulkan: static/package evidence exists; real-device execution
  is not claimed.
- CUDA Maxwell through Blackwell: compile/target policy is not a substitute
  for validation on real drivers and devices.
- Native OpenGL graphs with ABI/shape/driver defects remain on the safety or
  reference path until their independent gate passes.
- Legacy JIT/worker notes were removed from the source tree; they are not a
  production API.

## Promotion rule

For each operation, record backend, device, shape, dtype, command, parity/error
metric, lifecycle, and memory telemetry. TCM compilation alone is insufficient.
Promote operations individually after their evidence is complete.
