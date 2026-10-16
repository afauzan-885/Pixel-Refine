# Inspector Iteration 13 — FAIL

## Cakupan dan baseline

Meninjau Builder commit 94a8bedcb617db35cd1604b6719da6253d89bda9 setelah amend, terhadap PRD iterasi 10 dan evidence iterasi 13. Commit tersebut hanya menambah .goals/apap-native-tcm/builder-evidence-iteration13.md (104 baris); perubahan dari parent adalah evidence, perintah reproduksi, dan hash. Tidak ada perubahan APAP source/compiler/test atau TCM dalam commit. SHA-256 source saat ini cocok dengan hash baseline yang dicatat Builder: apap.py 3F4D6BB387EBF5CC740AA3C874A4D1FFAAAB6E41F95D1828ABF23D6ECC4468DA, compiler 6CC16FF786E3C47F16CE3BDC88E1A6B848484C27E4F2C8BB7D60665BD9B11C85, dan tes 3834E6B82E26F8EBB24878CEF18526779AC6465A097B5F9DECF8A9DE0BA3E2A1.

## Temuan terverifikasi

- Artefak matrix di %TEMP%\apap_iter13_sparse_rbf_full_matrix.json memuat 420 row unik untuk Cartesian product 7 count × 12 layout × 5 motion. Ukuran N=8, 16, 32, 64, 122, 300, 841; tiap query/output berukuran 825 titik (33×25), dtype float64. Evidence mencatat CPU Windows, Python 3.12.9, NumPy 2.5.2, SciPy 1.18.1, durasi 102.4 s. Ini eksekusi reference CPU; tidak ada CUDA pada screening ini.
- Saya hitung ulang gate dari setiap row: finite serta max error ≤1 px dan mean error ≤0.15 px. Hasilnya 91/420, sama dengan kolom pass; tidak ada row dengan metrik hilang atau exception solver. Angka agregat cocok: error maksimum 78.8186 px, rata-rata mean per fixture 1.52977 px, dan mean fixture terburuk 21.2231 px. Per count juga cocok: N=8 12/60, N=16 12/60, N=32 12/60, N=64 12/60, N=122 16/60, N=300 15/60, N=841 12/60. Per motion: homography 84/84, smooth parallax 0/84, moving patch 2/84, foreground/background 1/84, near boundary 4/84.
- Audit source harness menunjukkan seluruh N pasangan dipakai sebagai centers dan diagonal kernel tersedia per row; 8NN hanya menentukan radius. Tidak terlihat sampling, trimming, filtering, atau sorting ulang. Ini source-level audit: JSON tidak menyimpan assertion runtime terpisah atas count/order yang diteruskan ke solver, sehingga instrumentation count/order masih perlu dikunci dalam tes.
- Enam fixture yang di-audit dengan PCG lebih ketat (rtol=1e-12, hingga 1200 iterasi) memberi perubahan peta default-ke-ketat maksimum 5.97e-10 px; error fixture contoh tidak berubah. Ini mendukung bahwa toleransi CG bukan penyebab utama pada sampel audit tersebut, tetapi tidak mencakup seluruh matrix dan bukan dense exact-solve oracle.
- Nilai minimum Jacobian yang dilaporkan adalah Jacobian ground truth. Harness tidak mengukur Jacobian peta hasil kandidat, jadi gate PRD tentang output finite/Jacobian positif belum terverifikasi.
- Builder tidak membuat TCM atau menjalankan CUDA/native pada iterasi ini. Tidak ada bukti manifest/ABI target, eksekusi MX150, benchmark berpasangan dengan semantik residual sama, peak RSS/VRAM, atau promosi runtime. Kegagalan accuracy reference menghentikan screening sebelum tahap tersebut. Saya tidak menjalankan pytest atau compile; review memakai evidence/JSON tersimpan dan inspeksi source terbatas.

## Batas identifiabilitas

Untuk local deformation umum, gate error pada seluruh grid query tidak dapat diidentifikasi dari korespondensi yang hanya menutupi cluster berukuran kecil atau jumlahnya rendah: ada banyak field halus yang cocok pada semua pasangan teramati tetapi berbeda di wilayah tanpa dukungan. Regularisasi memilih salah satu prior; ia tidak menambahkan observasi tentang ground truth di luar support. Pada fixture ini generator memakai fungsi analitis yang diketahui harness, jadi ini bukan bukti bahwa fixture deterministiknya mustahil dipenuhi oleh model yang tepat. Namun PRD belum menetapkan prior deformasi yang boleh diasumsikan untuk menggeneralisasi dari titik terbatas ke seluruh frame. Ambang 1 px/0.15 px tetap dipertahankan; tidak ada pelonggaran yang diusulkan sebagai perubahan otomatis.

## Verdict dan rekomendasi

FAIL. Model gagal pada 329 dari 420 fixture terhadap ambang PRD; hasil homography saja tidak menutupi kegagalan parallax, objek bergerak, foreground/background, dan boundary. Angka threshold accounting konsisten, tetapi bukti Jacobian kandidat dan runtime count/order eksplisit juga masih kurang.

Satu iterasi CPU reference-only untuk menguji local-support adaptif/partition-of-unity secara teknis masih layak karena merupakan hipotesis representasi baru dan tidak memerlukan perubahan produk atau build native. Gunakan matrix 420 fixture, semua input rows, gate error yang sama, assertion count/order, dan Jacobian output. Jangan mulai build native sebelum seluruh fixture non-degenerate lolos. Jika eksperimen terbatas itu masih gagal, atau kualitas di luar support memerlukan prior yang belum disetujui, minta keputusan pengguna tentang asumsi model deformasi yang boleh dipakai sambil mempertahankan gate tetap. Jika itu memerlukan toleransi atau semantik kualitas baru, minta klarifikasi eksplisit sebelum mengubah PRD.

## Hygiene

Worktree berisi perubahan pengguna di luar scope. Sebelum commit, index nyata memuat empat path staged: pixel_refine_desktop/enhance_stack/core/algorithm/denoising/patch_process/__init__.py, pixel_refine_desktop/enhance_stack/core/algorithm/denoising/patch_process/multi_patch.py, pixel_refine_desktop/tests/test_fusionnet_multi_patch.py, dan taichi_vision/taichi_algorithm/denoising/nlm.py. Feedback ini dan status.json adalah satu-satunya path commit Inspector; tidak ada source, engine, atau TCM yang diedit.
