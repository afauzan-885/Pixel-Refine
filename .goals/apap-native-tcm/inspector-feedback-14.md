# Inspector Iteration 14 — FAIL

## Cakupan review

Meninjau commit Builder final 8adb987ca5f8aa5d12ce92a626e7b6aa3928b8f4 dan evidence iteration 14. Commit menambah satu file evidence saja; source/compiler/test/TMC/APAP runtime tidak berubah di commit. Hash source aktif cocok dengan baseline evidence: apap.py 3F4D6BB387EBF5CC740AA3C874A4D1FFAAAB6E41F95D1828ABF23D6ECC4468DA, compiler 6CC16FF786E3C47F16CE3BDC88E1A6B848484C27E4F2C8BB7D60665BD9B11C85, test_alignment.py 3834E6B82E26F8EBB24878CEF18526779AC6465A097B5F9DECF8A9DE0BA3E2A1. Diff commit terhadap parent tidak menyentuh alignment source atau direktori TCM.

## Verifikasi matrix dan threshold

- JSON tersimpan di %TEMP%apap_iter14_pou_local_quadratic_420.json berisi 420 row unik, persis Cartesian 7 count × 12 layout × 5 motion. Saya hitung ulang threshold per fixture: output finite, max error ≤1 px, mean error ≤0.15 px, dan Jacobian output positif untuk GT yang fold-free. Hitungan tersimpan dan hitungan ulang sama-sama 84/420.
- Semua 84 fixture homography lulus. Keempat motion non-homography masing-masing 0/84. Per count setiap N lulus 12/60 (semua homography).
- Error maksimum 3129.646287 px, mean dari mean-fixture 11.636392 px, mean-fixture terburuk 1062.783573 px. GT Jacobian positif 420/420, minimum 0.954351146.

## All-row, order, dan Jacobian kandidat

- Harness membentuk baseline DLT dari seluruh source/target, residual dari semua pasangan, satu local patch per correspondence, dan matriks training N×N. Ia tidak memfilter, menyampel, atau menyortir rows. JSON mengonfirmasi rows_received = rows_used = centers = N, center order dan query order bertanda benar, serta N² training weights positif pada 420/420 fixture. Salinan source/target sebelum/sesudah fit sama.
- Count/order assertions lolos seluruh matrix. ID center/query dibuat sebagai arange di harness; klaim order juga didukung struktur source yang menyalin centers langsung dari source dan memetakan query per slice dalam urutan yang sama. Assertion query tidak membandingkan q_before, sehingga bagian query-order sendiri adalah pemeriksaan struktur/source, bukan uji perturbasi independen.
- Jacobian kandidat diukur terpisah dari GT dengan finite differences. Kandidat positif 412/420; delapan fixture anisotropik N=8/16 menghasilkan assertion foldover, minimum det kandidat -5.422691999. Delapan assertion failure pada JSON hanya berasal dari pemeriksaan Jacobian kandidat. Ada 855 patch rank-deficient di seluruh matrix, hingga 110 dalam satu fixture, dengan rank lokal minimum 1; truncated SVD memilih solusi minimum-norm tetapi tidak menambah informasi untuk support yang tidak teramati.

## Scope dan keterbatasan bukti

Iterasi ini hanya CPU reference float64: Python 3.12.9/NumPy 2.5.2/SciPy, input N×2 dan query/output 825×2, CPU i7-8565U, durasi 92.953 s. Tidak ada TCM build, CUDA/MX150 execution, paired native performance, RSS/VRAM, atau runtime promotion. Saya memverifikasi source/evidence dan menghitung ulang JSON tersimpan; tidak menjalankan pytest atau compile.

## Verdict dan steering berikutnya

**FAIL.** Walaupun seluruh baris korespondensi dipertahankan dan count/order matrix terverifikasi, hanya 84/420 memenuhi accuracy gate dan delapan fixture foldover. Kandidat POU kuadratik tidak memenuhi gate untuk motion lokal.

Iteration 15 ditetapkan sebagai eksperimen CPU reference-only yang diarahkan ke global coarse homography lalu local residual deformation (global-to-local APAP variant). Pertahankan semua correspondence rows, compose coordinate maps dan lakukan satu final image resampling, serta keluarkan diagnostic error eksplisit saat local support tidak memadai. Max/mean gate tetap. Tidak ada perubahan PRD diam-diam dan tidak ada perubahan product/native build sebelum reference gate lulus.

## Git hygiene

Saat review dimulai, real index memuat empat staged path pengguna: pixel_refine_desktop/enhance_stack/core/algorithm/denoising/patch_process/__init__.py, pixel_refine_desktop/enhance_stack/core/algorithm/denoising/patch_process/multi_patch.py, pixel_refine_desktop/tests/test_fusionnet_multi_patch.py, dan taichi_vision/taichi_algorithm/denoising/nlm.py. Commit Inspector hanya mencakup feedback ini dan status.json, menggunakan temporary Git index; daftar serta blob staged user diperiksa kembali sesudah commit.