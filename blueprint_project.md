# Pixel Refine Project Blueprint

This is the maintained architecture and file-map blueprint. User-facing API
details belong in `taichi_library/documentation/`; normative agent rules belong
in `ai_governance/` and the operating contract in `agen.md`.

## Top-level structure

```text
Pixel Refine/
├─ main_desktop.py                    desktop entry point
├─ pixel_refine_desktop/              Qt desktop application layer
├─ taichi_library/                    native/AOT algorithm library
│  ├─ taichi_aot/                     runtime, lifecycle, memory, backend facade
│  ├─ taichi_algorithm/               single source for kernels and dispatch
│  ├─ AOT_BACKEND_MATRIX.md           canonical backend/ABI contract
│  └─ documentation/                  API, architecture, status, build guides
├─ ai_governance/                     normative rules and evidence snapshots
├─ test_algorithm/                    upstream Taichi source and experiments
├─ resources/                         shared desktop UI and animation library
└─ venv/                              project Python environment
```

Mobile Kotlin is a separate scope and is not part of the Windows desktop
production baseline unless explicitly requested.

## Taichi runtime layers

```text
application
  -> taichi_library.taichi_aot
  -> taichi_algorithm.aot_api
  -> taichi_aot.engine
  -> target bridge + taichi_c_api + target-qualified TCM
  -> native backend driver
```

`engine.py` owns backend selection, context/lifecycle, artifact resolution,
buffer ownership, memory pressure, cache residency, and recovery. The public
algorithm dispatcher owns dtype policy, API wrappers, block adapters, and
same-backend fallback decisions. Applications must not load DLLs or TCMs
directly.

## Algorithm source layout

Family implementations and family-local compilers are colocated:

```text
taichi_algorithm/
├─ aot_api/          public dispatch and research leaf exports
├─ aot_py/           shared build orchestration, validators, and tests
├─ aot_tcm/          target-qualified compiled archives
├─ alignment/        geometric alignment and RANSAC
├─ camera_api2/      camera/YUV helpers
├─ compression/      JPEG, PNG, WebP, HEIF/AVIF, DNG and RAW paths
├─ demosaicing/      bilinear, DCB, Hamilton, ARM, MLRI-ADMM
├─ denoising/        denoising family adapters
├─ feature_matching/ AKAZE/OFB and descriptors
├─ image_processing/ color, edges, morphology, enhancement, extended APIs
├─ interpolation/    sampling and interpolation
├─ math_ops/         numeric operations
├─ optical_flow/     Lucas–Kanade, Farneback, Horn–Schunck, block matching
├─ panorama/         panorama and stitching helpers
├─ pyramid/          image pyramid operations
├─ sfm/              stereo, MVS, registration, point clouds, Poisson
└─ smoothing/        Gaussian, bilateral and related filters
```

Canonical shared compiler modules are at the `taichi_algorithm` root:
`compile_common_tcm.py`, `compile_cast_tcm.py`, and
`compile_research_tcm.py`. Same-named files under `aot_py/` are compatibility
shims. New family compilers belong beside their kernels.

## Target artifacts and bridges

The current desktop target directories are:

- `aot_tcm/cpu_x86_64_windows/`
- `aot_tcm/cuda_x86_64_windows_nvidia/`
- `aot_tcm/opengl_x86_64_windows/`
- `aot_tcm/vulkan_x86_64_windows/`

Runtime bridges are under `aot_py/aot_dll/{cpu,cuda,opengl,vulkan}/`. A TCM,
bridge, C API, OS, architecture, vendor, and ABI must come from one target
profile. Artifact inventory is not runtime qualification.

Future profiles include ARM CPU, GLES, and Vulkan ARM; static artifacts or
cross-compilation do not qualify a real mobile device.

## Automatic pipeline and memory model

The default planner decides between full-frame and block execution from the
operation contract, shape, halo, dtype, and memory pressure. Allocation cache
and tile-result cache are separate. Block size is adaptive with a current
policy hard cap of 2048 pixels; it is not a universal fixed tile size.

Unknown, global, quarantined, or over-budget operations remain full-frame. A
failed block/native path must recover through the same-backend full-frame path.
Independent block concurrency is not implied by `auto_pipeline`.

## Desktop application boundary

`pixel_refine_desktop/` orchestrates UI, batch processing, denoising, alignment,
and persistence. It calls the Taichi Library and must not duplicate Taichi
kernels or backend selection. Retired C++ spatial-similarity implementations
and `denoising/Similarity.py` are not valid paths.

UI changes use `resources/GenericUILibrary`, existing live-update/translation
hooks, and the established animation library. Providers own persistence;
shared renderers own controls.

## Documentation and evidence

Start at `taichi_library/documentation/README.md`. The API catalog covers all
115 public `aot_api` function entry points. Algorithm labels are conservative:
qualified, experimental, pending, or quarantined. Every qualification record
must include backend, device, shape, dtype, command, observed result, lifecycle,
and memory evidence.
