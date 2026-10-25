# Inspector feedback 27 — generic OpenGL Gaussian compile

Tanggal: 2026-10-25 (Asia/Jakarta)  
Model Inspector: GPT-6 (fallback; dedicated Goal Inspector model unavailable)  
Verdict: **PASS_FOR_GENERIC_OPENGL_TCM_COMPILE_WITH_OBSERVED_INTEL_CONTEXT**

## Compile target, context, and C2 report

The one venv command compiled only `gaussian` for exact generic manifest
target `opengl_x86_64_windows`, with a new external artifact/report root and
TCM manifest enabled. Child exit is numeric `0`; stdout reports `[PASS]
gaussian`; stderr is empty. Report
`compile-1792911454810443800.json` is 8,162 bytes, SHA-256
`8D6F6CCCAC79BE319B3CB7059B270FADF80E273DE767686FD127DADCAF9A3AD4`. It
records backend OpenGL, status `compiled`, cache reason `gaussian:artifact_missing`,
8 graphs/dispatch nodes/kernels, 16 SPIR-V payloads, and 157,802 artifact
bytes. Schema-2 metrics include worker total 35.047089 s, compiler call
23.280615 s, module import 2.068563 s, Taichi import 3.356661 s,
fingerprint 5.036532 s, manifest 0.171242 s, validation 0.021664 s,
normalization 0.099920 s, and explicit nulls/reasons for backend init,
frontend lowering, backend codegen, archive, and per-graph timings.

The worker output tail contains direct OpenGL compiler-context diagnostics:
GLFW context; `expected_vendor='<unset>'`; `actual vendor='Intel'`; renderer
`Intel(R) UHD Graphics 620`; OpenGL `4.3.0 - Build 31.0.101.2145`; and
active GL procedure module path `...\\ig9icd64.dll` matching the reported
active ICD. This is evidence that the **compiler invocation actually used
an Intel GLFW OpenGL context**. It does not prove strict Intel selection by
the build request: vendor was unset, and the manifest/sidecar target is
deliberately generic `vendor=unknown`. Preserve both facts: observed
compiler context Intel; target qualification vendor-neutral/unconstrained.
No AOT bridge/C API load or staged bridge renderer check occurred in this
compile process.

## TCM manifest and payload validation

The only TCM is `artifacts/opengl_x86_64_windows/gaussian_opengl_x86_64_windows.tcm`,
157,802 bytes, SHA-256
`6D1192258794B8CE84EE9086AC40900810D7B22DACEF1F5F8548534106E60033`. Its
sidecar SHA-256 is
`5AABAC0A38D768C146BF6FF44186307E492311A939716A46150914826EAC7EAB` and its
artifact size/hash match. The embedded manifest is schema 1, format 1,
minimum ABI 1, target Windows/x86_64/OpenGL/vendor unknown, with required
features `COMPUTE` and `SSBO`; target-manifest hash matches the canonical
manifest. `graphs.json` has eight graph entries. I independently read the
archive and recomputed every SPIR-V payload size/hash; 16/16 match the
manifest. The manifest's `kernels` list is empty, so kernel declarations
are not inferred from it; worker inventory is separately available from
`graphs.json`.

Six warnings remain in the report tail: `f32` accumulators assigned to
`i32` outputs for the 3-channel x/y Gaussian integer kernels at
`gaussian.py:46–48` and `:94–96`. They indicate a potential precision-loss
path, not an output error measurement or parity result. No accuracy claim is
made.

## Isolation and verdict limits

Current report/TCM/sidecar hashes match the handoff. Preflight records the
artifact and report roots as external and `native_context=off`; the
compile invocation did not load a bridge/C API or TCM at runtime. Current
canonical TCM inventory is 1,694 files / 74,689,912 bytes, and Git status
contains only pre-existing unrelated user changes. Active/package/venv
binary and manifest hashes remain at their recorded values. No TCM runtime
load, graph dispatch, parity, or application test occurred.

This passes a generic OpenGL TCM compile and static archive/provenance gate,
with a directly observed Intel compiler context but no explicit Intel
selection contract. It does not yet qualify an AOT runtime bridge, Intel ICD
selection in that bridge, graph execution, parity, normal teardown, other
OpenGL devices, or production behavior.

## Next bounded runtime gate

One fresh staged Intel OpenGL Gaussian runtime/parity smoke is justified
after separate coordinator approval. Use the iter26 staged OpenGL bridge and
matching Dev4 C API plus this iter27 TCM. Before load, verify their hashes,
set strict direct-ICD mode (`PIXEL_REFINE_OPENGL_ICD_ONLY=1` or the
equivalent `PIXEL_REFINE_OPENGL_CONTEXT=icd`) and expected Intel vendor/name,
then require the AOT runtime's actual renderer to be Intel UHD 620 and the
active ICD/procedure module to resolve to the expected Intel ICD. Verify
Win32 bridge/C API module paths and hashes, target resolver identity
`opengl_x86_64_windows_intel` mapping to the exact generic iter27 TCM,
external TCM root, and ABI preflight before `load_tcm` or dispatch. If any
renderer/ICD/path/target/ABI check differs, stop before graph execution.

If the gates pass, run one float32 single-channel Gaussian case against
OpenCV `BORDER_REFLECT_101` and record exact command, renderer, ICD path,
shape/dtype, hashes, tolerance, and max/mean error. Do not use this case to
claim the warning-affected i32 path, all shapes/operations, performance, or
normal Intel teardown. No fallback, retry, compile, or artifact promotion is
included in that next gate.
