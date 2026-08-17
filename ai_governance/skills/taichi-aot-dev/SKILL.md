---
name: taichi-aot-dev
description: Tool-neutral Taichi AOT workflow for Pixel Refine. Use for TCM compilation, graph/API parity, backend capability work, artifact loading, and Taichi library changes.
---

# Taichi AOT Development Contract

## Scope and safety barriers

- Public APIs in `taichi_library.taichi_aot` and
  `taichi_library.taichi_algorithm.aot_api` must remain backward compatible
  unless the user explicitly requests an API change.
- `taichi_library/taichi_aot/engine.py` owns backend selection, runtime
  lifecycle, artifact loading, memory policy, cache residency, and block
  planning. Do not change it without explicit approval.
- Correctness and backend consistency take priority over throughput. An
  experimental or quarantined block path must recover through the established
  full-frame path on the same backend, or report an actionable error.
- Never describe a backend as supported merely because compilation succeeded.
  Record runtime evidence on the actual backend/device.

## Architecture contract

```text
algorithm kernel / compile script
    -> target-qualified .tcm artifact
    -> engine artifact resolver and AOTModuleWrapper
    -> public API wrapper
    -> parity, stress, and application validation
```

- Compiler scripts define Taichi kernels and register graph names.
- Target-qualified artifacts live under `taichi_algorithm/aot_tcm/`.
- Runtime bridges live under `taichi_algorithm/aot_py/aot_dll/`.
- The public wrapper calls the matching graph through `_mod(...).run(...)`.
- Do not mix artifacts across CPU architecture, OS, GPU backend, or mobile and
  desktop profiles.

## Required workflow

1. Inspect the API wrapper, compiler, artifact target, and existing test before
   modifying anything.
2. Reuse an existing family helper where possible; do not create a second
   implementation solely for one backend.
3. Add or update the kernel and compiler in the algorithm's own folder.
4. Register the graph with the canonical prefix and make the public wrapper
   call the exact same graph name.
5. Compile only the relevant target profile.
6. Run a focused parity or smoke test, then the appropriate comprehensive test.
7. For block mode, validate full-frame versus block output, cache behavior,
   memory telemetry, and a large-enough input to exercise the planner.
8. Report what was tested and what remains unverified.

## Graph naming

Use `{module_prefix}_{operation}_{variant}`. Typical prefixes include:

| Family | Prefix |
|---|---|
| common | `cmn_` |
| smoothing | `smth_` |
| interpolation | `intr_` |
| gradients | `grad_` |
| pyramid | `pyra_` |
| alignment | `algn_` |
| features | `feat_` |
| geometric | `geom_` |
| optical flow | `flow_` |
| demosaic | `demo_` |
| denoising | `deno_` |
| image processing | `imgp_` |
| HDR | `hdr_` |
| SfM | `sfm_` |
| math operations | `math_` |

## Common AOT checks

- `u8` unsupported by a target graph: use the established `i32` or normalized
  transport route; do not invent a silent dtype conversion.
- Array dimension mismatch: make graph argument ndim and kernel indexing agree.
- Taichi `range(start, stop, step)` failure: rewrite with a supported loop.
- Three-channel array mismatch: verify `InputArray(..., force_vector=False)`
  when a 3D ndarray must stay an ndarray rather than a vector field.
- `remap` coordinates must be `float32`.
- Document intentional differences from OpenCV, such as resize default
  interpolation or Gaussian parameter semantics.

## Validation and Git barriers

- Run `git diff --check` before commit.
- Do not commit `__pycache__`, `.cpu_aot_cache`, quarantined artifacts, compiler
  intermediates (`.obj`, `.exp`, `.lib`), or generated test reports.
- Preserve required `.tcm`, `.dll`, `.so`, and `.bc` runtime artifacts after
  checking the target manifest and runtime resolver.
- Never use `git add -A` in a dirty worktree. Stage only reviewed paths.
