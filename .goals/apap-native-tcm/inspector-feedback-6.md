# Inspector Feedback — Iteration 6

**Verdict: FAIL.** The pivoted TPS solve runs as one registered AOT graph, but that graph contains two native kernel dispatches (KKT system construction followed by the pivoted solve). A small CPU fixture is reported close to the NumPy oracle; the measured fit is 2.45× slower. There is no large-fixture CUDA result, runtime integration, or artifact promotion.

## Independent review

- Commit `747ec9b60bd1820f942eb92b619df7cfb3f82690` changes only `apap.py` and `compile_mesh_warp_tcm.py`; no TCM is committed.
- In `compile_mesh_warp_tcm.py:181-196`, graph `algn_apap_tps_pivoted_f32` contains two `GraphBuilder.dispatch` calls: `_build_tps_system_kernel` and `_solve_tps_pivoted_kernel`. The solver itself is one Taichi kernel (`apap.py:23`), with pivot iterations and elimination loops executed in that kernel. Runtime calls the single graph at `apap.py:980`. This is one graph and a native solve, but it is not one kernel for the complete KKT solve; matrix construction is a second native dispatch. The coefficients are produced in the TCM, while host-side condition checking follows readback.
- Staged CPU TCM: `%TEMP%/apap-native-i6-pivoted-cpu-20261016/cpu_x86_64_windows/apap_native_cpu_x86_64_windows.tcm`, SHA-256 `3157dbb7ed3fe1f42cceb77d329b22cf8d27eeeff38ec512db5b6d9e2cc7b42f`. Its manifest targets `cpu_x86_64_windows` and lists `algn_apap_tps_pivoted_f32` plus APAP fit/map and TPS map. Manifest compiler version remains the generic `taichi-(1, 7, 4)` string, without LLVM/bridge identity evidence.
- This candidate is outside `taichi_vision/taichi_algorithm/aot_tcm`; an independent inventory found zero runtime `apap_native` files. The iteration 6 commit contains only source/compiler paths, so it did not promote the staged candidate. The prior iteration 5 CUDA MINRES TCM does not contain this pivoted solver graph and is not CUDA evidence for commit 747ec9b.
- Builder-recorded CPU smoke: 16 TPS controls and 128 query points, max parity error `7.038e-5 px`; the status records a warm fit median `3.133 ms` versus NumPy `1.277 ms` (2.45× slower) and one-run RSS `109.09 MiB`. These are narrow Builder-reported results; the status has no raw command/log or paired memory baseline. Thus they do not pass the full parity/performance/memory criteria.
- No iteration 6 841-control CUDA solve or CUDA pivoted TCM exists in the available candidate directories. The prior 841-control MINRES solve did not converge, but that is prior-iteration evidence. No current 841-control flow parity should be inferred. I did not run or repeat the expensive fixture.
- No iteration 6 full pytest, `py_compile`, headless application import, DNG/RGB/RAW integration, full backend matrix, or paired RAM/VRAM gate is recorded. The normal runtime loader still cannot dispatch this candidate because it remains in temp staging.

## Acceptance status

- **Partial:** A single target-resolved AOT graph performs native KKT build and pivoted solve; the solver kernel is inside TCM. Small CPU parity is reported for one fixture.
- **Fail:** Runtime artifact integration and target ABI provenance remain incomplete; CPU timing is substantially slower with no paired memory reduction; no full TPS/APAP parity; no CUDA result for the new solver; no production/app integration or complete goal gates.
- **Unverified:** CPU smoke replay, 841-control pivoted TPS parity, CUDA/Vulkan/OpenGL, DNG output, headless app tests, and paired peak memory.

No tests or large workloads were rerun. No product source or TCM was edited. Only this feedback and the status verdict are changed.
