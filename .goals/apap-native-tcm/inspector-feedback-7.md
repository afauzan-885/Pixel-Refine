# Inspector Feedback — Iteration 7

**Verdict: FAIL.** The revised approximate gate is met only by the reported synthetic CUDA benchmark; production integration and several available-target gates remain unverified, while the CPU latency result regresses. The per-batch flush path is implemented and its focused ordering test passes, but the test uses a synthetic parameter-page/dialog harness rather than exercising the actual widget callback through application processing.

## Verified results

- Reviewed commit `c0aa4fc2` and the current follow-up source changes. `AlignmentParameterPage` connects dropdown changes to `_save_current_config`, exposes `flush_pending_config`, and writes batch-keyed OFB/AKAZE config to the DataStore bound to `database/align/batch_parameter.json`. `RightPanel.snapshot_settings_for_start` and Process All call the synchronous flush, which saves parameter-page values, the active batch's selection/checkbox values, then calls `DataStore.save_to_file()`.
- Focused command `PIXEL_REFINE_AOT_ARCH=cpu .\venv\Scripts\python.exe -m pytest pixel_refine_desktop\tests\test_algorithm_catalog.py::test_start_flushes_active_batch_warp_settings_before_runtime_snapshot -q`: **1 passed**. The test uses a `ParameterPage` stub and a fake ProcessDialog; it validates the flush ordering, JSON reload, and batch isolation, but does not emit a change from the real alignment dropdown and then run an actual worker.
- Headless command `PIXEL_REFINE_AOT_ARCH=cpu QT_QPA_PLATFORM=offscreen .\venv\Scripts\python.exe -c "import main_desktop; from PySide6.QtWidgets import QApplication; assert QApplication.instance() is None"`: passed; `main_desktop` imported without creating `QApplication`.
- `git diff --check` on the changed UI/test/APAP paths printed no whitespace diagnostics; only Windows line-ending warnings appeared.
- Builder reports synthetic CUDA MX150 benchmark at 841 correspondences and 1089 queries: NumPy median `1186.728 ms`, RSS `282.40 MiB`; candidate median `71.714 ms`, RSS `214.62 MiB`; max field error `0.819924 px`, mean `0.093663 px`, and nonzero maximum TPS displacement `9.159710 px`. These meet the revised numeric/throughput/RSS thresholds for that synthetic fixture, but the user decision requires the same persisted 841-control workload; the recorded fixture is explicitly synthetic and does not verify a real DNG correspondence set.
- Builder reports CPU 841-control native median `0.886 s` versus NumPy `0.426 s`, which misses the at-least-2x speedup gate for CPU. The CPU path is available and has no paired memory reduction reported.
- Synthetic OFB/AKAZE adapter smoke is reported on CUDA MX150 with `(96,128,3) float32` images and `(81,2) float32` injected correspondences. It exercised the APAP/TPS/map/sparse-warp graphs, but bypassed production feature extraction/matching. It is not a full application or real DNG validation.

## Artifact and remaining gate status

- CPU candidate SHA-256 `bddf1c12c345ee0de2ec05e003ea628877b522834f9064989599be688f3cb5c4`; CUDA MX150 candidate SHA-256 `d29b4a807285315143b35f1f1518bd678ad1a01861d2f45bb809c60bdfe2b4ef`. Both staged manifests identify their target and expected APAP/TPS/warp graphs, but `compiler_version` contains only `taichi-(1, 7, 4)` and does not name LLVM or bridge build identity. Both TCMs remain in `%TEMP%`; the runtime artifact tree has no `apap_native` TCM, and no candidate was promoted.
- Real DNG output, production OFB/AKAZE feature extraction, full headless APAP application flow, CPU performance acceptance, Vulkan/OpenGL, paired VRAM, full test suite, and complete compiler/bridge ABI provenance are unverified or fail the current gate.

No source or product TCM was edited by the Inspector. The feedback and goal status are the only process files for this iteration.
