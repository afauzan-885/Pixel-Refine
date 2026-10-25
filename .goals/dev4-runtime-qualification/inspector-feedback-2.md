# Inspector feedback 2 — Runtime Qualification Linkage Follow-up

Tanggal: 2026-10-25 (Asia/Jakarta)
Delta Builder yang diperiksa: working-tree patch `taichi_aot_engine.cpp` (belum di-commit)
Baseline: `f3e326221c2f30b546dddac268cddd723920e739`
Model Inspector: GPT-6 (fallback; dedicated Goal Inspector model tidak tersedia)
Verdict: **FAIL — source delta tampak benar, tetapi laporan C2375 ulang belum terjelaskan**

## Kesimpulan dan koreksi terkecil

Patch tiga fungsi di working tree sekarang sudah menambahkan `extern "C"` pada
definisi yang bersesuaian dengan deklarasi C-linkage di header. Berdasarkan
source translation unit yang terlihat, ini adalah koreksi source terkecil yang
didukung bukti; signature, struct layout, dan header tidak perlu diubah.

Builder melaporkan C2375 yang sama setelah patch. Namun current source memiliki
linkage yang sama pada deklarasi dan definisi, seluruhnya di global namespace,
dan tidak ada deklarasi source tambahan untuk nama-nama ini pada file/header
yang diperiksa. Karena handoff tidak menyertakan baris command `cl.exe` yang
sudah diekspansi maupun bukti source file yang benar-benar dikompilasi, alasan
error tetap muncul tidak dapat dijelaskan dari bukti yang ada. Jangan membuat
patch source kedua secara spekulatif. Iterasi berikutnya harus memastikan
identity input build terlebih dahulu.

Verdict `FAIL` ini berlaku pada checkpoint linkage/build investigation; tidak
menyatakan perubahan source terbukti salah. Goal runtime qualification tetap
belum selesai dan tidak ada DLL/TCM/runtime qualification.

## Bukti source/linkage

- `taichi_vision/taichi_algorithm/aot_py/native_memory_control.h:46-56`
  membuka dan menutup blok `extern "C"`; deklarasi berada pada baris 49,
  50, dan 53-54.
- Include header ada di `taichi_vision/taichi_algorithm/aot_py/taichi_aot_engine.cpp:17`.
  Working-tree diff menambahkan `extern "C"` tepat pada definisi baris 2054,
  2112, dan 2135-2136. `EXPORT` di Windows adalah `__declspec(dllexport)`
  pada baris 28; makro tersebut bukan linkage specifier.
- Source file tidak memiliki namespace yang membungkus definisi itu. Search
  exact symbol pada AOT source, header, tests, dan binding hanya menemukan
  deklarasi header, definisi source, dan penggunaan binding/test; tidak tampak
  deklarasi C++ kedua di source checkout yang ditinjau.
- Hash Inspector untuk source dengan delta saat ini adalah
  `97833F7377074482B48A9DB82835700BC2A22C38982F435025E6919D3C8A429D`, sama
  dengan source hash post-patch di handoff Builder.
- Arti diagnostik MSVC C2375 adalah suatu fungsi telah dideklarasikan dengan
  linkage specifier berbeda; lihat [dokumentasi resmi C2375](https://learn.microsoft.com/en-us/cpp/error-messages/compiler-errors-1/compiler-error-c2375?view=msvc-170).
  Secara statis, current declaration dan definition kini sama-sama C linkage.
- Handoff 2 melaporkan diagnostik yang sama pada source:2054/header:49,
  source:2112/header:50, dan source:2135/header:53 setelah menambahkan linkage.
  Ini tidak konsisten dengan translation unit yang terlihat saat Inspector
  membacanya, tetapi bukan bukti pasti build memakai file lama: expanded
  `cl.exe` input path, compiler response file, dan preprocessed input tidak
  dilampirkan.

## Verifikasi staging dan artefak aktif

- Handoff mencatat command build dengan root unik
  `D:\temp\pixel_refine_dev4_runtime_qualification_20261025_7ab5e244_iter2`
  dan override `PIXEL_REFINE_BRIDGE_OUTPUT_DIR=...\bridge\cpu`, lalu
  `build_engine_msvc.bat cpu baseline`. Handoff melaporkan C2375 dan tidak ada
  DLL/import library/C API copy yang dibuat. Inspector melihat scratch root dan
  `bridge\cpu` ada tetapi hanya berisi direktori kosong `bridge\cpu`.
- Hash Inspector cocok dengan post-build evidence Builder untuk production
  bridge CPU/CUDA/OpenGL/Vulkan: `CEA5B53BE236F1D6BAB30DBC2A540B650889119B91EA582C44406BFF85FED270`,
  `6127AA2F4DA5ACF4B7C372C3DA88C4AF21A294E719263AF109D9628B6B38A493`,
  `914B6ED4D6F7E20AB01B0ECE42186252210E85EF879C0D16CF94985A3A76B2EE`, dan
  `6DAD0D648D250A76EF1E8676035DCE1AB783F29E0E1C672B308B0F1518A6CAD4`.
- Keempat packaged C API tetap 51,319,808 byte, hash sama
  `73190273F18B658762FAFD98B62C11CEE349A96564D211A919AA137D689F6C73`.
  Venv Dev4 `taichi_c_api.dll` tetap
  `B29073835F7496B5A08307ADF7C088651FC17A14BF469C46319D3C50F213CBCF`,
  import library tetap `6E7D0BE02CAFE084E8D24A93F1D12FE541FE82585653F4A229F5FF3381191413`,
  headers tetap `77F33ACD7D985162AFBB85F3541290B5D460D65675B574F0DFB96AD401A61FEC`
  dan `FBFCA94C7BCD6F9FC4C10BAF02FFFD25405E7371AC3BA0A89CDB0D2FA19201FE`.
  Target manifest tetap
  `485A813D70768435D78C0B596EE874D2577516C7DDB2C102AE7ED68B1C2323E3`.
- Git status memuat satu tracked delta Builder pada
  `taichi_aot_engine.cpp` serta user-owned untracked `ops_matrix.json` dan
  `taichi_vision/taichi_aot/neural_universal/`. Tidak ada perubahan tracked
  production bridge/TCM atau venv. Hasil hash menegaskan binary aktif dan
  manifest cocok dengan handoff; tidak ada TCM compile/load yang dilaporkan.

## Langkah aman berikutnya

1. Pertahankan tiga prefix `extern "C"` saat ini; jangan ubah signature/header
   atau menambah wrapper API.
2. Sebelum source patch atau build ulang, Builder perlu mencatat hash source
   aktual tepat sebelum command dan command `cl.exe` aktual beserta path input
   translation unit; aktifkan echo/logging batch secara sementara atau gunakan
   log toolchain agar terlihat executable dan source path yang dipanggil.
3. Jalankan paling banyak satu build CPU baseline ke scratch root baru yang
   unik. Jika C2375 berulang dengan source hash dan input path terbukti cocok,
   hentikan iterasi source; lampirkan include/preprocessor context yang cukup
   untuk menemukan deklarasi tambahan/linkage context sebelum memilih koreksi
   baru. Jangan load DLL atau compile TCM selama kontradiksi ini belum selesai.

Inspector tidak menjalankan build, syntax-only, tes, atau DLL load; tidak
mengubah source/status; dan tidak mengulang hash/probe di luar pemeriksaan
statis yang disebut di atas.
