# `taichi_vision`

`taichi_vision` is Pixel Refine's AOT algorithm and native-runtime integration
layer.
The public facade is:

```python
from taichi_vision import taichi_aot as aot
```

## Canonical package boundary

This `taichi_vision` directory is the only maintained algorithm/runtime
package. `taichi_vision copy` is an obsolete snapshot and is not part of the
package, build, test, wheel, or application import path.

No legacy namespace alias is registered at runtime. All application imports,
compiler commands, documentation, and package data must use `taichi_vision`.
Historical archives or migration records are not runtime inputs.

Runtime lifecycle, backend selection, target-qualified bridges, TCM loading,
memory policy, and block/full-frame recovery are owned by
`taichi_vision/taichi_aot/engine.py` and its dispatch layer. Applications must
not load DLLs or TCM archives directly.

## Documentation hub

| Document | Contents |
|---|---|
| [`documentation/README.md`](documentation/README.md) | Documentation map and evidence rules |
| [`documentation/API_USAGE.md`](documentation/API_USAGE.md) | Public imports, backend selection, buffers, and API examples |
| [`documentation/ARCHITECTURE.md`](documentation/ARCHITECTURE.md) | Runtime layers, AOT graphs, cache, memory, and block compute |
| [`documentation/ALGORITHM_STATUS.md`](documentation/ALGORITHM_STATUS.md) | Qualified, experimental, pending, and quarantined algorithms |
| [`documentation/BUILD_AND_VALIDATION.md`](documentation/BUILD_AND_VALIDATION.md) | AOT compilation, ABI checks, parity, and validation |
| [`AOT_BACKEND_MATRIX.md`](AOT_BACKEND_MATRIX.md) | Canonical backend and artifact contract |

Algorithm source and family-local compilers are under
`taichi_algorithm/`. Target-qualified TCM archives are under
`taichi_algorithm/aot_tcm/`.

The LLVM20 runtime build tutorial belongs to the Taichi fork README, not this
library README. Keep runtime packaging and algorithm AOT artifacts as separate
layers, and keep their bridge, C API, ABI, and LLVM provenance identical.
