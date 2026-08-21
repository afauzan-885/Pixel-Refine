# Build and Validation

## Build

Run commands from the maintained `taichi_vision` package namespace. The
retired `taichi_library` namespace and the `taichi_vision copy` snapshot must
not be used for compilation, tests, or wheel assembly.

Family compiler scripts live beside their kernels. Shared orchestration lives
in `taichi_algorithm/aot_py/`; target artifacts live in
`taichi_algorithm/aot_tcm/<target>/`.

```powershell
python -m taichi_vision.taichi_algorithm.aot_py.compile_aot_backend_suite --help
python -m taichi_vision.taichi_algorithm.aot_py.tests.test_comprehensif --fast
```

Use the project venv. Never mix bridge, C API, or TCM artifacts from different
LLVM/Taichi builds.

## Minimum gates

1. Run `py_compile` on changed source/compiler files.
2. Run TCM/bridge preflight and target/ABI checks.
3. Run a graph smoke test on the actual backend/device.
4. Compare against NumPy/OpenCV references for relevant shapes and dtypes.
5. For block mode, compare full-frame vs block, cache hit/miss, memory
   telemetry, and recovery when the budget is insufficient.
6. Run `git diff --check` before committing.

Artifacts, caches, reports, and compiler intermediates must follow the target
manifest. Do not remove DLLs/TCMs still referenced by the resolver or packaging.

## Evidence format

```text
backend=<cpu|cuda|vulkan|opengl|gles>
device=<renderer/vendor>
shape=<H,W[,C]>
dtype=<dtype>
command=<exact command>
result=<pass/fail + metric>
```

See `AOT_BACKEND_MATRIX.md` for detailed backend and safety gates.
