# Inspector feedback 11 — No-Export Differential Result

Tanggal: 2026-10-25 (Asia/Jakarta)
Checkpoint: Builder handoff 11c; source patch produksi tetap uncommitted
Model Inspector: GPT-6 (fallback; dedicated Goal Inspector model tidak tersedia)
Verdict: **PASS_FOR_NO_EXPORT_RESULT_ONLY**

## Hasil inspeksi

Saya membandingkan reproducer export-present iterasi 9 dengan no-export
reproducer iterasi 11c. Perbedaan source-nya hanya penghapusan tiga
`__declspec(dllexport)` pada definisi; header, outer `extern "C"`, signatures,
dan body `return 0` tetap sama. Reproducer no-export lulus `cl /Tp /c` (exit 0)
dan menghasilkan `.obj` 871 byte. Log `/showIncludes` menyatakan `stdint.h`
diambil dari MSVC `include`; scratch hanya berisi `.cpp`, `.obj`, dan log.

Varian export-present iterasi 9 gagal C2375, tetapi handoff-nya tidak merekam
`INCLUDE`/Windows SDK environment dan tidak memiliki `/showIncludes`. Iterasi
11c memakai `vcvars64.bat`, INCLUDE MSVC + SDK, `/showIncludes /FC`, dan command
yang tercatat lengkap. Karena itu dua hasil tersebut belum menjadi A/B yang
terkontrol, walaupun perbedaan source memang hanya atribut export. Bukti ini
belum cukup untuk menyatakan `__declspec(dllexport)` menyebabkan C2375.

Rehash/no-mutation handoff 11c cocok dengan pemeriksaan saya: source/header,
production bridge/C API, venv C API, dan manifest tidak berubah. Iterasi 11c
menghasilkan object reproducer di scratch saja; tidak ada link, DLL, TCM,
load, runtime, parity, atau source edit. Git status tetap memiliki patch
Builder pada `taichi_aot_engine.cpp` serta beberapa user-owned/untracked paths;
Inspector tidak mengubah atau stage paths itu.

## Kesimpulan source

Belum ada production source correction yang dibenarkan. Hasil no-export lulus,
namun export-present belum diuji dengan environment identik. Header Pixel
mendeklarasikan fungsi di dalam `extern "C"` tanpa `dllexport`, sementara
definisi scratch export-present menambahkan atribut. Kesamaan signature dan C
linkage tidak cukup untuk memutuskan pindah atribut export ke header atau
mengubah deklarasi publik.

## Langkah aman berikutnya

Jika coordinator melanjutkan, minta bounded approval baru untuk **satu**
reproducer export-present yang dipasangkan dengan iterasi 11c:

1. Pertahankan source no-export reproducer 11c sebagai template dan tambahkan
   hanya tiga `__declspec(dllexport)` pada definisi. Header, outer C block,
   signatures, bodies, compiler, flags semantik, dan environment harus sama.
2. Inisialisasi MSVC x64 dengan `vcvars64.bat` yang sama; catat `where cl.exe`,
   versi/hash compiler, urutan `INCLUDE` lengkap, serta `/showIncludes` untuk
   membuktikan `stdint.h` dan Pixel `native_memory_control.h` yang digunakan.
   Gunakan root scratch baru dan `CL` kosong.
3. Jalankan satu direct `/Tp /c` ke `.obj` scratch, tanpa `/LD`, `/link`,
   libraries, `/O2`, `/GL`, defines tambahan, DLL copy, atau TCM command. Simpan
   command/log/exit/hash input dan output.
4. Stop setelah satu invocation. Jika export-present C2375 dan no-export pass
   di environment matched, atribut export menjadi kandidat yang terisolasi pada
   reproducer minimal—tetap minta review sebelum merancang source fix. Jika
   C2375 tidak terulang, jangan patch production dari hasil lama. Jika C1083
   muncul, environment masih tidak matched dan tidak ada kesimpulan atribut.
   Dalam semua kasus tidak ada retry/load/link/TCM tanpa review baru.

Bounded approval iterasi 11 sudah dipakai oleh no-export compile; invocation
export-present berikutnya memerlukan approval bounded baru dari coordinator.
Otorisasi umum `compilation_allowed=true` tetap berlaku dan tidak memerlukan
permintaan baru kepada pengguna.

## Batas review

Saya meninjau Builder handoff 9/10/11b/11c, status/memory, reproducer scratch,
log, hash/no-mutation evidence, dan header/source Pixel. Tidak ada compiler,
test, DLL/TCM load, atau source/status edit dari Inspector.
