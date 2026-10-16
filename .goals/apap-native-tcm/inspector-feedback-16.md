# Inspector Iteration 16 — FAIL

## Cakupan dan provenance

Saya memeriksa `.goals/apap-native-tcm/builder-evidence-iteration16.md`, harness, serta JSON tersimpan tanpa menjalankan ulang screen atau pytest. HEAD saat review `1f8ec65711b27216a75ea6aaf55fbbbf912e3398` adalah commit Inspector i15; evidence Builder i16 masih untracked, tanpa commit i16. SHA-256 evidence `4B86C6A76049612CA53772018D4B72264A6B13195126DC39AE4989FBA2BFB275`; harness `FBF96AE3641142B665A962679BE3C5A129064206BED6BFEB171FDDC391F41836`; full JSON `1225D2EA06A3CF2DF7C39831A09CEE5B19B47C7C58A959167DCD0BF91A3CD932`; Jacobian JSON `0B7CFDFEB49C9534731C0ED5D7FFB34D4511524278D1462EDD5DCEE94446973B`. Hash `apap.py` aktif cocok dengan laporan (`3F4D6BB387EBF5CC740AA3C874A4D1FFAAAB6E41F95D1828ABF23D6ECC4468DA`). Eksperimen mengimpor generator fixture dari `%TEMP%`, bukan API produksi; `quality.py` yang sedang dirty tidak dipakai harness ini. Tidak ada perubahan source, test, compiler, TCM, runtime, UI, engine, atau PRD oleh i16.

## Hitung ulang gate dan foldover

- Full JSON berisi 2.520 row unik, yaitu 420 fixture × 6 kombinasi `(σ/D, γ)`. Jacobian GT terpisah berisi 420/420 fixture fold-free dengan determinant minimum `0,954351146`. Saya hitung ulang status lulus langsung dari error max/mean, finite output, dan Jacobian kandidat; semua hasil cocok dengan kolom `pass` JSON.
- Untuk konfigurasi terbaik tetap `(σ/D=0,05, γ=0,005)`, gate lulus `96/420`: 84 homography dan 12 motion non-homography. Jadi `324/336` kasus non-homography masih gagal; error maksimum `76,145 px`, mean dari mean-fixture `1,48352 px`, mean fixture terburuk `20,84293 px`.
- Jumlah lulus konfigurasi lain juga cocok: `93/420` pada `(0,05; 0,01)`, lalu `84/420` pada masing-masing `(0,15; 0,005)`, `(0,15; 0,01)`, `(0,35; 0,005)`, dan `(0,35; 0,01)`. Semua 84 homography lulus di setiap konfigurasi. Kasus tambahan di konfigurasi terbaik hanya berada pada grid-jitter, high-uniform, atau portrait-uniform; clustered, anisotropic, edge-heavy, dan corner-heavy hanya meluluskan homography.
- Saya hitung ulang empat kandidat Jacobian foldover: `(0,15; 0,005)` anisotropic-horizontal N=8 smooth-parallax `−0,044330`, N=8 moving-patch `−0,529069`, N=16 moving-patch `−0,053710`; `(0,15; 0,01)` anisotropic-horizontal N=8 moving-patch `−0,083818`. Ground truth Jacobian terpisah positif pada 420/420.
- Semua 2.520 row mencatat `rows_received=N`, `rows_used_per_query=N`, `2N` baris DLT, urutan correspondence/query, dan output/Jacobian finite; tidak ada exception. Harness memverifikasi bahwa source tidak dimutasi. Jacobian kandidat dihitung dengan finite difference pada grid 33×25 (825 query) termasuk batas frame, jadi bukti positivity adalah hasil sampling pada grid tersebut.

## Formula dan tingkat bukti

Varian ini adalah direct per-query Moving DLT dengan bobot `w=max(exp(-||x*−x_i||²/σ²), γ)`, kedua baris correspondence dikali `w`, dan SVD langsung atas `WA`; secara aljabar objective memakai `w²`. Seluruh N row masuk ke fit final untuk setiap query. Tidak ada grid-node interpolation, TPS, homography fallback, atau global-to-local prior. Formula serta hitungannya konsisten dengan paper yang sedang diuji.

Hasil hanya CPU NumPy/LAPACK float64 pada Intel i7-8565U; frame `1280×960` atau portrait `720×1280`, tiap fixture `N×2` dengan 825 query. Full screen memerlukan 493,96 s dan sampled process RSS `100.835.328 B`; itu bukan paired latency/RAM benchmark. Tidak ada CUDA/TCM, aplikasi, pytest, atau uji native. `py_compile` di laporan hanya memeriksa harness. Accuracy gate gagal jauh, jadi tidak ada dasar untuk build native/promosi.

## Verdict dan arah i17

**FAIL.** Direct canonical Moving DLT mempertahankan semua rows dan lolos pada 12 kasus non-homography, tetapi tetap gagal 324 dari 336 kasus non-homography pada konfigurasi terbaik, dengan error hingga 76,145 px dan empat foldover pada konfigurasi lain. Satu eksperimen CPU reference-only berbasis spatial cross-validation masih layak sebagai uji adaptasi parameter; i16 hanya membandingkan enam konfigurasi tetap global.

Untuk i17, pinjam mekanisme pemilihan parameter EadCat saja: spatially blocked folds, skor reprojection held-out, dan pemilihan kandidat yang lebih halus dalam toleransi terhadap skor terbaik. Source yang diperiksa membagi source matches ke empat spatial folds, menghitung held-out SSE, lalu memilih pasangan `(sigma, gamma)` terhalus dalam toleransi 1%; lihat [`stitching/apap.py`](https://raw.githubusercontent.com/EadCat/APAP-Image-Stitching/main/stitching/apap.py). Jangan menyalin formula/kernel atau sigma numerik EadCat: source tersebut memakai `exp(-r/sigma²)`, sementara i16 menguji formula paper `exp(-r²/sigma²)`. Tetapkan candidate grid dan satuan sigma secara eksplisit untuk formula canonical, dan pilih parameter hanya dari data correspondence, tanpa label motion atau ground truth.

CV fold boleh menahan baris sementara hanya untuk mengukur pilihan `(sigma, gamma)`. Setelah parameter dipilih, hitung ulang final field dengan **seluruh N correspondence** dan assert count/order; jangan gunakan hasil fit fold sebagai output final, dan jangan drop baris dari fit final. Untuk fold yang rank-deficient atau tidak punya support pelatihan cukup, keluarkan diagnostic no-selection; jangan diam-diam memakai fallback. Pertahankan max/mean gate PRD, tanpa TPS, global-to-local, perubahan produk, native build, atau TCM promotion. Jika matrix kembali gagal atau support tidak teridentifikasi di luar match support, laporkan untuk keputusan pengguna sebelum mengubah PRD.

## Git hygiene

Real index sebelum commit memuat tiga staged path pengguna: `patch_process/__init__.py` (`e0c89b748be7096b563b0876ea1c55088b0532c0`), `patch_process/multi_patch.py` (`39d1560562ba51ede600dff8e5c3506b91996722`), dan `test_fusionnet_multi_patch.py` (`f9a666c5475426cfcca03e8546854c4333fbafa0`). Saya mencatat hash penuh real index sebelum commit; commit Inspector hanya berisi feedback ini dan `status.json` melalui temporary Git index, kemudian memverifikasi hash real index dan OID staged tetap sama.
