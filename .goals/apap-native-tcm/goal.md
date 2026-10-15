# Goal: APAP Native Taichi TCM

## User Request

> `/copilot-goal-skill:goal berarti APAP ini masih berfungsi pada numpy saja bukan di kompilasi menjadi .tcm pada taichi vision? saya ingin dikompilasikan ke .tcm dan juga seluruh sourch kodenya pindahkan ke taichi vision yang dikelompokan bersama homography, untuk fallback homography pada taichi_vision\taichi_algorithm\alignment\mesh_warp.py saya melihat adanya fallback ke cpu ataupun numpy, saya ingin tidak ada fallback lagi jika tidak mendukung perangkat kerasnya maka tampilkan errornya`

## Refined Goal

Move APAP's production computation into the Taichi Vision alignment family and compile target-qualified TCM graphs so APAP model fitting/field generation and image warping execute through the selected native backend. Keep the existing public APAP/homography facades and callers compatible while reducing the current APAP latency. Remove silent CPU, NumPy, OpenCV, zero-image, and cross-backend fallbacks from `mesh_warp.py`; when the selected backend/device lacks the exact compatible graph, raise an actionable error. Preserve the NumPy implementation only as a test/reference oracle, not as a production fallback.

## Acceptance Criteria

- [ ] APAP weighted local homography fitting, optional residual/TPS behavior, APAP field/flow generation, and image sampling used by production callers have a documented Taichi Vision owner and target-qualified TCM graph. Logs/evidence identify graph and actual backend/device; an existing generic flow-remap TCM alone does not satisfy native APAP fitting.
- [ ] APAP source is grouped with Taichi Vision alignment/homography. Desktop retains only settings, routing, and thin compatibility wiring. Existing public facades (`fit_apap`, `APAPWarp`, `warp_apap`, alignment exports and AOT wrapper entrypoints) continue to work unless a discovered incompatibility is documented and explicitly resolved.
- [ ] CPU, CUDA, Vulkan and OpenGL TCM profiles are compiled/tested independently for the available target identities. Artifacts have matching target/ABI provenance and the required APAP graph manifest. Compile/load success alone is insufficient; each available backend has an execution smoke, while unavailable devices are reported as unverified.
- [ ] No selected native warp path silently switches to NumPy, OpenCV, Taichi JIT CPU, another backend/vendor artifact, unrefined output, or an all-zero image. Missing artifact/graph, target mismatch, or unsupported hardware produces a clear error naming the requested operation and active target. Degenerate local APAP nodes may retain the existing algorithmic global-homography model fallback if parity tests confirm it; this is distinct from hardware/backend fallback.
- [ ] Existing homography behavior and APAP outputs are compared against the preserved NumPy oracle on deterministic global-homography, local-parallax/motion, outlier and degenerate fixtures. Current numerical tolerances remain unchanged; add no tolerance widening. Include final warped image/coordinate and flow-grid endpoint/scaling checks.
- [ ] Existing RGB, RAW/CFA, standalone OFB/AKAZE, and panorama callers are audited. Run focused tests, headless `main_desktop.py` import, and headless application-level APAP integration on available RGB and RAW synthetic/real input. Cancellation, cleanup and facade compatibility are covered where their lifecycle changes.
- [ ] Paired baseline/candidate APAP workloads use identical inputs/configuration/backend/device, warm-up and repeated measurements. Report median latency, peak process RAM, runtime buffers and VRAM when available. Target median latency improves; peak memory never increases. A regression up to 5% is acceptable only if peak RAM decreases. Do not extrapolate one backend to another.
- [ ] TCM candidates are built in isolated target-qualified staging locations. Existing untracked/modified APAP TCMs are hash-backed up before promotion; no target artifact is overwritten or deleted until manifests/references and rollback are verified. `taichi_vision/taichi_aot/engine.py` is not changed.
- [ ] Run venv `py_compile`, relevant pytest, headless app import plus an actual headless integration path, and `git diff --check`. Stage/commit only APAP goal files and task-owned hunks; preserve all unrelated dirty worktree changes.

## Scope Boundaries

**In scope:**
- `taichi_vision/taichi_algorithm/alignment/` APAP model, native kernels, compiler integration, target-qualified TCM graphs, strict runtime resolution, tests and public facades.
- Remove the CPU/NumPy/OpenCV/JIT/zero-image fallback behavior in `mesh_warp.py` for callers that selected a native backend; audit all APAP/homography callers affected by this strict contract.
- Minimal desktop call-site migration in `pixel_refine_desktop` so APAP feature alignment delegates fitting/field generation/warping to Taichi Vision while preserving per-batch settings and public entrypoints.
- Target-specific compile, execution, numerical parity, latency and memory evidence for each available CPU/CUDA/Vulkan/OpenGL backend/device.

**Out of scope:**
- Changes to `taichi_vision/taichi_aot/engine.py`, generic homography/RANSAC algorithm semantics, OFB/AKAZE feature thresholds/matcher behavior, UI redesign, denoising/HDR/SR algorithms, and unrelated artifact rebuilds.
- Removing the NumPy oracle from tests or research APIs; it must simply not be a hidden runtime fallback when native execution is selected.
- Cross-backend fallback, target/vendor/ABI mixing, silent backend changes, and promoting artifacts without runtime/device validation.

## Applicable Project Conventions

**Quality gate command:**
- `venv\Scripts\python.exe -m pytest pixel_refine_desktop\tests\test_pipeline_process_migration.py pixel_refine_desktop\tests\test_algorithm_catalog.py taichi_vision\taichi_algorithm\alignment\test_alignment.py taichi_vision\taichi_algorithm\panorama\test_panorama_alignment.py -q`
- `venv\Scripts\python.exe -m py_compile <changed Python sources>` and headless `import main_desktop` with `QApplication.instance() is None`.
- Compile and run APAP TCM probes independently per actual target/backend; inspect manifests/graph names. Run app-level synthetic/real RAW and RGB tests headless. Use only test files already present where possible.
- Record command, backend, actual device, shape, dtype, result, and evidence level. Baseline handoff: `ai_governance/APAP_RAW_CARRIER_HANDOFF_20261015.md`; task memory: `ai_governance/APAP_NATIVE_GOAL_MEMORY_20261016.md`.

**Commit convention:**
- Goal-skill iteration commits: `type(scope): [B] description` for Builder and `chore(scope): [I] description` for Inspector, each with `Assisted-by:` trailer. Respect stricter root/project instructions and stage only reviewed goal hunks; do not sweep existing user modifications into commits.

**Guidelines:**
- `AGENTS.md`
- `ai_governance/GLOBAL_RULES.md`
- `ai_governance/OPERATING_PROTOCOL.md`
- `ai_governance/MULTI_AGENT_PROTOCOL.md`
- `ai_governance/skills/taichi-aot-dev/SKILL.md`
- `taichi_vision/AOT_BACKEND_MATRIX.md`
- `taichi_vision/documentation/BUILD_AND_VALIDATION.md`
- `ai_governance/APAP_RAW_CARRIER_HANDOFF_20261015.md`

**Rules:**
- Keep `taichi_vision/taichi_aot/engine.py` untouched.
- AOT/APAP TCM graph names must match compiler definitions and runtime dispatch. Verify target ID, vendor, ABI, TCM manifest and bridge provenance; do not select hardcoded sibling/generic artifacts after an exact target failure.
- Use full-frame native execution or report an actionable error; never silently run CPU/NumPy/OpenCV after native dispatch fails.
- The baseline worktree is dirty. Files already modified/untracked, particularly APAP source, mesh warp, compiler/tests and TCM artifacts, are user work. Capture before/after hashes/diffs and stage only task-owned hunks.
- Report backend/device evidence separately. Artifact availability, static validation, graph execution, numerical parity and application-level execution are distinct evidence levels.
