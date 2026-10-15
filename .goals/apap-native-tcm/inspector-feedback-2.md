# Inspector Feedback — Iteration 2

**Verdict: FAIL.** The change now propagates errors from `warp_image` when sparse native dispatch is selected and restores the old TPS-enabled default, but default APAP production calls immediately fail because the native TPS graph is still absent. Native-fit parity and all backend, application, performance, and memory gates remain unmet.

## Independent checks

- Read the frozen `.goals/apap-native-tcm/goal.md`, iteration 1 feedback, current `status.json`, and inspected the current source and worktree delta.
- `taichi_vision/taichi_algorithm/alignment/apap.py:754-760` now directly dispatches to `warp_image_sparse_mesh` when `use_sparse_mesh=True`; the old broad catch and full-image fallback are gone. The explicit `use_sparse_mesh=False` branch remains a CPU/reference path. I ran a small explicit reference smoke: backend `cpu`, input `(10,10) float32`, identity map, output `(10,10) float32`, valid mask all true, MAE `0.0`. This preserves that explicit route. It does not validate GPU dispatch or broader public caller behavior.
- The default is restored to `enable_residual_spline=True` at `apap.py:561-570`, but `fit_apap` checks it and raises at lines 583-586 because the native TPS graph does not exist. I independently called the public default with a small five-point synthetic correspondence set under `PIXEL_REFINE_AOT_ARCH=cpu`; result: `RuntimeError: The native APAP TCM does not include the optional TPS residual graph...`. Thus production default APAP does not execute. `mesh_warp.warp_apap` calls `fit_apap` without overriding the default at `mesh_warp.py:561-567`; the resident denoising APAP route does the same at `resident_pipeline.py:1794-1797`. These main call paths therefore fail before the fit graph runs.
- The native weighted-fit kernel in `apap.py:20-89` still constructs an 8x8 normal equation and solves it with float32 Gauss-Jordan elimination. The prior independent candidate-vs-NumPy check remains the only numerical evidence: CPU, correspondences `(48,2) float64`, query `(128,2) float64`, maximum Euclidean mapped-point discrepancy `0.4699 px`. No iteration 2 parity result was provided or observed, and the kernel still contains the same normal-equation approach that produced that mismatch.
- Candidate TCM in `%TEMP%/apap-native-tcm-candidate-20261016/cpu_x86_64_windows/apap_native_cpu_x86_64_windows.tcm` still hashes to `acfd283093cf0402e5740afcdc8fcaee032575a58ef5ef4d33791fec3f7e3af5`. No `apap_native` artifact is present in the runtime `taichi_vision/taichi_algorithm/aot_tcm` tree. Iteration 2 did not add a TPS graph, target-qualified manifest, or promoted/integrated candidate. The earlier archive inspection found no `tcm_manifest.json` in this CPU candidate.
- No iteration 2 pytest, `py_compile`, headless `main_desktop.py` import, headless RGB/RAW APAP application integration, CUDA/Vulkan/OpenGL/CPU APAP backend matrix, paired latency, or RAM/VRAM evidence was found. The only new runtime check above covers the explicit CPU reference warp and the failure of default `fit_apap`.
- `git diff --check` over the inspected Python paths emitted only line-ending warnings; no whitespace diagnostics were printed. This does not substitute for compile/import/test gates.

## Acceptance status

- **Partial:** `warp_image(..., use_sparse_mesh=True)` now propagates the native mesh dispatch error; explicit `use_sparse_mesh=False` reference warp still works in the small CPU smoke. Public function names and parameters are present.
- **Fail:** The default APAP fit and `warp_apap` production route raise before execution because default TPS is unsupported; prior weighted-fit parity discrepancy is unresolved; no native TPS/flow-composition evidence; no runtime-integrated candidate manifest; no tests or headless APAP application integration; no backend, performance, or memory evidence.
- **Unverified:** CPU TCM execution for this iteration and all CUDA/Vulkan/OpenGL APAP executions. The prior CPU candidate dispatch is iteration 1 evidence only, not evidence for the current default route or current runtime integration.

## Required follow-up

1. Provide a native TPS residual graph or a compatible production route that preserves the established default behavior while allowing `fit_apap` and `warp_apap` to complete; the default must produce a warp rather than an error.
2. Resolve the existing weighted-DLT mismatch and rerun the fixed NumPy parity fixtures without widening tolerances.
3. Integrate a target-qualified, manifest-backed TCM through the runtime resolver without replacing the preserved APAP artifacts.
4. Run focused tests, headless app import and real headless APAP integration; then test available backend/device profiles and collect paired latency/RAM/VRAM measurements.

No product source or TCM was edited by the Inspector. Only this feedback and the iteration verdict in `status.json` are changed.
