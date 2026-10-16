# APAP Builder evidence — iteration 14

**Keputusan: PARTIAL / FAIL gate.** Eksperimen referensi CPU adaptive local-support / partition-of-unity selesai pada seluruh 420 fixture. Hanya 84/420 fixture lolos, seluruhnya kasus homography. Tidak ada perubahan source, test, compiler, TCM, runtime, UI, routing, atau `engine.py`; tidak ada build native atau benchmark CUDA karena gate referensi gagal.

## Cakupan dan model yang diuji

- Matriks tetap: 7 count (`8, 16, 32, 64, 122, 300, 841`) × 12 layout × 5 motion (`homography`, `smooth_parallax`, `moving_patch`, `foreground_background`, `near_boundary`) = 420 fixture. Layout mencakup `grid_jitter`, `high_uniform`, `medium`, `clustered_center`, `double_cluster`, `corner_clustered`, anisotropic horizontal/vertical, edge/corner heavy, moving-region cluster, dan portrait uniform.
- Tiap fixture memakai korespondensi source/target berukuran `N×2`, float64, dan query tetap berukuran `33×25×2` (825 titik) pada frame 1280×960 atau portrait 720×1280. Error dan finite-difference Jacobian diukur pada grid query yang sama dengan ground truth.
- Baseline: normalized DLT homography dihitung dari seluruh korespondensi. Residual `target − H(source)` dipelajari dengan satu polinomial kuadratik 6-term di setiap korespondensi sebagai pusat lokal. Support adaptif adalah `max(1.5 × jarak ke tetangga ke-8, 1e-6)` pada koordinat ternormalisasi; saat `N<9`, tetangga terjauh yang tersedia dipakai. Tiap patch memakai weighted least squares atas seluruh N rows dengan bobot Gaussian positif, SVD batched dan relative cutoff `1e-11`, tanpa ridge. Prediksi patch digabung dengan POU Gaussian berlebar `2× support`; query dievaluasi dalam chunk 64.
- Tidak ada correspondence yang dibuang, disampling, difilter, atau diurutkan ulang; setiap row juga menjadi pusat satu patch. Bobot training positif untuk seluruh `N²` pasangan row/patch. Tidak ada homography fallback untuk residual yang tak teridentifikasi dan tidak ada prior deformasi tambahan.
- Limitasi identifiability: patch lokal dapat rank-deficient saat distribusi titik tidak mengamati seluruh basis kuadratik. SVD memotong nilai singular di bawah cutoff dan menghasilkan solusi minimum-norm pada ruang null; itu konvensi numerik, bukan informasi geometri atau prior yang menjamin medan di luar support. Terdapat 855 patch rank-deficient dari total 420 fixture, hingga 110 dalam satu fixture, rank minimum 1. Bandwidth minimum terjepit di `1e-6` pada kasus degenerasi lokal.

## Assertion dan hasil gate

- **Count/order**: 420/420 benar. `rows_received == rows_used == centers == N`, ID pusat tetap urutan input, ID query tetap urutan input, input tidak dimutasi, dan jumlah entri bobot training positif sama dengan `N²`.
- **Eksekusi numerik**: output finite 420/420; tidak ada exception/harness error. Semua 420 fixture memiliki minimum determinant ground-truth positif pada grid evaluasi; nilai minimum `0.954351`.
- **Jacobian kandidat**: hanya 412/420 positif. 8 fixture menghasilkan foldover dan assertion kandidat gagal; minimum determinant kandidat `-5.422692`.
- **Akurasi** (gate PRD per fixture: maksimum ≤1,0 px dan rata-rata ≤0,15 px): 84/420 lolos; seluruhnya homography. Maksimum error global `3129.646287 px`, mean dari 420 mean-fixture `11.636392 px`, mean terburuk `1062.783573 px`. Dengan demikian seluruh 336 fixture non-homography gagal gate akurasi.
- **Tidak ada build/perf evidence**: referensi gagal sebelum build; tidak ada TCM baru, eksekusi native, perbandingan CUDA MX150, latency paired, RSS process, atau VRAM yang diukur. Tidak ada klaim parity/performa native.

## Hasil menurut motion

Format: `lolos/total; max error terburuk; rata-rata mean-fixture; mean-fixture terburuk; foldover`.

- `homography`: 84/84; `2.79e-10 px`; `3.21e-12 px`; `2.79e-10 px`; 0. Semua count/layout lolos.
- `smooth_parallax`: 0/84; `2130.670 px`; `20.160 px`; `721.761 px`; 3 foldover.
- `moving_patch`: 0/84; `3129.646 px`; `24.218 px`; `1062.784 px`; 2 foldover.
- `foreground_background`: 0/84; `1478.034 px`; `13.081 px`; `499.288 px`; 3 foldover.
- `near_boundary`: 0/84; `39.944 px`; `0.723 px`; `6.296 px`; 0. Mean agregatnya lebih rendah, tetapi maksimum per fixture tetap melewati 1 px.

## Hasil menurut count

Format: `lolos/60; maksimum error; mean-fixture terburuk; foldover`.

- N=8: `12/60`; `3129.646 px`; `1062.784 px`; 3.
- N=16: `12/60`; `2130.670 px`; `721.761 px`; 5.
- N=32: `12/60`; `257.455 px`; `70.127 px`; 0.
- N=64: `12/60`; `124.029 px`; `33.688 px`; 0.
- N=122: `12/60`; `46.646 px`; `10.725 px`; 0.
- N=300: `12/60`; `41.477 px`; `8.792 px`; 0.
- N=841: `12/60`; `54.079 px`; `9.093 px`; 0.

## Hasil layout dan interaksi motion × layout

Setiap layout berisi 35 fixture. Masing-masing meloloskan 7/35 (tujuh kasus homography); tidak ada layout yang meloloskan kasus non-homography. Di bawah, tiap entri adalah `lolos/7, maksimum error px, jumlah foldover` untuk motion tersebut.

- `homography`: `grid_jitter 7/7, 0.000, 0`; `high_uniform 7/7, 0.000, 0`; `medium 7/7, 0.000, 0`; `clustered_center 7/7, 0.000, 0`; `double_cluster 7/7, 0.000, 0`; `corner_clustered 7/7, 0.000, 0`; `anisotropic_horizontal 7/7, 0.000, 0`; `anisotropic_vertical 7/7, 0.000, 0`; `edge_heavy 7/7, 0.000, 0`; `corner_heavy 7/7, 0.000, 0`; `moving_region_cluster 7/7, 0.000, 0`; `portrait_uniform 7/7, 0.000, 0`.
- `smooth_parallax`: `grid_jitter 0/7, 11.238, 0`; `high_uniform 0/7, 12.843, 0`; `medium 0/7, 18.016, 0`; `clustered_center 0/7, 28.450, 0`; `double_cluster 0/7, 23.689, 0`; `corner_clustered 0/7, 4.671, 0`; `anisotropic_horizontal 0/7, 1537.114, 2`; `anisotropic_vertical 0/7, 2130.670, 1`; `edge_heavy 0/7, 34.638, 0`; `corner_heavy 0/7, 8.445, 0`; `moving_region_cluster 0/7, 47.894, 0`; `portrait_uniform 0/7, 11.510, 0`.
- `moving_patch`: `grid_jitter 0/7, 13.541, 0`; `high_uniform 0/7, 19.295, 0`; `medium 0/7, 38.661, 0`; `clustered_center 0/7, 47.417, 0`; `double_cluster 0/7, 59.215, 0`; `corner_clustered 0/7, 8.056, 0`; `anisotropic_horizontal 0/7, 3129.646, 1`; `anisotropic_vertical 0/7, 1068.675, 1`; `edge_heavy 0/7, 173.407, 0`; `corner_heavy 0/7, 8.072, 0`; `moving_region_cluster 0/7, 256.549, 0`; `portrait_uniform 0/7, 20.890, 0`.
- `foreground_background`: `grid_jitter 0/7, 5.851, 0`; `high_uniform 0/7, 24.552, 0`; `medium 0/7, 23.161, 0`; `clustered_center 0/7, 101.591, 0`; `double_cluster 0/7, 11.675, 0`; `corner_clustered 0/7, 3.796, 0`; `anisotropic_horizontal 0/7, 1478.034, 2`; `anisotropic_vertical 0/7, 657.233, 1`; `edge_heavy 0/7, 5.457, 0`; `corner_heavy 0/7, 4.171, 0`; `moving_region_cluster 0/7, 16.033, 0`; `portrait_uniform 0/7, 25.270, 0`.
- `near_boundary`: `grid_jitter 0/7, 5.538, 0`; `high_uniform 0/7, 6.895, 0`; `medium 0/7, 6.939, 0`; `clustered_center 0/7, 6.938, 0`; `double_cluster 0/7, 8.760, 0`; `corner_clustered 0/7, 39.944, 0`; `anisotropic_horizontal 0/7, 7.059, 0`; `anisotropic_vertical 0/7, 6.939, 0`; `edge_heavy 0/7, 6.939, 0`; `corner_heavy 0/7, 23.737, 0`; `moving_region_cluster 0/7, 6.904, 0`; `portrait_uniform 0/7, 6.937, 0`.

## Reproduksibilitas dan provenance

- Environment: venv proyek, Python 3.12.9, NumPy 2.5.2, SciPy tersedia; CPU `Intel(R) Core(TM) i7-8565U CPU @ 1.80GHz`, Windows x86_64. Backend CPU reference; dtype float64; correspondence `N×2`, output/query `825×2`, grid Jacobian `25×33`. Durasi screening yang tercatat 92.953 s. Ini bukan benchmark native.
- Command yang dijalankan dari root repo (PowerShell):
  ```powershell
  & .\venv\Scripts\python.exe -m py_compile "$env:TEMP\apap_iter14_pou_screen.py"
  & .\venv\Scripts\python.exe "$env:TEMP\apap_iter14_pou_screen.py"
  ```
- JSON hasil: `%TEMP%\apap_iter14_pou_local_quadratic_420.json`.
- SHA-256 harness i14: `2C620F97725C3005EB8319811DEE6FCBD9776F186CE5769F4F2AD01995D1F174`.
- SHA-256 JSON i14: `1E77C56EBBA795420D224C8D7A2D144D96B0DFC12D217E5B2686489A36DBC15C`.
- Generator fixture i13 yang dipakai harness: `%TEMP%\apap_iter13_sparse_rbf_screen.py`, SHA-256 `0443FED1BF1CD0EE83EDEF0FC9492726897C6EB442146C2E6F23D2CF8524B1D1`.
- Source baseline pada HEAD `b2f44d34151f76c919cabbe74190a8d39cc18fd2`: `apap.py` SHA-256 `3F4D6BB387EBF5CC740AA3C874A4D1FFAAAB6E41F95D1828ABF23D6ECC4468DA`; `compile_mesh_warp_tcm.py` `6CC16FF786E3C47F16CE3BDC88E1A6B848484C27E4F2C8BB7D60665BD9B11C85`; `test_alignment.py` `3834E6B82E26F8EBB24878CEF18526779AC6465A097B5F9DECF8A9DE0BA3E2A1`.
- Tidak ada file harness atau JSON hasil yang disalin ke repo. Tidak ada tes produksi yang dijalankan atau perubahan produk dibuat; `py_compile` hanya memeriksa sintaks harness.

## Tindak lanjut

Eksperimen POU kuadratik ini tidak layak dikompilasi ke native karena representasi gagal di seluruh empat kelas motion non-homography, disertai foldover terutama pada layout anisotropik. Langkah teknis berikutnya memerlukan keputusan model/kontrak untuk wilayah yang tidak teramati oleh correspondence (misalnya moving patch tanpa dukungan lokal memadai); menambah prior deformasi sembarang akan mengubah asumsi ground truth, jadi tidak dilakukan dalam iterasi ini. Tidak ada klaim iterasi selesai atau promosi runtime.
