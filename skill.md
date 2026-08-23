# Pixel Refine Taichi AOT Skill

This skill describes how to modify, compile, test, and document the Taichi AOT
library. It complements the normative rules in `ai_governance/` and the project
contract in `agen.md`.

## Scope and barriers

- Preserve public APIs in `taichi_vision.taichi_aot` and
  `taichi_vision.taichi_algorithm.aot_api`.
- Treat `taichi_vision/taichi_aot/engine.py` as the lifecycle/backend source
  of truth. Do not change it without explicit approval.
- Never mix target-qualified TCM, bridge, C API, OS, architecture, vendor, or
  ABI profiles.
- Full-frame is the correctness baseline. An unvalidated block/native path
  recovers through same-backend full-frame or reports an actionable error.
- Compilation success or artifact presence is not runtime support evidence.
- Do not stage unrelated changes, generated caches, compiler intermediates, or
  unreviewed artifacts.

## Canonical source layout

```text
algorithm family source + compiler
  -> target-qualified .tcm in taichi_algorithm/aot_tcm/<target>
  -> bridge/C API in taichi_algorithm/aot_py/aot_dll/<backend>
  -> engine artifact resolver and AOTModuleWrapper
  -> public aot_api wrapper
  -> parity, stress, and application validation
```

Family compiler scripts live beside their kernels. Shared compiler entry points
are `taichi_algorithm/compile_common_tcm.py`, `compile_cast_tcm.py`, and
`compile_research_tcm.py`; the same names in `aot_py/` are compatibility shims.

## Required workflow

1. Read `ai_governance/README.md`, `agen.md`, `blueprint_project.md`, this file,
   and `ai_governance/skills/taichi-aot-dev/SKILL.md`.
2. Inspect Git status, the public wrapper, caller, compiler, target artifact,
   manifest, and existing tests.
3. Reuse an existing family helper when ABI, dtype, border, and semantics match.
4. Add or modify the kernel and compiler in the family directory.
5. Register graph names with the canonical prefix and make the public wrapper
   call the exact graph name.
6. Compile only the relevant target profile.
7. Run a focused smoke/parity test, then the appropriate comprehensive test.
8. For block mode, compare full-frame and block outputs, cache hit/miss,
   memory telemetry, and recovery on a large enough input.
9. Run `git diff --check` and report exact evidence and remaining gaps.

## Public API and backend selection

```python
from taichi_vision import taichi_aot as aot
```

Set `PIXEL_REFINE_AOT_ARCH` to `cpu`, `cuda`, `vulkan`, `opengl`, or `gles`
before first import. `PIXEL_REFINE_AOT_DEVICE` is an ordinal hint;
`PIXEL_REFINE_TARGET_VENDOR` may constrain vendor selection. The native
renderer is validated and a mismatch is an error.

Use `InputArray`/`upload` for host-to-runtime transfer and `return_gpu=True`
for resident results. Release `TaichiGPUBuffer` objects after use and never
reuse them after `release`, `destroy`, `reinit`, or shutdown.

## Graph naming and dtype rules

Use `{family_prefix}_{operation}_{variant}`. Standard prefixes include:
`cmn_`, `smth_`, `intr_`, `grad_`, `pyra_`, `algn_`, `feat_`, `geom_`,
`flow_`, `demo_`, `deno_`, `imgp_`, `hdr_`, `sfm_`, and `math_`.

Keep graph argument ndim and kernel indexing identical. For f32-only graphs,
normalize integer input at the API boundary using the established policy.
Do not invent silent casts. Verify vector-vs-ndarray layout for 3-channel data,
and use float32 remap coordinates.

## `compute_block` contract

`compute_block` is an opt-in declaration/metadata boundary for operations that
can be partitioned safely. The planner still validates operation class, shape,
halo, dtype, target capability, and memory budget. A declaration is not proof
that an operation is block-safe.

Block adapters must define:

- input/output domains and halo requirements;
- tile shape and border behavior;
- deterministic stitching/core-write rules;
- cache key inputs (source checksum, shape, dtype, parameters);
- ownership and fence lifetime;
- full-frame recovery behavior.

Global reductions, unknown semantics, and quarantined graphs stay full-frame.
The current policy hard cap is 2048 pixels; adaptive memory may choose a
smaller tile or full-frame. Do not claim universal concurrent block execution.

## Automatic pipeline and memory

`auto_pipeline` and the scheduler manage stage ordering, residency, cache reuse,
and cleanup below the public API. Allocation cache and tile-result cache are
independent. Memory pressure may evict idle entries or reject a resident graph.
Inspect `get_memory_status()`, `get_block_config()`,
`get_block_cache_stats()`, and `get_last_block_execution()` during diagnostics.

## Backend validation

Minimum evidence format:

```text
backend=<cpu|cuda|vulkan|opengl|gles>
device=<renderer/vendor>
shape=<H,W[,C]>
dtype=<dtype>
command=<exact command>
result=<pass/fail + metric>
```

Required gates are syntax/compile checks, TCM/bridge ABI preflight, actual
backend smoke execution, reference parity, lifecycle cleanup, and memory
telemetry. ARM/GLES static artifacts are not mobile runtime qualification.

Useful commands from the project venv:

```powershell
python -m taichi_vision.taichi_algorithm.aot_py.compile_aot_backend_suite --help
python -m taichi_vision.taichi_algorithm.aot_py.tests.test_comprehensif --fast
python -m taichi_vision.taichi_algorithm.aot_py.validate_tcm_abi --help
```

## UI and application integration

Use `resources/GenericUILibrary` for UI components and the existing animation
and live-update infrastructure. Preserve translation/theme propagation and
provider-owned settings persistence. Do not reintroduce the retired C++ spatial
similarity path or deleted `denoising/Similarity.py`.

## Code quality and cleanup

- Prefer direct function references over trivial lambdas.
- Avoid duplicate implementations and unnecessary boilerplate.
- Keep comments/docstrings focused on non-obvious contracts.
- Remove only artifacts proven unreferenced by manifests, resolver, packaging,
  and tests.
- Keep documentation under `taichi_vision/documentation/`; retain only the
  root canonical `AOT_BACKEND_MATRIX.md` outside that hub.
