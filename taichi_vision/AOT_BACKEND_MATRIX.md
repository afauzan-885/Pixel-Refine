# AOT backend build and verification

> **Canonical developer/AI handoff document** (snapshot: 2026-09-06).  This
> file is the source of truth for the experimental `taichi_vision` runtime.
> It documents the stable contracts and the explicit gates around unfinished
> features so a new contributor does not need to reverse-engineer the entire
> repository.  The upstream Taichi source remains under
> `test_algorithm/taichi_upstream/stable-v1.7.4-development`; this document
> describes the Pixel Refine AOT layer built around that runtime.

### Navigation

Start with **Developer quick start** for the supported API and environment
variables, then use **Stable change ledger** for the current contract. Use
**New developer workflow** when adding an algorithm, **Build** when producing
TCM/bridge artifacts, **Verification** for parity and lifecycle evidence, and
**OpenGL safety gates** for driver-specific native/reference decisions.

## Developer quick start

### What is stable

The supported application boundary is:

```python
from taichi_vision import taichi_aot
```

The public algorithm calls do not contain backend-specific names.  Select the
backend before importing the module, then call the same function for CPU,
CUDA, Vulkan, OpenGL, or GLES.  The dispatcher resolves a target-qualified
TCM archive and its ABI-matching bridge automatically.  Full-frame execution
is always the correctness baseline; block execution, native OpenGL passes,
and recorded pipelines are guarded optimizations.

The following contracts are considered stable on the qualified desktop
targets:

* backend selection is explicit and a renderer/vendor mismatch is an error;
* target selection uses the vendor/device fingerprint, not only a volatile
  device ordinal;
* target-qualified `.tcm` archives are never relabeled across OS, ABI, or
  architecture;
* buffer ownership, runtime generations, cache validation, retry, quarantine,
  and full-frame recovery are enforced by the engine;
* integer host inputs are normalized at the API boundary whenever a native
  graph is f32-only; correctness is preferred over an unsafe cast;
* a feature without a validated tile executor remains full-frame.

ARM/GLES artifacts that have only static bridge, ABI, or SPIR-V evidence are
not runtime-qualified until the same process-level suite has run on the real
device.  Likewise, a complete artifact directory is not proof of numerical
or driver compatibility.

### Runtime map

```text
Application / Pixel Refine
        |
taichi_algorithm wrappers (optional OpenCV-style convenience API)
        |
taichi_vision.taichi_aot.__init__  <- compatibility facade + runtime exports
taichi_algorithm.aot_api            <- canonical public dispatch, dtype policy, tiles
        |
taichi_vision.taichi_aot.engine    <- one runtime/context/bridge owner
        |
target-qualified bridge + libtaichi_c_api + .tcm archive
        |
CPU / CUDA / Vulkan / OpenGL / GLES driver
```

`engine.py` is the runtime source of truth.  `__init__.py` owns the public
compatibility facade; `taichi_algorithm/aot_api` owns the public algorithm
dispatch and block/fallback wrappers.  `artifact_targets.py` and
`target_manifest.json` define how a backend, OS, architecture, ABI, and vendor
map to a TCM directory.  `target_registry.py` is the build-time view of the
same manifest; do not create a second handwritten target list.

### Canonical source layout

```text
taichi_vision/
├─ taichi_algorithm/                 # single source for algorithms
│  ├─ aot_api/                       # public AOT algorithms and dispatch
│  ├─ alignment/, demosaicing/, ...  # reusable algorithm families/kernels
│  ├─ aot_py/                        # shared build orchestration/tools
│  │  └─ tests/                      # comprehensive, parity, and stress tests
│  ├─ feature_matching/              # source + compile_akaze/ofb_tcm.py
│  ├─ interpolation/                 # source + compile_*_tcm.py
│  ├─ demosaicing/                   # source + compile_*_tcm.py
│  ├─ optical_flow/, alignment/, ... # source + family compiler scripts
│  ├─ aot_tcm/                       # target-qualified TCM artifacts
│  └─ source-only package files (documentation is under ../documentation/)
├─ taichi_aot/                       # runtime only: engine, memory, backends
│  └─ __init__.py                    # backwards-compatible façade
├─ backend_config.py, device_selection.py, ... # platform/probe infrastructure
└─ AOT_BACKEND_MATRIX.md             # canonical contracts and verification gates
```

`taichi_aot/extended.py` and `jpeg.py` are compatibility shims only; their
implementations are maintained under `image_processing/extended_aot.py` and
`compression/jpeg_aot.py`.  `aot_api/` retains only cross-family dispatch
(`research.py` and `research_pipeline.py`) plus compatibility shims.  A
family-specific compiler belongs beside its source family; `aot_py/` is for
shared orchestration and tests.  New algorithm code belongs in
`taichi_algorithm`, never in the runtime package.  Application orchestration
under `pixel_refine_desktop/.../core/algorithm` remains an application layer
and should call this library rather than duplicate its kernels.

### Minimal usage

Set the environment before the first import.  The device number is only a
hint; the loader validates the requested vendor and native renderer.

```powershell
$env:PIXEL_REFINE_AOT_ARCH = "vulkan"       # cpu, cuda, vulkan, opengl, gles
$env:PIXEL_REFINE_TARGET_VENDOR = "NVIDIA" # optional stable vendor contract
$env:PIXEL_REFINE_AOT_DEVICE = "0"          # ordinal hint for Vulkan/CUDA
python your_algorithm.py
```

```python
import numpy as np
from taichi_vision import taichi_aot as aot

image = np.ascontiguousarray(load_image(), dtype=np.float32)

# NumPy in -> NumPy out.  The dispatcher may use a native graph, a validated
# tile executor, or the same-backend full-frame/reference path.
blurred = aot.gaussian_blur(image, sigma=1.2, kernel_size=5)

# Keep data resident when several stages are chained.
gpu_input = aot.InputArray(image, is_vector=False)
gpu_output = aot.resize(gpu_input, (2048, 2048), return_gpu=True)
result = gpu_output.to_numpy()
gpu_output.release()
gpu_input.release()

print(aot.get_backend_name())
print(aot.backend_info())
print(aot.get_memory_status())
```

`InputArray` transfers an ndarray to the active runtime.  `OutputArray`
allocates a runtime-owned destination.  A returned `TaichiGPUBuffer` must be
released (or allowed to leave scope after the pipeline has synchronized).  Do
not reuse a buffer after `destroy()`, `release()`, `reinit()`, or runtime
shutdown.

### Block, cache, and automatic pipeline usage

The default policy is conservative.  Adaptive planning may select a block for
large, local, halo-aware operations; unknown, global, or quarantined
operations stay full-frame.  Explicit block mode is useful for controlled
tests and for the three optical-flow tile paths, but it is not required for
ordinary application calls.

```python
from taichi_vision import taichi_aot as aot

print(aot.get_block_config())
print(aot.get_memory_status(force=True))

# Only enable this when the operation has been qualified for the target.
aot.set_block_mode(
    enabled=True,
    size=512,
    threshold_bytes=512 * 1024 * 1024,
    adaptive_memory=True,
)

print(aot.get_block_cache_stats())

# Large host pipelines use the scheduler; it restores the previous policy
# even when a stage raises.
from taichi_vision.taichi_aot import PipelineStage, run_block_pipeline
result = run_block_pipeline(image, [
    PipelineStage("blur", lambda x: aot.gaussian_blur(x, sigma=1.5)),
    PipelineStage("gray", lambda x: aot.rgb2gray(x)),
])
```

Allocation caching is independent of tile-result caching.  A full-frame
allocation can be reused when byte capacity, dtype, vector layout, usage, and
memory domain match.  The memory governor may evict idle buffers when RAM or
VRAM pressure rises.  Set `PIXEL_REFINE_AOT_BUFFER_CACHE=0` only for a
diagnostic run.  Cache records are trusted only after source checksum, output
checksum, tuple arity, and shape validation; malformed records are discarded
and recomputed.

### Backend and device selection rules

* `PIXEL_REFINE_AOT_ARCH` is the requested backend.
* `PIXEL_REFINE_AOT_DEVICE` is an ordinal hint, not a persistent identity.
* `PIXEL_REFINE_TARGET_VENDOR` constrains selection to a vendor such as
  `NVIDIA` or `Intel`.
* `PIXEL_REFINE_OPENGL_CONTEXT=icd` requests the direct native Windows ICD
  path for an isolated qualification run.
* Dozen/D3D12 translation adapters are excluded by default.  Translation is
  a diagnostic opt-in only.
* `PIXEL_REFINE_GFX_COMPAT_MODE=auto` enables the conservative host-visible,
  serialized-dispatch policy for Intel Vulkan/OpenGL. Set it to `0` for strict
  admission or `1` for an explicit compatibility run.
* `PIXEL_REFINE_AOT_DISABLE_CACHE=1` disables artifact load-status caching for
  cache/ABI diagnosis. It is not a performance setting.
* OpenGL initialization verifies `GL_RENDERER`; it never silently accepts an
  Intel context when NVIDIA was requested, or the reverse.
* Android canonicalizes the historical `opengl` spelling to `gles` and never
  loads a desktop Windows DLL.

Changing a driver can reorder device ordinals.  The persisted vendor,
fingerprint, native driver identity, and artifact manifest are therefore
validated together before initialization.  A stale ordinal is discarded and
rescanned; a mismatch or failed explicit request is surfaced to the caller.

## Stable change ledger

This ledger separates changes that are safe to depend on from work that is
still gated.  The implementation details are described in the later build and
qualification sections.

| Area | Stable result | Gate or limitation |
|---|---|---|
| Runtime bridge | One ownership/lifecycle path for CPU, CUDA, Vulkan, OpenGL, and GLES targets | ARM/GLES device execution is still pending where noted below |
| Target artifacts | Manifest-driven, ABI-qualified TCM and bridge resolution | Missing host/cross toolchains remain explicit `pending_toolchain` results |
| Device mapping | Vendor/fingerprint mapping survives ordinal changes | A driver must expose a native renderer matching the request |
| Full-frame path | Always available as the accuracy and recovery baseline | Native artifact must exist for the selected target |
| Allocation cache | Full-frame and staging buffers reuse safely with lifecycle fencing | Daemon-thread idle reclamation is disabled by default; owner-thread safe points perform explicit trimming |
| Tile-result cache | Checksum/shape/tuple validation, retry, invalidation, quarantine | Generic result keys may not hit across distinct source objects |
| Adaptive memory | Shared-RAM/VRAM budget, pressure state, resident limit, recommended block size | It intentionally reserves memory and may choose full-frame |
| Automatic pipeline | Direct, recorded, or segmented plan without manual `rec_pipeline` pairs | It does not yet dispatch independent blocks concurrently |
| Safe blocks | Registered native paths remain conservative; custom algorithms can use `BlockComputeSpec` explicitly | Automatic native selection still requires parity evidence; custom `force` is memory-governed |
| Integer boundary | Saturating u8/u16 and signed i16 host conversions are tested on desktop paths | Some OpenGL graphs deliberately use synchronized NumPy/reference casts |
| OpenGL safety | Native ICD context, renderer checks, admission guard, isolated probes | Driver-specific f32/native guards remain; no universal native graph claim |
| Autodiff | CPU ndarray path and scalar `ti.field` workaround are validated | Taichi 1.7.4 OpenGL ndarray issue #8524 remains quarantined |

### Block capability summary

The registry currently contains 109 operation keys.  The automatic set covers
channel/pointwise operations, resize/remap/pyramid, blur/gradient and guided
filters, enhancement/highlight recovery, and Hamilton/DCB/ARM demosaic
variants.  `farneback_flow`, `lucas_kanade`, and `block_matching` have an
explicit halo-aware path but remain out of automatic selection because their
multi-stage pyramid/remap dependencies are not yet parity-qualified for every
target.  Global reductions and non-local algorithms such as Canny, CLAHE,
Otsu, FFT, histogram, RANSAC cleanup, Hough, AKAZE/OFB, homography, inpaint,
seamless clone, BM3D, and MLRI remain full-frame in the planner.

The block executor is deliberately ordered and deterministic.  Taichi kernels
may still parallelize internally, but Python-level concurrent block dispatch
is not a stable contract yet.  Do not infer parallel execution from the
`max_concurrency` telemetry field.

### Generic custom block contract

`taichi_vision/taichi_aot/generic_block.py` provides
`BlockComputeSpec`/`run_generic_blocks()` for algorithms whose tile semantics
are not represented by the native registry.  A custom spec owns its input
reader, halo, tile runner, validator, merger, cache namespace, and optional
same-backend full-frame callback.  The engine still owns adaptive sizing,
host/device residency, checksums, retry, quarantine, and lifecycle fencing.
`mode="force"` bypasses only the registry gate; it does not bypass the memory
governor.  Variable-cardinality outputs such as feature/keypoint payloads are
supported through `output_factory` and `merge_tile`.

For a regular NumPy image callable, the additive `@compute_block` declaration
can request the same generic path without changing its public invocation:

```python
from taichi_vision import taichi_aot as aot

@aot.compute_block(halo=8)
def custom_filter(image):
    return image + 1.0
```

The decorator is conservative: it slices matching image inputs and stitches
image-like outputs, while GPU buffers, destination buffers, global reductions,
variable payloads, and existing manual tile loops remain on the reference
path. Static `range`/slice information is diagnostic only; no arbitrary Python
bytecode is rewritten. Use `BlockComputeSpec` for non-image or multi-output
contracts.

## New developer workflow

### Add or modify an algorithm

1. Define the kernel and graph in the appropriate `compile_*.py` module.
2. Register one graph name and one declarative job in
   `compile_aot_backend_suite.py`; keep aliases explicit.
3. Add the public wrapper in `taichi_aot/__init__.py` without changing the
   backend-neutral call signature.
4. If the operation is a maintained native path, implement a halo-aware tile
   executor and add it to `OPERATION_PATHS`; add it to `AUTO_BLOCK_SAFE` only
   after parity, corruption, boundary, and memory tests pass.  If it is a
   custom/research path, use `BlockComputeSpec` instead of weakening the
   native registry; keep the spec's full-frame recovery explicit.
5. Compile through `background_compile.py` using the manifest target, never by
   copying or renaming a TCM emitted for another target.
6. Run the filesystem audit, SPIR-V validation where applicable, backend
   smoke/parity tests, and the large-image gate.
7. Record the evidence and any reference-path guard in this document before
   changing a feature from experimental to stable.

The graph name must match in three places: compiler `add_graph`, the job
registry, and the public `_mod(...).run(...)` call.  A mismatch is a build/API
failure, not a reason to add a fallback with a different public signature.
`engine.py` is the single runtime source of truth; avoid duplicating backend
selection, memory ownership, or native-library loading in an algorithm module.

### Required verification loop

```powershell
# 1. Static target/bridge/artifact audit (does not initialize a GPU)
python taichi_vision/taichi_algorithm/aot_py/audit_aot_matrix.py

# 2. Best-effort target matrix; pending toolchains remain visible
python taichi_vision/taichi_algorithm/aot_py/background_compile.py `
  --all-targets --best-effort --workers 2 --timeout 900

# 3. Re-run the public comprehensive and research suites on the selected target
python pixel_refine_desktop/ui/views/settings/Perfomance/test_comprehensif.py
python taichi_vision/taichi_algorithm/aot_py/tests/test_research_aot.py

# 4. Cache/lifecycle regression
python -m taichi_vision.taichi_algorithm.aot_py.tests.stress_block_copy

# 5. Generic custom block contract (no native device required)
python -m unittest test_algorithm.test_generic_block
python -m unittest test_algorithm.test_compute_block

# 5. Desktop Vulkan shader portability
python taichi_vision/taichi_algorithm/aot_py/validate_vulkan_spirv.py
```

Run the unit tests that do not require a physical GPU before any driver test:

```powershell
python -m unittest `
  test_algorithm.test_aot_cache_lifecycle `
  test_algorithm.test_memory_governor `
  test_algorithm.test_auto_pipeline `
  test_algorithm.test_aot_build_orchestrator
```

The matrix runner reports `success`, `pending_toolchain`, `timeout`,
`worker_error`, or `failed`.  A pending ARM/Linux toolchain is a real gap; it
must not be hidden by relabeling a Windows artifact.  A filesystem audit proves
inventory and ABI shape only; parity and native-driver runs are still required.

### Debugging order

1. Print `aot.backend_info()`, `aot.get_memory_status(force=True)`, and
   `aot.get_block_cache_stats()`.
2. Reproduce with the same target-qualified artifact in a fresh process.
3. Disable block mode and compare the same-backend full-frame output.
4. Check dtype, shape, vector layout, halo, and graph name before changing a
   kernel.
5. For OpenGL, verify `GL_RENDERER`, use an isolated ICD probe, and inspect the
   projected resident-memory guard before touching SSBO bindings.
6. Clear a block quarantine only after the failing artifact/driver pair has
   been rebuilt and retested:

```python
from taichi_vision import taichi_aot
taichi_aot.clear_block_quarantine("operation_name")
```

Do not turn on historical `PIXEL_REFINE_AOT_NATIVE_*` or large-pipeline
switches merely to make a failing test pass.  They are diagnostic overrides;
the normal dispatcher must decide from the target capability and memory
policy.

The public Python API is unchanged. Select the implementation before importing
`taichi_vision.taichi_aot`:

```powershell
$env:PIXEL_REFINE_AOT_ARCH = "cpu"       # or "vulkan" / "opengl" / "gles"
$env:PIXEL_REFINE_AOT_DEVICE = "1"      # Vulkan device index
$env:PYTHONPATH = (Resolve-Path .).Path
```

The loader selects the desktop bridge directories (`cpu`, `vulkan`, `opengl`)
or the target-qualified mobile bridge (`gles_arm64_android`) automatically.
Device selection is keyed by vendor/device UUID and native
driver identity rather than a volatile Vulkan ordinal. Microsoft
Direct3D12/Dozen adapters are always excluded. Native Intel Vulkan is enabled
only when the exact GPU, driver, bridge, runtime sources, test harness, and
Vulkan artifact inventory have a passing validation manifest; changing any of
them keeps Intel Vulkan unqualified until the next validation pass. Backend
selection is explicit and a failed request is reported; it is never silently
rewritten to OpenGL.

On Android, the legacy backend spelling `opengl` is canonicalized to `gles`
before bridge and TCM resolution, and automatic candidates are
`vulkan → gles → cpu`; a desktop OpenGL DLL can therefore never be selected by
an Android process.

When a saved vendor is present, the loader also validates any restored ordinal
against that vendor. A stale ordinal (including a harness default of device 0)
is discarded and a native scan selects the requested vendor before runtime
initialization, preventing an NVIDIA/Intel swap after driver reordering.

The General Settings selector is explicit rather than automatic: every native
GPU is listed once for Vulkan and once for OpenGL. Selecting Intel Vulkan never
rewrites the saved choice to OpenGL, and selecting either OpenGL entry verifies
that the runtime `GL_RENDERER` belongs to the selected vendor. A mismatch is an
error, not a silent device substitution. “Test Hardware Backend” runs the
complete API and 24.1 MP suite in an isolated process for every pair; Intel
Vulkan additionally runs and persists the lifecycle/artifact qualification
gate.

OpenGL vendor expectations now use `PIXEL_REFINE_TARGET_VENDOR` when an
OpenGL-specific expectation is not supplied. This prevents a process created
on NVIDIA from being silently reported as Intel (or vice versa); the active
ICD must match the selected vendor or initialization fails with an actionable
renderer-mismatch error. Artifact validation keys canonicalize Windows paths,
so drive-letter/path-case differences between the application and its child
hardware-test process cannot resurrect a stale quarantine record. Status writes
also use a cross-process sidecar lock, preventing concurrent validators from
losing one another's results during lifecycle/driver qualification.

An unseen native Intel fingerprint is now self-qualifying. The first launch
remains on OpenGL and schedules a detached validator. The validator waits for
Pixel Refine to exit, then checks every native Intel ICD sequentially using
the lifecycle, complete artifact inventory, 28-API parity, and 24.1 MP gates.
Only a complete pass changes the next launch to Vulkan. A crash, timeout,
driver failure, or incomplete result remains quarantined with a 24-hour retry
cooldown. Dozen devices are never scheduled. State and logs are written under
`%LOCALAPPDATA%\PixelRefine\intel_vulkan_qualification`.

## Build

From `test_algorithm/taichi_upstream/stable-v1.7.4-development`:

```powershell
cmd /c build_pixel_refine_wheel.bat
```

The generated artifact is a normal CPython 3.12 Windows wheel in `dist/`.

The MSVC bridge build uses `/GL` and `/LTCG` for cross-function optimization
while keeping the exported ABI unchanged. Set
`PIXEL_REFINE_BRIDGE_NO_LTO=1` only when diagnosing a compiler/linker issue.
The isolated background compiler accepts `cpu`, `vulkan`, `opengl`, `cuda`,
and explicit `gles` requests; GLES is intentionally not part of the desktop
default and should be built with the Android target profile.

The source compiler registry is shared by `compile_aot_backend_suite.py` and
`background_compile.py`; both read the target IDs from
`aot_tcm/target_manifest.json`.  This keeps one algorithm job definition while
still emitting ABI-qualified archives for each backend/OS/architecture:

```powershell
python taichi_vision/taichi_algorithm/aot_py/background_compile.py --all-targets --workers 2
python taichi_vision/taichi_algorithm/aot_py/audit_aot_matrix.py
```

For a workstation that does not have every host/cross toolchain, use
`--best-effort`; available targets are built in parallel while unavailable
profiles are returned as `status: pending_toolchain`. Worker timeouts are
reported as `status: timeout` instead of aborting the entire matrix:

```powershell
python taichi_vision/taichi_algorithm/aot_py/background_compile.py `
  --all-targets --best-effort --workers 2
```

The runner never relabels host LLVM as another platform.  ARM profiles require
an ARM/cross toolchain, and a target that cannot be built is reported as such;
graphics archives are accepted only after their SPIR-V payload is validated.
The filesystem audit also checks the native bridge and C-API runtime for every
manifest target, so a complete `.tcm` directory is not reported as runnable
until its matching bridge exists.  The same audit verifies every source `JOBS`
entry (compiler module and callable) before a build is considered complete; a
missing target toolchain remains an explicit gap instead of being hidden by a
renamed artifact.

On the current Windows workstation, the audit intentionally reports two
unbuilt profiles: `cpu_x86_64_linux` needs a Linux/glibc worker (or a matching
cross toolchain), and `cuda_arm64_linux_nvidia` needs NVIDIA's ARM64 CUDA host
toolchain.  They remain manifest entries so the same source registry can build
them when those toolchains are supplied; no Windows artifact is relabeled as
either target.

## Cache and block execution

Allocation caching is enabled by default, including full-frame execution.  A
released buffer is reused only when its byte size, dtype, vector layout, and
memory domain match; queued GPU work is synchronized before a retired handle
enters the pool.  The adaptive memory governor may evict idle entries under
pressure, and `PIXEL_REFINE_AOT_BUFFER_CACHE=0` explicitly disables reuse.
Query cache telemetry with:

```python
from taichi_vision import taichi_aot
print(taichi_aot.get_block_cache_stats())
```

The adaptive planner selects blocks automatically only for registered local,
halo-aware and parity-tested operations.  Custom algorithms can opt into the
same executor explicitly with `BlockComputeSpec`; they are not silently
promoted by the native registry.  The current automatic local set includes copy and
channel primitives, resize/remap, blur/gradient filters, NLM/guided/joint
bilateral filters, the extended threshold/normalize/morphology/filter2d/color
and enhancement/highlight-recovery kernels, plus the validated demosaic paths.
The BGR/RGB grayscale conversion path is included as well.  Global reductions,
optical-flow graphs, and any unknown/new operation remain full-frame until a
block executor is explicitly qualified.  A failed tile is retried, its cache
owner is quarantined, and the same-backend full-frame implementation is used
for the request; the quarantine can be cleared with
`taichi_aot.clear_block_quarantine()` after a controlled retest.  Thus block
execution is an optimization, never a prerequisite for cache reuse or
correctness.  Runtime reinitialization and shutdown invalidate every live
wrapper before the native context is replaced, so a stale buffer cannot be
submitted to a new backend generation; malformed cached tile shapes and
malformed multi-output checksum metadata are rejected in addition to normal
checksum validation.

The regression harness also disables block planning and submits two different
NumPy objects with the same frame size; the second full-frame dispatch records
a `buffer_pool` hit.  Therefore allocation reuse does not depend on the block
cache or on Python object identity.

## Verification

Install into an isolated venv, then run the complete algorithm and pipeline
suite:

```powershell
$py = "build/wheel-test-venv/Scripts/python.exe"
& $py -m pip install --force-reinstall --no-deps dist/*.whl
& $py pixel_refine_desktop/ui/views/settings/Perfomance/test_comprehensif.py
```

For CPU/Vulkan parity (including exact integer cases and one-ULP float checks):

```powershell
& $py taichi_vision/taichi_algorithm/aot_py/test_aot_backend_parity.py `
  --compare --compare-backend vulkan --device 1
```

The Intel UHD 620 native Vulkan gate is:

```powershell
python taichi_vision/vulkan_probe.py --comprehensive --all-intel --persist --repeat 5 --timeout 1200
```

## Current qualification addendum (2026-09-05)

The latest native desktop records are tied to exact device and driver
identities. Intel UHD Graphics 620 native Vulkan API 1.3.215 with driver
101.2115 passed 75/75 target-qualified TCM loads, 940/940 SPIR-V shader
validations, 28/28 algorithm checks, lifecycle/graph parity MAE
`3.7529832752625225e-07`, and the 8122x2966 float32 stress gate. The same
device through the explicit native `ig11icd64.dll` OpenGL ICD passed 29/29
comprehensive checks and the recorded 8122x2966 direct full-frame stress gate.

The fast hardware matrix also records CPU 5/5, CUDA on NVIDIA MX150 5/5,
native NVIDIA OpenGL 5/5, and native NVIDIA Vulkan 5/5 where the corresponding
process-level runs were available. These records qualify only the exact
devices, drivers, shapes, dtypes, and commands tested. They do not establish
universal support for historical drivers or arbitrary TCM graphs.

Native Intel graphics compatibility mode uses host-visible buffers and
serialized direct dispatch while retaining the selected GPU backend. Intel
OpenGL startup remains lazy because the native context is thread-affine.
Dozen/D3D12 translation adapters remain excluded from production selection;
`AOT_ALLOW_TRANSLATION=1` is diagnostic-only.

## Historical qualification snapshot

The following is the historical evidence-based status (2026-08-08). “Artifact”
counts are target-qualified archives; a percentage is not treated as a runtime
guarantee when a real device is unavailable.

| Target | Artifact coverage | Runtime evidence | Readiness estimate |
|---|---:|---|---:|
| CPU x86_64 Windows | 64/64 | 28/28 comprehensive, 25/25 research, 24.1 MP parity | ~95% |
| Vulkan x86_64 NVIDIA | 64/64 generic SPIR-V | 28/28 comprehensive, 25/25 research, native NVIDIA ICD | ~92% |
| Vulkan x86_64 Intel | 64/64 generic SPIR-V | 28/28 comprehensive, 25/25 research, native Intel ICD | ~90% |
| CUDA x86_64 NVIDIA | 64/64 | 28/28 comprehensive, 25/25 research on MX150 | ~90% |
| OpenGL x86_64 NVIDIA | 64/64 generic | 29/29 comprehensive, 25/25 research, native NVIDIA ICD | ~92% |
| OpenGL x86_64 Intel | 43 direct + 21 generic | 29/29 algorithm gate, native Intel ICD; 24.1 MP recorded pipeline passes, deep kernel-by-kernel replay remains time-limited | ~88% |
| CPU ARM64 Android/Linux | 64/64 + 467/467 AArch64 kernels | bridge/ABI/NEON, linked C API runtime, and LLVM lowering pass; no ARM device | ~90% static |
| OpenGL ARM64 Linux | 64/64 | AArch64 bridge + headless X11-free C API/RPATH gate; no ARM device | ~45% static |
| GLES ARM64 Linux | 64/64 | AArch64 bridge + headless X11-free C API/RPATH gate; no GLES device | ~40% static |
| Vulkan ARM64 Android | 64/64 promoted SPIR-V | 793/793 SPIR-V and bridge pass; no ARM device | ~20% runtime-qualified |
| GLES ARM64 Android | 64/64 compiled with `ti.gles` | 807/807 SPIR-V 1.3 payloads, bridge/ABI/NEON and linked C API pass; no GLES device | ~25% static |

The desktop percentages include the tested APIs, dtype policy, memory gates,
and native driver runs; they do not claim every arbitrary graph is free of a
reference-path guard. ARM CPU is deliberately reported as static until the
same parity and lifecycle suite runs on an ARM64 process.

The NVIDIA OpenGL qualification was repeated through the direct native ICD
path with `PIXEL_REFINE_OPENGL_CONTEXT=icd` and an NVIDIA vendor contract. The
bridge selected `nvoglv64.dll` and reported `NVIDIA GeForce MX150/PCIe/SSE2`;
the fast gate passed 5/5 and the full 24.1 MP gate passed 29/29. This is a
different proof from an ordinary Windows context, which may be created on the
Intel adapter and must therefore be rejected as a renderer mismatch.

The OpenCV-style `aot_wrapper.CLAHE` entry point now dispatches the real
target-qualified `clahe_pipeline_f32` graph instead of discarding its histogram
and LUT and returning a global normalize approximation. CPU full validation
remains 28/28 and native NVIDIA OpenGL remains 29/29 after this change; CLAHE
parity is MAE 0.168091 on CPU and 0.160461 on NVIDIA OpenGL for the standard
4x4 synthetic gate.

The wrapper `dilate`/`erode` calls were likewise corrected from a blur
approximation to the target-qualified morphology graphs. CPU and native
NVIDIA OpenGL 3x3 parity probes both produced zero MAE against OpenCV on the
binary-shape gate.

On the current driver `101.2115`, the native desktop matrix passes: CPU
28/28, Vulkan NVIDIA 28/28, Vulkan Intel 28/28, CUDA NVIDIA 28/28, and
OpenGL NVIDIA 29/29. OpenGL Intel passes the 29/29 algorithm gate and the
24.1 MP recorded-pipeline gate on the direct Intel ICD; its independent
kernel-by-kernel 24.1 MP replay is intentionally treated as time-limited on
the UHD 620 rather than reported as a completed deep result. The research
suite adds 25/25 checks on CPU, CUDA, both Vulkan adapters, and both OpenGL
ICDs at its qualified sizes. Device logs confirm native NVIDIA/Intel ICDs; no
Dozen adapter or CPU fallback was used for these qualification processes.

The validation manifest now also contains a static portability audit of every
embedded shader. The current desktop Vulkan archives contain 793 SPIR-V 1.3
shaders; all validate for Vulkan 1.1 and require only the base `Shader` capability. Maximum
compute local size is 128 invocations and maximum descriptor pressure is 6
storage buffers plus one uniform buffer per shader. Guided Filter's public
Vulkan path was split into portable passes, reducing its peak from 16 to 6
storage buffers; MLRI-ADMM step 2 was split by color, reducing its peak from 8
to 6 together with split gradient passes and scalar color-matrix dispatch.
BM3D was split into portable block-match, DCT, and overlap-add passes,
reducing its peak from 8 to 6. Farneback's three polynomial-weight tables are
packed into one Vulkan buffer, reducing its peak from 7 to 6 without changing
the public API or its CPU/OpenGL graph ABI. A driver/artifact pair is rejected
before dispatch when its declared
features cannot satisfy the audit.
Removing accidental `Float64` use from `common` and `gaussian` widened the
profile without changing their tested CPU/Vulkan/OpenGL output accuracy.
On multi-Intel systems each native adapter is qualified independently and
receives its own fingerprint/driver/artifact manifest entry.

Vulkan selection now applies the Dozen/D3D12 quarantine to explicit and
restored ordinals as well as automatic scans.  If an ordinal changes after a
driver update and lands on a translation adapter, the selector resolves the
same vendor's native adapter; translation can only be enabled deliberately
with `PIXEL_REFINE_AOT_ALLOW_TRANSLATION=1` for diagnostics.

The ARM CPU retarget runner is shared by both `cpu_arm64_android` and
`cpu_arm64_linux`: 64/64 archives (467 LLVM kernels) plus matching runtime
bitcode are generated and lowered to AArch64 objects, with explicit generic
`+neon` function features.  The ARM gate also rejects stale x86/SSE/AVX
metadata.  LLVM 20 is used only for this offline
lowering check; production bitcode remains produced by the matching Taichi/
NDK LLVM toolchain.  No ARM device execution has been performed yet.

CPU ARM bridge shared objects are now cross-compiled for both profiles as
`aot_dll/cpu_arm64_android/taichi_aot_engine.so` and
`aot_dll/cpu_arm64_linux/taichi_aot_engine.so`; exported ABI symbols are
present and the ELF headers are AArch64.  `ti_cast_buffer` is compiled with
ARMv8 NEON/ASIMD conversion instructions (verified by
`validate_arm_bridge.py`), while the public C ABI remains unchanged.  The
Android and Linux bridge directories carry an ABI-matching
`libtaichi_c_api.so` with a sibling `$ORIGIN` runtime path.  The Linux C API
was linked with the headless `TI_WITH_X11=OFF` profile and exposes the stable
`LIB_C_API_1.0` symbols; its `libc.so.6`/`libm.so.6` dependencies are resolved
by the target distribution (the validator also rejects any accidental X11
dependency).  Device execution is still pending.

The ARM bridge build uses `-O3` (GNU AArch64 for Linux, NDK Clang for Android)
while retaining the generic `armv8-a+simd` compatibility floor (no fast-math
or CPU-specific `-mcpu` is enabled). The Linux OpenGL and GLES bridges now
also pass the ELF/ABI/NEON/C-API gate with no host sysroot RPATH; device
execution remains pending.

OpenGL pipeline admission now checks projected resident allocation before
calling the native driver. This is important for Intel shared-memory ICDs,
which may return `GL_INVALID_OPERATION` from `glGenBuffers` instead of a
recoverable allocation error when a graph is over-committed. OpenGL
`reinit()` preserves the validated native ICD context and resets modules and
buffers in place; destroying and recreating a raw Intel context in the same
process is not reliable on the tested driver.

The GLES Android profile is now compiled through the real `ti.gles` Taichi
architecture rather than relabeling desktop OpenGL archives. All 64 target
qualified TCM modules are present, the six analysis modules are compiled
directly for GLES, and the GLES bridge is linked against the matching
`libtaichi_c_api.so`. The embedded 807 SPIR-V payloads pass the generic
`spv1.3` validator; this is a static shader/ABI gate only and does not claim
that every Android GLES driver accepts the required compute-shader extensions.
The public dispatcher now treats `gles` as a graphics backend for host-cast
coherency, pipeline recording, optical-flow lifecycle, camera synchronization,
and worker initialization; it no longer silently takes desktop-OpenGL-only
branches. Capability policy still marks GLES as runtime-pending until an
Android process creates and exercises a real GLES context.

The desktop and ARM bridges share the same saturating f32→u8/u16 conversion
contract for SIMD and scalar tails (including NaN/out-of-range inputs).  This
keeps baseline x86, AVX2, and ARM NEON host-buffer normalization numerically
consistent without changing the exported ABI.

Signed `i16` host-buffer conversion is now native for `f32`/`i16` and copy
operations on CPU, Vulkan, and CUDA bridges, with defined clamping for float
values outside the representable range.  OpenGL deliberately uses the
synchronized NumPy path for host casts because Windows ICD mapping can expose
non-coherent storage; this preserves correctness across NVIDIA and Intel
drivers instead of assuming a coherent pointer.
The x86 AVX2 and ARMv8 NEON bridges use vector narrowing/widening for the
bulk of these conversions, with scalar tails for odd lengths and NaN values.
The `dtype_probe.py --dtype int16` gate now exercises this conversion and its
round-trip on CPU, Vulkan, CUDA, and OpenGL; all four tested desktop paths
passed.

CPU Windows packaging carries both the AVX2 bridge and an SSE2-compatible
baseline bridge. Runtime feature detection selects the baseline DLL on hosts
without AVX2. The baseline now vectorizes f32/i16 and normalized f32/u8/u16
host conversions with SSE2, retaining scalar tails for exact saturation and
NaN behavior; a forced-baseline fast smoke test passes 5/5 and the int16 dtype
probe passes without changing the public API or TCM graph set. On the local
4-million-element u16 cast probe, the SSE2 baseline completed in 12.1 ms
(best sample) versus 9.0 ms for AVX2, while producing identical edge-case
results.

The desktop Vulkan set contains 793 SPIR-V shaders; all pass
`spirv-val --target-env vulkan1.1` and use only the `Shader` capability plus
`SPV_KHR_storage_buffer_storage_class`.  Those architecture-neutral archives
are promoted to `vulkan_arm64_android` (64/64), but the ARM
Vulkan bridge/device gate remains pending.  This promotion must not be read as
Android runtime support until a real ARM64 Vulkan process completes the
lifecycle and parity suite.  The companion bridge is now cross-compiled at
`aot_dll/vulkan_arm64_android/taichi_aot_engine.so`; its ELF/ABI is validated,
but it still requires a Vulkan-enabled ARM `taichi_c_api` runtime.
The target manifest (schema 1) records architecture/backend/runtime
requirements and keeps ARM device execution explicitly pending; it does not
claim that static cross-compilation is an ARM runtime qualification.

The comprehensive gate now invokes BM3D through its public API and all five
MLRI-ADMM APIs. Their deterministic CPU signatures are checked on every
backend; Intel UHD 620 parity measured below `3e-8` mean absolute error.

Vulkan memory policy reads `VK_EXT_memory_budget` directly. Intel shared heaps
are jointly clamped by the driver budget and available Windows RAM; discrete
NVIDIA heaps are clamped by their dedicated VRAM budget.

The block planner now refines its resident block size from the operation
shape (channel count) instead of assuming every workload is four live RGB
`float32` buffers.  Grayscale/flow and compact `u8`/`u16` workloads can
therefore use more of the safe iGPU shared-memory budget, while the 2048-pixel
hard cap and pressure/driver-heap limits remain unchanged.  This policy is
covered by the deterministic memory-governor suite (21/21).

OpenGL now has a native standalone Windows context: the C API creates a hidden
GLFW OpenGL 3.3 context when no application context was imported, then activates
it before runtime allocation. A minimal `opengl_smoke.tcm` graph has been loaded
and executed successfully through the same AOT API (buffer upload, dispatch,
readback). The target-qualified desktop inventory now contains 64 generic
OpenGL TCMs (with 43 direct Intel aliases), and the full 29/29 suite passes on
both tested native ICDs; GLES/EGL remains a separate mobile target.

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

OpenGL Canny now uses the native multi-pass graph by default
(`PIXEL_REFINE_AOT_NATIVE_CANNY=1`). The full ICD gates measured IoU 0.957
on the tested synthetic edge case; setting the switch to `0` remains an
explicit OpenCV reference escape hatch for driver triage.

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
is recorded and executed successfully on both CPU and OpenGL. The 24.1 MP
master graph also passes its accuracy gate on the qualified desktop backends;
arbitrary fallback-heavy graphs remain guarded until their individual resource
and dtype contracts are validated.

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
from taichi_vision.taichi_aot import PipelineStage, run_block_pipeline

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
