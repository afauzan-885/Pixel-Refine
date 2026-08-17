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
- skills/taichi-aot-dev/SKILL.md: workflow kompilasi dan validasi Taichi AOT.

## Aturan kerja singkat

- Inspect Git status, target, import, caller, konfigurasi, dan artefak sebelum mengedit.
- Jaga API publik; engine.py adalah sumber kebenaran runtime dan tidak diubah tanpa persetujuan eksplisit.
- Jangan menyamakan keberadaan artefak dengan bukti eksekusi. Klaim wajib mencantumkan backend, device, shape, dtype, command, dan hasil.
- Jalur block yang belum tervalidasi memakai full-frame backend yang sama atau error jelas; tidak ada fallback GPU-ke-CPU diam-diam.
- Jangan menghapus TCM, DLL/SO, BC, source, atau cache runtime sebelum referensi dan peran packaging diverifikasi.
- Gunakan venv proyek untuk pengujian Python.

## DeepSeek

Mulai sesi DeepSeek dengan DEEPSEEK_PROMPT.md. Aturan ini menggantikan dokumen .qoder dan agen-docs yang sudah dipensiunkan.
