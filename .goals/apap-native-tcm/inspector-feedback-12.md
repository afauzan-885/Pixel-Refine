# Inspector Iteration 12 — FAIL

## Cakupan review

Meninjau Builder commit `7ba4539251dcad2382731fe2c5c9e5b9d46b3e5a` terhadap `.goals/apap-native-tcm/prd-robust-apap-iteration10.md`, source dan tes APAP, arsip TCM staging, manifest/payload hashes, matriks CUDA, dan benchmark. Tidak mengubah source, `engine.py`, atau TCM. Worktree saat review berisi banyak perubahan staged/unstaged pengguna; hanya feedback dan status goal yang menjadi scope commit Inspector.

## Temuan terverifikasi

- Commit Builder mengubah `apap.py`, `compile_mesh_warp_tcm.py`, `test_alignment.py`, dan menambah evidence iteration 12. Tidak ada TCM dalam commit tersebut. SHA-256 source saat ini cocok dengan evidence Builder: `apap.py` `3F4D6BB387EBF5CC740AA3C874A4D1FFAAAB6E41F95D1828ABF23D6ECC4468DA`, compiler `6CC16FF786E3C47F16CE3BDC88E1A6B848484C27E4F2C8BB7D60665BD9B11C85`, tes `3834E6B82E26F8EBB24878CEF18526779AC6465A097B5F9DECF8A9DE0BA3E2A1`.
- Implementasi native membentuk satu design row untuk setiap baris `source`, membentuk normal equation dengan loop hingga `source.shape[0]`, dan tidak menerapkan sampler/cap. Harness matriks yang tersimpan menangkap upload source/target: `native_input_count == input_count`, urutan cocok, dan hasil finite pada 42/42 pemanggilan. `filter_apap_correspondences` tidak dipanggil oleh production APAP/resident path saat ini; pemakaian yang ditemukan di test adalah pengujian helper eksplisit.
- Screening CUDA Builder terdiri dari 42 kasus: ukuran 8, 16, 32, 64, 122, 300, 841 pada enam layout (`high_uniform`, `medium`, `low_clustered`, `anisotropic`, `edge`, `moving_patch`). Query tiap kasus 1089 titik. Harness menyimpan backend `cuda`, device id 0, vendor NVIDIA, target `cuda_x86_64_windows_nvidia`; `nvidia-smi -L` yang dijalankan Inspector mengidentifikasi GPU 0 sebagai NVIDIA GeForce MX150.
- Gate error PRD adalah maksimum `<=1.0 px` dan rata-rata `<=0.15 px`. Matriks tersimpan hanya meloloskan **9/42**:
  - `high_uniform`: 5/7 (N=32, 64, 122, 300, 841); N=841 max/mean `0.5110 / 0.0658 px`.
  - `medium`: 1/7 (N=300); N=841 `2.5037 / 0.2180 px`.
  - `low_clustered`: 0/7; N=841 `21.5606 / 3.2123 px`.
  - `anisotropic`: 0/7; N=841 `1.4014 / 0.4627 px`.
  - `edge`: 0/7; N=841 `4.0823 / 1.0687 px`.
  - `moving_patch`: 3/7 (N=122, 300, 841); N=841 `0.9192 / 0.1105 px`.
- Coverage matriks belum memenuhi seluruh PRD. `high_uniform` hanya random uniform; tidak ada fixture grid/jitter terpisah. `anisotropic` hanya satu orientasi tipis; tidak ada pasangan tinggi-tipis, rentang/aspect-ratio alternatif, atau corner-heavy terpisah. Semua layout memakai transform analitis yang sama berupa affine ringan ditambah satu Gaussian bump, sehingga homography global, parallax/foreground-background gabungan, dan displacement dekat batas belum diuji terpisah. Matriks native juga tidak memuat kasus duplikat, kolinear, kurang titik minimum, atau rentang efektif nol.
- Bukti native dan reference dibedakan. Matriks native mengukur terhadap ground truth analitis. Test baru `test_apap_fixed_grid_residual_uses_all_122_rows_across_layouts` menjalankan oracle NumPy double-precision `fit_apap_tps_grid_reference` pada empat layout N=122; ia tidak mengeksekusi kernel native. Screening double-precision fixed-grid N=841 yang dicatat Builder juga menunjukkan model 64 basis itu sendiri melewati gate pada clustered (`2.7882 / 0.3128 px`) dan edge (`1.7328 / 0.3969 px`), sebelum tambahan error solver float32. Hasil native-vs-reference yang dicatat Builder pada benchmark fixture adalah max/mean `0.339050 / 0.061007 px` terhadap oracle fixed-grid dan `0.373737 / 0.061725 px` terhadap full-TPS NumPy.
- **Benchmark berpasangan yang dilaporkan Builder** memakai CUDA MX150, N=841, source/target `(841,2)` dan query `(1089,2)`, API `float64`, transport native `float32`; satu warm-up dan lima pengulangan per subprocess. Perintah kedua arm tercatat pada `builder-evidence-iteration12.md` dan harness sementara masih tersedia di `%TEMP%\apap_iter12_builder_harness.py`. Native median `74.9095 ms`, peak process RSS `221.5273 MiB`; NumPy median `704.3152 ms`, RSS `245.7305 MiB`. VRAM tidak terukur pada WDDM. Harness native memakai RBF fixed 8x8/64 basis, sedangkan baseline `fit_tps_checked` memakai full TPS/841 kontrol. Karena semantik model residualnya berbeda, pasangan ini **tidak memenuhi** acceptance benchmark PRD yang meminta semantik residual sama. Benchmark hanya satu fixture sebaran tinggi; tidak ada pasangan waktu/RSS low dan medium.
- **Arsip TCM staging** `%TEMP%\apap_iter12_builder_cuda_mx150_20261016\cuda_x86_64_windows_nvidia\apap_native_cuda_x86_64_windows_nvidia.tcm` berukuran 132,751 byte. SHA-256 terhitung `CFA48531A045C64D9F55D8419FCB8A7346396478B3FC044A3A71D5BD1A334D70`, cocok dengan evidence Builder. Manifest embedded menyatakan CUDA/Windows/x86_64/NVIDIA, `minimum_runtime_abi: 1`, dan graph APAP/TPS termasuk `algn_apap_tps_lowrank_f32`; 13 payload LLVM IR cocok dengan ukuran dan SHA-256 manifest. Manifest hanya mencatat `compiler_version: taichi-(1, 7, 4)` dan tidak mengikat LLVM build, bridge/C API binary, atau hash runtime core, sehingga provenance ABI target yang lengkap belum dibuktikan.
- **Staging vs runtime kanonis:** kandidat berada di `%TEMP%`; commit Builder tidak menambah/mengganti TCM kanonis. Arsip kanonis CUDA saat ini masing-masing berukuran 71,752 byte, hash `1CA3BC9506E0D2B31B5494974E5C4640899E0CA983BACF327E9A3137151A8DC8`, metadata compiler `taichi-1.7.4.dev3-llvm20.1.5-consistent-43ed4e86be79`, dan manifest `kernels` kosong; graph low-rank kandidat tidak dipromosikan ke runtime.
- Inspector mengulang tes bounded menggunakan venv, device CUDA 0 dan TCM staging kandidat:

  ```powershell
  $env:PIXEL_REFINE_AOT_ARCH='cuda'
  $env:PIXEL_REFINE_AOT_DEVICE='0'
  $env:PIXEL_REFINE_TARGET_VENDOR='NVIDIA'
  $env:PIXEL_REFINE_AOT_TCM_ROOT=Join-Path $env:TEMP 'apap_iter12_builder_cuda_mx150_20261016'
  $env:OPENBLAS_NUM_THREADS='1'
  $env:PYTHONPATH=(Get-Location).Path
  .\venv\Scripts\python.exe -m pytest `
    taichi_vision\taichi_algorithm\alignment\test_alignment.py::TestAlignment::test_apap `
    taichi_vision\taichi_algorithm\alignment\test_alignment.py::TestAlignment::test_apap_reference_keeps_all_correspondences_across_adversarial_layouts `
    taichi_vision\taichi_algorithm\alignment\test_alignment.py::TestAlignment::test_apap_rejects_nonfinite_rows_instead_of_silently_dropping_them `
    taichi_vision\taichi_algorithm\alignment\test_alignment.py::TestAlignment::test_apap_fixed_grid_residual_uses_all_122_rows_across_layouts -q
  ```

  Hasil: `4 passed`, `8 subtests passed`, satu warning deprecation Taichi, `6.49 s`. `test_apap` menjalankan fit APAP native pada 16 korespondensi `float64` API di staging CUDA; tes lain menguji oracle reference, preservasi input, validasi non-finite, dan oracle fixed-grid. Hasil focused ini bukan bukti bahwa matriks kualitas native lulus.

## Gap penerimaan

- Robustness native gagal pada 33/42 kasus, termasuk seluruh ukuran low-clustered, anisotropic, dan edge. Model fixed-grid double-precision juga sudah gagal pada sebagian sebaran; perubahan presisi solver saja tidak dapat memenuhi kriteria tersebut.
- Benchmark speed/RSS belum membuktikan perbandingan semantik-setara dan belum mencakup pasangan low/medium/high. VRAM tidak tersedia.
- ABI/bridge provenance lengkap, backend CPU/Vulkan/OpenGL, degenerasi native, real DNG, headless full-app/integration smoke, serta aplikasi yang menggunakan TCM kanonis belum terverifikasi pada iteration 12.
- Kandidat tidak dipromosikan; tidak ada klaim readiness atau parity lintas backend.

## Verdict

**FAIL.** Semua baris korespondensi dipertahankan dan kandidat berhasil dieksekusi pada staging CUDA MX150, tetapi gate robust error hanya lolos 9/42. Benchmark yang tersedia tidak memakai semantik residual yang sama, coverage PRD belum lengkap, dan provenance ABI/runtime aplikasi belum memenuhi gate. Pertahankan TCM di staging; iteration berikutnya perlu mengganti pendekatan residual/model untuk sebaran clustered, anisotropic, dan edge sebelum mengulang kualifikasi.
