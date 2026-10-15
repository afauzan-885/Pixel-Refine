# Inspector Feedback — Iterasi 1, Fase 0

## Verdict

**BLOCKED — gate penerimaan pertama belum terpenuhi.** Goal meminta source dan baseline yang cocok. PRD Fase 0 mensyaratkan core fork dibangun dari source commit yang sama, harness menghasilkan laporan reproduktif, dan baseline tersedia untuk CPU, CUDA, Vulkan, OpenGL Intel, serta OpenGL NVIDIA sebelum fase dapat ditutup ([PRD, §15](../../ai_governance/TAICHI_FORK_NEURAL_RUNTIME_PRD_20261016.md#15-rencana-fase-dan-gate-berurutan)).

Tidak ada bukti source-matched build atau baseline tersebut dalam status dan handoff. Builder melaporkan tidak menjalankan build maupun tes; status runtime core yang dirujuk masih `unknown`. Pemeriksaan independen tidak menjalankan build atau tes.

## Bukti yang diperiksa

- Goal: [goal.md](./goal.md). Status sebelum review: `inspecting`; Builder menyatakan BLOCKED di Fase 0. Handoff yang dibaca: [Builder](../../ai_governance/TAICHI_FORK_GOAL_BUILDER_HANDOFF_20261016.md) dan [Explore](../../ai_governance/TAICHI_FORK_GOAL_EXPLORE_HANDOFF_20261016.md).
- `Pixel-Refine`: branch `main`, HEAD `7bde21c30b4f572475373089b76e3a532267e954`; `git status --porcelain=v1 --untracked-files=normal` menunjukkan 597 entri (442 modified, 88 deleted, 67 untracked).
- `fork_taichi`: branch `main`, HEAD `92bfb3ab88805872faa727a6521a3da8c37c2039`; status menunjukkan 419 entri (319 modified, 4 deleted, 96 untracked). Git juga mengeluarkan warning akses ditolak untuk `.pytest_cache/`; warning bukan entri status tambahan.
- `cl.exe`, `vswhere.exe`, dan variabel `VCToolsInstallDir`, `VSINSTALLDIR`, `WindowsSdkDir` tidak ditemukan pada probe PATH/environment. Direktori Visual Studio dan Windows Kits standar di `C:\Program Files`/`C:\Program Files (x86)` serta registry discovery key yang diperiksa tidak ada.
- Payload SDK hasil ekstraksi tersedia di `E:\APP Developer\Eel-Dance\builder-tools\windows-sdk-10.0.26100\extracted\Windows Kits\10`. Di sana terdapat `Include\10.0.26100.0\um\Windows.h`, `Include\10.0.26100.0\ucrt\corecrt.h`, `Lib\10.0.26100.0\um\x64\kernel32.Lib`, dan `Lib\10.0.26100.0\ucrt\x64\ucrt.lib`. Jadi SDK ada sebagai ekstraksi, walau tidak terdaftar pada path/registry standar yang diperiksa.
- `builder-tools\msvc-build-tools` hanya berisi `vs_BuildTools.exe` berukuran 4.478.032 byte. Ekstraksi LLVM 20.1.5 menyediakan `clang-cl.exe`, `lld-link.exe`, `llvm-rc.exe`, dan `llvm-mt.exe`, tetapi pemeriksaan pada payload tersebut tidak menemukan `cl.exe`, `VsDevCmd.bat`, `vcruntime.h`, `msvcprt.lib`, `libcmt.lib`, `libvcruntime.lib`, atau `msvcp140.lib`.
- Handoff Builder mencatat Python 3.12.9 dan core Taichi terpasang dengan commit `unknown`; provenance wheel yang tersedia tidak mengikat core ke source HEAD fork saat ini. Handoff juga menyatakan model metadata/graph belum dikunci dan baseline source-matched belum tersedia.

## Cakupan dan batas bukti

Review ini hanya memutuskan gate Fase 0 dan membaca status/handoff serta lokasi toolchain relevan. Tidak ada file source, artefak, konfigurasi, atau environment global yang diubah; tidak ada build, tes, backend probe, benchmark, instalasi, staging, atau commit yang dijalankan sebelum pembuatan catatan Inspector ini.

Pemeriksaan toolchain mencakup PATH/environment, lokasi instalasi standar dan registry Windows yang disebut, folder installer, ekstraksi LLVM, serta ekstraksi SDK di `builder-tools`. Ini tidak membuktikan bahwa tidak ada alternatif compiler di seluruh volume host. SDK hasil ekstraksi dapat dipakai setelah dikonfigurasi, tetapi keberadaannya sendiri tidak membuktikan build source-matched atau menyediakan runtime C++ MSVC yang tidak ditemukan pada lokasi tersebut.

## Risiko

- Menggunakan wheel/core lama sebagai baseline dapat mencampur source, ABI, atau binary yang tidak cocok dengan fork HEAD dan menghasilkan bukti Phase 0 yang tidak valid.
- SDK tidak terdaftar pada lokasi standar yang diperiksa; skrip build yang bergantung pada discovery standar mungkin tidak menemukannya tanpa konfigurasi terverifikasi.
- Toolchain alternatif non-standar mungkin ada, tetapi belum ada inventory, command build, provenance, atau hasil yang membuktikan kelayakannya.

## Tindakan berikutnya

Sediakan toolchain C++ MSVC lengkap yang sesuai atau alternatif source-build yang terdokumentasi dan dapat diverifikasi; konfigurasi SDK 10.0.26100 untuk toolchain tersebut; bekukan manifest source/toolchain/model; lalu bangun core dari fork HEAD yang sama dan jalankan harness Phase 0. Catat source/core provenance serta laporan reproduktif dan baseline terpisah untuk semua target wajib. Inspector perlu menilai ulang gate Fase 0 setelah bukti tersebut tersedia; jangan mulai fase berikutnya sebelum gate lulus.
