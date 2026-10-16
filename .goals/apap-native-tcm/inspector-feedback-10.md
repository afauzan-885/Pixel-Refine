# Inspector Iteration 10 — FAIL

## Scope reviewed

Reviewed frozen goal, iteration 10 PRD and user decisions, Builder commit `57644e8`, the APAP source/test changes, and the recorded execution evidence. No product source, test, or TCM was changed by this review.

## Findings

- **Partial static requirement met:** APAP local fitting and TPS no longer use `argpartition`/control sampling or an active control cap. The native weighted-fit kernel iterates the supplied row count. The legacy sampling helper/constants remain but are not called by the production fit path.
- **Correspondence preservation is not end-to-end:** the resident pipeline still calls `filter_apap_correspondences` before APAP fitting (`pixel_refine_desktop/enhance_stack/core/algorithm/denoising/pipeline_process/resident_pipeline.py`, around lines 1817–1834). That means the production caller can still discard rows before they reach the now all-row fit; this conflicts with the iteration 10 instruction to trust its selected correspondences.
- **Native/APAP production gate failed:** Builder evidence records CUDA N=841 fit median/runtime 105.783 s, with no paired baseline and thus no demonstrated >=2x improvement. The N=841 evidence does not establish the required latency gate. Runtime has no promoted `apap_native` TCM; candidates were reported as remaining in Temp. I did not independently inspect a candidate manifest/hash in this closeout, so manifest/hash consistency is **unverified**.
- **Parity evidence is incomplete:** recorded CPU native parity is for N=122 (max error 0.000756 px, mean 0.000154 px), and CUDA N=841 reports max 0.076944 px / mean 0.022544 px. These do not establish the required adversarial distributions and full production/APAP-TPS path across the target matrix. The new all-row tests exercise the NumPy reference path; native count/order parity is not demonstrated.
- **Test evidence is not clean:** the focused alignment suite result recorded for this iteration is 9 failed, 5 passed, and 4 subtests passed. Missing runtime `apap_native` TCM causes native APAP execution failures; other failures also remain. `py_compile`, headless `main_desktop` import without creating `QApplication`, and `git diff --check` passed, but these do not establish application algorithm behavior.
- **Unverified:** CUDA paired performance, peak RAM, Vulkan/OpenGL profiles, actual end-to-end DNG/APAP output, and production TCM manifest/hash. The 105.783 s CUDA workload was not rerun.

## Verdict

**FAIL.** Source changes address in-fit row sampling, but correspondence preservation is not complete at the resident caller, the N=841 performance gate is missed/unpaired, required target artifacts are not promoted, and runtime/backend/application acceptance remains incomplete. Do not treat this iteration as accepted or production-ready.
