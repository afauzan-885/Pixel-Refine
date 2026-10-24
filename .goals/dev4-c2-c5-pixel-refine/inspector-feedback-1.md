# Inspector feedback 1 — C2/C5 Dev4 Pixel Refine

Tanggal: 2026-10-25 (Asia/Jakarta)
Commit yang diperiksa: `7511e4ba23c8973fe23fd6ccd8de148358e84616`
Model Inspector: GPT-6 (fallback; role Goal Inspector tidak tersedia)
Verdict iterasi: **FAIL — perlu revisi source C2 dan bukti/tes C5**

## Ringkasan

Perubahan dua file C2 memperketat parsing payload worker dan mempertahankan
compiler-internal phases sebagai `null`. Namun acceptance C2 belum terpenuhi:
test baru hanya memeriksa parser/schema, bukan wiring timing dengan fake clock,
dan satu deskripsi boundary tidak cocok dengan timer saat native OpenGL context
opt-in. C5 telah memiliki shared registry dan beberapa guard fail-closed, tetapi
belum ada validasi yang mengikat manifest, selector CLI, resolver, dan layout
artefak menjadi satu konsistensi; inventaris terkini juga menunjukkan layout
legacy/target yang tidak selaras. Hasil ini source-level saja dan tidak
mengualifikasi runtime.

## Kriteria

### C2 — FAIL (parsial)

- Source yang berubah hanya `taichi_vision/taichi_algorithm/aot_py/compile_aot_backend_suite.py`
  (SHA-256 `E1E55E87320A4D548B9B2A36762EBC786C821FD549DCAB29DD688C904B3CEA65`) dan
  `taichi_vision/taichi_algorithm/aot_py/tests/test_compile_pipeline_contracts.py`
  (SHA-256 `1C3C9990BA66CC15F8E6047697735BFA1AE42111FE75A1CD901B3E9209820531`).
- `_worker_metrics` kini memeriksa schema/unit, definisi boundary/reason, nama
  phase yang tepat, nilai finite non-negative, required values, object inventory,
  dan mewajibkan internal compiler phases bernilai `null`. Tiga test tambahan
  menguji unknown tetap null dan penolakan payload malformed/schema-unit salah.
  Builder melaporkan command direct-file suite dengan venv `-B` menghasilkan
  **15 passed**; saya tidak mengulang kategori validasi yang sudah dilaporkan.
- Gap acceptance: test yang ditambahkan tidak menggunakan fake clock dan tidak
  membuktikan wiring nilai timer dari worker ke parser/report. Pada source,
  `phase_started` dimulai sebelum optional import `taichi_vision.taichi_aot`
  ketika `PIXEL_REFINE_AOT_NATIVE_CONTEXT=1`; lalu `compiler_module_import_seconds`
  dihitung sebagai elapsed sejak `phase_started` dikurangi hanya durasi import
  `taichi`. Karena itu metadata yang menyebut fase “time after the Taichi import
  through compiler module import completion” tidak tepat pada mode opt-in:
  import native-context ikut dihitung. Sesuaikan boundary atau pecahkan timer,
  kemudian tambahkan fake-clock/wiring test murni.
- Validasi yang tersedia membuktikan kontrak parser source, bukan akurasi timer
  compiler internal atau runtime compile. Fase internal yang tidak diekspos API
  tetap unknown/null, sesuai batas bukti.

### C5 — FAIL (struktur source konsisten, acceptance gabungan belum dibuktikan)

- `target_registry.py` membangun `SUPPORTED_TARGETS` dan `TARGET_BACKENDS` dari
  `target_manifest.json`; `compile_aot_backend_suite.py` dan
  `background_compile.py` mengonsumsi registry bersama. Selector compiler
  menerima ID target dari mapping itu, dan `target_runtime_report` fail-closed
  saat requirement/evidence kualifikasi native hilang. Test terkait sudah ada
  pada `test_target_registry.py`, `test_release_bundle_manifest.py`, dan
  `test_compile_pipeline_contracts.py`.
- Namun tidak ditemukan test yang memeriksa satu set target manifest sekaligus
  terhadap pilihan selector kedua CLI, resolver/runtime requirement, dan
  `target_artifact_report`/layout filesystem. Test compiler-contract saat ini
  hanya memeriksa keberadaan tiga ARM ID di registry. Tambahkan pure test
  konsistensi lintas komponen, termasuk target yang tak punya profile lengkap.
- `target_manifest.json` saat ini mendeklarasikan 7 target dan tidak memiliki
  `runtime_requirements`. Dengan demikian keberadaan target/TCM bukan bukti
  kualifikasi; status harus tetap unverified. Dari pemeriksaan folder langsung,
  folder kanonik ARM `cpu_arm64_android`, `cpu_arm64_linux`, dan
  `vulkan_arm64_android` tidak ada. Ada direktori tidak dideklarasikan
  `vulkan_desktop`, direktori `cuda_x86_64_windows` di luar ID kanonik dengan
  vendor NVIDIA, serta 36 file TCM di root.
- Pemeriksaan nama/path saja menunjukkan 382 file `.tcm` total: root 36;
  jumlah rekursif per folder `cpu_x86_64_windows` 86;
  `cuda_x86_64_windows` 6; `cuda_x86_64_windows_nvidia` 87;
  `opengl_x86_64_windows` 81; `vulkan_desktop` 2;
  `vulkan_x86_64_windows` 84. Angka ini cocok dengan handoff Builder; 16 file
  berada di empat subfolder `application_assets` (masing-masing 4). Hitungan
  file tepat di folder target tanpa subfolder masing-masing 82, 6, 83, 77, 2,
  dan 80. Tidak ada payload `.tcm` yang dibuka.

### Dev4 provenance DLL/bridge — PASS untuk inventaris statis terbatas

- Pemeriksaan ulang `Get-FileHash -Algorithm SHA256` menemukan C API venv
  `venv/Lib/site-packages/taichi/_lib/c_api/bin/taichi_c_api.dll` sebesar
  51,376,128 byte dengan SHA-256
  `B29073835F7496B5A08307ADF7C088651FC17A14BF469C46319D3C50F213CBCF`.
- C API yang dibundel di `taichi_vision/taichi_algorithm/aot_py/aot_dll/{cpu,cuda,opengl,vulkan}/taichi_c_api.dll`
  berukuran 51,319,808 byte dan hash sama pada keempat salinan:
  `73190273F18B658762FAFD98B62C11CEE349A96564D211A919AA137D689F6C73`.
  Hash berbeda menunjukkan bytes berbeda saja; bukan bukti ABI inkompatibel.
- Pembacaan PE header tanpa load menghasilkan signature `0x00004550` dan
  machine `0x8664` (AMD64) untuk DLL venv, C API bundled CPU, dan bridge CPU.
  Bridge hashes CPU/CUDA/OpenGL/Vulkan masing-masing dicatat di handoff Builder
  dan cocok dengan hasil penghitungan ulang untuk semua empat bridge. Wheel
  `1.7.4.dev4` dan hash wheel yang dirujuk di handoff tidak dihitung ulang pada
  review ini; catat sebagai bukti Builder, bukan pengukuran Inspector.
- `dumpbin`, `llvm-readobj`, dan `llvm-objdump` tidak tersedia menurut handoff;
  exports/imports/dependencies karenanya tetap unknown. Tidak ada DLL yang
  dimuat, disalin, diganti, atau dipromosikan. Tidak ada kesimpulan runtime ABI.

### Audit C++ backend — PASS untuk audit statis, optimisasi deferred

- Source bridge bersama `taichi_vision/taichi_algorithm/aot_py/taichi_aot_engine.cpp`
  hash SHA-256 `BABA48AF5DC79BF17BEDA669C85BE45421E60A30993690CAB22225BACA024F14`.
  Search source menunjukkan satu engine bersama dengan `ti::Runtime`,
  `ti::AotModule`, `ti::ComputeGraph`, graph launch, dan pengelolaan buffer;
  tidak ditemukan satu source C++ terpisah per backend.
- Audit statis Builder membedakan jalur CPU/CUDA/Vulkan/GLES yang berbagi
  runtime engine dengan jalur Windows OpenGL native ICD/EGL yang memiliki
  context/device selection khusus. Risiko ownership/lifecycle, ABI, sync, dan
  thread/context affinity layak dicatat; logical byte accounting tidak sama
  dengan telemetry VRAM. Belum ada dasar yang dapat dinilai untuk optimisasi
  C++ terhadap Dev4 tanpa kontrak API/ABI dan gate compile/runtime yang diizinkan.
- Handoff mencantumkan rekomendasi slice lanjutan dan hash source. Pemeriksaan
  ini tidak menjalankan compiler, build, native/device, atau DLL load.

### `.tcm` — PASS untuk file inventory saja; runtime gate tetap pending

- File `.tcm` hanya dihitung menurut nama/path di atas. Payload metadata,
  archive structure, graph, loadability, device execution, dan parity tidak
  diperiksa. Batas ini sesuai `compilation_allowed=false`.

### Scope dan kebersihan — PASS

- Commit Builder hanya mengubah dua file C2 yang disebut di atas. Working tree
  masih memuat perubahan pengguna: dua file desktop Python, `ops_matrix.json`,
  dan `taichi_vision/taichi_aot/neural_universal/`; tidak ada yang diubah atau
  di-stage dalam review ini.
- Tidak ada klaim speedup, compatibility runtime, parity, atau readiness yang
  didukung oleh hasil ini.

## Perintah dan batas validasi Inspector

- `git show --format=fuller --stat 7511e4ba` dan
  `git diff 7511e4ba^ 7511e4ba -- <dua path C2>`: memeriksa commit/diff.
- `Get-FileHash <DLL/source> -Algorithm SHA256`; pembacaan byte PE dengan
  PowerShell `ReadAllBytes`/`BitConverter`; `Get-ChildItem ... -Filter '*.tcm'`:
  hash, arsitektur PE dan jumlah path, tanpa load binary/TCM.
- `rg -n` pada source registry, selector, resolver dan C++ bridge serta review
  test file: inspeksi statis saja.
- Tidak menjalankan test tambahan, compile/build/JIT/`py_compile`, syntax-only,
  load DLL/TCM, native/device, parity, benchmark, atau aplikasi.

## Next action Builder

1. Koreksi definisi/pengukuran `compiler_module_import_seconds` agar tepat saat
   `PIXEL_REFINE_AOT_NATIVE_CONTEXT=1`, tambahkan fake-clock test untuk boundary
   dan wiring tanpa menginisialisasi Taichi.
2. Tambahkan pure consistency coverage manifest → compiler/background CLI
   selectors → runtime/artifact resolver/layout, asserting unsupported/missing
   profile tetap fail-closed/unverified.
3. Perbarui handoff inventaris dengan hitungan direktori terkini dan bedakan
   fakta Builder yang terukur dari fakta Inspector yang diulang.
4. Pertahankan no-compile/no-load; runtime `.tcm`, ABI, backend, parity, dan
   performa tetap belum terkualifikasi.
