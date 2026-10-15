# Inspector Feedback — Iteration 1

**Verdict: FAIL.** The current delta demonstrates CPU execution of APAP weighted fitting and point mapping through a candidate TCM, but it does not meet the frozen goal's parity, TPS, strict no-fallback, target provenance, integration, backend, performance, or memory gates.

## Independent checks

- Candidate file inspected: `%TEMP%/apap-native-tcm-candidate-20261016/cpu_x86_64_windows/apap_native_cpu_x86_64_windows.tcm`; SHA-256 `acfd283093cf0402e5740afcdc8fcaee032575a58ef5ef4d33791fec3f7e3af5`. Its `graphs.tcb` contains `algn_apap_fit_weighted_f32`, `algn_apap_map_points_f32`, `sparse_mesh_warp_2d_f32`, `sparse_mesh_warp_3d_f32`, and `adaptive_refine_2d_f32`. It has no `tcm_manifest.json`; candidate graph presence does not establish target/ABI manifest provenance.
- I loaded that candidate directly into the active CPU engine and routed the APAP test call to it in an isolated process. Backend/device: `cpu` / Taichi CPU device 0; source correspondences `(48, 2) float64`; query points `(128, 2) float64`. Compared `fit_apap(..., enable_residual_spline=False)` against `fit_apap_reference(..., enable_residual_spline=False)`: maximum absolute coordinate difference `0.3462 px`, mean absolute coordinate difference `0.0389 px`, and maximum Euclidean point difference `0.4699 px`. This is a parity failure/unresolved numerical mismatch, not evidence of equivalent output. No image raster was used in this check.
- Focused command: `$env:PIXEL_REFINE_AOT_ARCH='cpu'; .\\venv\\Scripts\\python.exe -m pytest taichi_vision\\taichi_algorithm\\alignment\\test_alignment.py -k apap -q`. Result: **4 failed, 1 passed, 7 deselected**. Four tests failed because `apap_native` is not present in the active runtime artifact root (`taichi_vision/taichi_algorithm/aot_tcm`); the staged candidate is still in `%TEMP%`. This means current application dispatch is not integrated with the candidate artifact.
- Builder baseline record: `%TEMP%/apap-native-builder-baseline-20261016.sha256`. I independently recomputed hashes for all nine existing `*apap*.tcm` paths listed there; **all nine are unchanged**. The staged candidate did not overwrite or promote any of them.
- Static review confirms `mesh_warp.py` now resolves `apap_native` through the active TCM loader and raises on load/dispatch failure rather than selecting JIT/CPU/OpenCV fallback. However, `apap.py::warp_image` still catches every exception from `warp_image_sparse_mesh` and proceeds to full NumPy coordinate generation plus OpenCV/NumPy sampling (`apap.py` around lines 377–470). The strict no-fallback acceptance criterion therefore remains unmet for that public path.
- The native fit entry point has changed `enable_residual_spline` default from the previous `True` to `False`; passing `True` now raises because no native TPS residual graph exists. The public symbol/signature names remain, but this default/behavior change breaks the prior default APAP behavior and leaves the goal's TPS criterion incomplete.
- Native kernels cover weighted local solve and point mapping, but host work remains in `fit_apap`: global homography estimation, correspondence normalization, centers and Gaussian/top-k weight construction, candidate denormalization/validation, and `to_flow` grid construction/scaling. The RGB path still constructs a sparse mesh on the host, reads native mapped points back, then uploads the mesh for image sampling. No evidence demonstrates fully native field/flow generation or the requested latency improvement.

## Acceptance status

- **Partial:** APAP-specific weighted-fit and point-map graph names exist in the staged CPU TCM and were dispatched successfully on CPU. Public APAP names remain exported. `mesh_warp.py` itself has strict error handling after the current edit.
- **Fail:** Native/default TPS semantics; strict fallback behavior through `apap.py::warp_image`; numerical parity; runtime artifact integration; candidate manifest/provenance; headless application APAP integration; RAW/RGB, OFB/AKAZE, and panorama end-to-end coverage; performance and memory gates.
- **Unverified:** CUDA (NVIDIA MX150), Vulkan (NVIDIA MX150 and Intel UHD 620), OpenGL (available GPU devices). Host inventory reports those devices, but there is no execution evidence for this iteration. No evidence shows headless `main_desktop.py` import or application-level APAP smoke passed.

## Required follow-up before acceptance

1. Restore parity against the NumPy oracle on fixed global-homography, local-motion/parallax, outlier and degenerate fixtures without loosening current tolerances; resolve the `0.4699 px` maximum mapped-point discrepancy.
2. Implement/retain the optional TPS residual behavior in the native route without changing the public default, or document and explicitly resolve the compatibility change before acceptance.
3. Remove the remaining silent fallback in `apap.py::warp_image` when native execution is selected and add a negative test proving missing graph/target raises an actionable error.
4. Produce a target-qualified TCM with manifest/ABI provenance and integrate it through the runtime resolver without overwriting any of the nine baseline artifacts. Execute and record each available backend/device separately.
5. Run the prescribed full focused pytest set, headless app import, and actual headless RGB and RAW/CFA APAP integrations; then collect paired latency and RAM/VRAM measurements against the same worktree baseline.

No product source or TCM was edited by the Inspector. The only planned writes are this feedback and the goal status history.
