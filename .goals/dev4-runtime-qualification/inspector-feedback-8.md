# Inspector feedback 8 — Minimal Linkage Reproducer

Tanggal: 2026-10-25 (Asia/Jakarta)
Checkpoint: Builder handoff 8; source patch tetap uncommitted
Model: GPT-6 (fallback; Goal Inspector khusus tidak tersedia)
Verdict: **PASS_FOR_DIAGNOSTIC_EVIDENCE_ONLY**

## Hasil

Reproducer scratch meng-include Pixel `native_memory_control.h` dan
mendefinisikan ketiga API dengan signature yang cocok, outer `extern "C"`,
prefix `extern "C" __declspec(dllexport)` per fungsi, dan body `return 0`.
MSVC `/Tp /c` keluar 2 dengan tiga C2375 yang menunjuk ke definisi reproducer
dan prototype header yang tepat. Log aktual serta `.cpp` cocok dengan handoff;
scratch hanya berisi `.cpp` 466 byte dan log 2,220 byte, tanpa `.obj`.

Ini mempersempit error ke reproduksi minimal header/declarations/definitions/
linkage/export: body engine, Taichi API, library C API, dan linker tidak
diperlukan untuk memunculkan C2375. Namun reproducer menggabungkan **outer C
block, prefix C per fungsi, dan `dllexport`**, sehingga belum membuktikan
komponen mana yang memicu diagnostic. Tidak ada source patch yang didukung.

Hash Inspector cocok dengan handoff: source
`97833F7377074482B48A9DB82835700BC2A22C38982F435025E6919D3C8A429D`, header
`9775DB46C1880DA86D472B47783ECB94829A615CE3453960CEBE9376177BC116`, production
CPU bridge `CEA5B53BE236F1D6BAB30DBC2A540B650889119B91EA582C44406BFF85FED270`,
CPU C API `73190273F18B658762FAFD98B62C11CEE349A96564D211A919AA137D689F6C73`,
venv C API `B29073835F7496B5A08307ADF7C088651FC17A14BF469C46319D3C50F213CBCF`,
manifest `485A813D70768435D78C0B596EE874D2577516C7DDB2C102AE7ED68B1C2323E3`.
Status masih menunjukkan patch Builder dan user-owned/untracked files; Inspector
tidak mengubah source/status. Tidak ada link, DLL/TCM, load, runtime, atau parity.

## Differential diagnostic berikutnya

Jika coordinator melanjutkan, minta **approval bounded baru** untuk tepat satu
semantic compile di scratch baru, karena invocation iterasi 8 sudah digunakan.
Gunakan reproducer satu-varian: include header Pixel yang sama; pertahankan
outer `extern "C"` block dan `__declspec(dllexport)` pada ketiga definisi;
hapus hanya prefix `extern "C"` per fungsi. Jalankan MSVC yang sama dengan
`/Tp /c`, `/Fo` ke `.obj` scratch, opsi dasar `/EHsc /std:c++20 /MT /arch:SSE2`,
include path ke `aot_py`, dan `CL` kosong. Jangan sertakan `/O2`, `/GL`, defines,
`/LD`, `/link`, library, DLL copy, atau TCM.

- Jika variant ini lulus, itu mengisolasi prefix per-fungsi pada **reproducer
  minimal**; belum membenarkan edit production source karena C2375 pernah muncul
  pada build baseline penuh. Hentikan dan minta review sebelum patch.
- Jika tetap gagal, belum ada dasar mengubah ABI/header; hentikan. Variant kedua
  yang mengubah `dllexport` memerlukan approval terpisah dan review atas hasil
  variant pertama. Jangan mengubah dua faktor sekaligus atau menjalankan retry.

Hasil reproducer saat ini diterima sebagai bukti diagnostic saja; goal runtime
qualification tetap belum tercapai. Inspector tidak menjalankan compiler,
test, DLL/TCM load, atau mengubah source/status.
