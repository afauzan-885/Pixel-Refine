# Block Migration Audit

This inventory covers the public AOT APIs in `taichi_aot/__init__.py`.
An operation must opt in only when its category preserves output correctness.

## Migrated

| API | Strategy | Notes |
| --- | --- | --- |
| `copy` | independent tile | output checksum is compared with the source tile |
| `absdiff` | independent tile | both sources are checksummed before cache reuse |
| `rgb2gray` | independent tile | RGB input and grayscale output use matching tile coordinates |
| `split_3ch`, `merge_3ch` | independent tile | fused common graphs run once per tile; split outputs are cached together |
| `extract_channel`, `insert_channel` | independent tile | insertion keeps its in-place NumPy API contract |
| `gaussian_blur` | halo tile | halo equals the Gaussian kernel radius |
| `box_filter` | halo tile | halo equals half the kernel size |
| `median_filter` | halo tile | fixed one-pixel halo for the supported 3x3 graph |
| `laplacian` | halo tile | one-pixel halo |
| `sobel` | halo tile | one-pixel halo; cached as an `dx`/`dy` output pair |
| `non_local_means` | halo tile | halo equals search radius plus patch radius |
| `smooth_flow_gpu` | halo tile | halo equals the Gaussian kernel radius |
| `joint_bilateral_filter` | halo tile | source and guide share the same halo crop |
| `guided_filter_aot` | halo tile | halo equals twice the box-filter radius |
| `enhance_grayscale` | independent tile | source and blur use matching tile coordinates; LUT checksum is part of the cache key |
| `remap` | output tile | source remains global on GPU; coordinate maps and result are tiled without changing sampling coordinates |
| `resize` | cached output tile | linear, cubic, and area graphs use global output offsets |
| `image_pyramid` | cached level-ordered output tile | each level completes before the next; downsample centers retain global 2x alignment |
| `remap_with_flow` | cached output tile | source and flow remain global; flow interpolation uses global output coordinates |
| `warp_perspective` | cached output tile | inverse homography is evaluated from global tile coordinates |
| all Hamilton/ARM demosaic variants and `demosaic` dispatcher | Bayer-phase-aware native AOT tile | full-resolution graphs use even-origin halos; fused half-resolution graphs map output tiles directly to Bayer 2x2 footprints |
| `lucasKanade`, `blockMatching` | aligned grid halo tile | tile geometry is aligned to `grid_step`; unsupported sparse/diagnostic forms retain fallback |
| `farneback_flow` | pyramid-aware halo tile | conservative receptive-field halo; iterative work completes inside each cached tile |

## Local Operations

These have bounded neighborhoods and can use the shared executor after parity
tests at tile boundaries.

| APIs | Required strategy |
| --- | --- |
| `box_filter`, `median_filter` | halo tile using filter radius |
| `sobel`, `laplacian` | halo tile, usually one pixel |
| `non_local_means` | halo tile with search-window radius |
| channel/color conversions | independent tile when no histogram is used |

## Custom Tile Mapping

These require output-to-input coordinate mapping, tile-scale accounting, or
algorithm-specific overlap. They cannot use a simple source crop.

| APIs | Required strategy |
| --- | --- |
| `joint_bilateral_upsample` | map high-resolution output tiles to low-resolution source and guide footprints |
| `inpaint`, `seamless_clone` | domain decomposition with overlapping solver iterations |

## Global Or Coordinated Operations

These are intentionally excluded from the generic executor because partial
tiles cannot independently produce the final result.

| APIs | Required strategy |
| --- | --- |
| `fft2`, `ifft2`, `phase_correlation` | global transform or staged distributed FFT |
| `otsu_threshold_aot`, `clahe_aot`, `hough_lines_aot`, `align_mtb` | tile-local partial reductions followed by global reduction |
| `ncc_alignment`, `zncc`, `find_homography`, `ransac_flow_cleanup` | global candidate/reduction phase before output generation |
| `ofb`, `akaze` | global feature/correspondence coordination |
| Horn-Schunck flow | overlap plus cross-tile iterative state exchange |
| `bm3d`, `bilateral_grid_filter` | global aggregation or grid state with controlled ownership |
| `mlri_admm` demosaic | distributed ADMM with boundary-state synchronization |

## Rules

1. Keep `TaichiGPUBuffer` inputs on the existing full-frame GPU path.
2. Add block mode only for NumPy inputs after full-frame parity is covered.
3. Cache keys include source tile checksums and operation parameters.
4. Silent-output validation is mandatory only where an inexpensive invariant
   exists; otherwise retries cover execution failures and parity tests guard
   the implementation.
