# Inspector feedback 5 — Runtime Qualification Preprocessor Review

Tanggal: 2026-10-25 (Asia/Jakarta)
Checkpoint: Builder handoff iterasi 5, source delta tetap uncommitted
Model Inspector: GPT-6 (fallback; dedicated Goal Inspector model tidak tersedia)
Verdict: **PASS_FOR_ONE_BOUNDED_SEMANTIC_REPLAY**

## Temuan pada `.i` dan log

Saya membaca file aktual dari scratch yang dilaporkan Builder:

- `D:\temp\pixel_refine_dev4_runtime_qualification_20261025_7ab5e244_iter5_preprocess\taichi_aot_engine.preprocessed.i`
  ukuran 8,303,300 byte; SHA-256
  `9CC2D9CEAD8585B7A0E577B47B7353944C7A8693398BDDFAA726F3888969854F`.
- `...\msvc_preprocess.log` ukuran 114,434 byte; SHA-256
  `5BE81E8E8F60573E6EB4729A4A37D180D1BEF97B83747424C4F0B382BA59AB48`.

Search read-only dengan `rg -n -F` menemukan tepat **tiga kemunculan** setiap
nama simbol dalam `.i`: satu prototype, satu definisi, dan satu string literal
nama operasi yang diteruskan ke `memory_boundary`. Tidak ditemukan deklarasi
kedua atau deklarasi/definisi non-C dengan nama yang sama.

- `ti_aot_get_memory_snapshot`: prototype `.i:117715` di dalam blok
  `extern "C"` yang terbuka pada `:117712` dan ditutup `:117722`; definisi
  `.i:462634` tertulis `extern "C" __declspec(dllexport)`. Satu referensi
  string ada di `:462635`.
- `ti_aot_set_memory_limits`: prototype `.i:117716` dalam blok header yang
  sama; definisi `.i:462692` tertulis `extern "C" __declspec(dllexport)`.
  Satu referensi string ada di `:462693`.
- `ti_aot_trim_memory_cache`: prototype `.i:117719-720` dalam blok header yang
  sama; definisi `.i:462715-716` tertulis `extern "C" __declspec(dllexport)`.
  Satu referensi string ada di `:462717`.

Builder handoff 4 melaporkan C2375 untuk masing-masing definisi pada source
`:2054`, `:2112`, `:2135` dengan note ke prototype header `:49`, `:50`, `:53`.
Path `/FC` dan include log menunjuk ke Pixel translation unit dan sibling
`native_memory_control.h`; `.i` memperlihatkan hasil preprocessing dari pasangan
tersebut. Meskipun demikian, `/P` tidak menjalankan semantic compiler, jadi
hasil ini belum mereproduksi atau menjelaskan C2375. Preprocessed text yang
tersedia tidak mendukung patch source baru.

Log yang dibaca adalah capture PowerShell berisi wrapper `NativeCommandError`
dan `/showIncludes`; pencarian menemukan source `taichi_aot_engine.cpp`, header
lokal `native_memory_control.h`, serta Dev4 `taichi.hpp`/`taichi_opengl.h`.
Tidak ditemukan `error C2375` di log preprocessing, konsisten dengan command
`cl /P` yang dilaporkan exit 0. Log/hash sesuai handoff; terminalisasi output
PowerShell membuat log tersebut wrapper teks, bukan raw process transcript.

## Source fix

Tidak ada source correction baru yang justified. Source `.cpp` memiliki outer
`extern "C"` block yang mencakup fungsi-fungsi ini; preprocessed declarations
dan definitions juga sama-sama C linkage. Tiga prefix per-fungsi pada source
working tree redundan, tetapi saya tidak mengubah atau merekomendasikan edit
sebelum semantic replay. Bila diperlukan, hapus prefix hanya setelah coordinator
memutuskan berdasar hasil replay dan review berikutnya.

## Langkah aman berikutnya: satu semantic replay dari `.i`

Satu kompilasi frontend terkendali terhadap file `.i` diperlukan untuk
menentukan apakah C2375 muncul kembali dari **preprocessed input yang sama**.
Kompilasi ini tidak memakai translation unit source/header lagi, tidak link,
tidak menghasilkan bridge, dan tidak memuat DLL. Microsoft mendokumentasikan
bahwa `/P` menghasilkan file preprocessed dan meniadakan kompilasi; untuk
semantic replay file itu dikompilasi ulang sebagai input `.i` dengan `/c`
([`/P`](https://learn.microsoft.com/en-us/cpp/build/reference/p-preprocess-to-a-file?view=msvc-170),
[`/Fi`](https://learn.microsoft.com/en-us/cpp/build/reference/fi-preprocess-output-file-name)).

Batas wajib untuk Builder pada iterasi berikutnya:

1. Jangan edit source/header. Gunakan `.i` di atas dengan hash yang dicatat,
   MSVC `cl.exe` yang sama (versi `19.42.34435.0`, SHA-256
   `3E761C082F491950ED5565F198F2113A8043897CE4D8084E37DE8E0FEE43202A`) dan
   scratch root baru yang unik di luar repo.
2. Jalankan satu direct `cl.exe` invocation dalam mode `/c` terhadap file `.i`
   itu dan arahkan `/Fo` ke `.obj` di scratch baru. Pertahankan opsi semantic
   yang relevan (`/std:c++20`, `/EHsc`, `/MT`, `/arch:SSE2`); jangan panggil
   `build_engine_msvc.bat`.
3. Hilangkan `/P`, `/LD`, `/link`, `/OUT`, `/IMPLIB`, C API library inputs, dan
   post-build copy. Pastikan `CL` environment tidak menyuntikkan hidden flags.
   Satu-satunya artifact yang boleh muncul adalah object file dan log di scratch.
4. Capture command, source `.i` hash pre/post, full stdout/stderr, exit status,
   dan hash object bila berhasil. Stop setelah percobaan ini.
5. Jika C2375 muncul lagi, jangan mengedit source atau mencoba ulang: serahkan
   diagnostics yang menunjuk ke line marker `.i` untuk review berikutnya.
   Jika `.i` lulus compile, jangan langsung menjalankan full bridge build; minta
   review baru untuk membandingkan opsi semantic/preprocessor dan menentukan
   apakah sumber saat ini perlu perubahan.

Semantic replay ini hanya diagnosis. Ia tidak mengualifikasi bridge/ABI, tidak
menghasilkan DLL yang boleh dimuat, dan tidak membuka gate TCM/runtime/parity.

## Scope dan batas review

- Hash serta ukuran `.i`/log di atas diverifikasi read-only; pencarian exact
  token dilakukan pada file `.i` dan log aktual.
- Source hash tetap `97833F7377074482B48A9DB82835700BC2A22C38982F435025E6919D3C8A429D`;
  header tetap `9775DB46C1880DA86D472B47783ECB94829A615CE3453960CEBE9376177BC116`.
  Status Git tetap satu source delta Builder dan dua user-owned untracked path.
- Tidak ada compiler, preprocessing, test, DLL/TCM load, atau source/status edit
  yang dijalankan Inspector.
