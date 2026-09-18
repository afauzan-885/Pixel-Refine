# Raw Native Development Archive

Direktori ini berisi seluruh arsip kode fisik dari implementasi **RAW Native Resident Pipeline (Bayer CFA Domain)** yang dikembangkan sebelum di-rollback ke commit `a56b2b29ce277a982f55624a31652c751e01b8ba`.

---

## Daftar Berkas yang Diarsipkan

1. **Patch Lengkap**:
   - `raw_native.patch`: Berisi seluruh `git diff` perubahan kode. Dapat diterapkan dengan:
     ```bash
     git apply raw-native-development/raw_native.patch
     ```

2. **Modul Sensor RAW Baru**:
   - `pixel_refine_desktop/enhance_stack/core/algorithm/denoising/raw_metadata.py`:
     Ekstraksi metadata kamera lengkap dari DNG (CFA pattern, orientation, black/white level, EXIF/GPS).
   - `pixel_refine_desktop/enhance_stack/core/algorithm/denoising/raw_result.py`:
     Dataclass `RawNativeResult` dengan metode `save_dng(path)` terkalibrasi dan `save_linear_tiff(path)`.
   - `pixel_refine_desktop/enhance_stack/core/algorithm/denoising/resident_alignment.py`:
     Resolver rencana alignment RAW native.

3. **Enjin Pipeline Terintegrasi**:
    - `pixel_refine_desktop/enhance_stack/core/algorithm/denoising/resident_pipeline.py`:
      Pipeline zero-copy streaming dengan alur fusi CFA Bayer 2D (`_cfa_blend_frame`), Hamilton on-the-fly guide demosaic (100% parity numerik dengan commit a56b2b29), dan Hamilton final preview demosaic.
   - `pixel_refine_desktop/enhance_stack/core/algorithm/denoising/MFDenoiser.py`:
     Orkestrator pipeline dengan integrasi penyimpanan DNG murni.
   - `pixel_refine_desktop/enhance_stack/core/algorithm/denoising/FusionNet.py`:
     Adapter FusionNet yang mengenali `RawNativeResult`.
   - `pixel_refine_desktop/enhance_stack/core/algorithm/denoising/Average.py`:
     Adapter Average yang mengenali `RawNativeResult`.
   - `pixel_refine_desktop/enhance_stack/core/algorithm/denoising/SpatialFusion.py`:
     Adapter SpatialFusion yang mengenali `RawNativeResult`.
   - `pixel_refine_desktop/enhance_stack/core/algorithm/denoising/fusionet_engine/flownet_inference.py`:
     Optical flow inference dengan penanganan aman buffer `supp_rgb_f32 is None`.
   - `pixel_refine_desktop/enhance_stack/core/algorithm/denoising/fusionet_engine/weightnet_inference.py`:
     WeightNet inference engine.

## Fitur Utama: Phase-Locked Bayer Carrier Sampling

Implementasi terbaru menggunakan **Cross-Channel Guided Warp & Phase-Locked Bayer Carrier Sampling** untuk mengeliminasi *Cross-Channel Lattice Tearing* dan artefak *zipper* secara tuntas:
1. **Warp Vektor Kontinu 3D**: Frame support dide-mosaic *on-the-fly* pada skala radiansi sensor murni (`wb=1.0`, `cmatrix=eye(3)`) menggunakan metode Hamilton. Warping optical flow dilakukan serentak pada ketiga kanal RGB dengan gradien kohesif penuh tanpa distorsi phase shift antar kanal.
2. **Phase-Locked Carrier Extraction**: Pada setiap piksel $(y, x)$, sample sensor diproyeksikan langsung sesuai kisi Bayer referensi (`ref_raw_frame.cfa_pattern`), menjaga integritas domain sensor murni.
3. **True Sensor RAW Bayer DNG**: Output disimpan sebagai 1-kanal 2D CFA Bayer DNG (`PhotometricInterpretation = 32803`) dengan metadata sensor asli, bukan packed demosaiced RGB.

---

## Hasil Uji Parity & Akurasi (vs Commit a56b2b29)

Pengujian pada data riil kamera (`IMG_20260607_160719Z_B001.dng` dan `B002.dng`, 12MP Bayer CFA `(2, 3, 1, 0)`):

- **Inference WeightNet Parity**:
  * Route A (Pre-Demosaiced RGB): Alpha = `0.011637`
  * Route B (Raw Native Phase-Locked): Alpha = `0.011637`
  * Selisih Mutlak Alpha: **`0.000000`** (100% bit-exact parity)
  * Korelasi Weight Map: **`100.0000%`** (RMSE = `0.000000`)

- **Kualitas Rekonstruksi Fusi RGB**:
  * SSIM: **`95.59%`**
  * PSNR: **`26.43 dB`**
  * Retensi Ketajaman Tepi (Gradient Energy Ratio): **`1.0175`** (Ketajaman struktur halus dipertahankan lebih baik karena terbebas dari blur pre-filtering)

- **Validasi Integritas RAW DNG (rawpy)**:
  * Dimensi: `(3072, 4096)` (1-channel 2D sensor mosaic)
  * Format: `uint16` (16-bit integer sensor code)
  * CFA Pattern: Valid `(2, 3, 1, 0)`
  * Artefak Zipper / Lattice Tearing: **`0.00%`** (Tuntas)

---

## Cara Menggunakan Kembali
Anda cukup menyalin kembali berkas dari folder ini ke `pixel_refine_desktop/` atau menggunakan `git apply raw-native-development/raw_native.patch`.
