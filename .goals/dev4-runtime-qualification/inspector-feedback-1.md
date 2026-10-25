# Inspector feedback 1 — Runtime Qualification P0

Tanggal: 2026-10-25 (Asia/Jakarta)
Commit source Builder: tidak ada; handoff memeriksa baseline `7ab5e244391c2a223ebde51cd59ef287a28acc59`
Model Inspector: GPT-6 (fallback; dedicated Goal Inspector model tidak tersedia)
Verdict checkpoint: **PASS_FOR_PREFLIGHT_DIAGNOSIS_ONLY**

## Kesimpulan

Diagnostik MSVC C2375 didukung oleh source yang diperiksa. Tiga deklarasi
memory-control berada dalam C linkage pada header, sementara definisi yang
ditunjuk diagnostik tidak ditulis di linkage block dan makro `EXPORT` Windows
hanya menambahkan `__declspec(dllexport)`. Perubahan paling kecil yang
didukung bukti adalah memberi C linkage eksplisit pada ketiga definisi
(`extern "C"` per fungsi atau satu block). Ini belum membuktikan perubahan akan
berhasil dikompilasi; Builder harus melakukan satu rebuild scratch-only setelah
perubahan.

PASS ini hanya menerima temuan dan batas P0 sebagai dasar iterasi source
berikutnya. Goal runtime qualification belum selesai: tidak ada bridge Dev4
yang berhasil dibuat, tidak ada TCM compile/load, backend run, parity, atau
runtime qualification.

## Bukti source dan diagnostik

- `taichi_vision/taichi_algorithm/aot_py/native_memory_control.h:46-56`
  membuka/menutup `extern "C"` pada deklarasi tiga fungsi; deklarasinya berada
  di baris 49, 50, dan 53-54.
- `taichi_vision/taichi_algorithm/aot_py/taichi_aot_engine.cpp:17` memasukkan
  header tersebut. Definisi berada di global scope pada baris 2054,
  2112, dan 2135-2136. Makro Windows `EXPORT` didefinisikan sebagai
  `__declspec(dllexport)` pada baris 28; makro itu tidak menyatakan language
  linkage. Tidak ada `extern "C"` yang membungkus definisi-definisi tersebut.
- Output Builder melaporkan MSVC C2375 `redefinition; different linkage` pada
  tiga pasangan lokasi tersebut: `taichi_aot_engine.cpp:2054` vs header:49,
  `:2112` vs header:50, dan `:2135` vs header:53. Diagnosis konsisten dengan
  deklarasi/definisi yang dibaca. Nama fungsi juga merupakan nama C yang
  diambil langsung oleh binding native-memory Python; bentuk C linkage pada
  definisi sesuai kontrak header. Tidak ada dasar untuk mengubah signature,
  layout ABI struct, API Python, atau implementasi memory policy.
- Rehash Inspector: `taichi_aot_engine.cpp`
  `BABA48AF5DC79BF17BEDA669C85BE45421E60A30993690CAB22225BACA024F14`,
  `native_memory_control.h`
  `9775DB46C1880DA86D472B47783ECB94829A615CE3453960CEBE9376177BC116`, dan
  `build_engine_msvc.bat`
  `CDCFAB019B42CFA173C378A23DFDCB2526E8B7128E70D98525A48CCC806597B4`.

## Perintah build dan staging

- Handoff mencatat satu command:
  `PIXEL_REFINE_BRIDGE_OUTPUT_DIR=D:\temp\pixel_refine_dev4_runtime_qualification_20261025_7ab5e244\bridge\cpu`,
  `PIXEL_REFINE_BRIDGE_ISA=baseline`, `PIXEL_REFINE_BRIDGE_CRT=MT`, lalu
  `build_engine_msvc.bat cpu baseline`.
- Source `build_engine_msvc.bat:25-42` menetapkan output default ke tree CPU,
  kemudian override ke `PIXEL_REFINE_BRIDGE_OUTPUT_DIR` bila variabel tersedia.
  Compiler dipanggil pada baris 121-128; penyalinan `taichi_c_api.dll` ke
  output hanya terjadi setelah `cl.exe` sukses pada baris 130-136. Handoff
  melaporkan compile berhenti pada tiga C2375 sebelum DLL/link/copy.
- Pemeriksaan filesystem read-only Inspector menemukan scratch root ada dan
  `bridge\cpu` ada tetapi kosong. Tidak ada DLL hasil pada staging tersebut.
  Tidak ada build ulang, load, atau pemanggilan compiler oleh Inspector.

## Pemeriksaan tidak ada mutasi artefak aktif

- Status Git saat review hanya menunjukkan file pengguna `ops_matrix.json` dan
  `taichi_vision/taichi_aot/neural_universal/` sebagai untracked; tidak ada
  perubahan tracked di source, bridge, atau TCM yang dilaporkan. Handoff
  menyatakan status sebelum/sesudah juga tidak berubah.
- Rehash Inspector bridge production: CPU
  `CEA5B53BE236F1D6BAB30DBC2A540B650889119B91EA582C44406BFF85FED270`, CUDA
  `6127AA2F4DA5ACF4B7C372C3DA88C4AF21A294E719263AF109D9628B6B38A493`, OpenGL
  `914B6ED4D6F7E20AB01B0ECE42186252210E85EF879C0D16CF94985A3A76B2EE`, Vulkan
  `6DAD0D648D250A76EF1E8676035DCE1AB783F29E0E1C672B308B0F1518A6CAD4`.
- Keempat packaged C API saling identik, masing-masing 51,319,808 byte dengan
  SHA-256 `73190273F18B658762FAFD98B62C11CEE349A96564D211A919AA137D689F6C73`.
  C API venv Dev4 tetap 51,376,128 byte dengan hash
  `B29073835F7496B5A08307ADF7C088651FC17A14BF469C46319D3C50F213CBCF`.
  Manifest aktif tetap SHA-256
  `485A813D70768435D78C0B596EE874D2577516C7DDB2C102AE7ED68B1C2323E3`.
  Nilai Inspector cocok dengan hash handoff. Hash berbeda antar C API tetap
  fakta perbedaan byte; ini bukan bukti sendiri bahwa ABI inkompatibel.
- Command yang dicatat membangun bridge CPU ke output override, tidak memanggil
  compiler TCM. Builder melaporkan tidak ada TCM yang dibuat/dibaca/dimuat.
  Tidak ada bukti perubahan DLL/TCM produksi atau venv.

## Batas bukti dan langkah aman berikutnya

- Ini inspeksi source/header dan rekonsiliasi dengan diagnostik build Builder,
  bukan reproduksi error oleh Inspector. MSVC command output yang tersedia
  cukup untuk menemukan linkage mismatch, tetapi satu compile failure tidak
  membuktikan bahwa C linkage adalah satu-satunya blocker selanjutnya.
- Inventaris PE sebelumnya membuktikan machine AMD64 dan closure nama import
  untuk simbol yang diperiksa, bukan signature ABI seluruh C API. Tidak ada
  DLL dimuat. Tidak ada hasil `.tcm`, backend/device, shape/dtype, parity,
  performa, atau aplikasi.
- Iterasi berikutnya yang aman: Builder menambahkan C linkage hanya pada tiga
  definisi ini tanpa mengubah signature/layout; tinjau delta dan jalankan
  `git diff --check`; lalu build ulang `cpu baseline` dengan root scratch baru
  yang unik di luar repo. Jika gagal, laporkan error baru tanpa mencoba target
  GPU atau mengubah artefak aktif. Jika berhasil, verifikasi hash/output dan
  import/export/dependency statis dari pasangan bridge + C API staging sebelum
  meminta review gate load/runtime. Jangan lanjut ke TCM/load hanya berdasar
  hilangnya C2375.
