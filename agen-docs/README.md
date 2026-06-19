# Pixel Refine - Agen Knowledge Base

Dokumentasi universal untuk kolaborasi antar agen AI. Dikonsolidasi dari seluruh sumber pengetahuan:
- `.qoder/memories/` (86 file Qoder memory)
- `.agents/memories/` (86 file Agent memory)  
- `.kun/data/` (Kun app config & thread history)
- `.qoder/plans/` (Rencana implementasi)
- `.qoder/commands/` (Commands & preferences)
- `.codex/skills/` (15 Codex curated skills)

## Struktur Dokumentasi

```
agen-docs/
├── README.md                    # File ini
├── global/
│   └── language-preference.md   # Preferensi bahasa Indonesia
├── architecture/
│   ├── project-overview.md      # Ikhtisar proyek & kemampuan
│   ├── tech-stack.md            # Technology stack lengkap
│   ├── mfdenoiser.md            # Arsitektur MFDenoiser & denoising
│   ├── genericui-mobile.md      # GenericUILibrary & arsitektur mobile
│   ├── optical-flow-aot.md      # Optical flow & Taichi AOT modules
│   └── mfdenoiser-resolution.md # Resolution handling
├── decisions/
│   └── architecture-decisions.md # Keputusan arsitektur penting
├── pitfalls/
│   └── common-pitfalls.md       # Jebakan yang sering terjadi
├── tech-stack/
│   └── full-stack.md            # Tech stack lengkap dengan detail
├── build-config/
│   ├── project-structure.md     # Struktur & environment proyek
│   └── aot-compilation.md       # AOT compilation & TCM
├── plans/
│   └── template-flow-refactor.md # Rencana refactor template_flow.py
└── kun-config/
    └── kun-settings.md          # Konfigurasi Kun app
```

## Sumber Data

| Sumber | Lokasi | Jumlah File | Status |
|--------|--------|-------------|--------|
| Qoder memories | `.qoder/memories/` | 86 | ✅ Dibaca semua |
| Agent memories | `.agents/memories/` | 86 | ✅ Dibaca semua (mirror) |
| Kun config | `.kun/data/config.json` | 1 | ✅ Dibaca |
| Kun MCP | `.kun/mcp.json` | 1 | ✅ Dibaca |
| Qoder commands | `.qoder/commands/` | 1 | ✅ Dibaca |
| Qoder plans | `.qoder/plans/` | 1 | ✅ Dibaca |
| Kun attachments | `.kun/data/attachments/` | 7 | ✅ Metadata tercatat |
| Kun threads | `.kun/data/threads/` | 2 | ✅ Metadata tercatat |
| Codex skills | `.codex/vendor_imports/skills/` | 15 skills | ✅ Terdaftar |
