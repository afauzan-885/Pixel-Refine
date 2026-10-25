# Inspector feedback 30 — staged CUDA Gaussian runtime smoke

Tanggal: 2026-10-25 (Asia/Jakarta)  
Model Inspector: GPT-6 (fallback; dedicated Goal Inspector model unavailable)  
Verdict: **PASS_FOR_ONE_CUDA_MX150_FLOAT32_GAUSSIAN_SMOKE**

## Driver identity, bridge, and C API

I read the iter30 smoke script, PowerShell runner, stdout, stderr, exit file,
and staged artifact references; no runtime, compiler, DLL load, or test was
run by this Inspector. The corrected TCM verifier reads and stores the
embedded manifest bytes/hash inside the `ZipFile` context, so the iter25
closed-archive error is fixed. The fresh child first queries CUDA Driver API
ordinal 0 and reports NVIDIA GeForce MX150, compute capability 6.1, device
attributes 75/76 `[6,1]`, UUID `79cb253ff59071e62a5af8dcc95b8874`, driver API
13.0. This is same-process device identity, not an inference from
`AOT_DEVICE=0` or the prior compile.

Before AOT import, the process checks staged bridge/C API/TCM sizes and
hashes, preloads the Dev4 C API by absolute path, and logs that path/hash.
After AOT initialization it verifies Win32-loaded bridge and C API paths and
hashes. They are exactly the iter22 CUDA staging files:

- Bridge `taichi_aot_engine_baseline.dll`, 451,584 bytes, SHA-256
  `2B4068BA92093635023635B0887A3492B9BF4B6A9C37DBF9BC9CBC05FE3E2462`.
- C API `taichi_c_api.dll`, 51,376,128 bytes, SHA-256
  `B29073835F7496B5A08307ADF7C088651FC17A14BF469C46319D3C50F213CBCF`.

Runtime config is explicit/strict CUDA NVIDIA ordinal 0. The empty CUDA
`gpu_name`/`device_name` accessor is not used as device evidence; the Driver
API result supplies the device identity.

## TCM target, provenance, and ABI preflight

The script's static gate validates the iter22 staged TCM and sidecar against
their pinned hashes and sizes. TCM is 173,454 bytes, SHA-256
`4B80591E0E4F597EB63BFFE11BAA9FD70729630FD36F9BD2C06D4151B582469F`; the
sidecar is SHA-256
`A18315B5358A5C2E065362EDF37749F1055513B1B4471ECC1C5A7CC6D8FD5C4D`. The
embedded ABI manifest is CUDA/Windows/x86_64/NVIDIA, minimum ABI 1, and its
eight NVPTX payload hashes/triples are rechecked. The canonical target
manifest and exact target row are checked. One telemetry field,
`sidecar_build_fingerprint`, is null because the script reads that field
from `build_identity`, while the sidecar records it at the root; the exact
sidecar hash, artifact identity, target, compiler label, and payload checks
still pin the staged artifact. Do not interpret that null field as a
runtime ABI failure or claim the runtime independently revalidated the
build fingerprint.

Runtime resolver reports exact target `cuda_x86_64_windows_nvidia`, the
iter22 external artifact root, and the exact TCM path/hash. With
`AOT_TCM_ABI_PREFLIGHT=1`, legacy acceptance off, and `AOT_TCM_RUNTIME_ABI=1`,
`aot.load_tcm("gaussian")` returns `AOTModuleWrapper`; cache contains
`gaussian` and runtime logs the TCM loaded. The strict target/root/hash checks
precede that call. This is one successful load through the configured
preflight, not a universal ABI guarantee.

## Graph operation and parity

The script invokes the public API with `aot.InputArray` and a deterministic
float32 single-channel 64x64 input (NumPy seed 20261025). It calls
`aot.gaussian_blur(..., sigma=1.0, kernel_size=5, return_gpu=False)` and
compares against OpenCV 5.0.0 GaussianBlur with 5x5 kernel, sigma X/Y 1.0,
and `BORDER_REFLECT_101`. Script/source path confirms this 2D float32 input
uses the Gaussian module's x/y one-channel graph path. The recorded result
has finite float32 64x64 output and `allclose(rtol=1e-5, atol=1e-5)=true`;
max absolute error is `8.940696716308594e-08`, mean absolute error is
`6.803020369261503e-09`. Input, output, reference, TCM, bridge and C API
hashes are captured. This is one CUDA MX150 sample, not i32 parity or
general CUDA accuracy.

## Exit, isolation, and limits

Child exit file contains numeric `0`; stdout/stderr/exit are separately
captured. Post-run staged hashes match pre-run values. The canonical TCM
inventory remains 1,694 files / 74,689,912 bytes; active/packaged bridge and
C API, venv, manifest, and production artifacts remain at recorded hashes.
Iter22 artifact directory contains its original TCM and sidecar only; no
runtime cache or promotion was added. Git status has only pre-existing
unrelated user changes. No source or status mutation is reported.

The smoke proves one staged CUDA runtime initialization, TCM load, public
Gaussian operation, and float32 OpenCV parity sample on the MX150. It does
not identify the GPU used by the iter22 compiler process, qualify i32
specializations, other shapes/operations/devices, performance, application
integration, normal teardown, or production readiness. The goal remains
incomplete; do not generalize or promote these staging artifacts.
