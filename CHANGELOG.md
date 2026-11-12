# Changelog

## 2026-11-12 - Taichi fault trace

Ringkasan: lapisan pelacakan fault runtime taichi 1.8.0 yang menghasilkan
laporan lengkap dan hint perbaikan.

Perubahan:
- Tambah `taichi_fault_trace/`: config, summarizer, snapshot native/env,
  hint registry, renderer laporan, wrapper runtime, autoinstall, dan CLI.
- Tambah `tools/install_taichi_fault_trace.py` untuk install/uninstall/status/
  verify aktivasi venv lewat `.pth` di `site-packages`. Paket `taichi` tidak
  diubah.
- Instrumen 1.026 callable runtime taichi (fungsi, metode kelas, generator,
  coroutine) secara transparan; tipe exception asli dipertahankan.
- Laporan memuat rantai pemanggilan + argumen, frame `file:line` + locals,
  backend/device/handle/DLL bridge, `last_error` native, env, artefak TCM
  (size/mtime/sha256), dan hint.
- Artefak JSON ditulis ke direktori laporan; `faulthandler` aktif untuk crash
  native.
- Noise front-end (`ti.ndrange`/`ti.static`) dan shutdown dibuat senyap.

Verifikasi:
- `python -m taichi_fault_trace --selftest` -> 2/2 OK.
- `python -m taichi_fault_trace --inventory` -> total=1026.
- WeightNet resident CUDA, 4 frame 3072x4096 float32:
  load 0.472 s, prepare 0.205 s, infer 3.073 s (0.78 s/frame steady).
- Overhead tracer pada jalur sukses: <2% (3.487 s vs 3.447 s).

Temuan:
- `_view_sync()` di `onnx_resident_aot.py` memanggil
  `_raise_native_engine_error()` tanpa memeriksa `last_error`, sehingga
  `close()` melaporkan `unknown native failure` palsu. Belum diubah pada
  commit ini.
