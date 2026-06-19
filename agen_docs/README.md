# Pixel Refine Documentation Index

> Folder ini berisi dokumentasi terorganisir untuk proyek Pixel Refine.
> Semua memori, pengalaman, rules, dan pengetahuan teknis diekstrak ke sini.

## Daftar Isi

| File | Deskripsi |
|------|-----------|
| [`01_project_overview.md`](./01_project_overview.md) | Status proyek, kapabilitas utama, performance benchmarks |
| [`02_tech_stack.md`](./02_tech_stack.md) | Taichi AOT architecture, engine.py, TCM modules, VRAM protection |
| [`03_mfdenoiser_architecture.md`](./03_mfdenoiser_architecture.md) | MFDenoiser pipeline, single truth source, backend selection, spatial fusion |
| [`04_optical_flow.md`](./04_optical_flow.md) | BMA, Horn-Schunck, Farneback AOT/JIT, compilation, test results |
| [`05_development_practices.md`](./05_development_practices.md) | Code simplicity rules, Taichi rules, UI rules, QML rules |
| [`06_pitfalls_and_fixes.md`](./06_pitfalls_and_fixes.md) | Critical bugs, common pitfalls, QML issues, debugging tips |
| [`07_build_and_compile.md`](./07_build_and_compile.md) | AOT compilation scripts, rules, testing |
| [`08_environment_config.md`](./08_environment_config.md) | Project structure, environment variables, configuration files |

## Quick Reference

### Single Source of Truth
- **File**: `engine.py`
- **Rule**: DILAR dimodifikasi tanpa persetujuan eksplisit

### Default Backend Selection
```json
{
    "merging_mode": "spatial_fusion",
    "optical_flow_type": "alignment_tile",
    "alignment_backend": "taichi_gpu"
}
```

### Key Entry Points
- `MFDenoiser.py` — Main orchestrator
- `Similarity.py` — Legacy orchestrator (backup)
- `main_desktop.py` — Application entry point

### TCM Modules Location
- `taichi_library/taichi_algorithm/aot_tcm/` — Algorithm modules
- `ui/data/aot_assets/` — UI-related modules

### Compile Command Pattern
```bash
$env:AOT_MODE="0"
python -m taichi_library.taichi_algorithm.aot_py.compile_<module>_tcm
```

## Update Policy

> **Penting**: Untuk kedepannya, semua memori, pengalaman, rules, dan pengetahuan baru **wajib** ditambahkan ke folder `agen_docs/` ini.
> 
> Jika ada informasi yang sama tetapi belum up-to-date, integrasikan bagian yang baru ke file yang sesuai.

## Related Files

| File | Lokasi | Deskripsi |
|------|--------|-----------|
| `agen.md` | Root project | Main knowledge base (legacy, akan dimigrate ke agen_docs) |
| `skill.md` | Root project | Technical skill guide (legacy, akan dimigrate ke agen_docs) |
| `.agents` | Root project | Agent configuration |
