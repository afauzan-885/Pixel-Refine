# Build and Validation

## Build

Run commands from the maintained `taichi_vision` package namespace. The
standalone hardware test is maintained beside Performance Settings.

Family compiler scripts live beside their kernels. Shared orchestration lives
in `taichi_algorithm/aot_py/`; target artifacts live in
`taichi_algorithm/aot_tcm/<target>/`.

```powershell
python -m taichi_vision.taichi_algorithm.aot_py.compile_aot_backend_suite --help
python pixel_refine_desktop/ui/views/settings/Perfomance/test_comprehensif.py --run-logic --fast
```

Use the project venv. Never mix bridge, C API, or TCM artifacts from different
LLVM/Taichi builds.

The canonical desktop artifact layout is target-qualified:

```text
taichi_algorithm/aot_tcm/cpu_x86_64_windows/
taichi_algorithm/aot_tcm/cuda_x86_64_windows_nvidia/
taichi_algorithm/aot_tcm/opengl_x86_64_windows/
taichi_algorithm/aot_tcm/vulkan_x86_64_windows/
```

Do not copy a generic or legacy TCM into a target directory by renaming it.
The target, bridge, C API, OS, architecture, vendor, and ABI must be produced
from the same LLVM/Taichi profile.

## Minimum gates

1. Run `py_compile` on changed source/compiler files.
2. Run TCM/bridge preflight and target/ABI checks.
3. Run a graph smoke test on the actual backend/device.
4. Compare against NumPy/OpenCV references for relevant shapes and dtypes.
5. For block mode, compare full-frame vs block, cache hit/miss, memory
   telemetry, and recovery when the budget is insufficient.
6. Run `git diff --check` before committing.

For Vulkan portability and ABI checks, use the validators that match the
artifact profile:

```powershell
python taichi_vision/taichi_algorithm/aot_py/validate_tcm_abi.py --help
python taichi_vision/taichi_algorithm/aot_py/validate_vulkan_spirv.py
python -m pytest taichi_vision/taichi_aot/tests/test_spirv_compatibility_tools.py
python -m pytest taichi_vision/taichi_aot/tests/test_watchdog_lifecycle.py
```

`spirv-val` and `spirv-dis` may be resolved from explicit environment paths,
the bundled Vulkan tool directory, `PATH`, or `VULKAN_SDK`. The last two test
commands are lifecycle/policy regression tests; they do not replace a real
backend/device smoke test.

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
