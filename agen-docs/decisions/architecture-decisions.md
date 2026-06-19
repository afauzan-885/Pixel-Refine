# Keputusan Arsitektur Penting

**Sumber**: 7 memory files dari `.qoder/memories/.../important_decision_experience/`

## 1. GenericUI Binding Rule

**Keputusan**: Semua UI WAJIB menggunakan Python-based GenericUI components SAJA.

**Ruang Lingkup**:
- Tidak boleh raw QML atau manual QML file creation
- Components di-bind dan di-orchestrate via Python scripts
- Leverage existing QML bindings

**Berlaku Untuk**: Semua UI development task dalam pixel_refine_mobile yang menggunakan GenericUILibrary

## 2. GPU AOT Backend Integration Policy (MFDenoiser)

**Keputusan**: 
- Tambahkan sebagai opsi `spatial_fusion` di `stage_merge()`
- Gunakan GPU AOT secara **eksklusif**
- Raise `RuntimeError` dengan pesan console jika GPU AOT engine tidak tersedia
- **TIDAK ADA** CPU fallback

**Berlaku Untuk**: Semua GPU AOT-based denoising backend (temporal_fusion, adaptive_spatial, dll)

## 3. Optical Flow Backend Pipeline Strategy

**Keputusan**:
- Backend: Gunakan `farneback_jit`
- Leverage `taichi_algorithm.farneback_flow()` sebagai lazy-initialized Taichi JIT module
- Pipeline:
  1. Compute optical flow di `work_res` (lower resolution pyramid level)
  2. Perform warping di `full_res` (original resolution)
- Hasil: High-quality alignment dengan performa optimal

**Berlaku Untuk**: Semua GPU-accelerated image alignment pipeline

## 4. GPU Watchdog Idle Timeout and Cleanup

**Keputusan**:
- **Idle timeout**: 60 detik (default value)
- **Trigger action**:
  1. Eksekusi global cleanup (release semua VRAM)
  2. Kirim SIGTERM untuk terminate process
- **Tujuan**: Ensure OS langsung回收 GPU context

**Berlaku Untuk**: Semua GPU-accelerated Python engine

## 5. to_qml() Scope Decision

**Keputusan**:
- Scope: Terapkan ke **SEMUA komponen** dalam GenericUILibrary, bukan subset
- Bug Fix: Prioritaskan dan sertakan duplicate-title bug fix di `Card.__init__()` sebagai bagian dari parity effort

**Berlaku Untuk**: Semua work yang bertujuan mencapai full API parity desktop-mobile

## 6. Desktop-to-Mobile Architecture Porting

**Keputusan**:
- Focus eksklusif pada **5 komponen inti**: Home Page, MFDenoiser, MFResolution, HDR, Panorama
- Leverage dan port konsep desktop yang sudah terbukti
- Build NEW components dengan arsitektur yang mirip dengan versi desktop
- Pertahankan **identical signal contracts** dan **data flow patterns**

**Berlaku Untuk**: Semua mobile project yang harus mencapai feature dan API parity dengan desktop

## 7. AOT Compiler Script Naming Convention

**Keputusan**:
- Script rename dari `compile_new_algorithms_tcm.py` → `compile_analysis_suite_tcm.py`
- Alasan: Mencakup kompilasi `color_convert`, `otsu`, `clahe`, `canny`, `hough`, dan `guided_filter`

**Berlaku Untuk**: Semua AOT compilation scripts
