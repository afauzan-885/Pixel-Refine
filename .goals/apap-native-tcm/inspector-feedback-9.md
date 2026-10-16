# Inspector Feedback — Iteration 9

**Verdict: FAIL.** The iteration is diagnostic-only and makes no production changes. The recorded real-data OFB/AKAZE results are far outside the revised APAP approximation gate and include foldovers; there is no native artifact or runtime integration.

## Evidence review

- Read the frozen goal, iteration 7 user decision, prior Inspector feedback, and status history. The user's revised acceptance still requires maximum displacement error `<=1 px`, at least `2x` speedup on the same persisted 841-control workload, no peak RAM increase, preserved local TPS deformation, and explicit unsupported-target errors.
- Status records that local-only APAP without optional TPS was faster for real OFB (`371.576 ms` versus NumPy `1854.026 ms`) but had maximum field error `12341.143 px` and `8.17%` negative-Jacobian grid cells. The AKAZE diagnostic had maximum error `231.485 px` and `11.85%` foldovers. TPS-enabled excursions were also reported as pathological. No commands, raw logs, dimensions/dtypes, or output DNG were added for independent replay. These metrics are Builder-reported and sufficient to fail the stated accuracy/local-warp quality gate; the Inspector did not rerun any APAP/DNG workload.
- Worktree inspection shows the reviewed `apap.py` and compiler are clean relative to HEAD, consistent with the report that grid/residual experiments were restored. The only commit cited for UI batch-flush work, `4e5c38c`, changed `right_panel.py` and `batch_selection_handler.py`. No iteration 9 production APAP changes are committed.
- Runtime inventory still has no `apap_native` TCM. The older sparse-mesh TCMs remain separate pre-existing user artifacts; no native APAP candidate was promoted in iteration 9. Thus production runtime dispatch for native APAP remains unavailable.
- The per-batch OFB/AKAZE UI path had already passed the focused actual-QComboBox test (2/2) in iteration 8, including batch switch/reload, Start/Process All flush, and failed-save blocking. Headless `main_desktop.py` import and scoped `git diff --check` also passed in that iteration. Those UI results do not address the failing APAP field quality.
- Backend qualification, a persisted 841-control real-DNG performance comparison, peak RAM/VRAM, and full application output remain unverified. Since the diagnostic reports fail the approximation and foldover gates, further promotion is not supported by current evidence.

No tests, compiles, or APAP/DNG workloads were run in this Inspector turn. No product source or TCM was edited. Only this feedback and the status verdict are process changes.
