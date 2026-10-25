# Inspector feedback 12 — Matched Export Differential

Tanggal: 2026-10-25 (Asia/Jakarta)  
Checkpoint: Builder handoff 12, production source patch tetap uncommitted  
Model Inspector: GPT-6 (fallback; dedicated Goal Inspector model tidak tersedia)  
Verdict: **PASS_FOR_MINIMAL_EXPORT_DIFFERENTIAL_ONLY**

## Hasil verifikasi

Saya membandingkan scratch sources iterasi 11c dan 12. Diff menunjukkan satu
perubahan faktor saja: tiga token `__declspec(dllexport)` ditambahkan ke
definisi iterasi 12. Header, outer `extern "C"`, signature, trivial bodies,
compiler, `/Tp /c`, `/EHsc /std:c++20 /MT /arch:SSE2`, include path, dan
environment MSVC/Windows SDK tercatat sama. Iterasi 11c tanpa export lulus dan
menghasilkan `.obj`; iterasi 12 dengan export gagal C2375 pada ketiga definisi,
dengan notes ke deklarasi header yang sama. Ini mendukung bahwa export
annotation pada definition adalah faktor penyebab pada reproducer minimal,
bukan hanya dugaan dari dua invocation dengan environment berbeda.

Saya memeriksa handoff 12 dan isi scratch yang dicatat. Tidak ada `.obj` pada
iterasi 12; hanya reproducer `.cpp` 433 byte dan log 4,526 byte. Rehash Inspector
cocok dengan handoff untuk source/header Pixel, CPU production bridge/C API,
venv C API, dan target manifest. Status Git tetap memiliki patch Builder pada
`taichi_aot_engine.cpp` serta user changes/untracked lain; tidak ada yang
diubah atau di-stage. Tidak ada link, DLL/TCM, runtime, parity, atau benchmark.

## Batas kesimpulan dan source fix

Hasil ini mengisolasi interaksi `__declspec(dllexport)` pada definition dengan
prototype header yang belum membawa annotation dalam reproducer minimal. Ia
tidak membuktikan bahwa produksi dapat diperbaiki hanya dengan menambahkan
`dllexport` ke header, dan belum membuktikan export table/ABI setelah link.
Karena itu **belum ada production source patch yang saya sahkan**. Memindahkan
atau menyamakan export annotation di header/definition adalah kandidat terkecil
yang layak diuji, tetapi perlu satu fixture scratch lagi sebelum mengubah header
atau source aktif.

Handoff independen terpisah untuk iterasi 12 tidak tersedia di `.goals`; saya
memakai Builder handoff 11c/12, Investigator audit yang tercatat, dan
pemeriksaan langsung atas diff reproducer/log/scratch. Audit input environment
iterasi 11c/12 konsisten: `vcvars64.bat`, `CL` kosong, compiler
19.42.34435.0/hash sama, urutan INCLUDE sama, dan `/showIncludes` menunjuk ke
header Pixel serta `stdint.h` MSVC.

## Next step yang disarankan

Minta bounded approval baru untuk satu C++ compile-only fixture di scratch,
tanpa production edit:

1. Salin `native_memory_control.h` Pixel ke scratch sebagai fixture dan tambah
   `__declspec(dllexport)` hanya pada tiga prototype C-linkage di salinan itu.
   Simpan hash header asli dan fixture; jangan mengubah header Pixel.
2. Buat reproducer di direktori scratch yang sama: include fixture header,
   definisikan fungsi dalam outer `extern "C"` block dengan signature identik,
   body `return 0`, dan **tanpa** `__declspec(dllexport)` di definitions.
   Dengan demikian attributes berada pada declaration side saja.
3. Gunakan compiler/environment sama dengan iterasi 11c/12, `/Tp /c`, `/Fo`
   ke object scratch, `/EHsc /std:c++20 /MT /arch:SSE2`, include path ke
   scratch header, `CL` kosong, `/showIncludes`, dan log lengkap. Jangan pakai
   `/LD`, `/link`, library, full bridge, DLL, TCM, atau production source/header.
4. Satu invocation saja lalu stop. Jika lulus, itu mendukung header-side export
   placement pada fixture minimal, tetapi production patch masih perlu review
   API/platform guards dan kemudian validasi export table pada bridge scratch.
   Jika C2375/C1083 tetap terjadi, tidak ada source fix; kirim log untuk review.

Invocation iterasi 12 sudah memakai bounded approval sebelumnya; test header
fixture adalah invocation baru dan memerlukan approval baru dari coordinator.
Goal umum tetap memiliki `compilation_allowed=true`; tidak perlu meminta ulang
izin compile dari pengguna.
