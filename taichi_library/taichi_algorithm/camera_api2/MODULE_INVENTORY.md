# Modul Baru yang Perlu Dibuat untuk Camera2 Pipeline

## Modul Prioritas 1 (Kritis - Pintu Masuk Data)
| # | Modul | Fungsi | Status |
|---|-------|--------|--------|
| 1 | `yuv_converter.py` | YUV_420_888/NV21/NV12 → RGB float32 (ti.kernel) | **BARU** |
| 2 | `camera_pipeline.py` | Orchestrator: capture→process→output | **BARU** |
| 3 | `frame_manager.py` | Buffer pool, frame queue, zero-copy | **BARU** |
| 4 | `__init__.py` (folder camera_api2) | Public API export | **BARU** |

## Modul Prioritas 2 (Enhancement Spesifik Camera2)
| # | Modul | Fungsi | Leverage Taichi Existing |
|---|-------|--------|--------------------------|
| 5 | `white_balance.py` | WB correction dari Camera2 AWB gains | `color_convert.py` |
| 6 | `tone_mapping.py` | HDR tone mapping, exposure compensation | `normalize.py`, `clahe.py` |
| 7 | `temporal_merge.py` | Multi-frame stacking | `farneback_flow.py`, `phase_correlation.py`, `compute_spatial.py` |
| 8 | `adaptive_denoise.py` | ISO-aware denoise param selector | `nlm.py`, `bm3d.py`, `guided_filter.py` |

## Modul Prioritas 3 (Advanced Features)
| # | Modul | Fungsi | Leverage Taichi Existing |
|---|-------|--------|--------------------------|
| 9 | `metadata_adapter.py` | Camera2 metadata → algorithm params | - |
| 10 | `quality_assessor.py` | Real-time SSIM/PSNR monitoring | `ssim.py` |
| 11 | `unsharp_mask.py` | Sharpening via gaussian | `gaussian.py`, `absdiff` |

## Modul yang 100% Reuse (Tidak Perlu Buat Baru)
Dipanggil langsung dari `taichi_algorithm`:
- `ta.non_local_means()` → denoising per-frame
- `ta.hfcd_denoise()` → heavy denoise
- `ta.gaussian()` → blur/sharpen base
- `ta.guided_filter()` → edge-preserving smooth
- `ta.bilateral()` → bilateral filter
- `ta.median()` → median filter
- `ta.clahe()` → adaptive histogram equalization
- `ta.canny()` → edge detection
- `ta.cvtColor()` → color conversion (BGR↔Gray)
- `ta.cvtColor_extended()` → BGR↔HSV, BGR↔LAB, BGR↔YCrCb
- `ta.farneback_flow()` → optical flow alignment
- `ta.phase_correlation()` → global motion estimation
- `ta.compute_spatial_weight()` → ghost rejection
- `ta.build_image_pyramid()` → multi-scale processing
- `ta.resize()` → scaling (bilinear, bicubic, area, nearest)
- `ta.remap()` → geometric remapping
- `ta.absdiff()` → frame difference
- `ta.otsu_threshold()` → auto thresholding
- `ta.ssim()` → quality metric
- `ta.gpu_histogram()` → histogram analysis
- `ta.dilate()` / `ta.erode()` → morphology
- `ta.hamilton_demosaic()` / `ta.arm_demosaic()` → RAW Bayer demosaic
- `ta.align_mtb()` → median threshold bitmap alignment
- `ta.ransac()` → flow cleanup
- `ta.inpaint()` → image inpainting
- `ta.enhance_grayscale()` → grayscale enhancement
- `ta.NoiseEstimator` → noise level estimation
- `ta.box_filter()` → box/mean filter
- `ta.sobel()` / `ta.laplacian()` → gradient operators
