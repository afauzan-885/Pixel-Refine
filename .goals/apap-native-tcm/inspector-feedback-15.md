# Inspector Iteration 15 — FAIL

## Cakupan dan provenance

Saya meninjau `.goals/apap-native-tcm/builder-evidence-iteration15.md` dan ketiga JSON di `%TEMP%`, tanpa menjalankan ulang screen atau pytest. HEAD masih `a7df4dcb739922ddff61ecd8216a66a68456cd09` (Inspector i14); evidence Builder i15 saat review masih untracked, jadi belum ada commit Builder i15 untuk dibandingkan. SHA-256 evidence saat review `6C8F6931CE3805F74D41C94757AFC8FBAF18A73071E66C29E469F77DB485585A`. Hash `apap.py` aktif cocok dengan laporan (`3F4D6BB387EBF5CC740AA3C874A4D1FFAAAB6E41F95D1828ABF23D6ECC4468DA`). Tidak ada perubahan dari review ini pada source, test, compiler, TCM, PRD, atau runtime.

## Hitung ulang matrix dan gate

- JSON source-bbox berisi 4.200 row (420 fixture × 2 track × 5 varian); image-grid piecewise 2.100 row (420 × 5); smooth image-grid subset 270 row (90 × 3). Saya hitung ulang `pass` per row. PRD tetap mensyaratkan untuk setiap fixture non-degenerate max error ≤1,0 px dan mean ≤0,15 px, output finite, serta Jacobian positif pada GT fold-free.
- Pada strict source-bbox setiap varian lulus 69/420; 75 fixture gagal dengan coverage error, total 43.075 query unsupported per varian. Emulasi support policy API lulus 84/420 per varian. Kedua track hanya meluluskan motion homography. Track API adalah emulasi; parity langsung A hanya dua kontrol N=122.
- Image-grid piecewise lulus 84/420 per varian, semuanya homography; empat motion non-homography masing-masing 0/84. Max error A/B `285,681 px`, C `116,626 px`. Lompatan sampled antar-cell maks `146,792 px` untuk A/B dan `65,332 px` untuk C; metrik ini sampling lintas cell, bukan ukuran limit satu sisi yang eksak.
- Smooth image-grid subset hanya 90 fixture dan lulus 18/90 per varian, semuanya homography. Semua motion non-homography gagal. Max error A/B `25,527 px`, C `41,160 px`. Karena subset ini sudah jauh melewati gate, perluasan screen tersebut tidak dibuktikan oleh evidence i15.
- Row JSON mengonfirmasi semua N correspondence dipakai di setiap fit, urutan correspondence/query dipertahankan, dan output finite. Jacobian kandidat sampel positif pada screen image-grid yang dilaporkan. Hal ini tidak mengatasi miss akurasi.

## Kesesuaian formula dan batas klaim

- Varian B mengalikan kedua baris DLT setiap pasangan dengan `w`, sehingga least-squares memakai koefisien `w²`, sesuai bentuk objective paper `||WAh||²`. Namun screen memakai bandwidth anisotropik `σx=W/4`, `σy=H/4`; ia belum merupakan reproduksi penuh Moving DLT kanonik dengan parameter/domain/evaluator yang sama. Varian C juga dinyatakan sebagai bentuk kernel, bukan reproduksi default EadCat.
- Screen full-image 420 memakai satu homography per cell dan bersifat piecewise. Screen smooth hanya mencakup 90/420 fixture. Jadi belum ada full-matrix bukti akurasi untuk field full-frame halus dengan formula paper yang tepat.
- `B_rank_update_eigh` hanya membangun identitas matriks normal lalu menjalankan eigensolve biasa; ini bukan implementasi percepatan secular/rank-one dan tidak membuktikan performa. Tidak ada native/TCM, CUDA MX150, pytest, aplikasi, benchmark paired, RSS, atau VRAM pada i15. Hasil adalah CPU NumPy float64 reference-screen saja.
- Kontrol API langsung berjalan terhadap working-tree `quality.py` yang memiliki perubahan `full_matrices=True`; perubahan itu tidak tercatat dalam hash evidence. Karena itu kontrol dua fixture tersebut bukan parity yang dapat direproduksi dari hash source yang dicantumkan saja. Source APAP aktif juga masih memakai node di bbox correspondence, blending matriks Gaussian, dan TPS residual default; screen i15 adalah eksperimen, bukan bukti integrasi produk.

## Verdict dan arah berikutnya

**FAIL.** Semua formula gagal gate pada setiap motion non-homography di screen 420; screen smooth full-frame yang tersedia juga baru subset 90 dan gagal seluruh motion non-homography. Tidak ada dasar untuk build native atau promosi runtime.

Satu iterasi reference-only berikutnya masih beralasan untuk menguji pertanyaan yang belum dicakup i15 secara penuh: pure canonical Moving DLT dengan formula paper `w=max(exp(-||x*-x_i||²/σ²), γ)`, parameter `σ`/`γ` dan koordinat/domain eksplisit, semua baris korespondensi dipertahankan, lalu evaluasi field halus di seluruh frame. Jangan tambahkan TPS residual atau prior global-to-local, dan jangan mengubah threshold PRD. Jika support lokal tidak teridentifikasi atau gate kembali gagal, laporkan batas tersebut dan minta keputusan pengguna sebelum mengubah scope/PRD. Tidak ada product/native build sebelum reference gate lulus.

## Git hygiene

Sebelum commit, real index memuat tiga staged path pengguna berikut dengan blob OID: `patch_process/__init__.py` `e0c89b748be7096b563b0876ea1c55088b0532c0`, `patch_process/multi_patch.py` `39d1560562ba51ede600dff8e5c3506b91996722`, dan `test_fusionnet_multi_patch.py` `f9a666c5475426cfcca03e8546854c4333fbafa0`. Commit Inspector dibatasi ke feedback ini dan `status.json` memakai temporary Git index; entri dan hash real index diverifikasi tetap sama setelah commit.
