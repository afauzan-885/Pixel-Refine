# Inspector Feedback — Iteration 3

**Verdict: FAIL.** The source now declares a 9D homogeneous weighted-DLT kernel and the compiler registers it, but the compile attempt timed out without producing a new TCM. There is no graph execution or parity evidence, and the frozen goal still cannot be accepted.

## Independent inspection

- In `taichi_vision/taichi_algorithm/alignment/apap.py:20-89`, `_fit_apap_weighted_nodes_kernel` forms a 9x9 weighted normal matrix from homogeneous DLT rows and uses 12 Jacobi sweeps to select the smallest-eigenvalue vector. This is a source-level implementation of a 9D homogeneous fit; it is not evidence that a TCM was produced or that the graph runs correctly.
- In `taichi_vision/taichi_algorithm/alignment/compile_mesh_warp_tcm.py:24, 134-142`, the compiler imports the kernel and registers `algn_apap_fit_weighted_f32`; static wiring is present. Builder's `status.json` says compilation exceeded about 169.7 CPU seconds and emitted no TCM. I did not recompile.
- Independent artifact inventory found **zero** `apap_native` TCMs in `taichi_vision/taichi_algorithm/aot_tcm`. The only candidate remains the earlier CPU archive in the temp staging folder, SHA-256 `ACFD283093CF0402E5740AFCDC8F8CAEE032575A58EF5EF4D33791FEC3F7E3AF5`; it predates the 9D kernel and cannot provide execution evidence for this iteration. It also previously had no `tcm_manifest.json`.
- No new native execution, parity, pytest, application, or backend evidence is recorded for this iteration. CPU, CUDA, Vulkan, and OpenGL execution remain unverified; no paired performance or RAM/VRAM measurements exist. The Builder's compile timeout is not a test pass.
- `fit_apap` still defaults `enable_residual_spline=True` at `apap.py:588`; its check at lines 601-604 raises because there is no native TPS residual graph. The user explicitly chose to preserve TPS behavior, so a TPS-off workaround is not authorized. Even after a successful fit-graph compile, production-default APAP still would not complete.
- Static numerical risk: the Jacobi kernel diagonalizes `A.T @ A`, rather than the direct weighted design matrix. This squares the design matrix condition number. Whether 12 sweeps and float32 preserve existing APAP tolerances cannot be established without execution/parity tests. This is a risk to validate, not a claim that the new kernel is numerically incorrect.

## Acceptance status

- **Partial:** 9D-DLT/Jacobi kernel source and compiler graph registration exist.
- **Fail:** No TCM emitted, no native graph execution, no numerical parity, no native TPS graph/default APAP success, and no runtime integration or target manifest for this iteration.
- **Unverified:** Every backend profile/device, headless app integration, latency, peak RAM, runtime buffer use, and VRAM.

## Required follow-up

1. Make the 9D graph compile in an isolated target-qualified staging directory and inspect its manifest and graph list; do not replace the older candidate or runtime artifacts.
2. Execute the graph on CPU and compare weighted homographies, mapped points, flow endpoints/scaling, and final warp against the NumPy oracle on the frozen fixtures.
3. Preserve and implement the TPS residual behavior so default `fit_apap` completes; then integrate exact-target loading and run the prescribed app/backend/performance/memory gates.

No product source or TCM was edited by the Inspector. Only this feedback and the status verdict are changed.
