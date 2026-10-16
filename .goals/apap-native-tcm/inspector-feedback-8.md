# Inspector Feedback — Iteration 8

**Verdict: FAIL.** The OFB/AKAZE per-batch persistence path now has a focused actual-QComboBox test and fail-closed JSON verification. The APAP acceptance gate fails on the reported real-DNG comparison, and no candidate TCM is integrated into runtime.

## Batch persistence review

- Commit `4e5c38c4` changes only `right_panel.py` and `batch_selection_handler.py`. Switching batches flushes the prior batch before changing `current_batch_id`. Single Start calls `snapshot_settings_for_start`; Process All flushes before opening its processing dialog. Flush writes the visible alignment page and card state, calls `DataStore.save_to_file()`, then reloads JSON and compares it to in-memory data. A missing file binding, save/read error, or mismatch raises before dispatch.
- Focused command: `PIXEL_REFINE_AOT_ARCH=cpu .\\venv\\Scripts\\python.exe -m pytest pixel_refine_desktop\\tests\\test_algorithm_catalog.py::test_real_alignment_dropdown_flushes_before_batch_switch_start_and_process_all -q` — **2 passed** (OFB and AKAZE; one Taichi deprecation warning). It uses actual Qt combo controls, `AlignmentParameterPage`, and a DataStore bound to a temporary JSON file; it exercises APAP selection, batch 7/8 switching and reload, Start/Process All snapshots, and failed-save rejection. Start and Process All dispatch are represented by a lightweight harness/fake dialog, not a full worker run.
- Headless command: `PIXEL_REFINE_AOT_ARCH=cpu QT_QPA_PLATFORM=offscreen .\\venv\\Scripts\\python.exe -c "import main_desktop; from PySide6.QtWidgets import QApplication; assert QApplication.instance() is None"` — passed; no `QApplication` was created.
- `git diff --check` on changed UI, test, and APAP paths produced no whitespace diagnostics; only CRLF normalization warnings appeared.

## APAP review

- Builder's iteration 8 real-DNG report: B001/B002 at `(1536,2048,3) uint8`, OFB reported 106 inliers. Candidate output was finite, but field error was max `74.936 px`, mean `9.768 px`; native fit/field time `1.116 s` versus NumPy `0.789 s`. This fails the revised `<=1 px` error and `>=2x` speed gates on the reported real input. A 16x residual grid failed the Jacobian gate and an 8x grid was inaccurate; Builder reports restoring those experiments.
- Iteration 7's CUDA synthetic metrics (max error `0.819924 px`, `16.55x`, RSS decrease `67.78 MiB`) do not outweigh the real-DNG failure. Builder reports no saved/validated DNG result, and the synthetic OFB/AKAZE adapter smoke injected correspondences instead of exercising actual feature extraction.
- Current APAP source is clean relative to the reviewed baseline commit for iteration 8; Builder reports the failed grid prototypes were restored. Runtime artifact inventory has zero `apap_native` TCMs. No candidate TCM was promoted, so a normal runtime load of `apap_native` remains unavailable. CPU/CUDA candidates remain staging artifacts; Vulkan/OpenGL, VRAM, and complete compiler/bridge ABI proof remain unverified.

## Acceptance status

- **Pass, limited:** OFB/AKAZE settings flush, batch isolation/reload, Start/Process All ordering test (2/2), failed-save rejection, headless `main_desktop` import, and scoped diff-check.
- **Fail:** Real-DNG APAP error and latency thresholds; CPU speed gate from the prior reported fixture; no APAP TCM integrated into runtime.
- **Unverified:** Full worker/application dispatch, persisted DNG output, production feature extraction, Vulkan/OpenGL, VRAM, and exact target bridge ABI.

No APAP/DNG workload was rerun by the Inspector. No product source or TCM was edited. Only this feedback and the status verdict are included in the process commit.
