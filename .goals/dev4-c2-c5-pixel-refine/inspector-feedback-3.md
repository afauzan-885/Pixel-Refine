# Inspector feedback 3 — C2/C5 Dev4 Pixel Refine

Tanggal: 2026-10-25 (Asia/Jakarta)
Commit Builder: `1caf81d3a5606fb2f826850a0efd0579fac4cd5f`
Parent Builder: `b7b13df3d7f4ca9986fe08a3cea82e1310b6ab02`
Model Inspector: GPT-6 (fallback; dedicated Goal Inspector model tidak tersedia)
Verdict iterasi: **PASS_SOURCE_ONLY — alias target yang diminta sudah konsisten**

## Cakupan

Delta commit Builder hanya `taichi_vision/taichi_algorithm/aot_py/target_registry.py`
dan `taichi_vision/taichi_algorithm/aot_py/tests/test_compile_pipeline_contracts.py`.
Tidak ada perubahan C2, target manifest aktif, runtime `engine.py`, C++, DLL,
TCM produksi, atau file pengguna. Commit parent `1caf81d3` adalah
`b7b13df3`.

## Hasil inspeksi

### Alias OS/arsitektur — PASS

- Registry kini mengkanonisasi `darwin` → `macos`, `i386`/`i686` → `x86`, dan
  `armv7l` → `armv7`, serta menghapus spasi arsitektur. Daftar alias dan
  normalisasi ini cocok dengan `artifact_targets.py::canonical_os` dan
  `canonical_arch` untuk alias yang ditangani perubahan ini. Alias yang sudah
  ada untuk `amd64`, `aarch64`, `arm64-v8a`, Android OpenGL→GLES, dan target
  aktif juga tetap dicakup oleh source/tests yang ada.
- Test baru `test_registry_and_cli_selectors_normalize_runtime_identity_aliases`
  menguji enam kombinasi backend CPU/Vulkan × alias `i386`, `i686`, dan
  `armv7l`, semuanya dengan OS `darwin`. Setiap fixture membandingkan ID dari
  registry terhadap `TargetSpec.target_id`, lalu memeriksa kedua selector CLI.
  Cabang Vulkan juga membuat archive SPIR-V sintetis, memeriksa hasil
  `resolve_artifact`, dan memastikan layout report tidak fail-closed.
- Test konsistensi sebelumnya masih membandingkan tujuh ID dari manifest aktif
  dengan registry, kedua selector, runtime `TargetSpec`, resolver/layout
  sintetis dan report qualification. Test incomplete identity tetap memeriksa
  penolakan OS/arsitektur wajib yang hilang. Dengan cakupan itu, dua finding
  C5 iterasi 2 terjawab pada level source/config yang diminta.

### Perubahan signature loader — PASS, terbatas pada helper privat

- `_load_target_backends` kini menerima `manifest_path` opsional, mengubahnya
  menjadi `Path`, dan tetap menggunakan `MANIFEST_PATH` sebagai default. Pada
  repo, pemanggil production tetap inisialisasi module-level
  `TARGET_BACKENDS = _load_target_backends()`; pemanggil kedua hanya test baru
  yang mengirim fixture path eksplisit. Tidak ada pemanggil lama yang berubah,
  dan parameter baru bersifat additive pada helper privat.
- Test alias memakai fixture manifest satu target untuk mengisolasi normalisasi
  dan tidak mengubah manifest aktif. Resolver/layout fixture memakai direktori
  temp. Ini bukan bukti bahwa alias macOS/ARMv7 sudah tersedia, mempunyai
  artefak, atau qualified di runtime Pixel Refine.

### Batas validasi

- Builder melaporkan direct-file pure test **19/19** dan scoped diff-check pass;
  saya tidak menjalankan ulang test maupun diff-check yang sudah dilaporkan.
- Tidak ada compile/build/JIT/`py_compile`, load DLL/TCM, native/device,
  parity, benchmark, atau aplikasi. `.tcm` dalam regression adalah fixture
  sintetis sementara.
- Kriteria C2 dari iterasi 2 tidak diubah oleh commit ini; penilaian source
  C2 dan fake-clock wiring tetap mengacu pada review sebelumnya, tanpa klaim
  pengukuran compiler internal.
- Target produksi yang belum punya layout/qualification dan provenance/runtime
  DLL/TCM tetap seperti yang dicatat pada feedback iterasi 1; PASS ini hanya
  mengesahkan scope source-level C2/C5 sesuai batas no-compile, bukan runtime,
  ABI, backend, parity, performa, atau readiness.

## Bukti yang ditinjau

- `git show --stat --format=fuller 1caf81d3` serta diff terhadap `a99b227f`;
  dua path produk di atas saja berubah pada commit Builder.
- Source canonicalizer: `target_registry.py` `_ARCH_ALIASES`, `_OS_ALIASES`,
  `_canonical_arch`, `_canonical_os`, dan `_load_target_backends`;
  `artifact_targets.py` `canonical_arch`, `canonical_os`, `TargetSpec`, dan
  `resolve_artifact`.
- Regression: `test_compile_pipeline_contracts.py` alias test (baris 221),
  manifest/selector/resolver/layout test (baris 161), dan incomplete identity
  test (baris 208).
- Handoff Builder 3 melaporkan command direct-file dengan venv `-B` → 19
  passed; tidak diulang oleh Inspector.
