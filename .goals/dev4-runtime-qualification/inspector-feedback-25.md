# Inspector feedback 25 — CUDA smoke stopped in static TCM preflight

Tanggal: 2026-10-25 (Asia/Jakarta)  
Model Inspector: GPT-6 (fallback; dedicated Goal Inspector model unavailable)  
Verdict: **FAIL_CHECKPOINT_CUDA_SMOKE_NOT_REACHED**

## Temuan independen

Saya membaca `cuda_gaussian_smoke.py`, runner, stdout, stderr, dan exit file.
Child Python berakhir dengan exit `1`; stdout berisi Driver API identity
MX150 lalu traceback `ValueError: Attempt to use ZIP archive that was
already closed`. Error terjadi dalam `verify_tcm_contract()` ketika fungsi
mencoba membaca `tcm_manifest.json` pada return expression setelah keluar
dari `with zipfile.ZipFile(...)`. Ini bug lifetime pada harness preflight,
bukan hasil CUDA execution.

Driver API gate **lulus** sebelum kegagalan: proses memperoleh ordinal 0,
NVIDIA GeForce MX150, CC 6.1, UUID
`79cb253ff59071e62a5af8dcc95b8874`, API 13.0. Script juga telah menghitung
hash/ukuran bridge, C API, dan TCM staging yang diharapkan. Namun panggilan
`verify_tcm_contract()` melempar sebelum mengembalikan objek preflight atau
mencetak event `staged_preflight`; validasi statis gabungan belum selesai.
Pemeriksaan byte dan payload sebelumnya di fungsi berjalan, menurut log dan
handoff, tetapi tidak menghasilkan gate sukses.

Kegagalan terjadi sebelum C API preload, impor facade AOT, load bridge,
resolver target, ABI preflight runtime, pemuatan TCM, upload input, dispatch,
atau parity. Perlu dibedakan: script memang memuat `nvcuda.dll` untuk query
Driver API, tetapi tidak memuat bridge/C API produk atau TCM. `python-exit-code.txt`
berisi numeric `1`; stderr kosong. Jadi iter25 membuktikan device identity,
bukan CUDA AOT runtime.

Saya menghash ulang staged inputs dan memperoleh bridge
`2B4068BA92093635023635B0887A3492B9BF4B6A9C37DBF9BC9CBC05FE3E2462`, C API
`B29073835F7496B5A08307ADF7C088651FC17A14BF469C46319D3C50F213CBCF`, TCM
`4B80591E0E4F597EB63BFFE11BAA9FD70729630FD36F9BD2C06D4151B582469F`, serta
sidecar `A18315B5358A5C2E065362EDF37749F1055513B1B4471ECC1C5A7CC6D8FD5C4D`.
Active/packaged CUDA binaries, venv C API, target manifest, dan canonical TCM
inventory tetap pada hash/count yang tercatat; canonical tree masih 1,694
file / 74,689,912 byte. Git status hanya memuat perubahan pengguna yang
sudah ada. Tidak ada source, status, venv, production artifact, atau
canonical TCM mutation. Inspector tidak menjalankan build, runtime, atau
test.

## Batas otorisasi dan status goal

Resolusi coordinator iter24 memberi tepat satu invocation runtime dan
menyatakan **jangan retry jika invocation gagal**. Iter25 menggunakan
invocation itu dan gagal sebelum AOT/native bridge/TCM. Karena itu tidak ada
retry yang boleh dilakukan berdasarkan otorisasi iter24. CUDA TCM load,
graph, parity, dan CUDA runtime qualification tetap **belum tercapai**.
Goal harus tetap terbuka/incomplete; jangan menandai `status.json` complete.

Jika coordinator kelak memberi otorisasi baru, perbaikan yang dibutuhkan
terbatas pada lifetime pemeriksaan statis: baca/hash `tcm_manifest.json`
selagi archive masih terbuka (atau simpan bytes-nya sebelum context exit),
barulah keluarkan hasil `staged_preflight`. Setelah gate statis utuh
lulus, invocation baru harus tetap memverifikasi identitas Driver API,
bridge/C API paths/hashes, target exact `cuda_x86_64_windows_nvidia`, dan
ABI preflight sebelum TCM load/graph. Berhenti pada mismatch atau error;
jangan memakai iter25 sebagai bukti eksekusi maupun menginferensikan device
compile iter22 dari MX150 runtime identity iter24.
