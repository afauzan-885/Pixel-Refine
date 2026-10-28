# API Usage

This is the complete quick-reference for the public entry points exported by
`taichi_vision.taichi_algorithm.aot_api`, including research and compatibility
wrappers. Function signatures in source remain authoritative.

## Canonical import and backend selection

```python
from taichi_vision import taichi_aot as aot
```

Select a backend before the first import:

```powershell
$env:PIXEL_REFINE_AOT_ARCH = "cpu"       # cpu, cuda, vulkan, opengl, gles
$env:PIXEL_REFINE_AOT_DEVICE = "0"       # GPU ordinal hint
$env:PIXEL_REFINE_TARGET_VENDOR = "NVIDIA"  # optional vendor constraint
python your_script.py
```

The loader validates the native renderer/vendor. A mismatch is an explicit
error; the application must not silently use another GPU.

## Runtime, block, and memory APIs

| API | Use |
|---|---|
| `get_engine()` | Inspect the canonical engine handle. |
| `set_block_mode()` | Set block enablement, tile size, threshold, and adaptive memory. |
| `get_block_config()` | Read the active block configuration. |
| `get_block_cache_stats()` | Read tile-result cache hit/miss counters. |
| `get_last_block_execution()` | Inspect full-frame/block/recovery and readback strategy. |
| `clear_block_quarantine()` | Clear an operation quarantine after controlled revalidation. |
| `get_memory_status()` | Read RAM/VRAM pressure, resident limits, and budget. |
| `trim_memory_pool()` | Release idle buffers after a large batch. |
| `auto_pipeline()` | Build an automatic pipeline from graph/stage specifications. |
| `configure_block_reservation()` | Reserve memory budget for a block operation. |
| `load_tcm()` | Lazily load a target-qualified TCM module. |
| `unload_all_modules()` | Release all loaded TCM modules. |
| `research_aot_module()` | Resolve a research leaf module; normally used internally. |

## Buffers, channels, and numeric preparation

| API | Use |
|---|---|
| `upload()` | Upload an ndarray; set `is_vector=True` for flow/vector data. |
| `copy_field()` | Copy between compatible fields/buffers. |
| `copy()` | Copy an image or buffer, optionally remaining GPU-resident. |
| `extract_channel()` | Extract one grayscale/channel plane. |
| `split_3ch()` | Split RGB/BGR into three planes. |
| `merge_3ch()` | Merge three planes into a 3-channel image. |
| `insert_channel()` | Write one plane into a destination channel. |
| `rgb2gray()` | Convert RGB/BGR to luminance. |
| `absdiff()` | Absolute difference for motion/noise masks. |
| `cvtColor()` | OpenCV-compatible color conversion codes supported by the API. |
| `normalize_image()` | Normalize dtype and value range at the API boundary. |
| `to_gamma_proxy()` | Apply a gamma-proxy transform for display previews. |

## Resize, sampling, and filters

| API | Use |
|---|---|
| `resize()` | Bicubic, bilinear, area, or nearest resize. |
| `sample_at_bicubic()` | Single-point bicubic sampling. |
| `sample_at()` | Single-point sampling using the selected default mode. |
| `sample_at_bilinear()` | Single-point bilinear sampling for maps/flow. |
| `box_filter()` | Local mean/box smoothing. |
| `gaussian_blur()` | Gaussian denoise or feature/flow pre-blur. |
| `image_pyramid()` | Coarse-to-fine image pyramid. |
| `median_filter()` | Impulse and hot-pixel removal. |
| `sobel()` | X/Y gradient computation. |
| `laplacian()` | Second-derivative detail/edge response. |
| `joint_bilateral_filter()` | Edge-preserving denoise with a guide image. |
| `joint_bilateral_upsample()` | Upsample low-resolution data using a high-resolution guide. |
| `bilateral_grid_filter()` | Bilateral-grid edge-preserving smoothing. |
| `guided_filter_aot()` | Guided filtering with a separate guide. |
| `non_local_means()` | Patch-based non-local denoising. |
| `non_local_means_aot()` | Explicit AOT entry point for non-local means. |
| `bm3d()` | BM3D denoising for burst or single-frame inputs. |

## FFT, alignment, and optical flow

| API | Use |
|---|---|
| `generate_hanning_window_2d()` | Generate an FFT/phase-correlation Hanning window. |
| `mean_division()` | Normalize an accumulator by mean/count. |
| `normalize_accumulator()` | Stabilize weighted tile accumulation. |
| `stitch_tile()` | Write a tile into an output canvas. |
| `stitch_tile_normalized()` | Stitch a tile with weights/normalization. |
| `fft2()` | 2D FFT; use `use_hanning=True` to reduce leakage. |
| `ifft2()` | Inverse FFT with an optional target shape. |
| `phase_correlation()` | Estimate global translation between frames. |
| `ncc_alignment()` | Normalized cross-correlation alignment. |
| `zncc()` | Zero-mean normalized cross-correlation. |
| `ransac_flow_cleanup()` | Remove flow outliers with a RANSAC threshold. |
| `ransac_flow_cleanup_aot()` | Explicit AOT name for flow cleanup. |
| `remap()` | Canonical warp: one packed `(H,W,2)` coordinate field with `coordinate_mode`. |
| `remap_with_flow()` | Compatibility adapter for `remap(..., coordinate_mode="displacement_xy")`. |
| `smooth_flow_gpu()` | Smooth a flow field before warping. |
| `build_flow_maps()` | Build coordinate maps from flow/transform data. |
| `farneback_flow()` | Dense Farneback optical flow. |
| `lucasKanade()` | Lucas–Kanade optical-flow adapter. |
| `blockMatching()` | Block-matching optical-flow adapter. |
| `align_mtb()` | Median Threshold Bitmap alignment for exposure brackets. |
| `warp_perspective()` | 3x3 homography warp. |
| `warp_affine_aot()` | 2x3 affine warp from the extended AOT API. |

### Resident image warps

`warp_affine_aot()` and `warp_perspective()` infer the result location from the
source. NumPy images still return NumPy by default; an existing
`TaichiGPUBuffer` now returns a device-resident buffer by default. Set
`return_gpu=False` explicitly to request a NumPy result (and the associated
readback). Both functions retain caller ownership of the source; release the
returned buffer when finished. Image pixel loops remain in AOT Taichi; matrix
inversion/validation remains a small host-side setup operation.

```python
warped_gpu = warp_affine_aot(image_gpu, affine_2x3, dsize)  # no image readback
warped_np = warp_affine_aot(image_gpu, affine_2x3, dsize, return_gpu=False)
warped_gpu = warp_perspective(image_gpu, homography_3x3, dsize)
```

## Remap: canonical contract and resident usage

`remap()` is the single warp entry point and stays as short as `cv2.remap`.
Everything that can be inferred is inferred.

```python
out = remap(src, flow)              # flow (H,W,2) displacement -> NumPy result
out = remap(src, map)               # map  (H,W,2) absolute (x, y)
out = remap(src_gpu, flow_gpu)      # GPU operands -> GPU result, no host copy
```

Full signature, with the optional controls spelled out:

```python
remap(
    src,                  # (H,W) or (H,W,3); GPU buffer keeps work resident
    coordinates,           # (H,W,2) float32
    output_size=None,     # defaults to src spatial shape
    coordinate_mode=None,  # inferred; "displacement_xy" or "absolute_xy"
    return_gpu=None,      # inferred from operands: GPU in -> GPU out
    dst=None,             # optional reusable destination buffer
    session=None,         # defaults to the active/default BufferSession
)
```

Inference rules:

- `output_size` falls back to `src.shape[:2]`.
- `coordinate_mode` is `"displacement_xy"` unless the split-map form
  (`remap(src, map_x, map_y)` or `map_x=`/`map_y=`) selects `"absolute_xy"`.
- `return_gpu` follows the operands: any GPU buffer means the result stays on
  the device; host arrays return NumPy.
- `session` resolves to the innermost `with BufferSession(...)` block on the
  current thread, otherwise a lazily created process default.
- `absolute_xy` needs host coordinates and raises `NotImplementedError` for
  device coordinates instead of silently copying to the host.

### Efficient resident usage

```python
from taichi_vision.taichi_algorithm.buffer_session import BufferSession

with BufferSession(engine=aot.engine) as session:
    src_gpu, _ = session.upload_if_needed(src, is_vector=True)
    flow_gpu, _ = session.upload_if_needed(flow)
    dst_gpu = session.acquire_buffer((h, w, 3), dtype=np.float32,
                                     is_vector=True, tag="remap_dst")
    for frame_flow in flow_frames:
        out_gpu = remap(src_gpu, frame_flow, dst=dst_gpu)
    session.sync()
    result_np = dst_gpu.to_numpy()   # the only host transfer
```

Guidelines:

- Pass GPU buffers for `src` and `coordinates`; `upload_if_needed` caches by
  array identity, so repeated calls do not re-upload.
- Reuse one `dst` for a frame loop. With `return_gpu` results and no `dst`, the
  returned buffer is caller-owned and must be released by the caller; a
  session scratch slot would be recycled underneath you.
- Keep `dst` distinct from `src`: bilinear sampling reads neighbouring taps, so
  an in-place remap would read already-written pixels.
- Call `to_numpy()` only at the pipeline boundary. It dominates the cost
  (roughly 50-65 ms for an 11 MB 720p float32 frame on an Intel UHD 620 Vulkan
  device, versus about 6.5 ms of kernel compute).
- Never bounce through NumPy between GPU stages just to pass data along.

Measured on Vulkan (Intel UHD Graphics 620), source/output float32 720x1280x3,
flow float32 720x1280x2: resident GPU-to-GPU median about 8.1 ms versus about
64 ms for the host-array path, bit-identical output. The compact call and the
long explicit call measured 8.13 ms and 8.11 ms respectively, so the short form
costs nothing. Absolute maps and other backends (CUDA/OpenGL) are unverified.



The demosaic functions accept Bayer RAW data and the corresponding CFA/white
balance parameters. `half_res` returns half resolution; `1channel` returns a
single luminance/green plane; `3channel` returns full RGB.

| API | Use |
|---|---|
| `demosaic()` | Universal dispatcher selected by `method` and `half_res`. |
| `bilinear()` / `bilinear_demosaic()` | Fast stable preview baseline. |
| `dcb()` / `dcb_demosaic()` | Directional Color Balance demosaic. |
| `dcb_demosaic_1channel()` | DCB single-channel output. |
| `dcb_demosaic_half_res()` | DCB half-resolution output. |
| `dcb_demosaic_rgb_half_res()` | DCB half-resolution RGB output. |
| `dcb_demosaic_3channel()` | DCB full-resolution RGB output. |
| `hamilton()` / `hamilton_demosaic()` | Hamilton–Adams edge-directed demosaic. |
| `hamilton_demosaic_1channel()` | Hamilton single-channel output. |
| `hamilton_demosaic_half_res()` | Hamilton half-resolution output. |
| `hamilton_demosaic_rgb_half_res()` | Hamilton half-resolution RGB output. |
| `hamilton_demosaic_3channel()` | Hamilton full-resolution RGB output. |
| `arm()` / `arm_demosaic()` | Adaptive Residual/Refinement Method demosaic. |
| `arm_demosaic_1channel()` | ARM single-channel output. |
| `arm_demosaic_half_res()` | ARM half-resolution output. |
| `arm_demosaic_rgb_half_res()` | ARM half-resolution RGB output. |
| `pure_arm_demosaic()` | ARM path without additional post-processing. |
| `mlri_admm()` | MLRI-ADMM core/research solver. |
| `mlri_admm_demosaic()` | MLRI-ADMM full RGB demosaic. |
| `mlri_admm_demosaic_1channel()` | MLRI-ADMM single-channel output. |
| `mlri_admm_demosaic_half_res()` | MLRI-ADMM half-resolution output. |
| `mlri_admm_demosaic_rgb_half_res()` | MLRI-ADMM half-resolution RGB output. |
| `mlri_admm_demosaic_3channel()` | MLRI-ADMM full-resolution RGB output. |
| `highlight_recovery()` | Recover clipped highlights before tone mapping. |
| `rotate_by_flip()` | Normalize CFA orientation using a flip code. |

```python
rgb = aot.demosaic(raw, method="hamilton", half_res=False)
preview = aot.demosaic(raw, method="dcb", half_res=True)
```

## Tone mapping and enhancement

| API | Use |
|---|---|
| `get_natural_tone_mapping_lut()` | Build a natural tone-mapping LUT. |
| `apply_coarse_texture_boost()` | Texture boost on a CPU ndarray. |
| `coarse_texture_boost_gpu()` | Texture boost while resident on the GPU. |
| `apply_natural_tone_mapping_np()` | Natural tone mapping on NumPy. |
| `naturalTonemapping()` | Compatibility tone-mapping facade. |
| `tone_map_srgb()` | Convert linear/scene-referred data to sRGB. |
| `enhance_grayscale()` | Grayscale contrast/detail enhancement. |
| `cvtColor_extended()` | Extended color conversion codes. |

## Feature matching and geometry

| API | Use |
|---|---|
| `generate_brief_pattern()` | Create a deterministic BRIEF sampling pattern. |
| `ofb()` | O-FAST-BRIEF detection, description, and matching. |
| `akaze()` | AKAZE feature detection/description/matching. |
| `find_homography()` | Homography estimation with robust outlier cleanup. |
| `get_fed_step_sizes()` | FED step schedule for diffusion preprocessing. |

### Kontrak numerik estimasi geometri

`find_homography()` adalah estimator **hybrid**, bukan komputasi GPU-only:
hipotesis empat titik dan skor konsensus berjalan di AOT; shortlist maksimal
8 kandidat per putaran direfine di host menggunakan normalized SVD float64,
geometric least squares, dan iterasi mask inlier. Input GPU memerlukan readback
korespondensi untuk tahap host ini. `return_gpu=True` meng-upload mask final
int32 `(N,)`; keluaran host tetap uint8 `(N,1)`. Error perangkat diteruskan,
bukan dialihkan ke estimator CPU/OpenCV. Signature dan seed tetap kompatibel.
Nama `method="MAGSAC++"` historis tetap diterima, tetapi kernel menggunakan
soft Tukey scoring, bukan implementasi penuh MAGSAC++.

`alignment.quality.ransac_transform(model="affine")` tetap estimator referensi
NumPy/CPU. Fitting affine dinormalisasi; seleksi dan local refinement memakai
truncated reprojection cost (MSAC), tanpa mengganti affine menjadi similarity
atau homography menjadi affine pada distribusi yang lemah. Data kolinear
persis ditolak; strip tipis/cluster sempit dengan noise tetap dapat menghasilkan
error extrapolasi besar. Mask inlier bukan jaminan akurasi di seluruh frame.

Untuk parity `warp_affine`/`warp_perspective`, gunakan matriks **dan border**
yang sama. Default kernel menggunakan reflect-101; membandingkannya dengan
OpenCV `BORDER_CONSTANT=0` mencampurkan beda border dengan error interpolasi.

## Segmentation, thresholding, and restoration

| API | Use |
|---|---|
| `otsu_threshold_aot()` | Automatic Otsu thresholding. |
| `clahe_aot()` | Contrast Limited Adaptive Histogram Equalization. |
| `canny_aot()` | Multi-pass Canny edge detector. |
| `hough_lines_aot()` | Hough line detection. |
| `inpaint()` / `inpaint_aot()` | Fill masked defects or regions. |
| `seamless_clone()` / `seamless_clone_aot()` | Masked Poisson/seamless cloning. |
| `dilate_aot()` | Morphological dilation. |
| `erode_aot()` | Morphological erosion. |
| `histogram_aot()` | Intensity/channel histogram. |
| `ssim_aot()` | Structural Similarity Index. |
| `filter2d_aot()` | General 2D kernel convolution. |
| `copy_make_border_aot()` | Image padding and border creation. |
| `normalize_aot()` | Extended AOT normalization. |
| `threshold_aot()` | Extended AOT thresholding. |
| `gaussian_window_aot()` | Gaussian window for FFT/weight graphs. |
| `joint_bilateral_guidance_aot()` | Bilateral guidance map. |
| `enhance_image_aot()` | Extended image enhancement. |

## HDR, camera, SfM, and research APIs

These entry points are exported for focused experiments and are marked
**EXPERIMENTAL** unless `ALGORITHM_STATUS.md` says otherwise.

| Group | Entry points |
|---|---|
| HDR | `hdr_weight_aot`, `hdr_normalize_weights_aot`, `hdr_downsample_aot`, `hdr_upsample_aot`, `hdr_subtract_aot`, `hdr_add_weighted_laplacian_aot`, `hdr_add_aot`, `hdr_deghost_residual_aot`, `hdr_response_quantise_aot`, `hdr_merge_linear_aot`, `hdr_merge_log_aot` |
| Tone pyramid | `tone_luminance_aot`, `tone_reinhard_aot`, `tone_srgb_aot`, `tone_simulate_exposure_aot`, `tone_blend_weight_aot`, `tone_weighted_blend_aot`, `tone_contrast_aot`, `tone_downsample_aot`, `tone_upsample_aot`, `tone_subtract_aot`, `tone_add_aot` |
| Research pipeline | `hdr_fuse_aot`, `hdr_fusion_aot`, `local_tone_map_aot`, `tone_map_aot` |
| Camera | `camera_yuv420_aot`, `camera_nv21_aot`, `camera_nv12_aot`, `camera_y_to_gray_aot`, `camera_unsharp_aot` |
| Stereo/SfM | `plane_sweep_stereo_aot`, `multi_view_plane_sweep_aot`, `point_cloud_preprocess_aot`, `bundle_adjust_lm_aot`, `poisson_reconstruct_aot`, `sfm_l2_distance_aot`, `sfm_knn_aot`, `sfm_match_l2_aot`, `sfm_build_5pt_system_aot`, `sfm_batch_build_5pt_system_aot`, `sfm_cheirality_minimal_aot`, `sfm_cheirality_full_aot`, `sfm_triangulate_adaptive_aot`, `sfm_warp_ncc_aot`, `sfm_sweep_depths_aot`, `sfm_winner_take_all_aot`, `sfm_bilateral_refine_depth_aot`, `sfm_sgm_path_aot`, `sfm_patchmatch_iteration_aot` |
| SfM geometry | `vsac_fundamental_aot`, `sfm_icp_accumulate_aot`, `sfm_tsdf_integrate_aot`, `sfm_knn_distance_aot`, `sfm_sor_filter_aot`, `sfm_radius_filter_aot`, `sfm_voxel_hash_aot`, `sfm_voxel_accumulate_aot`, `sfm_normals_pca_aot`, `sfm_reprojection_errors_aot`, `sfm_bundle_normal_equations_aot`, `sfm_apply_point_update_aot`, `sfm_apply_camera_update_aot`, `sfm_cost_aot` |
| Poisson/graph | `sfm_poisson_rasterize_aot`, `sfm_poisson_occupancy_aot`, `sfm_poisson_step_aot`, `graph_cut_unary_aot` |

## Compression and RAW boundary

| API | Use |
|---|---|
| `encode_grayscale_aot()` | JPEG AOT grayscale encoding. |
| `encode_rgb_aot()` | JPEG AOT RGB encoding. |
| `jpeg_encode_aot()` | General JPEG compatibility wrapper. |
| `raw_frame_from_dng()` | Build a `RawMosaicFrame` from DNG. |
| `dng_capability_report()` | Report native DNG capabilities for a target. |
| `raw_flow_tile_contract()` | Define the RAW flow-tile contract. |
| `raw_alignment_guide()`, `raw_alignment_guide_dng()`, `raw_alignment_guide_native()` | Build RAW alignment guidance. |
| `raw_normalize_headroom_native()` | Native RAW headroom normalization. |
| `raw_weight_map()`, `raw_weight_map_native()` | Build RAW fusion weight maps. |
| `fuse_raw_pair_native()` | Fuse two RAW frames on the native path. |

## Practical recipes

```python
# Burst denoise: keep stages resident to avoid repeated transfers.
frames = [aot.InputArray(frame.astype("float32")) for frame in burst]
smoothed = [aot.gaussian_blur(frame, sigma=1.0, return_gpu=True) for frame in frames]

# Alignment followed by warp (canonical packed-coordinate form).
flow = aot.farneback_flow(smoothed[0], smoothed[1], return_gpu=True)
aligned = aot.remap(
    smoothed[1],
    flow,
    output_size=smoothed[0].shape[:2],
    coordinate_mode="displacement_xy",
    return_gpu=True,
)
# remap_with_flow(smoothed[1], flow, *smoothed[0].shape[:2], return_gpu=True)
# is the equivalent compatibility adapter.

# Edge and feature preview.
edges = aot.canny_aot(aot.rgb2gray(image), low_threshold=40, high_threshold=120)
matches = aot.ofb(reference, image, max_kps=1500)
```

`return_gpu=True` returns a `TaichiGPUBuffer`; call `release()` when ownership
ends. Adaptive planning may choose full-frame for small, global, or unqualified
operations. A block failure recovers through the same-backend full-frame path;
there is no silent GPU-to-CPU substitution.

The source signature in `taichi_algorithm/aot_api/__init__.py` and the relevant
research module is always authoritative for defaults and accepted parameters.
