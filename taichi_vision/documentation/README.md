# `taichi_vision` Documentation

This folder is the developer reference hub for `taichi_vision`.

`taichi_vision` is the single maintained package boundary. No legacy namespace
alias is registered at runtime, and existing archives or historical Git
records are migration history only.

## Documentation map

| Document | Contents |
|---|---|
| [API_USAGE.md](API_USAGE.md) | Public imports, backend selection, input/output, buffers, and examples |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Runtime model, AOT graphs, TCM, cache, memory, and block compute |
| [ALGORITHM_STATUS.md](ALGORITHM_STATUS.md) | Algorithm status matrix: qualified, experimental, pending |
| [BUILD_AND_VALIDATION.md](BUILD_AND_VALIDATION.md) | Compilation, target artifacts, parity, smoke tests, and evidence |
| [../AOT_BACKEND_MATRIX.md](../AOT_BACKEND_MATRIX.md) | Canonical backend, ABI, device-routing, and safety contracts |
| [../taichi_algorithm/](../taichi_algorithm/) | Algorithm source tree |

## Status labels

- **QUALIFIED**: execution evidence exists for the named target/device and the
  documented gates pass.
- **EXPERIMENTAL**: the path exists or is partially validated, but evidence is
  insufficient for a cross-target production claim.
- **PENDING**: source or artifacts may exist, but required runtime/parity gates
  are unfinished.
- **QUARANTINED**: the path is intentionally disabled because of an ABI,
  driver, or lifecycle issue; the API must use the established safe path.

Do not promote a status merely because compilation succeeded or a `.tcm` file
exists. Every claim must name the backend, device, shape, dtype, command, and
observed result.

## Sources of truth

Use `AOT_BACKEND_MATRIX.md` and `taichi_aot/engine.py` for backend, lifecycle,
ABI, target resolution, and memory policy. These pages explain usage and
context; historical documentation must not change those contracts.
