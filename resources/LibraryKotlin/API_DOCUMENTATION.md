# 📚 Dokumentasi Lengkap & Panduan API: LibraryKotlin

> **Pixel Refine Multiplatform Design System & Computational Photography Suite**  
> Standar Arsitektur: **KISS**, **Deklaratif**, **Zero-Boilerplate**, dan **Pythonic 1-Line Facade**.

---

## 🐍 Pythonic 1-Line Cheatsheet (Cukup 1 Baris Saja)

| Komponen / Fungsionalitas | Cara Pemanggilan Gaya Python (1-Baris) |
| :--- | :--- |
| **Tone Curve Editor** | `tone_curve_editor(on_change = { ... })` |
| **Histogram Viewer** | `histogram_viewer(red_data = r, green_data = g, blue_data = b)` |
| **Filmstrip Timeline** | `filmstrip(images = list, on_select = { ... })` |
| **Segmented Pill Control** | `segmented_control(items = listOf("RGB", "Luma"), on_select = { ... })` |
| **Preset Selector** | `preset_selector(selected_id = "night_denoise", on_select = { ... })` |
| **Dual Range Slider** | `range_slider(min_val = 0f, max_val = 100f, on_change = { ... })` |
| **Pixel Loupe Magnifier** | `magnifier(zoom_factor = 4f) { ... }` |
| **Button Anti-Spam** | `button(text = "Proses", on_click = { ... }, is_loading = state)` |
| **Status Badge** | `badge(text = "Processing", variant = Variant.Warning, show_pulse = true)` |
| **Toast Notifikasi** | `toast("Sukses!", Variant.Success)` |
| **AI Smart Culling** | `auto_cull(images, buffers, 4000, 3000)` |
| **Preset Manager** | `get_preset("night_denoise")` / `list_presets()` / `save_preset(...)` |
| **Session Checkpoint** | `save_checkpoint(batch_id, 50, 25)` / `has_recovery(batch_id)` |

---

## 📑 Daftar Isi
1. [Arsitektur & Filosofi Desain](#1-arsitektur--filosofi-desain)
2. [Sistem Tema & Variasi (Theme & Variants)](#2-sistem-tema--variasi)
3. [Katalog Komponen UI Lengkap](#3-katalog-komponen-ui-lengkap)
   - [Buttons & Form Controls](#31-buttons--form-controls)
   - [Cards & Media Containers](#32-cards--media-containers)
   - [Overlays, Modals, & Notifications (Toast)](#33-overlays-modals--notifications-toast)
   - [Pro Computational Photography Controls](#34-pro-computational-photography-controls)
4. [Sistem Animasi Multi-Chaining](#4-sistem-animasi-multi-chaining)
5. [Domain & Logic Management](#5-domain--logic-management)
   - [State Manager & Konkurensi](#51-batch-state-manager--konkurensi)
   - [AI Smart Culling & Sharpness Metric](#52-ai-smart-culling--sharpness-metric)
   - [Algorithm Presets Store](#53-algorithm-presets-store)
   - [Fault-Tolerant Session Recovery](#54-fault-tolerant-session-recovery)
   - [Image Streamer & Adaptive Chunk Processor](#55-image-streamer--adaptive-chunk-processor)
6. [Integrasi Taichi AOT C++ Native Pipeline](#6-integrasi-taichi-aot-c-native-pipeline)

---

## 1. Arsitektur & Filosofi Desain

`LibraryKotlin` dibangun untuk menjembatani UI modern berbasis **Compose Multiplatform (Desktop & Android)** dengan mesin komputasi citra berkinerja tinggi **Taichi AOT C++ Native DLL/PYD**.

* **KISS & Zero-Boilerplate**: Semua fungsi dapat dipanggil dalam 1–3 baris kode deklaratif.
* **Non-Destructive & Thread-Safe**: State batch dan pemrosesan thread terlindungi secara `synchronized` dan bebas data collision.
* **Direct Memory Sharing**: Menggunakan direct pointer `ByteBuffer` (zero-copy) dari Kotlin langsung ke runtime C++.

---

## 2. Sistem Tema & Variasi

Semua komponen bereaksi secara otomatis terhadap tema aplikasi melalui `LocalGenericTheme.current`.

### Varian Warna Semantik (`Variant`)
* `Variant.Primary` $\rightarrow$ Aksen Brand (Biru / Indigo)
* `Variant.Secondary` $\rightarrow$ Aksen Netral / Muted
* `Variant.Success` $\rightarrow$ Status Berhasil / Hijau
* `Variant.Danger` $\rightarrow$ Status Error / Merah
* `Variant.Warning` $\rightarrow$ Status Peringatan / Oranye
* `Variant.Info` $\rightarrow$ Status Informasi / Cyan

---

## 3. Katalog Komponen UI Lengkap

### 3.1 Buttons & Form Controls

#### 🔘 `Button` & `IconButton`
Dilengkapi debounce anti-spam, visual wait state, dan auto-timeout recovery (10s):
```kotlin
Button(
    text = "Proses Batch",
    variant = Variant.Primary,
    isLoading = isProcessing,
    loadingText = "Wait...",
    onClick = { startHeavyBatch() }
)
```

#### 🎚️ `RangeSlider` (Dual Thumb)
Untuk filter rentang eksposur, ISO, atau focal length:
```kotlin
RangeSlider(
    valueRange = 100f..6400f,
    currentRange = selectedIsoRange,
    onRangeChange = { selectedIsoRange = it },
    variant = Variant.Primary
)
```

#### 💊 `SegmentedControl`
Switch tab mode pro (e.g. RGB vs Luma):
```kotlin
SegmentedControl(
    items = listOf("RGB", "Red", "Green", "Blue"),
    selectedIndex = selectedChannel,
    onSelect = { selectedChannel = it }
)
```

---

### 3.2 Cards & Media Containers

#### 🖼️ `Filmstrip`
Horizontal timeline viewer untuk burst shot RAW:
```kotlin
Filmstrip(
    images = currentBatch.images,
    selectedIndex = activeIndex,
    onSelectImage = { activeIndex = it }
)
```

#### 🪟 `SplitPane`
Panel fleksibel resizable untuk perbandingan Before / After:
```kotlin
SplitPane(
    orientation = SplitOrientation.Horizontal,
    initialSplitRatio = 0.5f,
    first = { CanvasBefore() },
    second = { CanvasAfter() }
)
```

---

### 3.3 Overlays, Modals, & Notifications (Toast)

#### 🔔 `GlobalToastManager` & `ToastHost`
Menampilkan pesan status global yang otomatis hilang (*auto-dismiss*):
```kotlin
// Pemanggilan 1-baris dari mana saja:
GlobalToastManager.show(
    message = "Ekspor 100 frame RAW berhasil!",
    variant = Variant.Success,
    position = OverlayPosition.BottomCenter,
    durationMs = 3000L
)

// Root Host di layar utama:
ToastHost()
```

#### 🔍 `Magnifier` (Pixel Loupe)
Kaca pembesar detail piksel (2x–16x) untuk inspeksi noise:
```kotlin
Magnifier(
    zoomFactor = 4.0f,
    loupeSize = 120.dp
) {
    RawImageSurface()
}
```

---

### 3.4 Pro Computational Photography Controls

#### 📈 `ToneCurveEditor`
Editor kurva nada spline interaktif dengan proteksi $NaN$ dan boundary clamping:
```kotlin
ToneCurveEditor(
    variant = Variant.Primary,
    onCurveChanged = { controlPoints ->
        // controlPoints: List<ControlPoint(x, y)>
        updateToneMappingKernel(controlPoints)
    }
)
```

#### 📊 `HistogramViewer`
Visualisasi 256-bin real-time histogram kurva RGB & Luminance:
```kotlin
HistogramViewer(
    redBins = rBins,
    greenBins = gBins,
    blueBins = bBins,
    height = 100.dp
)
```

#### 🏷️ `PresetSelector`
Pemilih profil preset algoritma 1-klik:
```kotlin
PresetSelector(
    selectedPresetId = "night_denoise",
    onSelectPreset = { preset ->
        applyAlgorithmParameters(preset.parameters)
    }
)
```

---

## 4. Sistem Animasi Multi-Chaining

Menggabungkan beberapa animasi (Fade + Slide + Scale) dalam satu modifier deklaratif:

```kotlin
Box(
    modifier = Modifier
        .combinedAnimation(
            visible = isVisible,
            fade = true,
            slide = true,
            zoom = true,
            slideDirection = SlideDirection.FromBottom
        )
) {
    CardContent()
}
```

Tersedia juga animasi mikro:
* `Modifier.pulseAnimation()` $\rightarrow$ Denyut status aktif.
* `Modifier.shakeAnimation(trigger)` $\rightarrow$ Getar saat validasi salah/gagal.
* `shimmerBrush()` $\rightarrow$ Efek skeleton loading berkilau.

---

## 5. Domain & Logic Management

### 5.1 Batch State Manager & Konkurensi
Manajer batch thread-safe berbasis proteksi `synchronized(lock)`:
```kotlin
val batchManager = BatchStateManager()

// Menambah batch dengan validasi path otomatis
val batch = batchManager.addBatch("Night Landscape", rawFilePaths)

// Memilih batch aktif
batchManager.selectBatch(0)
```

---

### 5.2 AI Smart Culling & Sharpness Metric
Otomatis mendeteksi foto tertajam dalam burst shot menggunakan Laplacian Variance Subsampling 4x4 (Zero-Copy):
```kotlin
val rawImages = batch.images

// Hitung metrik ketajaman
val scores = rawImages.map { img ->
    SharpnessMetric.computeSharpness(img.directBuffer, 4000, 3000)
}

// Otomatis assign Best Frame / Hero Frame (★)
val culledImages = SharpnessMetric.autoAssignBestReference(rawImages, scores)
```

---

### 5.3 Algorithm Presets Store
Registry parameter algoritma bawaan dan kustom:
```kotlin
// Mengambil preset bawaan
val preset = PresetStore.getPresetById("astro_stack")

// Menyimpan preset kustom baru
val custom = PresetStore.saveCustomPreset(
    name = "Ultra Astro HDR",
    description = "Stacking 30 frame dengan alignment bintang",
    params = mapOf("alignment_mode" to "feature", "denoise_strength" to 0.50)
)
```

---

### 5.4 Fault-Tolerant Session Recovery
Pencatatan checkpoint progres per frame untuk pemulihan otomatis saat aplikasi tertutup paksa:
```kotlin
// Simpan progres saat memproses:
SessionCheckpointManager.recordProgress(
    batchId = "batch_101",
    total = 50,
    completed = 25,
    lastPath = "D:/Burst/IMG_0025.DNG"
)

// Cek pemulihan saat aplikasi dibuka:
if (SessionCheckpointManager.hasPendingRecovery("batch_101")) {
    val cp = SessionCheckpointManager.getCheckpoint("batch_101")
    resumeBatchFrom(cp.completedFrames)
}
```

---

### 5.5 Image Streamer & Adaptive Chunk Processor
Aliran memori datar ($\le 50\text{ MB}$) untuk burst shot hingga 50MP:
```kotlin
AdaptiveChunkProcessor.processAdaptive(imageItems) { chunk ->
    // Memproses item bertahap (50 -> 100 -> 200 -> 400 item per chunk)
    deleteOrProcessFiles(chunk)
}.collect { progress ->
    println("Progres: ${(progress.progressFraction * 100).toInt()}%")
}
```

---

## 6. Integrasi Taichi AOT C++ Native Pipeline

Pemanggilan kernel komputasi citra langsung ke compiled binary C++ (`.pyd` / `.dll`):

```kotlin
// Paritas 1:1 pemanggilan API Taichi AOT:
TaichiAot.gaussian_blur(directBuffer, kernelSize = 5, sigma = 1.5f)
TaichiAot.color_convert(directBuffer, COLOR_BGR2GRAY)
TaichiAot.resize(sourceBuffer, destBuffer, newWidth = 1920, newHeight = 1080)
```

---

### 🌟 Manfaat Utama LibraryKotlin:
1. **Performa Native C++ Tanpa Beban**: Operasi berat dieksekusi di GPU/C++ binary; Kotlin bertindak sebagai *thin declarator* yang sangat lincah.
2. **Resilience & Zero-Crash**: Imun terhadap $NaN$, drift viewport, memory leaks, dan race conditions.
3. **Pengalaman Pengguna Kelas Pro**: Setara dengan tool fotografi RAW standar industri (Lightroom & Capture One).

---

## 7. API Baru & Perbaikan (Agustus 2026)

### 7.1 ThemeShadow

Representasi shadow dari design tokens:

```kotlin
data class ThemeShadow(
    val offsetX: Dp,
    val offsetY: Dp,
    val blur: Dp,
    val spread: Dp = 0.dp,
    val color: Color,
)

// Akses melalui theme:
val theme = LocalGenericTheme.current
val shadow = theme.shadowMd  // ThemeShadow(offsetX=0.dp, offsetY=2.dp, blur=4.dp, ...)
```

### 7.2 Card dengan onClick

```kotlin
Card(
    title = "My Card",
    onClick = { /* handle click */ },
    content = { /* card content */ }
)
```

### 7.3 Variant.fromString Error Handling

```kotlin
// Throws IllegalArgumentException untuk typo detection
try {
    val variant = Variant.fromString("primery") // typo!
} catch (e: IllegalArgumentException) {
    println(e.message) // "Unknown variant: 'primery'. Valid variants: primary, secondary, ..."
}

// Fallback ke default jika tidak dikenal
val variant = Variant.fromStringOrDefault("invalid", Variant.Secondary)
```

### 7.4 GenericUILibrary Facade

Import semua komponen dalam satu baris:

```kotlin
import org.pixelrefine.genericui.*

// Semua komponen, tema, animasi, domain logic tersedia
Button(text = "Click", variant = Variant.Primary, onClick = { ... })
val batch = BatchStateManager()
TaichiAot.init(arch = "cuda")
```

### 7.5 RangeSlider dengan Drag Gesture

```kotlin
RangeSlider(
    minVal = 0f,
    maxVal = 100f,
    currentRange = 20f..80f,
    onRangeChange = { newRange ->
        println("Range: ${newRange.start} - ${newRange.endInclusive}")
    },
    title = "ISO Range",
    variant = Variant.Primary
)
```

### 7.6 Magnifier dengan Position Tracking

```kotlin
Magnifier(
    zoomFactor = 4.0f,
    loupeSize = 120.dp
) {
    // Content yang akan di-magnify
    Image(bitmap = imageBitmap, contentDescription = "Photo")
}
// Drag untuk menggeser area inspeksi
```

### 7.7 GridContainer dengan Parameter Order yang Diperbaiki

```kotlin
// itemsCount sekarang di posisi pertama (required)
GridContainer(
    itemsCount = 10,
    columns = 3,
    spacing = 8.dp
) { index ->
    // Render item
}
```
