# APAP Native TCM — Builder Evidence Iteration 13

## Keputusan

**PARTIAL / FAIL.** Tidak ada model referensi yang memenuhi gate error PRD. Screening lengkap atas kandidat sparse RBF affine-tail tidak dilanjutkan ke build TCM, benchmark CUDA, atau promosi runtime. Tidak ada source APAP, compiler, test, caller, engine, UI, maupun artefak TCM yang diubah pada iterasi ini. Perubahan repository iterasi ini hanya dokumen evidence ini.

## Model dan batas eksperimen

Screening menguji referensi CPU float64, bukan graph native:

- Fit homography DLT ternormalisasi menggunakan seluruh N pasangan, lalu affine tail pada residual.
- Gunakan Wendland C2 compact RBF dengan **semua N correspondence sebagai centers** dan diagonal kernel untuk setiap row. Tidak ada trimming, filtering, sampling, atau pengurutan ulang input. Radius memakai 3 × median jarak tetangga ke-8; tetangga hanya menentukan skala radius, bukan memilih centers.
- Kernel sparse dinormalisasi simetris: `D^-1/2 K D^-1/2 + 0.01 I`; solve dua komponen dengan Jacobi-preconditioned CG, float64, `rtol=1e-9`, `atol=0`, maksimum 320 iterasi. Affine tail menangani komponen polinomial residual.
- Bandingkan peta pada grid query 33 × 25 (825 query) terhadap ground-truth motion. Gate tiap fixture: seluruh nilai finite, max error ≤ 1 px, mean error ≤ 0.15 px. GT Jacobian dihitung dengan finite difference pada grid.

Eksperimen pilot membandingkan frame/whitened metric, radius dan regularisasi. Degree normalization menghilangkan kegagalan CG yang terlihat pada formulasi tak ternormalisasi, tetapi kualitas model belum lolos. Pilot radius lebih lokal juga tidak memperbaiki hasil secara berarti. Kandidat full matrix dibekukan pada frame metric, faktor radius 3, lambda 0.01 karena pilot menunjukkan solver stabil tanpa melonggarkan gate kualitas.

## Matriks deterministik lengkap

Generator membuat Cartesian matrix 7 count × 12 layout × 5 motion = **420 fixture**. Setiap fixture memetakan N rows ke 825 query dengan dtype float64. Bentuk utama: source/target `(N,2)`, query/output `(825,2)`, kernel CSR `(N,N)`. Semua 420 fixture diproses dalam 102.4 s pada CPU Windows melalui Python 3.12.9, NumPy 2.5.2, SciPy 1.18.1. Tidak ada eksekusi CUDA pada screening ini.

Hasil keseluruhan:

- Gate lulus: **91/420 (21.7%)**. Kegagalan bukan akibat exception atau ketidak-konvergenan: solver failure **0/420**, residual norma maksimum `4.313e-8`, iterasi CG maksimum 193. Maksimum density matriks `1.0` pada konfigurasi kecil; N=841 memiliki sparse kernel sesuai radius tiap fixture.
- Error model maksimum di seluruh matrix: **78.819 px**; mean error rata-rata antarfixture `1.530 px`; fixture dengan mean tertinggi `21.223 px`.
- GT Jacobian nonpositive: **0/420**; minimum determinant `0.95435`.
- Per count, gate pass: N=8 **12/60**, N=16 **12/60**, N=32 **12/60**, N=64 **12/60**, N=122 **16/60**, N=300 **15/60**, N=841 **12/60**. Setiap count memakai seluruh 12 layout dan 5 motion.

Per motion (84 fixture per motion; `mean avg` adalah rata-rata dari mean error fixture):

- Homography: **84/84**, max `1.39e-11 px`, max mean `4.10e-12 px`, mean avg `3.15e-13 px`.
- Smooth parallax: **0/84**, max `36.439 px`, max mean `10.614 px`, mean avg `2.028 px`.
- Moving patch: **2/84**, max `78.819 px`, max mean `21.223 px`, mean avg `2.858 px`.
- Foreground/background: **1/84**, max `35.580 px`, max mean `11.804 px`, mean avg `2.245 px`.
- Near boundary: **4/84**, max `6.939 px`, max mean `2.276 px`, mean avg `0.517 px`.

Local model memperbaiki mean homography pada 76/84 smooth-parallax, 80/84 moving-patch, 79/84 foreground/background, dan 84/84 near-boundary fixture. Namun improvement terhadap homography tidak memenuhi gate max/mean absolute error.

Per layout × motion di bawah ini merangkum semua 7 count untuk tiap sel. `pass` adalah jumlah fixture lolos dari 7; `max` adalah error maksimum terbesar dari 7 fixture.

- **Homography:** grid_jitter `7/7, max 0.00`; high_uniform `7/7, 0.00`; medium `7/7, 0.00`; clustered_center `7/7, 0.00`; double_cluster `7/7, 0.00`; corner_clustered `7/7, 0.00`; anisotropic_horizontal `7/7, 0.00`; anisotropic_vertical `7/7, 0.00`; edge_heavy `7/7, 0.00`; corner_heavy `7/7, 0.00`; moving_region_cluster `7/7, 0.00`; portrait_uniform `7/7, 0.00`.
- **Smooth parallax:** grid_jitter `0/7, max 6.12`; high_uniform `0/7, 7.55`; medium `0/7, 14.07`; clustered_center `0/7, 12.39`; double_cluster `0/7, 9.90`; corner_clustered `0/7, 3.47`; anisotropic_horizontal `0/7, 36.44`; anisotropic_vertical `0/7, 19.31`; edge_heavy `0/7, 11.17`; corner_heavy `0/7, 3.92`; moving_region_cluster `0/7, 12.96`; portrait_uniform `0/7, 5.82`.
- **Moving patch:** grid_jitter `1/7, max 8.09`; high_uniform `1/7, 21.44`; medium `0/7, 29.59`; clustered_center `0/7, 40.36`; double_cluster `0/7, 12.52`; corner_clustered `0/7, 8.07`; anisotropic_horizontal `0/7, 78.82`; anisotropic_vertical `0/7, 42.41`; edge_heavy `0/7, 7.49`; corner_heavy `0/7, 8.10`; moving_region_cluster `0/7, 21.30`; portrait_uniform `0/7, 8.86`.
- **Foreground/background:** grid_jitter `1/7, max 3.28`; high_uniform `0/7, 3.31`; medium `0/7, 12.21`; clustered_center `0/7, 28.72`; double_cluster `0/7, 9.28`; corner_clustered `0/7, 2.47`; anisotropic_horizontal `0/7, 29.17`; anisotropic_vertical `0/7, 35.58`; edge_heavy `0/7, 6.30`; corner_heavy `0/7, 2.57`; moving_region_cluster `0/7, 6.67`; portrait_uniform `0/7, 4.02`.
- **Near boundary:** grid_jitter `2/7, max 6.10`; high_uniform `0/7, 6.87`; medium `0/7, 6.94`; clustered_center `0/7, 6.94`; double_cluster `0/7, 6.64`; corner_clustered `0/7, 4.89`; anisotropic_horizontal `0/7, 6.93`; anisotropic_vertical `0/7, 6.94`; edge_heavy `1/7, 6.94`; corner_heavy `0/7, 5.32`; moving_region_cluster `0/7, 6.93`; portrait_uniform `1/7, 6.94`.

## Pisahkan solver dari representasi

Enam fixture audit terpilih di-solve ulang dengan `rtol=1e-12`, maksimum 1200 iterasi. Dibanding run default `rtol=1e-9`, maksimum 320, perbedaan peta max ≤ `5.97e-10 px` dan mean ≤ `1.68e-10 px`; error terhadap ground truth praktis tidak berubah. Contohnya:

- Worst fixture N=8 anisotropic_horizontal/moving_patch: max tetap `78.8186 px`, mean tetap `21.2231 px`; perubahan peta default-ke-ketat max `3.45e-10 px`.
- Worst N=841 anisotropic_vertical/foreground_background: max tetap `20.8117 px`, mean `8.17085 px`; perubahan peta max `5.97e-10 px`.
- N=8 clustered_center/smooth_parallax: max tetap `12.3929 px`, mean `3.06483 px`; perubahan peta max `2.56e-13 px`.
- N=8 edge_heavy/near_boundary: max tetap `6.93860 px`, mean `0.23378 px`; perubahan peta terukur `0 px`.
- N=841 homography/moving_region_cluster: max tetap `1.44e-12 px`.

Bukti ini menunjukkan bahwa ketidakakuratan pada kasus contoh bukan disebabkan toleransi CG. Secara teknis gap berada pada representasi/coverage basis dan regularisasi kandidat. Ini belum membuktikan error pemodelan murni terhadap solusi eksak sparse RBF untuk seluruh fixture: tidak dibuat dense exact solve sebagai oracle tambahan. Meski demikian, kandidat yang dijalankan dengan solver residual kecil dan lebih ketat tetap gagal jauh dari gate.

## Pilot desain dan degeneracy

- Symmetric degree-normalized pilot (122/841 × 7 layout × 3 motion × 4 config): 168 fit selesai, 0 solver failure, konfigurasi pass berturut-turut **16/42, 14/42, 16/42, 14/42**. Worst max error `46.607 px` pada anisotropic_horizontal/moving_patch.
- Radius/regularization rendah (4 config): hasil pass **3/42, 5/42, 11/42, 13/42**; solver failure **29, 25, 8, 7** dari 42. Radius lebih lebar menaikkan pass sedikit tetapi tidak memenuhi kualitas.
- Radius lokal (1.0/1.5 × median-8NN; frame/whiten, lambda .01): setiap config **14/42**, solver failure 0. Tidak memperbaiki kualitas matrix.
- Degeneracy diagnostics harness: kurang dari 4 pasangan, collinear source, dan zero-range source eksplisit ditolak sebagai `degenerate:`. Kasus seluruhnya duplikat terdeteksi melalui zero-range/collinear check; belum ada diagnostic label khusus duplicate. Semua fixture matrix penuh sendiri valid untuk generate dan fit.
- Satu pilot edge awal dibuang karena bug harness pada assignment scalar edge; generator diperbaiki sebelum pilot final dan full matrix. Angka pilot yang dilaporkan berasal dari run setelah perbaikan.

## Reproduksi dan artefak

Repository: `E:\APP Developer\Eel-Dance\Pixel-Refine`; baseline HEAD `1afb0be0f36e3db55a69f93be697f8be84665c37`. Perintah full matrix:

```powershell
& .\venv\Scripts\python.exe "$env:TEMP\apap_iter13_sparse_rbf_full_matrix.py"
```

Perintah screening pilot hyperparameter yang dijalankan:

```powershell
& .\venv\Scripts\python.exe "$env:TEMP\apap_iter13_sparse_rbf_normalized.py"
& .\venv\Scripts\python.exe "$env:TEMP\apap_iter13_sparse_rbf_radius.py"
& .\venv\Scripts\python.exe "$env:TEMP\apap_iter13_sparse_rbf_local.py"
```

Perintah audit sensitivitas solver:

```powershell
& .\venv\Scripts\python.exe "$env:TEMP\apap_iter13_sparse_rbf_tight_audit.py"
```

Script dan JSON berada di `%TEMP%`, tidak ditambahkan ke repository. JSON lengkap 420 row: `%TEMP%\apap_iter13_sparse_rbf_full_matrix.json`. Hash SHA-256:

- Full matrix script: `146D374C6C538685BCCA5E674C8FCC98DBB389E7EF36730B49172CFA1A41B81C`
- Full matrix JSON: `8B0CC4F785100101F13E25FD48062222958D3A513482D36D2336E7CD496B77BC`
- Base deterministic fixture generator: `0443FED1BF1CD0EE83EDEF0FC9492726897C6EB442146C2E6F23D2CF8524B1D1`
- Normalized pilot script / JSON: `B114A14B3AF89536C481317C0209A1977667B02FBB38BB54376AF55AFC1B5E20` / `493A6CD875BD6AD2053248627F3152FFBBA0CF69952F9BD29D193EA1DE17C51D`
- Radius pilot script / JSON: `B8FEF69512F8AFD03B3A859A2A06D67184CB74991379F1EF48563417A45A708F` / `81B2147CDB55CF865E4E45B0946FD1D4BF96F0575E859E310C2B150B51F799DC`
- Local-radius pilot script / JSON: `1492AC96A674B4DAF14377A710A9D5593A105DF65838CB83226E9859CF8684E7` / `2C1B4F490E5283450A3F5872D2C2D26503089E90986431D2F931FCBE33103053`
- Tight-solver audit script / JSON: `F7E8AB1C3C7992674011382BBC33071B6D460EDB25CD28DA685BA90D51DE59EF` / `624AF0041DDC2B2C0AAD04F3C4037D26C10566F44C4B5B608DAE48FE9C29EC01`
- APAP source / compiler / test at baseline: `3F4D6BB387EBF5CC740AA3C874A4D1FFAAAB6E41F95D1828ABF23D6ECC4468DA` / `6CC16FF786E3C47F16CE3BDC88E1A6B848484C27E4F2C8BB7D60665BD9B11C85` / `3834E6B82E26F8EBB24878CEF18526779AC6465A097B5F9DECF8A9DE0BA3E2A1`

`apap.py`, `compile_mesh_warp_tcm.py`, and `test_alignment.py` were unchanged in iteration 13. No TCM was compiled, staged, or promoted. CUDA device, paired performance timing, peak RSS, and VRAM are **not measured** because the CPU reference failed quality gate before the native-build stage. No conclusion about native CUDA parity or performance is supported by this evidence.

## Langkah teknis berikutnya

Jangan mempromosikan fixed-grid i12 atau kandidat sparse RBF i13. Langkah terukur berikutnya adalah membandingkan pada fixture yang gagal sebuah representasi residual dengan local support adaptif/partition-of-unity yang tetap memasukkan seluruh observation center, menggunakan evaluasi reference float64 yang sama dan matriks fixture yang sama. Ukur per kelas, terutama anisotropic-horizontal/vertical, clustered, moving-patch, dan near-boundary; tetapkan solver residual dan perubahan peta terhadap solve ketat sebagai kontrol. Build native hanya bila semua fixture valid memenuhi gate max/mean dan semua row/order assertions lebih dahulu lulus.
