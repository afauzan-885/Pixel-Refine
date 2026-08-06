# Perbandingan `taichi_library_experimental_20260628_150822.zip` dengan `taichi_library`

Tanggal pemeriksaan: 2026-08-06

## Ringkasan inventaris

| Sumber | Isi utama |
|---|---:|
| ZIP eksperimental | 358 file: 100 `.py`, 212 `.pyc`, 20 `.tcm`, 9 `.dll`, dan file build/dokumentasi |
| Library aktif | 157 `.py`, 217 `.tcm`, 336 `.ll`, 82 `.tcb`, dan 43 manifest JSON |
| Graph terdaftar pada source ZIP | 163 graph unik |
| Graph terdaftar pada source aktif | 236 graph unik |
| Modul TCM unik pada ZIP | 20 modul gabungan |
| Modul TCM unik aktif | 43 modul algoritma |

Catatan: 212 `.pyc` di ZIP adalah artefak bytecode. Modul yang hanya muncul sebagai `.pyc` tidak dianggap sebagai source yang terverifikasi; daftar tersebut perlu direkonstruksi/dekompilasi sebelum dijadikan algoritma resmi.

## Perbedaan arsitektur

ZIP memakai TCM gabungan:

`alignment`, `arm`, `color`, `common`, `demosaic`, `demosaice`, `denoising`, `features`, `geometric`, `gradients`, `hamilton`, `hdr`, `image_processing`, `interpolation`, `math_ops`, `mlri_admm`, `optical_flow`, `pyramid`, `sfm`, `smoothing`.

Library aktif memecahnya menjadi modul per algoritma dan target backend:

`akaze`, `area`, `arm`, `bicubic`, `bilateral_grid`, `bilinear`, `bilinear_demosaice`, `block_matching`, `bm3d`, `box_filter`, `canny`, `clahe`, `color_convert`, `common`, `dcb`, `farneback_flow`, `fft`, `gaussian`, `gradients`, `guided_filter`, `hamilton`, `highlight_recovery`, `horn_schunck`, `hough`, `inpaint`, `jbf`, `lucas_kanade`, `lucas_kanade_bm`, `math_ops`, `median_filter`, `mlri_admm`, `mtb`, `ncc`, `nearest`, `nlm`, `ofb`, `otsu`, `phase_corr`, `pyramid`, `ransac`, `remap`, `seamless_clone`, `template_flow`.

Dengan demikian, perbandingan nama graph secara literal tidak cukup: misalnya `flow_farne_*` di ZIP telah menjadi `farneback_*` di library aktif, dan `geom_*` telah dipecah ke `remap`, `inpaint`, dan `seamless_clone`.

## Status per keluarga algoritma

| Keluarga | ZIP eksperimental | Library aktif | Status |
|---|---|---|---|
| Common/channel | copy, split, merge, gray, absdiff, normalize, fill, fused ops | `common` + block runtime | Ada, direfaktor/dipecah |
| Smoothing | Gaussian, box, median, bilateral grid, guided | modul yang sama + `jbf` | Ada; aktif lebih modular |
| Interpolation | bilinear, nearest, area | bilinear, nearest, area, bicubic | Ada; aktif menambah bicubic |
| Gradients | Sobel, magnitude, Laplacian | Sobel, vector Sobel, Laplacian | Ada |
| Pyramid/FFT | downsample, upsample flow, FFT | `pyramid` + `fft` | Ada, graph berganti nama |
| Alignment | MTB, NCC, phase normalization | `mtb`, `ncc`, `phase_corr`, `ransac` | Ada; aktif menambah/menjadikan RANSAC AOT |
| Demosaicing | Hamilton, ARM, MLRI, helper hybrid | Hamilton, ARM, MLRI, DCB, bilinear | Ada; aktif menambah DCB dan bilinear demosaicing |
| Denoising | NLM, BM3D | NLM, BM3D | Ada; graph BM3D lebih rinci |
| Feature matching | OFB; `akaze` hanya terindikasi pada API/bytecode | OFB + AKAZE TCM | Aktif lebih lengkap dan terkompilasi |
| Optical flow | Farneback, Horn-Schunck | Farneback, Horn-Schunck, Lucas-Kanade, block matching | Aktif lebih lengkap |
| Geometric/restoration | remap, inpaint, seamless clone | `remap`, `inpaint`, `seamless_clone`, warp perspective | Ada, dipecah |
| Image processing | Canny, CLAHE, Hough, Otsu, color | modul-modul yang sama | Ada, dipecah |
| HDR fusion/tone mapping | TCM `hdr` dan graph HDR lengkap | source JIT `hdr_fusion.py`/`tone_mapping.py`; tidak ada `hdr*.tcm` aktif dan tidak ada API AOT `hdr_fusion` | **Gap AOT** |
| SfM | TCM `sfm` dan graph 5-point, cheirality, matching, triangulation | source JIT SfM lengkap di `taichi_algorithm/sfm`; tidak ada `sfm*.tcm` aktif | **Gap AOT** |
| Math/NumPy-like ops | graph math dan bytecode `gpu_numpy` | `math_ops` source/TCM parsial | Perlu audit parity; `gpu_numpy` ZIP hanya bytecode |
| JPEG compression | tidak terlihat | source + compile script ada, tetapi tidak ada `compression*.tcm` aktif | **Source/compile-only** |
| Camera2 pipeline | source dan bytecode Camera2 | source Camera2 aktif | Ada; perlu audit modul bytecode lama |

## Registry graph lengkap dari source ZIP

Graph di bawah adalah 163 graph unik yang ditemukan melalui `module.add_graph(...)`, dikelompokkan berdasarkan keluarga.

### Common dan fused — 27

`cmn_absdiff_2d`, `cmn_absdiff_3ch`, `cmn_copy_2d`, `cmn_copy_3ch`, `cmn_fill_2d`, `cmn_fused_absdiff_clamp`, `cmn_fused_absdiff_normalize`, `cmn_fused_copy_clamp`, `cmn_fused_gray_normalize`, `cmn_fused_merge_normalize`, `cmn_gray`, `cmn_hanning`, `cmn_mean_div_2d`, `cmn_merge_3ch`, `cmn_normalize_2d`, `cmn_split_3ch`, `cmn_zero_2d`, `copy_f32_2d`, `copy_i32_2d`, `copy_vec3_2d`, `copy_vec3_i32_2d`, `fused_absdiff_clamp`, `fused_absdiff_normalize`, `fused_copy_clamp`, `fused_gray_absdiff_normalize`, `fused_gray_normalize`, `fused_merge_normalize`.

### Alignment — 8

`algn_mtb_bmp`, `algn_mtb_err`, `algn_mtb_hist`, `algn_ncc_icol`, `algn_ncc_irow`, `algn_ncc_rglob`, `algn_ncc_rrow`, `algn_phase_norm`.

### Demosaicing — 22

`arm_demosaic`, `arm_demosaic_1channel`, `arm_demosaic_half_res`, `arm_demosaic_rgb_half_res`, `arm_median`, `arm_preprocess_green`, `arm_reconstruct`, `arm_red_blue_residual`, `ha_green`, `ha_preprocess`, `ha_red_blue`, `hamilton_demosaic`, `hamilton_demosaic_1channel`, `hamilton_demosaic_3channel`, `hamilton_demosaic_half_res`, `hamilton_demosaic_rgb_half_res`, `mlri_cross`, `mlri_final`, `mlri_gbtf`, `mlri_preprocess`, `pure_arm_demosaic`, `rgb_to_bgr_i32`.

### Denoising — 8

`deno_bm3d_accum`, `deno_bm3d_collate`, `deno_bm3d_norm`, `deno_bm3d_scale`, `deno_bm3d_scatter`, `deno_bm3d_zero`, `deno_nlm_1ch`, `deno_nlm_3ch`.

### Features — 4

`feat_ofb_desc`, `feat_ofb_kp`, `feat_ofb_match`, `feat_ofb_score`.

### Optical flow — 9

`flow_farne_clear`, `flow_farne_gauss_x`, `flow_farne_gauss_y`, `flow_farne_poly_h`, `flow_farne_poly_v`, `flow_hs_clear`, `flow_hs_grad`, `flow_hs_jacobi`, `flow_hs_upsample`.

### Geometric — 7

`geom_inpaint_dist`, `geom_inpaint_lvl`, `geom_remap`, `geom_seamless_comp`, `geom_seamless_copy`, `geom_seamless_div`, `geom_seamless_jac`.

### Gradients — 4

`grad_laplacian`, `grad_sobel_h`, `grad_sobel_mag`, `grad_sobel_v`.

### HDR — 10

`hdr_add_3ch`, `hdr_down_3ch`, `hdr_norm_weights`, `hdr_sub_3ch`, `hdr_tone_contrast`, `hdr_tone_luma`, `hdr_tone_reinhard`, `hdr_tone_srgb`, `hdr_up_3ch`, `hdr_weight`.

### Image processing — 11

`imgp_canny_dthresh`, `imgp_canny_gauss`, `imgp_canny_hyst`, `imgp_canny_nms`, `imgp_canny_sobel`, `imgp_clahe_clip`, `imgp_clahe_hist`, `imgp_hough_peaks`, `imgp_hough_vote`, `imgp_otsu_hist`, `imgp_otsu_thresh`.

### Interpolation — 7

`intr_area_2d`, `intr_area_3ch`, `intr_bilinear_2d`, `intr_bilinear_3ch`, `intr_bilinear_vec3`, `intr_nearest_2d`, `intr_nearest_3ch`.

### Math — 12

`math_clip`, `math_mag`, `math_mat3_det`, `math_mat3_inv`, `math_matmul`, `math_meshgrid`, `math_pow`, `math_rmax`, `math_rmin`, `math_rsum`, `math_sort`, `math_where`.

### Pyramid/FFT — 11

`pyra_down_2x`, `pyra_down_2x_3ch`, `pyra_fft_bitrev`, `pyra_fft_c2r`, `pyra_fft_cmag`, `pyra_fft_cmul`, `pyra_fft_hanning`, `pyra_fft_norm`, `pyra_fft_r2c`, `pyra_fft_stage`, `pyra_upsample_flow`.

### SfM — 7

`sfm_5pt`, `sfm_cheir`, `sfm_knn_bf`, `sfm_knn_sel`, `sfm_l2dist`, `sfm_ratio`, `sfm_triang`.

### Smoothing — 16

`smth_bilateral_grid`, `smth_box_3x3`, `smth_box_sep_h`, `smth_box_sep_v`, `smth_gauss_h_1ch`, `smth_gauss_h_3ch`, `smth_gauss_h_vec3`, `smth_gauss_v_1ch`, `smth_gauss_v_3ch`, `smth_gauss_v_vec3`, `smth_guided_apply`, `smth_guided_cov`, `smth_guided_mean`, `smth_guided_mul`, `smth_median_1ch`, `smth_median_3ch`.

## Modul yang terindikasi hanya berada sebagai `.pyc` di ZIP

Ini bukan daftar yang aman untuk langsung dipakai karena source tidak ikut dikemas, tetapi layak diaudit jika ingin memulihkan fitur lama:

- `gpu_numpy`: zeros/ones/full/empty, reshape/stack/concatenate/transpose, reductions, elementwise math, dot/matmul/cross, sort/argsort/unique, meshgrid, histogram.
- `temporal_denoise`: temporal denoise sederhana dan ghost rejection.
- `sfm/kd_tree`: `kd_tree_nearest`, `radius_count`, `batch_neighbor_stats`.
- `optical_flow/template_flow`: helper Horn-Schunck/template-flow multi-level.
- `features/akaze`: helper Scharr, Hessian, FED diffusion, descriptor, dan Hamming matching.
- Camera2 bytecode tambahan: burst capture, frame source/manager, white balance, HDR bracket, metadata adapter, face detection, video stabilization, dan post-capture processor.

## Item yang perlu diputuskan

1. Jika targetnya AOT penuh, port/compile kembali HDR dan SfM ke kontrak TCM aktif.
2. `compile_compression_image_tcm.py` sudah ada, tetapi artefak `compression*.tcm` belum ada; tentukan apakah JPEG akan menjadi AOT resmi atau tetap source/JIT.
3. Audit `gpu_numpy`, `temporal_denoise`, `kd_tree`, dan template-flow dari bytecode sebelum dianggap sebagai fitur library.
4. Setelah inventaris stabil, jalankan API-parity dan numeric parity per keluarga; keberadaan graph saja belum membuktikan bentuk input/output dan hasilnya identik.

