# Pixel Refine AI Governance

Governance ini adalah sumber aturan portabel untuk Codex, DeepSeek, dan agent lain yang bekerja pada Pixel Refine. Area mobile Kotlin tidak termasuk scope Windows desktop kecuali diminta eksplisit.

## Urutan aturan

1. Instruksi platform dan pengguna.
2. AGENTS.md.
3. Dokumen dalam ai_governance/.
4. agen/arsitektur proyek yang relevan.
5. Source code, konfigurasi, dan bukti pengujian.

## Dokumen aktif

- GLOBAL_RULES.md: barrier teknis, evidence, penghapusan, dan Git.
- OPERATING_PROTOCOL.md: alur kerja inspeksi dan validasi.
- MULTI_AGENT_PROTOCOL.md: aturan delegasi agent.
- CURRENT_IMPLEMENTATION.md: snapshot status aktual dan bukti backend.
- LLVM20_MIGRATION.md: status migrasi desktop LLVM20.
- TCM_ABI_ROADMAP.md: kontrak ABI dan validator TCM.
- BLOCK_COMPUTE_95_ROADMAP.md: kontrak keselamatan block compute.
- CUDA_ARCHITECTURE_COVERAGE.md: batas bukti arsitektur CUDA.
- LEGACY_POLICY.md: kebijakan kompatibilitas dan artefak legacy.
- LIBRARY_KOTLIN_FIXES.md: laporan bug fixes dan test coverage LibraryKotlin.
- LIBRARY_KOTLIN_FEATURES.md: laporan penambahan fitur LibraryKotlin (50+ komponen baru).
- TAICHI_VISION_KOTLIN_MOBILE_INTEGRATION.md: Rencana detail arsitektur & roadmap integrasi Taichi Vision Native.
- PIPELINE_MIGRATION_AND_SR_HANDOFF.md: Handoff lintas-sesi untuk migrasi resident pipeline (`pipeline_process/`), generic streaming runtime/prefetch denoising dan Splat SR, kontrak ownership `BufferSession`, splat SR reliability, routing parameter FusionNet, serta alur AutoEnhance-analysis-ke-grayscale FusionNet/SpatialFusion — termasuk batas bukti, izin, dan provenance artefak TCM.
- BUFFER_SESSION_RUNTIME_HANDOFF_20260927.md: Rename native tanpa alias, migrasi ownership RAW/RGB, phase release, prefetch bounded-before-decode, penghentian worker sebelum cleanup, bukti CPU/CUDA/Vulkan/OpenGL, fault injection, serta batas klaim peak memori/performa.
- SPLAT_SR_TILED_RECONSTRUCTION_HANDOFF_20260927.md: Rekonstruksi RGB tile HR 1024, overlap 25%, Hann, graph fused global-origin, backing disk tertransfer, parity per backend dan batas benchmark RAM/latensi.
- SPLAT_SR_RAM_ACCUMULATOR_HANDOFF_20260927.md: Jalur aktif memakai satu akumulator RAM, normalisasi patch in-place, transfer output tanpa salinan HR, guard RAM/prefetch, perbandingan disk, dan batas refinement/readback.
- FEATURE_MATCHING_RESIDENT_READBACK_HANDOFF_20260924.md: Bukti OFB resident canonicalization/compaction, readback RGB/RAW Vulkan, parity correspondence, artifact target, dan sisa gate AKAZE/peak memory.
- OPTICAL_FLOW_RESIDENT_READBACK_HANDOFF_20260924.md: Bukti reuse destination flow, non-owning view, lifecycle fence, dan smoke RGB/RAW Vulkan untuk optical-flow resident.
- BATCH_PERF_RAM_HANDOFF_20260924.md: Handoff optimasi app layer (bukan `core/algorithm`): kecepatan switch batch, perbaikan freeze 43 s saat membuka proyek, batas cache RAM, kebijakan worker idle adaptif, probe `perf_probe`, dan catatan test flaky.
- WEIGHTNET_V2_RGB_OPTIMIZATION_HANDOFF_20260927.md: Kandidat V2 RGB FP32 pooling separable, perbandingan V3, serta reference reuse/graph compact dengan parity, lifecycle, latency dan process RAM/VRAM MX150. Cache lebih cepat tetapi dedicated VRAM lebih tinggi; belum dipromosikan.
- WEIGHTNET_V3_REFERENCE_OPTIMIZATION_HANDOFF_20260927.md: Kandidat V3 cache reference, I/O binding dan scratch tetap; parity 256/512/1024 MX150, latency dan process memory 512, serta penolakan faktorisasi linear akibat cutoff. Belum diintegrasikan/dipromosikan.
- WEIGHTNET_OPTIMIZED_BUNDLES_HANDOFF_20260927.md: Bundle V2 eksperimen dan promosi bundle aktif V3 grayscale CPU/DirectML patch 512/1024, backup terverifikasi, model unified 256 dipertahankan untuk kompatibilitas, serta parity loader produksi.
- WEIGHTED_HDR_FOUNDATION_HANDOFF.md: streaming Weighted HDR dan SPDE-MR, histogram/reference fallback, MTB/AOT dispatch, output LDR/radiance relatif, perintah Start umum dari card, serta batas bukti runtime yang masih diperlukan.
- skills/taichi-aot-dev/SKILL.md: workflow kompilasi dan validasi Taichi AOT.
- RIGHT_PANEL_CARDS_HANDOFF_20260927.md: pembagian tinggi panel kanan, jarak kartu 5 px, isi kartu rapat, pemilihan SR/HDR/denoising eksklusif, serta bukti Qt offscreen dan batas validasi aplikasi.

## Aturan kerja singkat

- Inspect Git status, target, import, caller, konfigurasi, dan artefak sebelum mengedit.
- Jaga API publik; engine.py adalah sumber kebenaran runtime dan tidak diubah tanpa persetujuan eksplisit.
- Jangan menyamakan keberadaan artefak dengan bukti eksekusi. Klaim wajib mencantumkan backend, device, shape, dtype, command, dan hasil.
- Jalur block yang belum tervalidasi memakai full-frame backend yang sama atau error jelas; tidak ada fallback GPU-ke-CPU diam-diam.
- Jangan menghapus TCM, DLL/SO, BC, source, atau cache runtime sebelum referensi dan peran packaging diverifikasi.
- Gunakan venv proyek untuk pengujian Python.

## DeepSeek

Mulai sesi DeepSeek dengan DEEPSEEK_PROMPT.md. Aturan ini menggantikan dokumen .qoder dan agen-docs yang sudah dipensiunkan.
