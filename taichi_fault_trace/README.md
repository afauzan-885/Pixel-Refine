# taichi_fault_trace

Lapisan pelacakan fault untuk runtime `taichi` 1.8.0 di venv proyek. Tujuan:
setiap kegagalan runtime menghasilkan pesan yang bisa dibaca, memuat konteks
lengkap (rantai pemanggilan, argumen, backend/device, error native, artefak),
dan hint langkah perbaikan.

## Aktivasi

Tracer diaktifkan otomatis untuk venv lewat berkas `.pth`:

```powershell
.\venv\Scripts\python.exe tools\install_taichi_fault_trace.py --install
.\venv\Scripts\python.exe tools\install_taichi_fault_trace.py --status
.\venv\Scripts\python.exe tools\install_taichi_fault_trace.py --verify
.\venv\Scripts\python.exe tools\install_taichi_fault_trace.py --uninstall
```

Yang ditulis hanya `venv/Lib/site-packages/taichi_fault_trace_activate.pth`.
Paket `taichi` **tidak** diubah, sehingga reinstall taichi tidak merusak tracer.

Pemuatan bersifat malas: hook `import taichi` dipasang saat startup, sedangkan
modul tracer (yang mengimpor numpy) baru dimuat pada `import taichi` pertama.

Nonaktifkan sementara tanpa uninstall:

```powershell
$env:TAICHI_FAULT = "off"
```

## Pemakaian manual

```python
import taichi_fault_trace as tft

tft.install()                     # instrumen taichi + import berikutnya
tft.instrument("my.app.module")   # perluas cakupan ke modul aplikasi
with tft.trace_scope("burst-4x12mp"):
    ...
tft.diagnose()                    # snapshot backend/device/artefak
tft.last_report()                 # FaultReport terakhir
```

Dekorator untuk fungsi aplikasi:

```python
from taichi_fault_trace import trace

@trace
def run_pipeline(...):
    ...
```

## Isi laporan

Laporan dicetak ke `stderr` dan ditulis sebagai JSON ke
`TAICHI_FAULT_DIR` (default `%TEMP%/taichi_fault_trace`).

Bagian laporan:

- `KODE`, `JUDUL`, `TINGKAT`: hasil pencocokan hint.
- `BACKEND`, `HANDLE`, `NATIVE`: arch/device/generation, handle bridge,
  `last_error`, `context_backend`, `device_name`, `last_init_error`.
- `ENV`: `AOT_ARCH`, `AOT_DEVICE`, `TARGET_VENDOR`, `TI_LIB_DIR`, dan env
  relevan lain.
- `RANTAI RUNTIME`: pemanggilan runtime terakhir beserta argumen dan durasi.
- `FRAME PYTHON`: `file:line`, potongan sumber, dan locals yang sudah diringkas.
- `ARTEFAK`: `.tcm`/`.bundle`/DLL yang terlibat, ukuran, mtime, sha256.
- `HINT`: penyebab yang mungkin, langkah periksa, rujukan dokumen.

Setiap exception juga mendapat `exc.__taichi_fault_report__` dan catatan
PEP 678 (`add_note`). Tipe exception asli tidak diubah.

## Variabel lingkungan

- `TAICHI_FAULT`: `off` | `light` | `full` (default `full`).
- `TAICHI_FAULT_DIR`: direktori artefak laporan.
- `TAICHI_FAULT_MAX_ARTIFACTS`: retensi JSON (default 50).
- `TAICHI_FAULT_ARGS`: `0` untuk tidak merangkum argumen.
- `TAICHI_FAULT_LOCALS`: `0` untuk tidak merangkum locals.
- `TAICHI_FAULT_RENDER`: `0` untuk tidak mencetak ke konsol.
- `TAICHI_FAULT_RAISE`: `1` untuk melempar `TaichiFaultError`
  (subclass `RuntimeError`) alih-alih mempertahankan tipe asli.
- `TAICHI_FAULT_EXTRA`: daftar modul dipisah koma untuk
  diinstrumentasi juga, mis.
  `taichi_vision.taichi_algorithm.denoising.onnx_resident_aot`.
- `TAICHI_FAULT_FAULTHANDLER`: `0` untuk menonaktifkan log
  crash native.

## CLI

```powershell
.\venv\Scripts\python.exe -m taichi_fault_trace --diagnose
.\venv\Scripts\python.exe -m taichi_fault_trace --json
.\venv\Scripts\python.exe -m taichi_fault_trace --hints
.\venv\Scripts\python.exe -m taichi_fault_trace --artifacts pixel_refine_desktop\ui\data\aot_assets\neural
.\venv\Scripts\python.exe -m taichi_fault_trace --inventory
.\venv\Scripts\python.exe -m taichi_fault_trace --selftest
```

`--inventory` mencetak semua nama runtime yang sudah terinstrumentasi; pakai
ini untuk memastikan cakupan sebelum menyalahkan tracer.

## Menambah hint

Hint adalah data murni di `_hints.py` (`HINT_RULES`). Bentuk satu aturan:

```python
(
    lambda text, ctx: "pola error" in text,
    Hint(
        id="TAICHI-CONTOH",
        title="Judul singkat",
        severity="tinggi",
        causes=("penyebab 1", "penyebab 2"),
        checks=("perintah/snippet 1", "perintah/snippet 2"),
        docs="path/ke/dokumen",
        priority=80,
    ),
),
```

Urutan tampilan mengikuti `priority` (tertinggi lebih dulu). Bila tidak ada
yang cocok, `TAICHI-GENERIC` dipakai.

## Batasan

- Pengecualian Python dapat diperkaya penuh; crash native (segfault/abort)
  hanya tertangkap lewat `faulthandler` (`faulthandler.log`) karena proses
  berhenti sebelum Python dapat membangun laporan.
- Overhead hanya berupa pencatatan waktu masuk/keluar per pemanggilan runtime;
  perangkuman argumen/locals dibuat **saat fault**, bukan di jalur sukses.
- Tracer tidak mengubah nilai balik, signature, generator, atau coroutine.
- Klaim kesiapan produksi tetap mengikuti governance: satu backend/device/shape
  tidak membuktikan yang lain.
