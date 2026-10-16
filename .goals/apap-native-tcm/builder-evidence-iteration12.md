# APAP Builder Evidence — Iteration 12

Tanggal: 2026-10-16
Peran: Builder
Keputusan: kandidat low-rank tetap gagal gate distribusi; tidak dipromosikan.

## Source dan target

- Worktree HEAD sebelum commit: `26051e75c3f0b7c3fec808f2ccad21e13158fb55`.
- Source prototype menggunakan fixed 8×8 TPS/RBF residual (64 basis), membentuk design row untuk setiap korespondensi, dan tidak mengambil sampel atau memangkas baris.
- SHA-256 saat pengujian:
  - `taichi_vision/taichi_algorithm/alignment/apap.py`: `3F4D6BB387EBF5CC740AA3C874A4D1FFAAAB6E41F95D1828ABF23D6ECC4468DA`
  - `taichi_vision/taichi_algorithm/alignment/compile_mesh_warp_tcm.py`: `6CC16FF786E3C47F16CE3BDC88E1A6B848484C27E4F2C8BB7D60665BD9B11C85`
  - `taichi_vision/taichi_algorithm/alignment/test_alignment.py`: `3834E6B82E26F8EBB24878CEF18526779AC6465A097B5F9DECF8A9DE0BA3E2A1`
- Build dilakukan ke staging baru di `%TEMP%\apap_iter12_builder_cuda_mx150_20261016`; runtime TCM tidak ditimpa.
- Perintah build PowerShell:

  ```powershell
  $env:APAP_TCM_STAGING_ROOT = Join-Path $env:TEMP 'apap_iter12_builder_cuda_mx150_20261016'
  $env:PIXEL_REFINE_AOT_ARCH = 'cuda'
  .\venv\Scripts\python.exe taichi_vision\taichi_algorithm\alignment\compile_mesh_warp_tcm.py
  ```

- Hasil target-qualified: `cuda_x86_64_windows_nvidia`, Taichi 1.7.4, LLVM 20.1.5, Windows, Python 3.12.9. TCM berada di `%TEMP%\apap_iter12_builder_cuda_mx150_20261016\cuda_x86_64_windows_nvidia\apap_native_cuda_x86_64_windows_nvidia.tcm`, 132,751 byte, SHA-256 `CFA48531A045C64D9F55D8419FCB8A7346396478B3FC044A3A71D5BD1A334D70`.
- Manifest mencantumkan target CUDA/Windows/x86_64/NVIDIA dan graph `algn_apap_tps_lowrank_f32`, APAP fit/map, TPS pivoted/map, serta sparse mesh. Manifest hanya mencatat compiler `taichi-(1,7,4)`; identitas bridge/LLVM ABI tidak tercatat di manifest.
- `nvidia-smi -L` mengidentifikasi NVIDIA GeForce MX150 dengan VRAM 2048 MiB. Runtime `backend_info` mengonfirmasi CUDA device 0, vendor NVIDIA, target `cuda_x86_64_windows_nvidia`; dispatch AOT berhasil.

## Benchmark berpasangan N=841

Kedua proses memakai korespondensi, query, konfigurasi, dan inisialisasi Taichi CUDA API yang sama. Native mengangkut input ke float32; host API menerima source/target `(841,2)` float64 dan query `(1089,2)` float64. Kedua arm memetakan query dan menjalankan quality check; satu warm-up lalu lima pengukuran, pada proses terpisah.

Perintah:

```powershell
$env:PIXEL_REFINE_AOT_ARCH = 'cuda'
$env:PIXEL_REFINE_AOT_DEVICE = '0'
$env:PIXEL_REFINE_TARGET_VENDOR = 'NVIDIA'
$env:PIXEL_REFINE_AOT_TCM_ROOT = Join-Path $env:TEMP 'apap_iter12_builder_cuda_mx150_20261016'
$env:OPENBLAS_NUM_THREADS = '1'
$env:PYTHONPATH = (Get-Location).Path
.\venv\Scripts\python.exe (Join-Path $env:TEMP 'apap_iter12_builder_harness.py') --mode native --repeats 5
.\venv\Scripts\python.exe (Join-Path $env:TEMP 'apap_iter12_builder_harness.py') --mode numpy --repeats 5
```

- Native CUDA fit+map median: `74.9095 ms`; samples `78.6072, 70.1616, 74.9095, 75.1279, 69.6382 ms`.
- NumPy full TPS fit+map median: `704.3152 ms`; samples `704.3152, 701.1718, 714.1020, 708.1614, 594.4922 ms`.
- Observed speedup: `9.40x`.
- Peak process RSS: native `221.5273 MiB`; NumPy `245.7305 MiB` (native lower by `24.2032 MiB`).
- VRAM peak tidak tersedia: query `nvidia-smi --query-compute-apps=pid,used_memory` tidak mengembalikan baris proses pada driver WDDM. VRAM proses karena itu belum terukur.
- Pada fixture benchmark ini, native terhadap synthetic ground truth: max/mean `0.3731279 / 0.061732 px`; NumPy full TPS oracle: `0.0006710 / 0.0000511 px`. Native vs full TPS mapped output: `0.373737 / 0.061725 px`; native vs NumPy fixed-grid 8×8 reference: `0.339050 / 0.061007 px`.
- Kecepatan/RSS fixture tunggal memenuhi arah target; hasil tersebut tidak mengatasi kegagalan distribusi di bawah.

## Screening distribusi native: 42 fixture

Screening memakai count `8, 16, 32, 64, 122, 300, 841` dan enam kelas: `high_uniform`, `medium`, `low_clustered`, `anisotropic`, `edge`, `moving_patch`. Query mencakup 1089 titik. Quality gate per fixture: max error `<=1 px` dan mean error `<=0.15 px` terhadap synthetic ground truth. Instrumentasi upload mencatat jumlah dan urutan row; seluruh `42/42` kasus memakai semua korespondensi dalam urutan yang sama, memakai 64 basis, menghasilkan output finite, dan mengeksekusi graph native.

Perintah screening native dijalankan melalui harness sementara `%TEMP%\apap_iter12_builder_harness.py` dengan `--mode matrix`; environment CUDA/device/TCM sama seperti benchmark. Output rinci ada di `%TEMP%\apap_iter12_matrix_expanded.json`.

- Total lolos: `9/42`.
- `high_uniform`: lolos pada N=32, 64, 122, 300, 841; gagal N=8, 16. Pada N=841 max/mean `0.5110 / 0.0658 px`.
- `medium`: hanya lolos N=300; gagal N=8, 16, 32, 64, 122, 841. Pada N=841 `2.5037 / 0.2180 px`.
- `low_clustered`: gagal pada semua tujuh ukuran. Pada N=841 `21.5606 / 3.2123 px`.
- `anisotropic`: gagal pada semua tujuh ukuran. Pada N=841 `1.4014 / 0.4627 px`.
- `edge`: gagal pada semua tujuh ukuran. Pada N=841 `4.0823 / 1.0687 px`.
- `moving_patch`: lolos N=122, 300, 841; gagal N=8, 16, 32, 64. Pada N=841 `0.9192 / 0.1105 px`.

Perbandingan model double precision vs solver native membantu memisahkan dua sumber error. Pada N=841, NumPy reference model fixed-grid 8×8 sudah memberi max/mean: high-uniform `0.0638 / 0.00625`, medium `0.4907 / 0.0414`, clustered `2.7882 / 0.3128`, anisotropic `0.8105 / 0.3016`, edge `1.7328 / 0.3969`, moving-patch `0.5890 / 0.0798 px`. Jadi clustered dan edge sudah melampaui gate pada model double; untuk medium, anisotropic, dan edge, hasil native juga lebih buruk daripada fixed-grid reference, selaras dengan tambahan error dari normal-equation float32 solver. Perbandingan native terhadap fixed-grid reference pada N=841 secara langsung mencatat clustered max/mean `24.348 / 3.368 px` dan edge `2.891 / 0.889 px`.

## Screen desain alternatif, tetap memakai semua row

Semua probe di bawah bersifat screening NumPy double precision di CPU; bukan kandidat backend yang dikualifikasi. File skrip dan hasil berada di `%TEMP%`, tidak ditambahkan ke repo.

- TPS low-rank 64-center: variasi center seragam, axis-whitened, quantile, hybrid dan k-means hybrid; regularisasi `1e-4` sampai `1`. Screening deterministik 42 fixture memberi maksimum `14/42` lolos. Tidak ada konfigurasi global yang layak build ulang.
- Wendland C2 compact RBF dengan affine tail, semua observation rows, center seragam, radius `1–5x` dan axis-whitened. Konfigurasi global terbaik adalah uniform-coordinates radius `3x`: `21/42` lolos. Pass size per kelas: high-uniform N=32/64/122/300/841; medium semua tujuh ukuran; clustered tidak ada; anisotropic N=32/64/122/300/841; edge N=122; moving-patch N=122/300/841.
- Untuk N=841, hasil terbaik per kelas dari sweep radius compact adalah high-uniform `0.011 / 0.001 px` (factor 3), medium `0.089 / 0.019` (factor 3), clustered `1.855 / 0.332` (factor 5), anisotropic `0.203 / 0.056` (factor 5), edge `0.815 / 0.153` (factor 5), moving-patch `0.117 / 0.017` (factor 3). Clustered tetap gagal max dan mean; edge mean `0.153` sedikit melampaui gate.
- Wendland adaptif dengan quantile/hybrid centers dan affine tail, semua rows: terbaik global quantile radius `5x` median nearest-center spacing, lambda `1e-4`, lolos `11/42`. Best shared configuration per kelas: high-uniform `4/7`, medium `4/7`, clustered `0/7`, anisotropic `0/7`, edge `0/7`, moving-patch `3/7`. Pada N=841 konfigurasi shared terbaik per kelas menghasilkan: high `.032/.005`, medium `.067/.015`, clustered `741.77/2.082`, anisotropic `92359.10/175.55`, edge `201.09/.792`, moving `.157/.019 px`. Hybrid centers hanya lolos `1/42` pada radius factor 5.

Ringkasan screening lengkap (termasuk nilai per konfigurasi) tetap di file eksternal berikut:

- `%TEMP%\apap_iter12_design_screen.json`
- `%TEMP%\apap_iter12_compact_rbf_screen.json`
- `%TEMP%\apap_iter12_adaptive_compact_screen.json`
- `%TEMP%\apap_iter12_matrix_expanded.json`

Tidak ada kandidat yang mendukung rebuild secara bertanggung jawab. TCM kandidat tidak dipindahkan atau dipromosikan; TCM runtime kanonis dan `taichi_vision/taichi_aot/engine.py` tidak diubah.

## Tes dan batas bukti

Perintah focused pytest memakai venv dan root TCM staging CUDA yang sama:

```powershell
$env:PIXEL_REFINE_AOT_ARCH = 'cuda'
$env:PIXEL_REFINE_AOT_DEVICE = '0'
$env:PIXEL_REFINE_TARGET_VENDOR = 'NVIDIA'
$env:PIXEL_REFINE_AOT_TCM_ROOT = Join-Path $env:TEMP 'apap_iter12_builder_cuda_mx150_20261016'
$env:OPENBLAS_NUM_THREADS = '1'
.\venv\Scripts\python.exe -m pytest `
  taichi_vision\taichi_algorithm\alignment\test_alignment.py::TestAlignment::test_apap `
  taichi_vision\taichi_algorithm\alignment\test_alignment.py::TestAlignment::test_apap_reference_keeps_all_correspondences_across_adversarial_layouts `
  taichi_vision\taichi_algorithm\alignment\test_alignment.py::TestAlignment::test_apap_rejects_nonfinite_rows_instead_of_silently_dropping_them `
  taichi_vision\taichi_algorithm\alignment\test_alignment.py::TestAlignment::test_apap_fixed_grid_residual_uses_all_122_rows_across_layouts -q
```

Hasil: `4 passed`, 1 Taichi deprecation warning, 8 subtests, 4.44 s. Bukti ini hanya focused APAP pytest, eksekusi native CUDA, dan fixture sintetis; tidak membuktikan aplikasi penuh, data DNG nyata, backend lain, VRAM puncak, bridge ABI lengkap, atau kesiapan produksi. Gate distribusi gagal (`9/42`), sehingga hasil ini adalah PARTIAL/FAIL untuk promosi.
