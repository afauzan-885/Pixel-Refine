# Inspector feedback 3 — Runtime Qualification Diagnostic Build Gate

Tanggal: 2026-10-25 (Asia/Jakarta)
Source delta: uncommitted three-definition linkage patch, retained unchanged
Model Inspector: GPT-6 (fallback; dedicated Goal Inspector model tidak tersedia)
Verdict: **PASS_FOR_ONE_STAGED_DIAGNOSTIC_BUILD_ONLY**

## Koreksi review sebelumnya

Saya mengoreksi finding Inspector iterasi 1/2 yang menyatakan definisi tiga
fungsi berada di luar C-linkage block. Di source saat ini, block
`extern "C" {` dibuka pada `taichi_aot_engine.cpp:1632` dan ditutup pada
`:3329`; ketiga definisi `:2054`, `:2112`, dan `:2135-2136` sudah berada di
dalam block tersebut. Deklarasi header di `native_memory_control.h:49-54`
juga berada di block C linkage `:46-56`. Jadi source baseline sebelum patch
per-fungsi pun sudah menunjukkan C linkage pada scope luar.

Prefix `extern "C"` yang kini ditambahkan per fungsi redundant terhadap block
luar. Tidak ada bukti yang membenarkan source edit tambahan; jangan edit patch
ini sebelum diagnostic build yang diizinkan di bawah. C2375 yang dicatat pada
dua build sebelumnya tetap tidak terjelaskan oleh source/header yang terlihat.

## Keputusan gate

Bukti statis yang sekarang tersedia cukup untuk mengizinkan **satu** fresh
CPU-baseline diagnostic build di staging dengan `/showIncludes /FC`, tanpa
source edit terlebih dahulu. Tujuan run tunggal ini adalah merekam input/header
yang benar-benar dipakai MSVC dan menguji ulang C2375, bukan mengualifikasi
bridge atau mengizinkan DLL load. Investigator dan Inspector tidak menjalankan
build tersebut.

## Bukti identitas command dan toolchain

- `build_engine_msvc.bat` saat ini ber-hash
  `CDCFAB019B42CFA173C378A23DFDCB2526E8B7128E70D98525A48CCC806597B4` dan
  secara statis menetapkan source sebagai `%SCRIPT_DIR%\taichi_aot_engine.cpp`
  (script lines 4-5/125), `TAICHI_INC` ke venv C API include bila direktori ada
  (lines 16-21), linker input default ke venv `TAICHI_LIB` (line 23), dan
  output override ke `PIXEL_REFINE_BRIDGE_OUTPUT_DIR` (lines 25-43).
  `cl.exe` menerima `/I` untuk include venv dan Glad serta source tersebut
  langsung (lines 121-128). Ini sesuai dengan command hasil ekspansi yang
  dicatat Builder di handoff 3.
- Handoff Builder 3 mencatat invocation lama memakai source canonical
  `E:\APP Developer\Eel-Dance\Pixel-Refine\taichi_vision\taichi_algorithm\aot_py\taichi_aot_engine.cpp`,
  venv C API include/lib, Glad include, CPU baseline flags, dan output
  iter2 scratch. Build script menerima CPU baseline. `PIXEL_REFINE_TAICHI_LIB`
  dan PCH/forced-include/response-file override dilaporkan tidak digunakan.
- Path `cl.exe` yang dilaporkan dipilih di environment VS DevCmd adalah
  `D:\Program Files\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.42.34433\bin\Hostx64\x64\cl.exe`.
  Pembacaan metadata/hash Inspector (tanpa mengeksekusi compiler): versi file
  `19.42.34435.0`, SHA-256
  `3E761C082F491950ED5565F198F2113A8043897CE4D8084E37DE8E0FEE43202A`.
  Ini konsisten dengan identitas yang dicatat di handoff. Path/hashes adalah
  bukti statis pilihan toolchain yang dilaporkan, bukan log input proses build
  lama.
- Capture `/showIncludes /FC` masih penting karena build gagal iterasi 2 tidak
  mencatat hasil resolusi header (`/showIncludes`) atau nama source penuh pada
  diagnostics (`/FC`). Rekonstruksi statis tidak menggantikan log compiler.

## Pixel vs fork source/header

- Pixel source dengan patch saat ini ber-hash
  `97833F7377074482B48A9DB82835700BC2A22C38982F435025E6919D3C8A429D`; fork
  `unit_test/taichi_vision/.../taichi_aot_engine.cpp` ber-hash
  `BABA48AF5DC79BF17BEDA669C85BE45421E60A30993690CAB22225BACA024F14`.
  Diff tiga fungsi menambah prefix `extern "C"` dan mengubah indentasi
  continuation signature fungsi trim; path Pixel di script merujuk checkout
  Pixel, bukan source fork.
- Pixel dan fork `native_memory_control.h` keduanya ber-hash
  `9775DB46C1880DA86D472B47783ECB94829A615CE3453960CEBE9376177BC116`.
  Header C API venv Pixel `taichi.hpp` dan `taichi_core.h` juga dilaporkan
  byte-identik dengan header fork yang dipilih; ini source/header identity,
  bukan bukti kompatibilitas DLL/import library saat runtime.
- Include di Pixel `.cpp:17` memakai quoted include lokal. Handoff investigator
  memeriksa source-local header dan tidak menemukan duplikat
  `native_memory_control.h` di venv, Glad, MSVC, atau Windows SDK include roots.
  Karena compiler sebelumnya tidak mengeluarkan include trace, header yang
  benar-benar dibuka tetap belum teramati; diagnostic build menutup gap itu.

## Tidak ada mutasi artefak aktif

- Rehash Inspector cocok dengan handoff untuk keempat bridge production, keempat
  packaged C API, venv C API/import library/headers, dan target manifest. Hash
  dan ukuran DLL saat ini sama dengan feedback sebelumnya; tidak ada staging
  output iter2 selain direktori kosong `bridge\cpu`.
- Status Git hanya menunjukkan patch Builder pada
  `taichi_aot_engine.cpp`, serta user-owned untracked `ops_matrix.json` dan
  `taichi_vision/taichi_aot/neural_universal/`. Tidak ada source/status edit oleh
  Inspector. Handoff Builder/investigator juga menyatakan tidak ada build pada
  investigasi iterasi 3 atau mutasi DLL/TCM/venv.
- Pixel/fork file hash, MSVC executable metadata, artifact rehash, status Git,
  dan keberadaan/isi scratch directory diperiksa secara read-only. Tidak ada
  build, test, TCM compile, DLL load, atau perubahan source dari Inspector.

## Kondisi wajib untuk diagnostic run berikutnya

1. Gunakan source/header saat ini tanpa edit dan satu scratch root baru yang
   unik di luar checkout; jangan reuse output iter1/iter2. Batasi hanya CPU
   baseline bridge build.
2. Jalankan dari Pixel checkout dan capture command `cl.exe` yang benar-benar
   dieksekusi, `where cl.exe` setelah VsDevCmd, versi/hash toolchain, source
   hash tepat sebelum/sesudah, dan output utuh dengan `/FC /showIncludes`.
   Catat resolved path untuk translation unit dan `native_memory_control.h`.
3. Stop setelah satu run. Jika C2375 tetap ada meski trace mengonfirmasi Pixel
   source/header yang memiliki linkage block di atas, jangan edit source,
   jangan mengulang build, dan kirim diagnostics/include trace untuk investigasi
   baru. Jika build sukses, output tetap hanya scratch; review PE/import/export
   statis diperlukan sebelum gate runtime terpisah.
4. Diagnostic build ini tidak mengizinkan TCM compile, DLL load, runtime,
   parity, atau promosi artefak. ABI/runtime qualification tetap pending.
