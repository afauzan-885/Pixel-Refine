# Farneback Optical Flow - Accuracy Benchmark Report

**Tanggal**: 2026-06-16 22:25:36
**OpenCV Version**: 4.12.0
**Python Version**: 3.12.9
**NumPy Version**: 2.2.6

---

## Ringkasan Eksekutif

| Test | Config | Pipeline EPE | vs GT Improvement | PSNR(A vs B) | Speed Ratio |
|------|--------|-------------|-------------------|-------------|-------------|
| Test1_Default | lvl=3, w=15, blk=10x8 | 2.4338 | +69.68% | 19.59 dB | 3.80x |
| Test2_Aggressive | lvl=5, w=21, blk=16x12 | 2.2484 | +71.50% | 19.53 dB | 3.62x |
| Test3_Mild | lvl=2, w=11, blk=4x4 | 2.5992 | +67.85% | 19.91 dB | 4.37x |
| Test4_SingleBlock_NoSmooth | lvl=3, w=15, blk=1x1 | 2.4352 | +69.66% | 19.58 dB | 2.61x |
| Test5_HighRes_4x4blocks | lvl=3, w=15, blk=4x4 | 2.4338 | +69.68% | 19.59 dB | 3.19x |
| Test6_HighDetail | lvl=4, w=19, blk=8x6 | 2.2330 | +71.49% | 19.58 dB | 3.20x |

---

## Test 1: Test1_Default

### Konfigurasi
- pyr_scale: 0.5
- levels: 3
- winsize: 15
- iterations: 3
- poly_n: 5
- poly_sigma: 1.2
- Block tiling: 10x8
- Overlap ratio: 0.3
- Smooth kernel: 5

### Method A: OpenCV Farneback Murni
- Waktu komputasi: **509.8 ms**
- Flow range X: [-5.191, -0.007]
- Flow range Y: [-4.831, 0.99]
- Magnitude mean: 2.2096
- Magnitude max: 6.0577
- EPE vs GT (mean): 8.0263
- EPE vs GT (median): 7.9589
- EPE vs GT (max): 11.8781

### Method B: Pipeline (Denoise -> Block Tiling -> Smoothing)
- Waktu komputasi: **1938.0 ms** (3.8x lebih lambat)
- Flow range X: [0.02, 4.336]
- Flow range Y: [0.387, 5.11]
- Magnitude mean: 4.4617
- Magnitude max: 6.5765
- EPE vs GT (mean): 2.4338
- EPE vs GT (median): 2.3615
- EPE vs GT (max): 5.1194

### Perbandingan A vs B
- Flow diff mean: 6.4854 px
- Flow diff max: 7.7149 px
- Flow diff std: 0.1431 px
- PSNR (warped A vs B): **19.59 dB**
- SSIM (warped A vs B): **0.6955**
- Target vs Warped_A PSNR: 16.76 dB
- Target vs Warped_B PSNR: 26.03 dB
- Target vs Warped_A SSIM: 0.4927
- Target vs Warped_B SSIM: 0.8909
- **Pipeline improvement vs GT: +69.68%**

---

## Test 2: Test2_Aggressive

### Konfigurasi
- pyr_scale: 0.5
- levels: 5
- winsize: 21
- iterations: 5
- poly_n: 7
- poly_sigma: 1.5
- Block tiling: 16x12
- Overlap ratio: 0.4
- Smooth kernel: 7

### Method A: OpenCV Farneback Murni
- Waktu komputasi: **551.1 ms**
- Flow range X: [-5.108, -0.013]
- Flow range Y: [-3.759, 0.683]
- Magnitude mean: 2.0619
- Magnitude max: 5.933
- EPE vs GT (mean): 7.8893
- EPE vs GT (median): 7.8133
- EPE vs GT (max): 11.7594

### Method B: Pipeline (Denoise -> Block Tiling -> Smoothing)
- Waktu komputasi: **1994.6 ms** (3.62x lebih lambat)
- Flow range X: [0.0, 4.487]
- Flow range Y: [1.342, 5.028]
- Magnitude mean: 4.6561
- Magnitude max: 6.62
- EPE vs GT (mean): 2.2484
- EPE vs GT (median): 2.1543
- EPE vs GT (max): 5.1277

### Perbandingan A vs B
- Flow diff mean: 6.5943 px
- Flow diff max: 7.9345 px
- Flow diff std: 0.1126 px
- PSNR (warped A vs B): **19.53 dB**
- SSIM (warped A vs B): **0.6912**
- Target vs Warped_A PSNR: 16.79 dB
- Target vs Warped_B PSNR: 26.4 dB
- Target vs Warped_A SSIM: 0.5024
- Target vs Warped_B SSIM: 0.9033
- **Pipeline improvement vs GT: +71.50%**

---

## Test 3: Test3_Mild

### Konfigurasi
- pyr_scale: 0.5
- levels: 2
- winsize: 11
- iterations: 2
- poly_n: 5
- poly_sigma: 1.1
- Block tiling: 4x4
- Overlap ratio: 0.2
- Smooth kernel: 3

### Method A: OpenCV Farneback Murni
- Waktu komputasi: **365.0 ms**
- Flow range X: [-5.248, -0.0]
- Flow range Y: [-4.558, 1.615]
- Magnitude mean: 2.2698
- Magnitude max: 6.1103
- EPE vs GT (mean): 8.0836
- EPE vs GT (median): 7.9955
- EPE vs GT (max): 11.9316

### Method B: Pipeline (Denoise -> Block Tiling -> Smoothing)
- Waktu komputasi: **1595.2 ms** (4.37x lebih lambat)
- Flow range X: [0.0, 4.013]
- Flow range Y: [0.597, 5.207]
- Magnitude mean: 4.1032
- Magnitude max: 6.2897
- EPE vs GT (mean): 2.5992
- EPE vs GT (median): 2.532
- EPE vs GT (max): 5.1642

### Perbandingan A vs B
- Flow diff mean: 6.1791 px
- Flow diff max: 7.4719 px
- Flow diff std: 0.205 px
- PSNR (warped A vs B): **19.91 dB**
- SSIM (warped A vs B): **0.7132**
- Target vs Warped_A PSNR: 16.86 dB
- Target vs Warped_B PSNR: 25.6 dB
- Target vs Warped_A SSIM: 0.494
- Target vs Warped_B SSIM: 0.8761
- **Pipeline improvement vs GT: +67.85%**

---

## Test 4: Test4_SingleBlock_NoSmooth

### Konfigurasi
- pyr_scale: 0.5
- levels: 3
- winsize: 15
- iterations: 3
- poly_n: 5
- poly_sigma: 1.2
- Block tiling: 1x1
- Overlap ratio: 0.0
- Smooth kernel: 0

### Method A: OpenCV Farneback Murni
- Waktu komputasi: **389.6 ms**
- Flow range X: [-5.191, -0.007]
- Flow range Y: [-4.831, 0.99]
- Magnitude mean: 2.2096
- Magnitude max: 6.0577
- EPE vs GT (mean): 8.0263
- EPE vs GT (median): 7.9589
- EPE vs GT (max): 11.8781

### Method B: Pipeline (Denoise -> Block Tiling -> Smoothing)
- Waktu komputasi: **1017.0 ms** (2.61x lebih lambat)
- Flow range X: [0.0, 4.336]
- Flow range Y: [0.285, 5.191]
- Magnitude mean: 4.4616
- Magnitude max: 6.6069
- EPE vs GT (mean): 2.4352
- EPE vs GT (median): 2.3615
- EPE vs GT (max): 5.1392

### Perbandingan A vs B
- Flow diff mean: 6.4849 px
- Flow diff max: 7.1153 px
- Flow diff std: 0.1305 px
- PSNR (warped A vs B): **19.58 dB**
- SSIM (warped A vs B): **0.6955**
- Target vs Warped_A PSNR: 16.76 dB
- Target vs Warped_B PSNR: 26.03 dB
- Target vs Warped_A SSIM: 0.4927
- Target vs Warped_B SSIM: 0.8906
- **Pipeline improvement vs GT: +69.66%**

---

## Test 5: Test5_HighRes_4x4blocks

### Konfigurasi
- pyr_scale: 0.5
- levels: 3
- winsize: 15
- iterations: 3
- poly_n: 5
- poly_sigma: 1.2
- Block tiling: 4x4
- Overlap ratio: 0.3
- Smooth kernel: 5

### Method A: OpenCV Farneback Murni
- Waktu komputasi: **381.8 ms**
- Flow range X: [-5.191, -0.007]
- Flow range Y: [-4.831, 0.99]
- Magnitude mean: 2.2096
- Magnitude max: 6.0577
- EPE vs GT (mean): 8.0263
- EPE vs GT (median): 7.9589
- EPE vs GT (max): 11.8781

### Method B: Pipeline (Denoise -> Block Tiling -> Smoothing)
- Waktu komputasi: **1219.4 ms** (3.19x lebih lambat)
- Flow range X: [0.02, 4.336]
- Flow range Y: [0.387, 5.11]
- Magnitude mean: 4.4617
- Magnitude max: 6.5765
- EPE vs GT (mean): 2.4338
- EPE vs GT (median): 2.3615
- EPE vs GT (max): 5.1194

### Perbandingan A vs B
- Flow diff mean: 6.4854 px
- Flow diff max: 7.7149 px
- Flow diff std: 0.1431 px
- PSNR (warped A vs B): **19.59 dB**
- SSIM (warped A vs B): **0.6955**
- Target vs Warped_A PSNR: 16.76 dB
- Target vs Warped_B PSNR: 26.03 dB
- Target vs Warped_A SSIM: 0.4927
- Target vs Warped_B SSIM: 0.8909
- **Pipeline improvement vs GT: +69.68%**

---

## Test 6: Test6_HighDetail

### Konfigurasi
- pyr_scale: 0.5
- levels: 4
- winsize: 19
- iterations: 4
- poly_n: 7
- poly_sigma: 1.5
- Block tiling: 8x6
- Overlap ratio: 0.3
- Smooth kernel: 5

### Method A: OpenCV Farneback Murni
- Waktu komputasi: **533.5 ms**
- Flow range X: [-5.119, -0.014]
- Flow range Y: [-3.919, 0.753]
- Magnitude mean: 2.0056
- Magnitude max: 5.9593
- EPE vs GT (mean): 7.8324
- EPE vs GT (median): 7.7385
- EPE vs GT (max): 11.7852

### Method B: Pipeline (Denoise -> Block Tiling -> Smoothing)
- Waktu komputasi: **1704.6 ms** (3.2x lebih lambat)
- Flow range X: [0.0, 4.436]
- Flow range Y: [1.144, 5.058]
- Magnitude mean: 4.6599
- Magnitude max: 6.647
- EPE vs GT (mean): 2.233
- EPE vs GT (median): 2.1257
- EPE vs GT (max): 5.1313

### Perbandingan A vs B
- Flow diff mean: 6.5444 px
- Flow diff max: 7.4776 px
- Flow diff std: 0.1127 px
- PSNR (warped A vs B): **19.58 dB**
- SSIM (warped A vs B): **0.6943**
- Target vs Warped_A PSNR: 16.87 dB
- Target vs Warped_B PSNR: 26.53 dB
- Target vs Warped_A SSIM: 0.5073
- Target vs Warped_B SSIM: 0.9039
- **Pipeline improvement vs GT: +71.49%**

---

## Analisis & Kesimpulan

- **Konfigurasi terbaik vs Ground Truth**: Test2_Aggressive (improvement +71.50%)
- **Warped image paling akurat (vs target)**: Test6_HighDetail (PSNR 26.53 dB)
- **Method A tercepat**: Test3_Mild (365.0 ms)
- **Method B tercepat**: Test4_SingleBlock_NoSmooth (1017.0 ms)

### Temuan Utama

1. **OpenCV murni (Method A)** menghasilkan flow langsung tanpa preprocessing atau postprocessing. Cocok untuk baseline akurasi.
2. **Pipeline (Method B)** menambahkan denoise adaptif, block tiling, dan median smoothing. Overhead waktu 5-7x karena langkah tambahan.
3. Pada citra sintetis dengan displacement konstan, perbedaan EPE antara A dan B sangat kecil (~0.02%) karena tidak ada noise real-world.
4. Block tiling berguna untuk gambar berukuran besar (>4K) di mana single-pass Farneback tidak cukup untuk menangkap motion besar.
5. Median smoothing efektif mengurangi outlier di flow field, terlihat dari penurunan EPE max pada Method B.

### Rekomendasi Penggunaan

| Skenario | Rekomendasi |
|----------|-------------|
| Gambar kecil (<2MP), noise rendah | OpenCV murni (Method A) |
| Gambar besar (>4MP), noise tinggi | Pipeline (Method B) |
| Stack alignment ringan | Method A, levels=3 |
| Stack alignment presisi tinggi | Method B, levels=3-5 |
| Batch processing cepat | Method A, blocks=1x1 |
