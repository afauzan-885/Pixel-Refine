# Inspector feedback 14 — CPU bridge build and static PE gate

Tanggal: 2026-10-25 (Asia/Jakarta)  
Model Inspector: GPT-6 (fallback; dedicated Goal Inspector model unavailable)  
Verdict: **PASS_FOR_CPU_BRIDGE_STATIC_PREFLIGHT_ONLY**

## Source review

I inspected commit `0e9efe4f` and its two-file diff. The header introduces
`TI_AOT_MEMORY_CONTROL_EXPORT`, which expands to `__declspec(dllexport)` only
for `_WIN32` plus `PIXEL_REFINE_TAICHI_AOT_ENGINE_BUILD`; the helper is
undefined after the three declarations. The engine translation unit opts in
immediately around this include and undefines the producer macro immediately
afterward. The three definitions no longer carry definition-side `EXPORT` or
per-function linkage prefixes and remain within the existing outer
`extern "C"` scope. Signatures and ABI struct declarations/layout assertions
are unchanged. This keeps the export annotation producer-scoped in this
translation unit; the header has no unconditional Windows attribute for
consumers or non-Windows builds.

## Build and static artifact evidence

Builder handoff 14 reports one successful `cpu baseline` bridge build to
`D:\temp\pixel_refine_dev4_runtime_qualification_20261025_7ab5e244_iter14_cpu_baseline\bridge\cpu`, using the Pixel MSVC script, x64 MSVC 19.42.34435.0, the
Dev4 venv headers/import library, and the copied venv `taichi_c_api.dll`.
The exact invocation is `call "...\\build_engine_msvc.bat" cpu baseline`;
the captured build log records exit 0 and `Finished generating code`. Its
SHA-256 is `0FD4F32A936EB1AC45153177D03868B11D83D8A49C217230B11944F72DB7A39B`.
The staged bridge DLL is 451,584 bytes, SHA-256
`E484881C4ADF1B192C02ED95AA6BFED5C9C3D682A8D2FC43E8010BB3CA3ED6D9`; the
copied C API DLL is the venv file, 51,376,128 bytes, SHA-256
`B29073835F7496B5A08307ADF7C088651FC17A14BF469C46319D3C50F213CBCF`.

I read the scratch `bridge_exports.txt`, `bridge_imports.txt`,
`capi_exports.txt`, `bridge_headers.txt`, and `build.log`. Static PE output
reports both DLLs as AMD64/PE32+. The bridge export table contains the exact
undecorated names `ti_aot_get_memory_snapshot`,
`ti_aot_set_memory_limits`, and `ti_aot_trim_memory_cache`. All 16 names
imported by the bridge from `taichi_c_api.dll` appear in its 809-name export
table; I independently checked the 16 recorded names against the saved export
listing. The direct dependencies shown are the paired C API DLL plus Windows
system DLLs. `dumpbin` inspection is static; it did not exercise Windows
loader resolution, delay loads, or runtime ABI calls.

Handoff 14 records matching before/after hashes for the product header/source,
manifest, active and packaged bridges/C APIs, and venv C API/import library;
all build outputs are under the unique external scratch root. No DLL was
loaded and no TCM was compiled. Unrelated user modifications remain
unstaged. This review did not build, load, or run tests.

## Verdict limits and next gate

The narrow export fix and CPU bridge have passed source review, compile/link,
architecture, named-export, and import-name closure checks. This is enough to
proceed with a **CPU-only staged AOT compile**; it is not yet runtime or full
ABI qualification. It says nothing about CUDA, Vulkan, OpenGL, or other CPU
profiles.

Next command should compile one representative smoke artifact only, using the
project venv and a new unique scratch TCM root, for example:

```powershell
$env:PIXEL_REFINE_AOT_TCM_ROOT = 'D:\temp\pixel_refine_dev4_runtime_qualification_20261025_7ab5e244_iter15_cpu_tcm'
& 'E:\APP Developer\Eel-Dance\Pixel-Refine\venv\Scripts\python.exe' `
  'E:\APP Developer\Eel-Dance\Pixel-Refine\taichi_vision\taichi_algorithm\aot_py\compile_aot_backend_suite.py' `
  --target cpu_x86_64_windows --only gaussian
```

Capture exact output, target artifact/runtime reports, cold/cache state, and
TCM hashes; verify the emitted artifact is inside the new scratch root and
matches the CPU Windows target before any load. If that gate passes, a
separate fresh-process CPU smoke may use the staged bridge via
`AOT_ENGINE_DLL` and that same `PIXEL_REFINE_AOT_TCM_ROOT`, with the staged
matching `taichi_c_api.dll` beside the bridge. Run only the Gaussian graph
against an OpenCV oracle, recording device/backend, input shape/dtype, exact
command, error metrics, and all source/bridge/C API/TCM hashes. Stop on any
load/API/target mismatch; do not fall back to another backend or use active
production artifacts. The compile gate itself should not load the bridge.

This does not clear the remaining AOT coverage, runtime smoke/parity,
GPU-specific C5 coverage, or C++ modernization criteria. The runtime goal is
still incomplete.
