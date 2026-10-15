# APAP Native TCM — Task Memory

- Date: 2026-10-16.
- applies_to: requested goal to move APAP implementation into `taichi_vision/taichi_algorithm/alignment`, compile/run it through target-qualified TCM, preserve callers with thin facades, optimize the slow path, and fail clearly if active hardware lacks native support.
- Status: discovery complete; immutable `.goals/apap-native-tcm/goal.md` is frozen; implementation pending. No code changed for this goal yet.
- Reuse rule: this is the active baseline/coverage/handoff for the goal. Refresh status and current evidence before reuse.

## User decisions

- Goal workflow: invoke `copilot-goal-skill:goal`; maximum agents = 2, one Goal Builder and one Goal Inspector.
- API/callers: preserve public facades/aliases where practical; move implementation core, do not gratuitously break existing callers.
- Backend gate: CPU, CUDA, Vulkan, OpenGL on profiles/devices available here; each backend is separate evidence. If unavailable, mark unverified.
- Unsupported device behavior: explicit actionable error; no silent CPU/NumPy fallback from a selected native backend.
- Parity/performance: compare against current worktree baseline/NumPy oracle with existing numerical contracts; optimize median APAP latency and do not increase peak RAM/VRAM. Earlier project preference permits at most 5% latency loss only when peak RAM decreases; exact limits to be reflected in final criteria after source discovery.

## Baseline

- Git HEAD: `7bde21c30b4f572475373089b76e3a532267e954`.
- The checkout has extensive pre-existing uncommitted changes. Preserve all of them; only task-related hunks may be staged/committed.
- APAP/mesh-warp source already exists as user work in this checkout: `taichi_vision/taichi_algorithm/alignment/apap.py` is modified; `mesh_warp.py`, `compile_mesh_warp_tcm.py`, `test_alignment.py`, and APAP sparse-mesh TCM files are untracked. They contain prior task work and are part of the baseline; inspect before editing or compiling over artifacts.
- Existing handoff: `ai_governance/APAP_RAW_CARRIER_HANDOFF_20261015.md`.
- Handoff evidence from the prior task: CUDA MX150/logical0, 12 real DNG, `(3072,4096) uint16` sensor, `(1536,2048,3) float32` analysis. Raw carrier received local AOT flow `(33,33,2)` for 11/11 OFB supports. AKAZE on one real pair had only one match and did not produce a transform. A warm single-support fit comparison using 841 real correspondences reported median `6.25s` at grid33 versus `3.96s` at grid17, with spline active and identical sampled flow; full pipeline time did not materially improve (46.87s vs 47.02s). Model fitting still uses CPU/NumPy. Treat these as scoped historical evidence, not universal backend claims.
- Discovery agent confirmed APAP core (`filter_apap_correspondences`, `_weighted_homography`, `fit_apap`, `APAPWarp.map_points`, `to_flow`) is already located under Taichi Vision, but implemented with NumPy/CPU. Existing `mesh_warp.py` kernels/TCM cover sparse 2D/3D image sampling and adaptive refine only; there is no AOT moving-DLT/local fit or APAP field-generation graph.
- Desktop RAW APAP flow: resident feature matching/RANSAC -> NumPy residual filtering and APAP fit/map -> upload `(33,33,2)` -> generic `remap_with_flow` / CFA AOT. Desktop RGB and standalone OFB/AKAZE read images back to NumPy and call `warp_apap`; panorama/stitch has two direct `fit_apap` callsites. Public facades include `taichi_vision.taichi_algorithm.aot_api.warp_apap`, `aot_wrapper.warp_apap`, alignment package exports, and `APAPWarp`/`fit_apap`.
- Confirmed silent fallback sites: `mesh_warp.py` attempts the active target plus hardcoded/vendor-neutral and generic backend artifact paths, swallows load failures, may return `None`; `warp_image_sparse_mesh` downloads GPU input to NumPy before dispatch, catches AOT exceptions, then tries Taichi JIT (including CPU init), OpenCV remap, then returns a zero image/mask. Adaptive-refine errors are swallowed and the unrefined warp returned. `apap.py:warp_image` falls through from mesh/AOT failure to NumPy/OpenCV. User's no-fallback request should eliminate these device/backend substitutions while preserving documented APAP model global-H fallback for degenerate local nodes.
- Artifact audit: nine existing APAP TCM archives are untracked. Exact CUDA NVIDIA and its APAP alias share hash prefix `1ca3bc...`; Vulkan/OpenGL local TCM manifests are vendor-neutral while detected local target IDs may include vendor. Existing archives contain only sparse-mesh/refine graphs, not local fitting. Never compile in-place; preserve each file, stage candidate artifacts separately with manifests/provenance, and promote only after tests. Filenames alone do not prove target ABI.
- Discovery found an extensive dirty tree, including target/compiler/tests and `taichi_vision/taichi_aot/engine.py`; engine is out of scope and must remain untouched. Existing APAP tests are in untracked `taichi_vision/taichi_algorithm/alignment/test_alignment.py`, panorama tests in `taichi_vision/taichi_algorithm/panorama/test_panorama_alignment.py`, and desktop migration/catalog tests; no test currently proves native APAP fitting or strict no-fallback behavior.
- Static backend inventory: venv Taichi 1.7.4/LLVM20.1.5 exposes CPU/CUDA/Vulkan/OpenGL; NVIDIA GeForce MX150 and Intel UHD 620 are visible. This is inventory only, not runtime qualification. Handoff suggests CUDA MX150, Vulkan NVIDIA plus Intel, OpenGL Intel, and CPU be reported independently if they can run; unavailable profiles stay unverified.
- Discovery quality-gate scan: no root `CONSTITUTION.md`, Makefile, justfile, package.json or commit guideline was found in the targeted search. Root AGENTS and AI governance are normative; focused pytest/headless/device commands are listed in the frozen goal file.

## Coverage and delegation record

| Agent | Role | Coverage | Status / restrictions |
|---|---|---|---|
| Coordinator `/root` | Integrator | Full goal, acceptance and final validation | Must preserve dirty user work and integrate independently |
| Agent 1 | `explorer` (Goal-skill Builder model launch failed before execution: GPT-5.6 Luna (copilot) unsupported for this account) | Read-only discovery of APAP source/call graph, fallback sites, artifact target provenance, tests and host inventory | Discovery complete. Reuse for independent final inspection; no edits |
| Agent 2 | `worker` (supported Builder substitute) | Implement only the frozen `.goals/apap-native-tcm/goal.md` after discovery | Use selected-hunk staging because target files already contain user work; no broad staging |

Multi-agent approval: explicit user invocation of goal workflow and user limit 2. The goal-skill-specific Builder model is unsupported by this account, so use supported `worker` and `explorer` roles while preserving the separate implementation/review duties. The failed model launch terminated before reading/editing. Reuse Agent 1 for inspection so total agents remains two. No overlapping edits: inspection is read-only apart from goal feedback/status artifacts.

## Initial risks and constraints

- `taichi_vision/taichi_aot/engine.py` is runtime source of truth; do not edit it.
- Do not replace, delete, or move TCM/DLL/BC artifacts until target ABI, graph manifest, runtime resolution, and rollback copy are verified. Compile candidates separately first.
- `mesh_warp.py` is used by APAP and other alignment/panorama callers; removing generic CPU/NumPy fallback has broader effects. Trace each caller and make unsupported device/backend failures explicit without changing unrelated algorithms.
- Preserve NumPy implementation as an oracle/test reference if useful, but production dispatch under a native backend must not fall through to it.
- Keep APAP (moving DLT/local warp) grouped with homography/alignment in Taichi Vision. Desktop may retain parameter/UI and thin compatibility wiring only.
- Geometry direction, coordinate scale, local correspondence filtering, optional TPS residual, image bounds, cancellation, CFA flow interpolation, and mesh endpoint convention are parity risks.
- No new temporary scripts should be added to the repository. Extend existing tests/compiler when possible. Existing external harness files are evidence only and may not be treated as tracked product source.

## Planned gates

1. Discovery: enumerate public exports/callers, current CPU/native paths, image and point transfer sites, APAP algorithm sources, compiler graphs, target-specific TCM hashes/manifests, and available tests/device inventory. Record exact paths in `.goals/apap-native/goal.md`.
2. Native parity: test moving-DLT/local field and final warped coordinates against the NumPy oracle using fixed synthetic homography, parallax/local-motion, outlier and degenerate fixtures. Do not weaken existing tolerances.
3. Native integration: headless `main_desktop.py` import plus a headless actual MFDenoiser APAP burst for RAW and RGB where available. Logs must show TCM graph/backend execution and selected local APAP; missing artifacts must raise a clear error.
4. Backend evidence: run each available CPU/CUDA/Vulkan/OpenGL profile/device independently. Never infer support from compile/load alone.
5. Performance/memory: warm-up and repeated, paired baseline/candidate runs with identical inputs/configs. Record median latency, peak process RAM and VRAM. Do not accept >5% slowdown unless peak RAM falls; do not accept increased peak memory. Mark absent measurements unverified.
6. No-fallback proof: force the native graph/device unavailable in a test and assert a diagnostic error, not NumPy/CPU warp.
7. Hygiene: `py_compile`, relevant pytest, headless app smoke/integration, target-manifest/ABI provenance, and `git diff --check`; stage only task hunks/files.

## Shared handoff / next action

Correction 2026-10-16: the frozen goal is `.goals/apap-native-tcm/goal.md` (not the earlier draft path shown in the initial next-action bullets). The Goal-skill Builder model launch is unsupported on this account; proceed with the supported worker substitute and reuse the explorer for independent inspection.

Inspector iteration 1 independently reproduced native-vs-oracle max mapped-point error `0.4699 px`, mean absolute error `0.0389 px`; focused APAP pytest had 4 failed/1 passed because the runtime TCM root lacked `apap_native`. It also found TPS default changed to unsupported, no candidate manifest, and remaining catch-to-NumPy/OpenCV in `apap.py::warp_image`. Verdict FAIL. Iteration 2 is rebuilding only from the immutable goal and this feedback; parity, TPS, strict fallback and artifact integration remain hard gates.

Iteration 1 update: discovery is complete, `.goals/apap-native-tcm/goal.md` is immutable, and supported worker returned a partial implementation. It changed only `apap.py`, `mesh_warp.py`, and `compile_mesh_warp_tcm.py`; the staged CPU TCM candidate (not promoted) is `%TEMP%\apap-native-tcm-candidate-20261016\cpu_x86_64_windows\apap_native_cpu_x86_64_windows.tcm`, SHA256 `ACFD283093CF0402E5740AFCDC8F8CAEE032575A58EF5EF4D33791FEC3F7E3AF5`.

Native fit/map compile and dispatch on CPU succeed, but a fixed 29-pair local-motion fixture has native-vs-NumPy mapped-point max difference `0.3735 px`, mean `0.1796 px`. Fit uses an 8-parameter normal equation instead of weighted 9D SVD. TPS residual is not implemented natively and production `apap.py:warp_image` still retains fallback behavior. No full pytest, app import/integration, GPU, TPS, benchmark, or memory gate passed. No artifact was promoted; the nine original APAP TCM hashes are reported unchanged. Inspector review is the next action.

- Builder discovery result: append a dated section here before implementation and copy verified facts into the goal file.
- Goal artifacts will live at `.goals/apap-native/goal.md`, `status.json`, feedback files and summary.
- Next: finalize immutable `.goals/apap-native/goal.md` from the discovery facts, ask the supported worker to implement it, then reuse the explorer for independent inspection.
