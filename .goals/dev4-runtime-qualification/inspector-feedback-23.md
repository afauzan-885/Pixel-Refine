# Inspector feedback 23 — CUDA init identity assertion

Tanggal: 2026-10-25 (Asia/Jakarta)  
Model Inspector: GPT-6 (fallback; dedicated Goal Inspector model unavailable)  
Verdict: **FAIL_CHECKPOINT_DEVICE_IDENTITY_UNVERIFIED**

## Observed stop point

I read the iter23 script, runner, stdout, stderr, and exit file. The child
exit is numeric `1`. Before AOT import, the script verifies and preloads the
iter22 staged Dev4 C API by absolute path; the logged path is the exact
`bridge/cuda/taichi_c_api.dll` and SHA-256
`B29073835F7496B5A08307ADF7C088651FC17A14BF469C46319D3C50F213CBCF`.
The AOT loader logs the requested iter22 CUDA bridge path. Native logs then
report `Backend siap: CUDA (perangkat 0)` and memory status. Python records
backend `cuda`, ordinal 0, but stops on an assertion that expects the
`gpu_name`/`device_name` accessor to equal “NVIDIA GeForce MX150”. Those two
fields are empty.

This is more consistent with a bad identity accessor than a demonstrated
CUDA initialization failure: `AOTEngine` reached the non-null runtime path
and emitted its backend-ready log. Source confirms `engine.py` obtains
`gpu_name` from `_get_runtime_device_name()` for CUDA
([engine.py:2707](../../taichi_vision/taichi_aot/engine.py#L2707)), while the
bridge sets `EngineContext.device_name` only for OpenGL
([taichi_aot_engine.cpp:1763](../../taichi_vision/taichi_algorithm/aot_py/taichi_aot_engine.cpp#L1763));
the exported getter returns that field
([taichi_aot_engine.cpp:1811](../../taichi_vision/taichi_algorithm/aot_py/taichi_aot_engine.cpp#L1811)).
So an empty name is expected for this CUDA bridge path and does not alone
show a broken CUDA runtime. It also means this invocation did **not** verify
the selected physical device. No independent current CUDA-driver identity
query was collected.

The identity assertion is before the script's post-init Win32 module-path
checks for both DLLs. Therefore the preloaded C API path/hash is proven, but
the post-init bridge/C API path pair is not. The bridge-load log names the
staged path but is not a substitute for the script's intended Win32
post-init checks. The unique iter23 TCM root remains empty; no resolver,
TCM load, graph, compile, parity, or performance action occurred.

## No-mutation evidence

I rechecked current staged iter22 bridge and C API hashes:
`2B4068BA92093635023635B0887A3492B9BF4B6A9C37DBF9BC9CBC05FE3E2462` and
`B29073835F7496B5A08307ADF7C088651FC17A14BF469C46319D3C50F213CBCF`.
The active bridge, packaged CUDA bridge/C API, venv C API, and target
manifest retain their recorded hashes. The canonical TCM tree remains
1,694 files / 74,689,912 bytes, the iter23 root is empty, and Git status
contains only pre-existing user changes. No source/status/production
artifact was changed; this Inspector did not load a DLL, run runtime, build,
or test.

## Safest next bounded step

The single iter23 invocation has been consumed; request a new coordinator
approval before any CUDA process. If approved, run one **init-only identity
preflight** in a fresh process with the same iter22 bridge/C API, device 0,
NVIDIA selection, empty external TCM root, and separate stdout/stderr/numeric
exit capture. Keep the C API preload-path/hash check. After AOT initialization,
first verify runtime backend `cuda`, ordinal 0, and Win32-loaded paths/hashes
for both staged DLLs. For physical device identity, query the CUDA Driver API
for ordinal 0 (`cuDeviceGet`, `cuDeviceGetName`, and
`cuDeviceComputeCapability`) rather than asserting the empty bridge
`gpu_name`/`device_name` fields. Record the returned device name, compute
capability, and UUID if available; compare with the expected MX150 only if
that identity is observed in this process.

Stop before TCM resolver/load if runtime creation fails, backend/ordinal is
wrong, driver identity cannot be queried, the renderer is not the expected
native NVIDIA device, or either loaded DLL path/hash differs. Keep the TCM
root empty and no graph dispatch in this identity gate. If it passes, submit
the evidence for another Inspector/coordinator review before attempting the
CUDA TCM load/graph smoke. Do not use the missing device-name accessor as a
CUDA failure claim or as proof of successful MX150 selection.
