# AOT backend build and verification

The public Python API is unchanged. Select the implementation before importing
`taichi_library.taichi_aot`:

```powershell
$env:PIXEL_REFINE_AOT_ARCH = "cpu"       # or "vulkan" / "opengl"
$env:PIXEL_REFINE_AOT_DEVICE = "1"      # Vulkan device index
$env:PYTHONPATH = (Resolve-Path .).Path
```

The loader selects `taichi_algorithm/aot_py/aot_dll/cpu`, `vulkan`, or `opengl`
automatically. Device names are probed at runtime; on the current machine
device `0` is Intel UHD 620 and device `1` is the Microsoft Direct3D12 Intel
adapter, so neither is treated as a safe native Vulkan AOT device. A discrete
NVIDIA adapter is selected only when its actual vendor name is reported.

## Build

From `test_algorithm/taichi_upstream/stable-v1.7.4-development`:

```powershell
cmd /c build_pixel_refine_wheel.bat
```

The generated artifact is a normal CPython 3.12 Windows wheel in `dist/`.

## Verification

Install into an isolated venv, then run the complete algorithm and pipeline
suite:

```powershell
$py = "build/wheel-test-venv/Scripts/python.exe"
& $py -m pip install --force-reinstall --no-deps dist/*.whl
& $py taichi_library/taichi_algorithm/aot_py/test_comprehensif.py
```

For CPU/Vulkan parity (including exact integer cases and one-ULP float checks):

```powershell
& $py taichi_library/taichi_algorithm/aot_py/test_aot_backend_parity.py `
  --compare --compare-backend vulkan --device 1
```

The verified result is 24/24 algorithms on CPU and OpenGL (with the documented
OpenGL host fallbacks). Deterministic cases are bit-identical; floating-point
cases are bounded to the suite tolerances. Vulkan artifact/parity validation is
available, but runtime validation remains quarantined on the current Intel
driver because the graphics process terminates during dispatch.

OpenGL now has a native standalone Windows context: the C API creates a hidden
GLFW OpenGL 3.3 context when no application context was imported, then activates
it before runtime allocation. A minimal `opengl_smoke.tcm` graph has been loaded
and executed successfully through the same AOT API (buffer upload, dispatch,
readback). Full algorithm artifacts still need to be regenerated and gated on
the target GPU/driver; GLES/EGL is not yet enabled by this Windows path.

## OpenGL safety gates

Taichi 1.7.4 graphics graphs are not uniformly portable across Intel OpenGL
drivers. Operations whose native graph currently has an ABI or shape defect
use an OpenCV/NumPy reference path on OpenGL (`box_filter`, `median_filter`,
`bilateral_grid_filter`, `joint_bilateral_upsample`, `guided_filter_aot`, `inpaint_aot`, and related
alignment helpers). This preserves the public API and accuracy while avoiding
driver process termination. The `PIXEL_REFINE_AOT_NATIVE_*` switches should be
enabled only after a rebuilt artifact passes the isolated runtime validator.
The rebuilt box-filter graph is now native by default for small/medium inputs;
it keeps a size guard for large RGB frames, and
`PIXEL_REFINE_AOT_UNSAFE_LARGE_BOX=1` is required to bypass that guard.

The OpenGL median graph is native by default for validated 2D scalar and
3-channel RGB float32 inputs. RGB dispatch is protected by an isolated
child-process probe; if the artifact or driver rejects the graph, the API
automatically falls back to OpenCV. Flow/vector inputs remain on the reference
path until their vector graph is independently validated.

Joint bilateral upsampling follows the same policy: scalar 2D inputs up to
256×256 output pixels use the native OpenGL graph by default; RGB/flow or
larger outputs remain on the reference path.

These policies are covered by `test_opengl_native_scalar.py`, which checks
native loading, OpenCV parity for box/median (including uint8 inputs), and
finite scalar upsampling (including integer-input fallback). Integer inputs
intentionally use the reference path because the shipped native graphs are
f32-only.

Gaussian blur also normalizes integer GPU buffers to f32 before dispatch, so
uploading a uint8/uint16 image cannot reach an incompatible f32 graph argument.

For Sobel and Laplacian, integer GPU buffers use the dtype-safe OpenCV
reference path; native gradient graphs remain reserved for float32 inputs after
an Intel OpenGL driver crash was reproduced during integer-buffer conversion.

`cvtColor` likewise normalizes integer GPU buffers before its f32 graph
dispatch, preventing the common uint8 RGB input from reaching an incompatible
graph argument. When the Intel OpenGL path would produce an incorrect result
after conversion, integer GPU color conversion uses OpenCV directly and
returns the correct dtype-preserving buffer.

The complete integer GPU boundary is covered by
`test_gpu_integer_dtype_policy.py` (resize, color conversion, blur, Sobel, and
Laplacian).

OpenGL Canny currently uses the OpenCV reference implementation by default.
The native graph is available behind `PIXEL_REFINE_AOT_NATIVE_CANNY=1` for
experimentation, but remains opt-in until its edge topology reaches the
OpenCV parity gate.

Resize keeps integer GPU inputs on OpenCV's dtype-preserving path; a trial f32
conversion produced incorrect zero-valued output on the current Intel OpenGL
driver, so it is deliberately not dispatched to the native graph.

The inpaint graphs are f32-only. `inpaint_aot` now normalizes common uint8 or
uint16 source/mask inputs at the API boundary, so they no longer fail with a
late graph dtype mismatch. Scalar 2-D f32 OpenGL inputs use an isolated driver
probe and native dispatch when it passes; RGB/integer inputs remain on OpenCV.

The same f32 mask normalization is applied to the experimental seamless-clone
graph. Its OpenGL native path is probe-guarded and now passes on the tested
Intel driver after synchronization fixes; native dispatch is limited to
3-channel f32 images, while scalar/degenerate inputs use OpenCV.

Guided-filter probing initially identified an OpenGL resource-binding/lifetime
error. The rebuilt bridge reports `GL_MAX_SHADER_STORAGE_BUFFER_BINDINGS=16`,
so index 9 is within the Intel limit. The actual issue was premature recycling
of asynchronous intermediate buffers; explicit runtime synchronization before
each temporary destroy fixes it. Native guided filtering now passes OpenCV
parity on the tested Intel context.

OpenGL pipeline selection is automatic. Small validated graphs are recorded
without requiring `PIXEL_REFINE_AOT_NATIVE_PIPELINE`; host fallbacks and the
resident-memory guard are handled internally. The historical environment
switches remain debug overrides only. Oversized graphs are rejected before
driver dispatch until the block scheduler can transparently decompose them.
CPU pipeline recording remains enabled.

The backend-neutral smoke graph (`resize -> cvtColor -> gaussian_blur -> sobel`)
is recorded and executed successfully on both CPU and OpenGL. This validates
the standalone context/bridge path without claiming that fallback-heavy
production graphs are pipeline-safe yet.

For large images, the block executor remains the safe composition path. On
the tested Intel OpenGL context at 512x512, tiled and full-frame outputs were
bit-identical for resize, Gaussian, remap, RGB-to-gray, and Sobel; tiled
execution also reduced dispatch time for each case. This is the basis for
future large-pipeline scheduling without a single oversized graph.

An isolated Intel OpenGL proof run with
`PIXEL_REFINE_AOT_NATIVE_PIPELINE=1`,
`PIXEL_REFINE_AOT_ALLOW_LARGE_PIPELINE=1`, and
`PIXEL_REFINE_AOT_PIPELINE_ONLY=1` successfully recorded and replayed the
24.1 MP RGB master graph for 10 iterations at 219.977 ms/iteration (4.55 FPS).
The proof-only mode is intentional: the same context must not immediately be
used for the separate kernel-by-kernel comparison on the affected Intel
driver, which can invalidate large SSBO bindings.

The internal scheduler is available as:

```python
from taichi_library.taichi_aot import PipelineStage, run_block_pipeline

result = run_block_pipeline(image, [
    PipelineStage("blur", lambda x: gaussian_blur(x, sigma=1.5)),
    PipelineStage("median", lambda x: median_filter(x)),
])
```

It restores the previous block policy even when a stage raises, and is the
recommended composition path for large OpenGL inputs until native multi-stage
recording is validated on the target driver.

Autodiff status: CPU ndarray autodiff passes. Taichi 1.7.4 OpenGL ndarray
autodiff still reproduces issue #8524 (`x=4, y=0, grad=0`); the validated
workaround is scalar `ti.field` autodiff, covered by
`test_autodiff_field_workaround.py`. The ndarray path remains quarantined until
the Taichi runtime itself is rebuilt with the upstream fix.
