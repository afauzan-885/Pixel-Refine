# Pixel Refine Agent Knowledge Base

This file is the project-level knowledge base for AI and human contributors.
Normative rules remain in `ai_governance/`; user-facing API documentation is
under `taichi_vision/documentation/`.

## Agent operating contract

Before changing code, read:

1. `ai_governance/README.md` and the relevant governance documents;
2. this file, `skill.md`, and `blueprint_project.md`;
3. `ai_governance/skills/taichi-aot-dev/SKILL.md` for Taichi AOT work;
4. the target file, callers, configuration, current Git status, and existing
   tests.

For multi-agent work, follow `ai_governance/MULTI_AGENT_PROTOCOL.md`. Do not
launch agents without explicit developer approval and a user-provided limit.

Non-negotiable barriers:

- Preserve public Taichi API compatibility unless the user explicitly approves
  an API change.
- `taichi_vision/taichi_aot/engine.py` is the runtime source of truth; do not
  change it without explicit approval.
- An unvalidated block path must recover through the same-backend full-frame
  path or report an actionable error. Never silently substitute CPU.
- Do not claim support, accuracy, performance, or production readiness without
  reproducible backend/device/shape/dtype/command/result evidence.
- Do not stage or commit unrelated dirty-worktree changes; never use
  `git add -A` for this repository.
- Use `apply_patch` for code/document edits and preserve user changes.

## Current runtime architecture

```text
Pixel Refine application
  -> taichi_vision.taichi_aot (stable compatibility facade)
  -> taichi_algorithm.aot_api (public dispatch, dtype and block policy)
  -> taichi_aot.engine (one lifecycle/context/bridge owner)
  -> target-qualified bridge + taichi_c_api + TCM
  -> CPU / CUDA / Vulkan / OpenGL / GLES driver
```

The public import is:

```python
from taichi_vision import taichi_aot as aot
```

`artifact_targets.py` and `target_manifest.json` resolve backend, OS,
architecture, ABI, vendor, and device identity. Device ordinals are hints;
renderer/vendor mismatch is an explicit initialization error.

## Current implementation snapshot

Scope: Windows desktop x86-64, snapshot 2026-08-17.

- Runtime: custom LLVM20 Taichi 1.7.4 runtime in the project environment.
- Desktop target trees: `cpu_x86_64_windows`,
  `cuda_x86_64_windows_nvidia`, `opengl_x86_64_windows`, and
  `vulkan_x86_64_windows`.
- Inventory observed by audit: 69 TCM archives per desktop target (276 total).
  Artifact presence is not runtime qualification.
- Public `aot_api` catalog: 115 non-underscore function entry points,
  documented in `taichi_vision/documentation/API_USAGE.md`.
- Full-frame is the correctness and recovery baseline. Native block execution,
  OpenGL native graphs, and recorded pipelines remain guarded optimizations.
- Allocation caching and tile-result caching are separate, bounded policies.
  Adaptive memory may choose full-frame; automatic pipeline does not imply
  concurrent independent block execution.

## Observed evidence and limits

The current fast hardware evidence recorded in
`ai_governance/CURRENT_IMPLEMENTATION.md` is:

| Backend | Device | Result |
|---|---|---:|
| CPU | Windows x86-64 host | 5/5 |
| CUDA | NVIDIA GeForce MX150 | 5/5 |
| OpenGL | NVIDIA GeForce MX150 | 5/5 |
| Vulkan | Intel UHD Graphics 620 | 5/5 |

These are smoke/compatibility gates, not universal performance or accuracy
claims. The broader matrix is conservative: desktop GPU targets are roughly
88–92% qualified in the current audit, while ARM CPU/GLES/Vulkan artifacts have
static/package evidence but no real-device qualification. CUDA Maxwell through
Blackwell remains a policy/compile coverage task until real driver evidence is
available.

## Algorithm status

Use `taichi_vision/documentation/ALGORITHM_STATUS.md` as the status matrix.
Resize, Gaussian/gradients/Canny, and recorded remap/warp gates are the current
qualified baseline for tested desktop targets. Demosaic variants, MLRI-ADMM,
optical flow/block matching, RANSAC/OFB/AKAZE, most denoisers, FFT/NCC, HDR,
SFM/MVS, and compression/RAW remain experimental unless a narrower gate says
otherwise. Promote each operation only with backend, device, shape, dtype,
command, parity, lifecycle, and memory evidence.

## Build and validation

- Family compiler scripts live beside their kernels.
- Shared compiler orchestration lives in `taichi_algorithm/aot_py/`.
- Canonical shared compilers are
  `taichi_algorithm/compile_common_tcm.py`, `compile_cast_tcm.py`, and
  `compile_research_tcm.py`; same-named `aot_py` files are compatibility shims.
- Target TCM archives live under `taichi_algorithm/aot_tcm/<target>/`.
- Run focused parity/smoke tests before comprehensive tests; for block mode
  compare full-frame vs block, cache behavior, telemetry, and recovery.
- Keep bridge, C API, and TCM artifacts from the same LLVM/Taichi build.

Canonical references:

- `taichi_vision/documentation/README.md`
- `taichi_vision/documentation/API_USAGE.md`
- `taichi_vision/documentation/ARCHITECTURE.md`
- `taichi_vision/documentation/BUILD_AND_VALIDATION.md`
- `taichi_vision/AOT_BACKEND_MATRIX.md`
- `ai_governance/CURRENT_IMPLEMENTATION.md`
- `ai_governance/skills/taichi-aot-dev/SKILL.md`

## Desktop application boundary

`pixel_refine_desktop/` is the application layer. Its denoising/alignment
orchestrators call `taichi_vision`; kernels and backend selection must not be
duplicated there. The retired C++ spatial-similarity files and
`denoising/Similarity.py` are no longer valid implementation paths.

For UI changes, use `resources/GenericUILibrary` and existing animation/live
update infrastructure. Keep settings persistence in its provider and preserve
translation/theme behavior.

## Historical policy

Old claims such as “100% algorithm coverage”, “universal bit-perfect parity”,
or “one big graph is always active” are historical and must not be repeated as
current facts. `ai_governance/LEGACY_POLICY.md` is archive-only. When evidence
and a historical note conflict, the current runtime audit and reproducible
test output win.
