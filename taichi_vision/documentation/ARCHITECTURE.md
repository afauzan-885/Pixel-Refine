# `taichi_vision` Architecture

## Runtime model

```text
Pixel Refine / Python application
        |
taichi_vision.taichi_aot (compatibility facade)
        |
taichi_algorithm.aot_api (dispatcher + dtype/block policy)
        |
taichi_aot.engine.py (single lifecycle/context/bridge owner)
        |
bridge + taichi_c_api + target-qualified .tcm
        |
CPU / CUDA / Vulkan / OpenGL / GLES driver
```

`engine.py` owns lifecycle, artifact selection, memory policy, cache residency,
and recovery. Kernels and compiler scripts live with their algorithm family;
compiled artifacts live under `aot_tcm/`.

## Artifact model

TCM, bridge, C API, operating system, architecture, vendor, and ABI must come
from the same target profile. The resolver rejects mismatches; a file name or
the presence of an artifact is not compatibility evidence.

## Operation flow

1. The API validates shape, dtype, and layout.
2. The dispatcher selects the graph and target-qualified TCM.
3. The engine acquires or allocates buffers through the memory governor.
4. The graph runs full-frame or block mode when the operation and budget are
   qualified.
5. The result is synchronized, validated, and returned as an ndarray or buffer.

## Memory, cache, and block compute

Allocation cache and tile-result cache are separate. Both are bounded by
lifecycle/fence, checksum, shape, dtype, and RAM/VRAM pressure. Block size is
adaptive; 2048 is the current hard policy cap, not a mandatory tile size.

Global or unvalidated operations remain full-frame. Local halo-aware operations
may be partitioned; tile results are written to a core/atlas to reduce readback.
If a validator or driver rejects block mode, recovery uses the same-backend
full-frame path.

## Design boundaries

- The public API does not expose backend suffixes.
- Applications do not manage DLLs or TCM archives directly.
- Native OpenGL/GLES is used only after the target safety gate passes.
- Static compilation, complete artifacts, or a single-machine benchmark is not
  proof of cross-device production support.
