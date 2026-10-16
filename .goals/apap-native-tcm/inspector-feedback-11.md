# Inspector Iteration 11 — FAIL

## Review scope

Reviewed the iteration 10 PRD and user decision, Builder commit `d78f5c07`, current APAP source, current resident-pipeline worktree hunk, and the isolated candidate test evidence. No product code or TCM was edited.

## Verified findings

- `apap.py` no longer contains `argpartition`, `_sample_tps_control_indices`, or `MAX_NATIVE_TPS_CONTROLS`; `max_controls_per_node` remains in compatible signatures/documentation but is ignored by production fitting. `filter_apap_correspondences` remains defined as an explicit helper, and source search finds no production call to it.
- The resident caller applies the returned RANSAC inlier mask through `_select_ransac_inlier_correspondences`, preserving selected input order. The two call sites are mutually exclusive branches for resident versus host match representations; they do not filter the same correspondence set sequentially. The worktree-only call-site hunk is inside the already dirty `resident_pipeline.py` and remains uncommitted; it was inspected but not edited by this review.
- Added tests cover 841 input rows in the NumPy reference fit, mask order/shape validation, GPU-mask readback, and adversarial reference layouts. The 841-row test is not a native kernel count/order assertion.
- Isolated CPU candidate test command passed: `PIXEL_REFINE_AOT_TCM_ROOT=<Temp>/apap_iter10_cpu_20261016/cpu_x86_64_windows PIXEL_REFINE_AOT_ARCH=cpu .\\venv\\Scripts\\python.exe -m pytest taichi_vision\\taichi_algorithm\\alignment\\test_alignment.py::TestAlignment::test_apap taichi_vision\\taichi_algorithm\\alignment\\test_alignment.py::TestAlignment::test_apap_reference_keeps_all_correspondences_across_adversarial_layouts pixel_refine_desktop\\tests\\test_algorithm_catalog.py::test_apap_full_input_keeps_all_841_control_rows_without_sampling pixel_refine_desktop\\tests\\test_algorithm_catalog.py::test_apap_caller_applies_ransac_mask_once_and_preserves_order -q` — 4 passed, 4 subtests passed, 4.99 s. The environment was CPU; candidate artifact was isolated in Temp. This does not qualify CUDA/Vulkan/OpenGL or prove end-to-end application behavior.
- No production `apap_native` TCM was promoted. The iteration 10 CPU candidate manifest identifies target `cpu/x86_64/windows`, but this review did not verify its payload hash against a Builder baseline. No runtime artifact was changed.

## Acceptance gaps

- The recorded CUDA N=841 APAP/TPS runtime remains 105.783 s with no paired NumPy baseline, so the PRD's >=2x median speed gate is not met or demonstrated.
- Native 841-row count/order evidence, paired RAM/VRAM, full adversarial native distribution matrix, other available backends, and real DNG/application output remain unverified.
- The focused candidate test is a bounded CPU smoke; it is not an acceptance result for all APAP goals.

## Verdict

**FAIL.** The second correspondence filter is removed from the production path and the in-fit code preserves supplied rows, but required performance and cross-target/native full-row qualification gates remain unmet or unverified. Keep APAP TCM candidates isolated; do not promote them.
