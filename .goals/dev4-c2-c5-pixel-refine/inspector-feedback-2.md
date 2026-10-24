# Inspector feedback 2 — C2/C5 Dev4 Pixel Refine

Tanggal: 2026-10-25 (Asia/Jakarta)
Commit Builder: `a99b227f4f2cc361351cfada5cdafe498eaa74be`
Parent: `aa56c810eb4fbcc204161b1a053e23c44251bdb1`
Model Inspector: GPT-6 (fallback; dedicated Goal Inspector model tidak tersedia)
Verdict iterasi: **FAIL — finding iterasi 1 tertangani; satu celah canonical target identity tersisa**

## Cakupan dan ringkasan

Saya meninjau perubahan lima file pada commit `a99b227f` terhadap Builder
checkpoint `7511e4ba`, dengan mengabaikan feedback Inspector yang berada di
antara dua checkpoint tersebut. Commit Builder menyentuh compiler metrics,
dua selector, target registry, runtime artifact manifest loader, dan pure
contract tests; tidak menyentuh engine source of truth, C++, manifest aktif,
DLL/TCM, atau file pengguna.

Dua finding iterasi 1 telah ditangani pada source dan tests. Namun konsistensi
target belum berlaku untuk semua alias yang diterima runtime: registry builder
tidak mengkanonisasi alias OS/arsitektur yang runtime `TargetSpec` terima, dan
validator baru hanya mengecek nilai `unknown` alih-alih allowlist identitas.
Oleh karena itu acceptance gabungan C5 belum sepenuhnya aman.

## Kriteria

### C2 — PASS untuk source contract/fake-clock wiring

- Boundary import kini terpisah: `native_context_import_seconds` bernilai null
  bila opt-in tidak dipakai; `_measure_phase` membungkus import native-context,
  import Taichi, dan panggilan `importlib.import_module` masing-masing. Metadata
  menjelaskan hanya interval yang diukur, sehingga masalah interval bertumpuk
  dari iterasi 1 teratasi.
- `test_fake_clock_worker_phases_reach_serialized_compile_report` memberi durasi
  fake-clock 0.5/0.25/0.125 detik kepada helper measurement, mengalirkan nilai ke
  serializer, parser `_worker_metrics`, lalu report file dan memeriksa nilai
  akhir. Test tidak menginisialisasi Taichi. Batasnya: test memverifikasi helper
  dan jalur serialization/report, bukan durasi import/compiler proses nyata
  atau eksekusi `_run_worker`.
- Builder melaporkan direct-file pure suite **18/18** dan diff-check scoped
  berhasil. Saya tidak mengulang kategori tersebut. Tidak ada compile/JIT,
  `py_compile`, DLL/TCM load, native/device execution, parity, atau benchmark.
- Kesimpulan C2 hanya mengenai source-level contract dan fake-clock wiring; fase
  internal compiler tetap unknown/null dan bukan hasil ukur Dev4.

### C5 — FAIL (cakupan aktif membaik, alias registry/runtime masih divergen)

- Test `test_target_manifest_selectors_resolver_layout_and_unqualified_gate_agree`
  membaca manifest aktif, membandingkan IDs dengan build registry dan kedua
  fungsi selector CLI, membentuk runtime `TargetSpec`, menyelesaikan fixture
  archive sintetis untuk tiap target, memeriksa artifact layout report, lalu
  memastikan target tanpa runtime evidence tetap `unverified`/fail-closed.
  Test `test_incomplete_target_identity_is_rejected_by_registry_and_resolver`
  membuktikan manifest loader dan runtime report menolak field `arch` yang
  hilang. Ini menutup gap test gabungan iterasi 1 untuk tujuh target manifest
  saat ini.
- Celah yang tersisa ada pada canonicalisasi umum. Di
  `target_registry.py`, `_OS_ALIASES` tidak memiliki alias runtime `darwin` →
  `macos` dan `_ARCH_ALIASES` tidak memiliki alias runtime `i686`/`i386` →
  `x86`; `validate_target_identity` hanya menolak string kosong/`unknown` dan
  menerima token OS/arsitektur lain. Sebaliknya,
  `artifact_targets.py::canonical_os` dan `canonical_arch` menerima alias itu.
  Karena compiler/build selectors mengambil ID dari registry, manifest valid
  secara field seperti `{"backend":"cpu","arch":"i686","os":"darwin"}`
  dapat menghasilkan `cpu_i686_darwin` di registry/CLI sedangkan `TargetSpec`
  runtime menghasilkan `cpu_x86_macos`. Resolver kemudian mencari nama lain.
  Ini melanggar konsistensi manifest → selector → runtime resolver untuk
  identitas yang tidak ada pada manifest aktif saat ini. Samakan alias
  canonicalizer atau tolak OS/arch di luar allowlist bersama, dan tambahkan
  pure test perbandingan lintas kedua jalur.
- Test fixture menunjukkan kesesuaian untuk manifest aktif saja; target list
  filesystem produksi yang legacy/missing dari review iterasi 1 tetap belum
  direnamai atau dikualifikasi. Fixture sintetis bukan bukti bahwa layout
  produksi sudah konsisten.
- Ketiadaan `runtime_requirements` pada manifest aktif tetap menghasilkan
  `native_runtime_count=0` dan semua target unverified. Tidak ada klaim backend
  qualified yang dibuat.

### Scope, bukti runtime, dan batas

- `git show --stat a99b227f` menunjukkan tepat lima file source/test: `background_compile.py`,
  `compile_aot_backend_suite.py`, `target_registry.py`,
  `tests/test_compile_pipeline_contracts.py`, dan `taichi_aot/artifact_targets.py`.
  Seluruhnya berada di scope goal; tidak ada perubahan engine/C++/binary.
- Perubahan pengguna tetap tampak di status checkout pada dua file desktop,
  `ops_matrix.json`, dan direktori `taichi_aot/neural_universal/`; saya tidak
  mengubah atau stage path tersebut.
- Inventaris DLL, bridge, TCM, dan audit C++ dari iterasi 1 tidak diubah oleh
  commit ini. Hash berbeda tetap bukan bukti inkompatibilitas; tidak ada DLL
  yang dimuat dan tidak ada payload TCM produksi yang dibuka.
- Bukti ini tidak mengualifikasi ABI/runtime, backend/device, parity, performa,
  atau readiness aplikasi. Tes C5 hanya memakai target manifest aktif dan
  arsip sintetis di temp directory.

## Bukti yang ditinjau

- `git show --stat --format=fuller a99b227f` serta diff lima file terhadap
  `7511e4ba`; commit parent teramati adalah `aa56c810`.
- Source interval C2: `compile_aot_backend_suite.py` pada deklarasi boundary,
  `_measure_phase`, dan `_run_worker` import setup.
- Source canonical target: `target_registry.py` alias/identity validation;
  `artifact_targets.py` canonical OS/arch, `TargetSpec`, dan resolver.
- Pure tests pada `test_compile_pipeline_contracts.py` (test fake-clock,
  gabungan selector/resolver/layout, incomplete identity).
- Builder melaporkan command
  `venv\Scripts\python.exe -B taichi_vision\taichi_algorithm\aot_py\tests\test_compile_pipeline_contracts.py`
  → 18 passed dan scoped `git diff --check` exit 0; hasil tersebut tidak
  dijalankan ulang.

## Tindak lanjut

Samakan atau batasi canonical OS/arsitektur pada registry build dan runtime,
lalu tambahkan pure test untuk alias `darwin` dan `i686`/`i386` agar ID yang
ditawarkan CLI pasti sama dengan `TargetSpec.target_id` dan artifact resolver.
Pertahankan batas no-compile/no-load.
