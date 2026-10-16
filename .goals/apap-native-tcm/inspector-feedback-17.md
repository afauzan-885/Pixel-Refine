# Inspector Iteration 17 — FAIL

## Cakupan dan provenance

HEAD saat review: 33db054bb9871464b2e95fe393a2304344a1d3ba. Evidence Builder i17 masih untracked dan belum memiliki commit Builder. Saya tidak menjalankan ulang screen atau pytest; audit ini membaca evidence/JSON dan melakukan hitung ulang pasca-run.

SHA-256 evidence: C985F374AEAFFBA5A1E5E9ECDE87D58C1D8E1BF9152CDE9E1385D1696BE92ED9; harness: 50EB4CAC4F612D808AA423CDDAA1D5EE5E977E9B4298435410BCAAF89D8A6BE9; full JSON: B71C82D272FAF921724E7FDE0456159FF1939D559A211B164E9C3A5F135C82B3; pilot JSON: EE85AE21215CF55D489C241FC7251D9AE4E85C31ED42ED2B94CA7F29EDA49BE8. Fixture generator: 0443FED1BF1CD0EE83EDEF0FC9492726897C6EB442146C2E6F23D2CF8524B1D1; i16 harness/full JSON: FBF96AE3641142B665A962679BE3C5A129064206BED6BFEB171FDDC391F41836 / 1225D2EA06A3CF2DF7C39831A09CEE5B19B47C7C58A959167DCD0BF91A3CD932.

JSON menyatakan CPU NumPy/LAPACK, Python 3.12.9, NumPy 2.5.2, float64; 420 fixture unik (7 count × 12 layout × 5 motion) dan 825 query pada grid 33×25 per fixture. Ini bukti eksekusi reference CPU sintetis. Tidak ada CUDA, native graph, TCM, real-image, aplikasi, atau paired performance gate.

taichi_vision/taichi_algorithm/alignment/apap.py bersih terhadap HEAD dan hash file aktif tetap 3F4D6BB387EBF5CC740AA3C874A4D1FFAAAB6E41F95D1828ABF23D6ECC4468DA, sama dengan baseline yang dicatat i16. Evidence i17 tidak mengubah source produksi dan tidak menjalankan build/promosi TCM. Ada perubahan lain di worktree bersama; tidak saya stage atau sentuh.

## Hitung ulang gate dan perbandingan i16

Saya hitung ulang gate per fixture dari max error ≤1.0 px, mean error ≤0.15 px, output finite, dan Jacobian kandidat finite/positif. Hasil 86/420 lulus dan 334/420 gagal, cocok dengan seluruh flag pass JSON (0 mismatch). Dari 334 kegagalan, 312 melewati kedua batas error, 19 hanya melanggar batas maksimum, dan 3 hanya melanggar batas mean. Tidak ada Jacobian kandidat foldover, output non-finite, CV-unavailable, atau exception.

Breakdown lulus: homography 84/84, smooth-parallax 0/84, moving-patch 1/84, foreground-background 1/84, near-boundary 0/84. Error maksimum 83.6065 px pada N=16 anisotropic-horizontal/moving-patch; mean fixture terburuk 20.7616 px pada N=8 dengan layout/motion yang sama. Mean dari 420 mean-fixture 1.3840 px.

CV-selected final map sama dengan row i16 untuk konfigurasi tetap yang dipilih pada masing-masing fixture: 420/420 cocok, selisih max/mean error 0, dan pass status sama. CV melewati 86/420, di bawah konfigurasi tetap terbaik (sigma/D=0.05, gamma=0.005) yang melewati 96/420. Nilai 97/420 adalah batas atas diagnostik bila setiap fixture boleh memilih hasil terbaik dari enam fixed config memakai ground-truth acceptance metric; ini bukan metode seleksi yang dapat dipakai saat runtime.

Hitung ulang fixed-config i16: (0.05,0.005)=96, (0.05,0.01)=93, dan empat konfigurasi lainnya masing-masing 84. CV menurunkan mean dari mean-fixture 0.0995 px dibanding fixed terbaik (0.05,0.005), tetapi kehilangan 10 pass dan menaikkan worst max error dari 76.1448 menjadi 83.6065 px; hasilnya tidak memenuhi gate atau memperbaiki coverage.

## Formula, fold, dan pelestarian correspondence

Formula tetap canonical squared-distance Moving DLT: w_i=max(exp(-||x*−x_i||²/sigma²), gamma). Harness mengalikan kedua baris DLT dengan w_i dan mengambil right singular vector terkecil dari W A, sesuai objective yang menghasilkan kontribusi w_i² per pasangan pada normal matrix. CV memakai formula dan normalisasi DLT i16; tidak memakai radial kernel EadCat, TPS, homography global, global-to-local prior, blending node, atau image warp.

Selector membagi indeks source secara recursive stable median k-d menjadi empat fold, mempool squared held-out correspondence error menjadi RMSE, memilih kandidat dalam 1% dari RMSE terbaik, lalu tie-break ke gamma terbesar dan sigma terbesar. Saya menghitung ulang keputusan dari enam skor CV pada seluruh 420 row; konfigurasi terpilih selalu cocok (0 mismatch). Saya regenerasi source point saja untuk 84 kombinasi count/layout; fold sizes hasilnya cocok dengan JSON, dan kode mengassert disjoint train/holdout serta setiap row held out tepat sekali. Untuk N=8, fold size [2,2,2,2] menyisakan enam row train; selector mensyaratkan setidaknya empat train row plus rank DLT ≥8, jadi kasus low-count tetap lebih rapuh daripada count yang lebih besar.

Selector hanya menerima correspondence source/target dan menilai held-out correspondence reprojection; dense expected field tidak masuk ke seleksi. Sesudah seleksi, final fit memanggil fungsi i16 pada array source/target asli dan seluruh query. Semua 420 row mencatat rows_received=N, rows_used_per_query=N, dlt_rows_per_query=2N, urutan correspondence/query tetap, input tak berubah, dan 825 query. Tidak ada fold CV yang dipakai sebagai final map.

Batas interpretasi: CV mengoptimalkan prediksi pada titik korespondensi yang ditahan, sementara PRD menilai mapping pada grid dense 33×25. Inferensi dari setup: parameter selection tidak menambah observasi lokal di wilayah tanpa correspondence support, sehingga hasil all-query di sana tetap bergantung pada perilaku model. Data ini tidak membuktikan secara matematis bahwa semua varian pure Moving DLT mustahil memenuhi gate.

## Verdict dan keputusan berikutnya

FAIL. I17 menjalankan 420 fixture sintetis CPU float64 dengan formula canonical, 4-fold selection, dan final all-N solve yang tertib. Hitung ulang independen mengonfirmasi 86/420 pass; pilihan CV kalah dari fixed config terbaik 96/420 dan gagal luas pada semua motion lokal non-homography. I15, i16, dan i17 kini tiga reference screen pure Moving DLT berturut-turut yang gagal max/mean gate PRD yang sama. Tidak ada dasar untuk build native atau mengklaim kesiapan produk.

Keputusan scope/threshold kini diperlukan sebelum eksperimen algoritma lanjutan: apakah tetap mempertahankan pure Moving DLT dan gate PRD saat ini sambil menerima bahwa hasil yang sudah diuji belum lolos, atau secara eksplisit mengubah scope/model maupun acceptance gate. Saya tidak mengubah PRD atau thresholds. Status goal ditandai blocked menunggu steering; arahan global-to-local terdahulu tetap superseded dan tidak dihidupkan kembali.

## Git hygiene

Commit Inspector mencakup tepat feedback ini dan status.json, dibuat dengan temporary Git index. Tiga staged path user tetap memiliki OID yang sama: e0c89b748be7096b563b0876ea1c55088b0532c0, 39d1560562ba51ede600dff8e5c3506b91996722, dan f9a666c5475426cfcca03e8546854c4333fbafa0. Hash byte real index yang tercatat sebelum dan sesudah commit awal berbeda; karena itu saya tidak menyatakan real index byte-for-byte identik. Perubahan hash tidak saya atribusikan tanpa bukti; staged user OID tetap utuh. Setelah HEAD memuat feedback i17, real index lama menampilkan D untuk feedback tersebut. Temporary index sudah dihapus dan commit tidak berisi path user.
