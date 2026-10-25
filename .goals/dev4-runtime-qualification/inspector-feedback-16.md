# Inspector feedback 16 — interrupted CPU runtime initialization

Tanggal: 2026-10-25 (Asia/Jakarta)  
Model Inspector: GPT-6 (fallback; dedicated Goal Inspector model unavailable)  
Verdict: **FAIL_CHECKPOINT_INCONCLUSIVE_RUNTIME_ATTEMPT**

## Evidence and interpretation

The scratch runtime script hash is `AA740C8A13850CA32BDF1723E5A646B4DC784FBC3DF96F48C2EE34327667AEB5`;
the captured log hash is
`BC91E43C20D8EBA08A174C2C24582FDB5C90949F86ACC98C664855F1226A12E1`.
The script set CPU selection, the iter15 staging TCM root, and the iter14
staging bridge path. Before importing the public AOT package, it pinned
`taichi_c_api.dll` by absolute path, checked the loaded module path and hash,
and logged the iter14 staging C API identity. The AOT loader then logged
`Backend bridge loaded:` with the iter14 staging bridge path. This is positive
path-selection/load-log evidence, but the planned post-init Win32 module-path
and hash checks for bridge/C API did not run, so they remain unverified.

The process output reached Taichi's
`lang_util.cpp:taichi::lang::runtime_lib_dir@58` diagnostic asking for
`TI_LIB_DIR` to identify `taichi.__path__[0]/_lib/runtime`. That diagnostic
means the runtime-library-directory lookup reported a problem; it does not
by itself prove whether this was a fatal runtime initialization error or a
recoverable diagnostic. The handoff does not record the effective
`TI_LIB_DIR`, so a missing or invalid value is plausible but not established.
The indicated venv directory
`venv/Lib/site-packages/taichi/_lib/runtime` exists and contains
`runtime_x64.bc`; explicitly setting it is a narrow environment correction
to test.

PowerShell's `$ErrorActionPreference='Stop'` converted native stderr into a
`NativeCommandError` and interrupted the wrapper's capture path. The wrapper
exit code 1 is not a reliable inner Python process exit code; that value and
later stdout/stderr are unknown. Consequently there is no evidence that
`get_backend_config()` completed, the actual backend/device was established,
the bridge module path was verified after initialization, the target
resolver selected the scratch TCM, a module was loaded/extracted, or a graph
was dispatched. No input/reference/output or parity metric exists. The
missing `.cpu_aot_cache` supports that no TCM was materialized in the cache,
but is not a substitute for a resolver checkpoint. Do not claim runtime,
TCM-load, graph, or parity success.

The handoff records unchanged hashes for staged bridge/C API/TCM and active,
packaged, venv, manifest, and canonical TCM artifacts; no source edit or
production mutation occurred. This Inspector only read the script/log and
runtime-library directory; no DLL was loaded and no test or build was run.

## Safest bounded next invocation

The attempt is inconclusive, so do not continue from it as though it reached
the graph. A new single retry requires coordinator authorization. If approved,
reuse the same script and exact staged inputs, but set
`TI_LIB_DIR=E:\APP Developer\Eel-Dance\Pixel-Refine\venv\Lib\site-packages\taichi\_lib\runtime`
before process start. Capture stdout, stderr, and the actual child exit code
independently (for example with a `ProcessStartInfo` wrapper redirecting both
streams and waiting for the process); do not let PowerShell's native-stderr
error-record policy terminate capture. Write all capture files only beneath
a fresh unique iter17 scratch directory, after confirming the expected
bridge/C API/TCM hashes again.

Keep the existing script's strict CPU selection, explicit staged paths,
post-init Win32 path/hash checks, target/root/artifact resolver checks, and
single float32 Gaussian/OpenCV comparison. Stop immediately on a nonzero
Python exit, the same `runtime_lib_dir` diagnostic without a completed
post-init checkpoint, any wrong DLL path/hash/backend/target/root, or any
graph/parity error. Do not retry, compile/JIT, switch backend, load an active
artifact, or promote outputs in that invocation. Only if all checks complete
should its recorded CPU smoke/parity be reviewed separately; it would still
not qualify i32, GPU targets, other graphs, or performance.
