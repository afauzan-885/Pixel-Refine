# Inspector feedback 28 — strict Intel ICD init, TCM smoke stopped

Tanggal: 2026-10-25 (Asia/Jakarta)  
Model Inspector: GPT-6 (fallback; dedicated Goal Inspector model unavailable)  
Verdict: **FAIL_CHECKPOINT_TCM_RUNTIME_SMOKE_NOT_REACHED**

## Exact stop and interpretation

The child exits with code `1`. Its stdout records successful static staging
preflight, staged C API preload, AOT facade initialization, strict OpenGL
Intel selection, and post-init Win32 bridge/C API path/hash checks. Native
logs identify the staged iter26 bridge and say the direct Intel ICD context
was initialized from `ig9icd64.dll` for `Intel(R) UHD Graphics 620`; the
engine reports backend OpenGL and context provider `ICD`. The script then
fails at `check_file(pathlib.Path(icd_path))` with `KeyError` before it emits
the loaded-ICD hash record, calls the resolver, performs runtime ABI
preflight, loads TCM, uploads input, or dispatches a graph.

This is a case-sensitive harness lookup defect, not evidence that Windows
loaded a different ICD or that OpenGL context initialization failed. The
script's expected-file dictionary uses the spelling `C:\\WINDOWS\\...`,
while `GetModuleFileNameW` returns the equivalent Windows path spelled
`C:\\Windows\\...`. Windows path lookup is case-insensitive, but Python
dictionary keys are not. The prior bridge and C API `check_file` calls have
already passed before the ICD lookup; the ICD file itself was also statically
preflighted by path/hash. Nevertheless, the script did not finish its
post-load ICD hash assertion, so that assertion cannot be reported as
passed. Taichi's log independently says the active GL procedure module
matches the ICD, which supports the direct-ICD initialization result but is
not a substitute for the intended loaded-file hash check.

The TCM static archive/manifest preflight earlier in the same process
completed. That is not the configured runtime ABI preflight: the script did
not reach `resolve_target`, `resolve_module_path`, or `aot.load_tcm`. There
is no TCM extraction/cache entry, graph result, image output, or parity
metric. The run logs `AOT_SAFE_TEARDOWN=1` and that the Intel native context
destructor was skipped; normal lifecycle remains unqualified.

## Scope, identity, and mutation

The selected Intel renderer and strict direct ICD context were observed in
this process, using the iter26 staged OpenGL bridge and paired Dev4 C API.
The iter27 artifact remains the generic OpenGL Windows/x86_64 vendor-unknown
TCM. Runtime target mapping to that generic artifact was not reached, so do
not claim it was resolved or loaded. No source edit, production bridge/CAPI,
venv, canonical TCM, status, or artifact promotion occurred; unrelated user
changes remain in Git status.

This Inspector read the scratch script/log/handoff and relevant source only.
I did not load a DLL, compile, run a runtime, or execute tests.

## Authorization boundary and required status

Iter28's one invocation has been consumed and the handoff authorizes no
retry. Therefore this checkpoint fails for the intended TCM runtime/parity
smoke, even though the strict Intel ICD initialization portion succeeded.
Do not retry or dispatch TCM from this feedback. The CUDA/OpenGL runtime goal
must remain open/incomplete; do not mark `status.json` complete.

If the coordinator later issues a new explicit authorization, the harness
fix should canonicalize Windows paths before map lookup (for example, compare
`normcase(realpath(path))` against the expected path and hash the canonical
preflight path). Preserve all strict Intel ICD, staged DLL, ABI-target,
artifact-root, and parity gates. The corrected process must still verify
post-init bridge/C API/ICD module identities, resolve the exact iter27
generic TCM for the Intel runtime target, pass runtime ABI preflight before
load, and stop on any mismatch. A new authorization is required before any
such invocation.
