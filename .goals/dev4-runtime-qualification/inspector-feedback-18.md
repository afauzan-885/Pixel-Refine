# Inspector feedback 18 — Vulkan Intel init-only preflight

Tanggal: 2026-10-25 (Asia/Jakarta)  
Model Inspector: GPT-6 (fallback; dedicated Goal Inspector model unavailable)  
Verdict: **PASS_FOR_ONE_VULKAN_INTEL_INIT_ONLY_PREFLIGHT**

## Bridge and runtime identity

I inspected iter18's build and runtime captures without invoking a compiler,
loading a DLL, or running a test. The Vulkan baseline bridge build log reports
child exit 0 and `Finished generating code`; stderr is empty. The staged
bridge is AMD64/PE32+ and has SHA-256
`644F3111DF639AD4D96846BC4FCBFB49677E35F9ECC9D0DE512CD64DDEC2E1DC`.
Static imports contain 17 names from `taichi_c_api.dll`; I compared them with
the staged Dev4 C API's 809-name export listing and found 0 missing. The
bridge exports the memory-control C names and required init/load entrypoints.
The staged C API hash
`B29073835F7496B5A08307ADF7C088651FC17A14BF469C46319D3C50F213CBCF` matches
the venv Dev4 DLL.

The init-only Python process exit file contains `0`. Before importing AOT,
the script preloaded C API from the staged bridge directory and verified its
Win32 module path/hash. After `AOTEngine(arch="vulkan")`, Win32 checks report
the exact staged Vulkan bridge and adjacent Dev4 C API paths and hashes
listed above. Backend config is Vulkan, strict, target family
`vulkan_desktop`, vendor `intel`, device id/ordinal `0`, renderer
`Intel(R) UHD Graphics 620`. The `runtime_device` and native context-backend
strings are empty; the renderer and ordinal come from the engine/device
configuration, not those empty accessors.

The process uses a unique empty external TCM root. The script checks the root
before and after initialization and reports `tcm_root_empty=true` and
`tcm_or_graph_loaded=false`; there is no TCM resolver call, AOT module, graph,
compile, JIT, or parity result. The native Vulkan DLL pair is therefore
qualified only for this one initialization path, not for artifact execution.
The current repository status contains only pre-existing unrelated user
changes; source/header/manifest hashes and production binaries are reported
unchanged. This Inspector did not modify source or status.

## Autoscan and Intel compatibility limits

The process was fresh and explicitly requested Intel via
`TARGET_VENDOR=Intel` / `PIXEL_REFINE_TARGET_VENDOR=Intel`, with
`AOT_AUTOSCAN=1` and an empty `AOT_DEVICE`. The resulting runtime config and
renderer independently report selected ordinal 0 and Intel UHD 620. Source
inspection shows the selection path calls `scan_vulkan_device_records()`
with its default `fresh=False`; in this fresh Python process there is no
prior per-process scan cache. Thus the observed renderer/ordinal is enough to
accept this **bounded init-only selection**. It does not establish a
serialized `fresh=True` device list or stable ordinal across later processes.
For any later attempt that must use this same adapter, explicitly set
`AOT_DEVICE=0` and verify the renderer again rather than assuming enumeration
order persists.

The probe explicitly enabled `AOT_INTEL_PROBE=1` and
`AOT_ALLOW_UNSAFE_INTEL=1`. Logs report legacy compatibility mode and
`Intel native VULKAN safe teardown: native context destructor skipped`.
The engine source confirms Intel may skip native context destruction to avoid
a known teardown assertion. This process establishes successful
initialization under that isolated override; it does not establish normal
Intel Vulkan policy, graph dispatch, cleanup/lifecycle safety, or production
readiness. The safe-teardown log is a real limitation, not a successful
destructor test.

## Next bounded gate

Prior hardware inventory and this selected Vulkan device support one
Vulkan-target **compile-only** canary, but not yet a GPU TCM runtime smoke.
Use exact target `vulkan_x86_64_windows`, job `gaussian`, the project venv,
and a new unique external `PIXEL_REFINE_AOT_TCM_ROOT`. Set `AOT_DEVICE=0` for
the attempted Intel ordinal and require the compile log to confirm the actual
renderer is still Intel UHD 620; if it selects another device, fails backend
init, or lacks a valid Vulkan payload, stop and record the target as failed or
unsupported. Attach/validate the target ABI manifest and record C2 metrics,
unknown phases, archive and payload hashes. Do not load that TCM or dispatch
a graph in the compile gate.

After compile review, any Vulkan TCM load/graph/parity attempt needs its own
bounded gate and must account for the Intel probe override and skipped
destructor; do not convert this init-only success into GPU execution or
lifecycle qualification. A separate device scan is not required to restate
the observed init result, but must be captured if a later target-selection
decision depends on the current device ordering.
