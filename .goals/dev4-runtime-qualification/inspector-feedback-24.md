# Inspector feedback 24 — CUDA Driver identity and init-only gate

Tanggal: 2026-10-25 (Asia/Jakarta)  
Model Inspector: GPT-6 (fallback; dedicated Goal Inspector model unavailable)  
Verdict: **PASS_FOR_CUDA_DEVICE_IDENTITY_AND_INIT_ONLY**

## Device identity and staged runtime

I read the iter24 script, PowerShell runner, stdout, stderr, and child exit
file; I did not load or run any CUDA/AOT runtime. The fresh process calls the
CUDA Driver API before importing the AOT facade. Its output records
`cuDeviceGet(0)` as NVIDIA GeForce MX150, compute capability 6.1, UUID
`79cb253ff59071e62a5af8dcc95b8874`, Driver API version 13.0. The physical
identity is directly observed in this invocation, not inferred from
`AOT_DEVICE=0`, host inventory, or the empty AOT `gpu_name` field.

After the identity check, the process hashes and preloads the iter22 staged
Dev4 C API from its absolute path. Its logged pre-load path and SHA-256 are
`...iter22_cuda/bridge/cuda/taichi_c_api.dll` and
`B29073835F7496B5A08307ADF7C088651FC17A14BF469C46319D3C50F213CBCF`. AOT
initialization reports CUDA ordinal 0 and logs `Backend siap: CUDA (perangkat
0)`. Post-init Win32 checks for both modules pass:

- CUDA bridge: iter22 scratch `taichi_aot_engine_baseline.dll`, SHA-256
  `2B4068BA92093635023635B0887A3492B9BF4B6A9C37DBF9BC9CBC05FE3E2462`.
- Dev4 C API: iter22 adjacent `taichi_c_api.dll`, SHA-256
  `B29073835F7496B5A08307ADF7C088651FC17A14BF469C46319D3C50F213CBCF`.

The `engine.gpu_name` and config `device_name` fields remain empty, as
expected for this bridge: the CUDA path returns the bridge's `EngineContext`
device name, which its initialization code currently populates only for
OpenGL. Iter24 correctly uses the Driver API as the CUDA identity source.
The memory line `device_available=0MB source=system_memory` is not evidence
of CUDA capacity or failure; this init-only process performed no CUDA AOT
allocation or graph dispatch.

## Boundaries and no-mutation check

The process exits `0`; stdout, stderr, and the numeric exit file are captured
separately. Its external TCM root is empty. It performs no target resolver,
TCM load, compile/JIT, graph, parity, or benchmark. I independently rehashed
the staged bridge/C API, active and packaged CUDA bridge/C API, venv C API,
and target manifest; values match the handoff. Canonical TCM inventory remains
1,694 files / 74,689,912 bytes. Git status contains only pre-existing
unrelated user changes. No source, production artifact, venv, canonical TCM,
or status file changed. This Inspector did not execute runtime/build/tests.

This resolves iter23's identity uncertainty: the empty device-name accessor
was the incorrect guard, not evidence of a CUDA initialization failure. It
does not retroactively identify the GPU used by the iter22 compile worker;
that compile device remains unknown. This gate proves staged CUDA bridge/C
API initialization with the MX150 selected by Driver API ordinal 0 only.

## Next bounded gate

One CUDA TCM load/graph/parity smoke is now justified, after separate
coordinator approval. Use the same iter22 staged bridge/C API and iter22
Gaussian TCM in one fresh process. Re-query the CUDA Driver API in that
process and require ordinal 0 to be MX150/CC 6.1; verify staged pre- and
post-init DLL paths/hashes; require runtime backend CUDA/ordinal 0; set
`AOT_TCM_ABI_PREFLIGHT=1` and legacy acceptance off; and require the resolver
to return the exact `cuda_x86_64_windows_nvidia` artifact from the iter22
staging root before calling `load_tcm`. Stop before graph dispatch on any
driver, path, backend, target, ABI, or hash mismatch. If those gates pass,
run only one float32 Gaussian case against OpenCV with fixed shape, sigma,
kernel size and border mode, and capture input/output/TCM/bridge/C API hashes,
device identity, max/mean error and tolerance. Do not use it to claim i32
parity, infer the prior compiler device, or generalize to other CUDA devices,
operations, performance, or production readiness. No fallback, retry, or
promotion is covered by this next gate.
