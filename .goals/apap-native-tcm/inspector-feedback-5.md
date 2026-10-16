# Inspector Feedback — Iteration 5

**Verdict: FAIL.** The MINRES prototype has target-labelled CPU/CUDA staging candidates and reports small-fixture CPU parity, but the CUDA 841-control TPS solve does not converge, so the RAW flow parity gate fails. The reported CPU timing is slower than NumPy, paired memory evidence is absent, and no runtime artifact or application integration was promoted.

## Independent inspection of the recorded iteration

- Commit `1fa27a4e` changes only `taichi_vision/taichi_algorithm/alignment/apap.py` and `compile_mesh_warp_tcm.py`; it contains no `.tcm` artifact. The source adds a TPS KKT-system builder, MINRES initialization/step kernels, and a point-map kernel. The compiler registers fit/map plus MINRES buckets and TPS map.
- Compiler graph semantics: `compile_mesh_warp_tcm.py:187-221` creates a separate graph for each iteration bucket and appends one `_tps_minres_step_kernel` dispatch per iteration. `apap.py:922-935` selects the bucket, using 2048 iterations for systems larger than 512. `apap.py:958-963` checks the solver's convergence state and raises if it did not converge; this is fail-closed rather than silently returning the partial solution.
- I inspected the staged CPU candidate `%TEMP%/apap-native-tcm-i5-minres-cpu-20261016/cpu_x86_64_windows/apap_native_cpu_x86_64_windows.tcm`, SHA-256 `5b83b48b8d2de4d4a1bf8da1f5d33afa3d02923293780368caa1a69aba7bc77a`. Its manifest targets `cpu_x86_64_windows` and lists APAP/TPS graphs. The staged CUDA candidate `%TEMP%/apap-native-tcm-cuda-minres-i5-20261016/cuda_x86_64_windows_nvidia/apap_native_cuda_x86_64_windows_nvidia.tcm`, SHA-256 `7c4b2d9837924df90fbd48c42578fc8366fa059bbd681821f9f1b4a99618ea35`, targets `cuda_x86_64_windows_nvidia` and contains the same graph set including the 2048-step graph. Both are outside the runtime artifact tree. Their `compiler_version` manifest value is only `taichi-(1, 7, 4)` and does not identify the LLVM/bridge build, so full ABI provenance is not established by this field alone.
- Builder's recorded CPU results: 300-point local-parallax APAP max error `0.02030 px`; 16-control TPS max error `6.15e-5 px`. These are narrow fixture reports, with no command/raw logs here for independent replay. The same status reports native time `1.894 s` versus NumPy `1.427 s` (about 32.7% slower), with no paired RAM/VRAM comparison. That does not satisfy the accepted latency gate.
- Builder's recorded CUDA result on MX150, 841-control TPS: MINRES did not converge after 2048 iterations; residual ratios were `5.0114e-4` and `2.0791e-3`. Consequently, no final TPS flow parity exists for the critical workload. I did not rerun this expensive solve, as requested.
- Runtime artifact inspection found zero `apap_native` files under `taichi_vision/taichi_algorithm/aot_tcm`. The two candidates remain in `%TEMP%`; commit `1fa27a4e` contains only the two source/compiler paths and no TCM. No product APAP artifact was promoted.
- No iteration 5 full pytest, `py_compile`, headless `main_desktop.py`, RGB/RAW application integration, Vulkan/OpenGL test, full APAP parity matrix, or paired memory evidence is recorded. Prior iteration 4 APAP baseline artifacts were hash-verified unchanged; this iteration has no product TCM commit or runtime `apap_native` promotion.

## Acceptance status

- **Partial:** MINRES fit/TPS kernels and target-named graph registration exist; CPU and CUDA staging archives include manifests and graph names; a few small CPU fixtures are reported as close to the NumPy oracle.
- **Fail:** Critical CUDA TPS fixture fails convergence and therefore lacks flow parity; CPU timing is reported slower than NumPy with no compensating memory reduction; the exact target artifact is not integrated; full TPS/APAP default production behavior is not demonstrated.
- **Unverified:** Independent replay of the small CPU fixtures and the claimed CUDA load/run; Vulkan/OpenGL; headless app paths; DNG output; peak RAM/VRAM methodology; exact compiler/bridge ABI beyond target ID.

No tests or expensive workloads were rerun. No product source or TCM was edited. Only this feedback and the status verdict are changed.
