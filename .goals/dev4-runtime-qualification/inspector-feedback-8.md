# Inspector feedback 8 — Runtime Qualification Minimal Linkage Reproducer

Tanggal: 2026-10-25 (Asia/Jakarta)
Checkpoint: Builder handoff 8, product source patch tetap uncommitted
Model Inspector: GPT-6 (fallback; dedicated Goal Inspector model tidak tersedia)
Verdict: **PASS_FOR_MINIMAL_REPRO_EVIDENCE_ONLY**

## Hasil inspeksi

Reproducer di scratch iterasi 8 benar-benar memuat Pixel
`native_memory_control.h`, membuka outer `extern "C"` block, lalu mendefinisikan
ketiga fungsi memakai signature header, prefix per-fungsi
`extern "C" __declspec(dllexport)`, dan body `return 0`. Saya membaca file
`.cpp` dan log aktual. Tiga signature cocok dengan deklarasi header di baris
49, 50, dan 53-54.

`cl.exe /Tp ... /c /Fo...` mengembalikan exit 2 dengan C2375 untuk ketiga nama;
setiap diagnostic dipasangkan dengan deklarasi Pixel header yang benar. `/Tp`
membuat file `.cpp` semantic C++; `/c` meniadakan link. Scratch berisi hanya
file reproducer 466 byte dan log 2,220 byte; tidak ada `.obj`. Hasil ini
mengisolasi error ke bentuk minimal header + definisi/export/linkage tersebut,
tanpa body engine, Taichi API, library C API, atau link. Ini bukan salah
extension seperti iterasi 6 dan bukan sekadar hasil preprocessing.

## Apa yang belum terisolasi

Reproducer ini menguji **bentuk current dengan kedua level**: outer
`extern "C"` block dan inner per-function `extern "C"` prefix. Karena kedua
bentuk muncul bersamaan, hasilnya belum membuktikan apakah C2375 dipicu oleh
inner prefix redundant, oleh outer-block-only definition sebagaimana source
asli sebelum patch, atau oleh kombinasi declaration/export/header di MSVC.
Karena itu tidak ada source correction yang dibenarkan oleh hasil ini.

Hash source/header, production CPU bridge/C API, venv C API, dan manifest yang
dilaporkan Builder tetap cocok dengan baseline. Saat pemeriksaan, Git status
menunjukkan Builder source patch; untracked `ops_matrix.json`,
`taichi_vision/taichi_aot/neural_universal/`, dan dua file test neural universal
yang baru tampak pada status (`test_neural_universal_kernels.py`,
`test_neural_universal_registry.py`). Tidak ada path tersebut diubah atau
di-stage oleh Inspector. Scratch reproducer tidak menghasilkan object, link,
DLL, atau TCM; tidak ada DLL load, runtime, atau parity.

## Next step yang paling kecil

Jika coordinator memilih melanjutkan, lakukan **satu** bounded differential
semantic compile ke scratch baru untuk bentuk original tanpa prefix per-fungsi:

```cpp
#include "native_memory_control.h"
extern "C" {
__declspec(dllexport) int ti_aot_get_memory_snapshot(void *runtime, TiAotMemorySnapshotV1 *output) { return 0; }
__declspec(dllexport) int ti_aot_set_memory_limits(void *runtime, const TiAotMemoryLimitsV1 *limits) { return 0; }
__declspec(dllexport) int ti_aot_trim_memory_cache(void *runtime, uint64_t target_bytes, uint64_t target_entries, TiAotMemoryTrimV1 *output) { return 0; }
}
```

- File reproducer sementara berada **di scratch saja** dan memakai include
  path ke Pixel `aot_py` agar tetap memilih header yang sama. Jangan mengubah
  product source/header.
- Gunakan compiler MSVC/path/hash yang sama dengan satu invocation langsung
  berbentuk `& $cl /nologo /Tp $repro /c "/Fo$object" /EHsc /std:c++20 /MT /arch:SSE2 "/I$headerDir"`.
  Isi `$repro`, `$object`, dan `$headerDir` dengan path scratch baru dan
  direktori `taichi_vision\taichi_algorithm\aot_py` Pixel yang dikutip.
  Kosongkan `CL`; jangan sertakan `/O2`, `/GL`, `PIXEL_REFINE_*` defines,
  `/LD`, `/link`, library input, DLL copy, atau TCM command.
- Satu-satunya keluaran yang diizinkan: `.obj` dan log di scratch. Catat hash
  repro/header, command, exit, diagnostic, dan object hash bila sukses. Stop
  setelah satu invocation; apa pun hasilnya, tidak ada retry, full bridge build,
  DLL load, atau TCM compile sebelum Inspector review.
- Jika outer-block-only variant lulus, itu hanya membuktikan bentuk minimal
  original header/linkage dapat dikompilasi; belum membuktikan per-function
  prefix adalah satu-satunya penyebab build lama. Jangan revert patch tanpa
  review. Jika gagal, tetap tidak ada dasar mengubah header/ABI; kirim diagnostic
  lengkap untuk review berikutnya.

Satu invocation tambahan ini memerlukan **bounded approval baru dari
coordinator** karena invocation minimal iterasi 8 sudah digunakan. Otorisasi
goal `compilation_allowed=true` tetap berlaku secara umum, tetapi tidak
memperpanjang batas satu invocation pada checkpoint sebelumnya.

## Batas review

Saya membaca goal/status/memory, Inspector feedback 7, handoff Builder 8,
command audit, reproducer scratch, log, header, source diff, dan status Git.
Saya tidak menjalankan compiler/test, tidak memuat DLL/TCM, tidak mengubah
source/status, dan tidak mengubah artefak production/venv.
