# Inspector feedback 9 — Outer-Linkage Differential

Tanggal: 2026-10-25 (Asia/Jakarta)
Checkpoint: Builder handoff 9; source patch production tetap uncommitted
Model Inspector: GPT-6 (fallback; dedicated Goal Inspector model tidak tersedia)
Verdict: **PASS_FOR_DIFFERENTIAL_EVIDENCE_ONLY**

## Hasil inspeksi

Saya membandingkan dua file reproducer scratch secara read-only. Differential
iterasi 9 hanya menghapus tiga prefix per-fungsi `extern "C"`; `#include`
header, outer `extern "C"` block, `__declspec(dllexport)`, signature, dan body
`return 0` tetap sama. Tidak ada perbedaan substansial lain.

Command Builder memakai MSVC `cl.exe /Tp ... /c /Fo...`, tanpa link. Log aktual
menunjukkan exit 2 dan C2375 untuk ketiga fungsi dengan note pada prototype
header Pixel yang tepat. Scratch berisi hanya `.cpp` 433 byte dan log 2,286
byte; tidak ada `.obj`. Hash source/header serta bridge, C API, venv, manifest
dan status cocok dengan handoff. Tidak ada source/header, production/venv,
DLL/TCM, atau user file dimutasi.

Reproduksi ini mengonfirmasi bahwa prefix C per-fungsi bukan penyebab yang
diperlukan: menghapus ketiganya sementara mempertahankan outer C block dan
`dllexport` **tidak** menghilangkan C2375. Error terlokalisasi ke reproducer
header + outer C-linkage definitions + export attribute; ini tidak melibatkan
engine body, Taichi API, atau linker.

## Kesimpulan source

Belum ada source patch yang justified. Differential ini belum memisahkan
`__declspec(dllexport)` dari prototipe header yang tidak memakai atribut itu.
Ini variabel berikut yang paling kecil dan relevan untuk diuji; jangan mengubah
production header/definisi berdasarkan dugaan sebelum hasilnya ada.

## Satu langkah diagnostik berikutnya

Jika coordinator memilih lanjut, minta bounded approval baru untuk **satu**
reproducer scratch yang identik dengan iterasi 9 kecuali semua tiga
`__declspec(dllexport)` di definisi dihilangkan. Pertahankan header Pixel,
signature, outer `extern "C"` block, tanpa prefix per-fungsi C, dan body
`return 0`. Gunakan satu direct MSVC `cl /Tp <scratch.cpp> /c /Fo<new-scratch>\repro.obj`
dengan compiler yang sama, `/EHsc /std:c++20 /MT /arch:SSE2`, include path ke
`aot_py`, dan environment `CL` kosong. Tidak ada `/LD`, `/link`, `/O2`, `/GL`,
define, library input, DLL copy, atau TCM action.

- Jalankan tepat satu invocation di scratch baru; simpan source/header hashes,
  command, exit, log lengkap, dan hash `.obj` jika berhasil.
- Bila reproducer tanpa `dllexport` lulus, hasil hanya menunjuk ke interaksi
  deklarasi/export di reproducer minimal. Jangan langsung mengubah production
  source; minta review atas hasil dan pilih kontrak export yang kompatibel.
- Bila C2375 tetap ada, `dllexport` bukan variabel yang cukup menjelaskannya;
  stop tanpa patch atau retry dan minta review sebelum menguji bentuk deklarasi
  yang lebih sederhana.
- Dalam kedua hasil, tidak ada link/DLL/TCM/runtime, dan tidak ada klaim
  kualifikasi backend.

Goal mengizinkan compile secara umum, tetapi invocation reproducer iterasi 9
sudah memakai bounded approval yang diberikan. Reproducer tanpa `dllexport`
adalah invocation baru dan memerlukan approval bounded baru dari coordinator.
Inspector tidak menjalankan compiler/tes, tidak mengedit source/status, dan
tidak memuat DLL/TCM.
