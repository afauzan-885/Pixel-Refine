# LibraryKotlin (Generic UI Kotlin Multiplatform)

> 📖 **[Lihat Dokumentasi Lengkap & Panduan API (API_DOCUMENTATION.md)](API_DOCUMENTATION.md)**

Porting lengkap **GenericUILibrary** dari PySide6/Python ke **Kotlin Multiplatform (Compose Multiplatform)** yang mendukung **Desktop (JVM)** dan **Android**.

---

## 🚀 Fitur Utama

1. **85+ Komponen UI**: Button, Card, Filmstrip, HistogramViewer, ToneCurveEditor, SplitPane, Magnifier, Toast, PresetSelector, Typography, Slider, Tooltip, Drawer, Alert, Chip, Avatar, Divider, DatePicker, Snackbar, Notification, Popover, dan banyak lagi.
2. **Animasi Multi-Chaining**: `Modifier.combinedAnimation` (Fade, Slide, Scale), Shake, Pulse, Shimmer.
3. **Logic Domain Tangguh**: Smart AI Culling (Laplacian Sharpness), Preset Store, Fault-Tolerant Session Recovery, Adaptive Chunk Processor, Form Validation, Markdown, CodeBlock.
4. **Zero-Config Taichi AOT Native**: Memanggil langsung kernel citra terkompilasi C++ (`.pyd` / `.dll`).

---

## 📊 Status Implementasi

### ✅ Bug Fixes Sebelumnya
16 bug fungsional telah diperbaiki (lihat LIBRARY_KOTLIN_FIXES.md).

### 🆕 Penambahan Fitur Terbaru (Agustus 2026)

**50+ Komponen Baru** ditambahkan dalam 11 batch:

| Batch | Kategori | Jumlah |
|---|---|---|
| 1 | Core UI (Typography, Slider, Tooltip, Divider, Avatar, Chips) | 6 |
| 2 | Input & Forms (NumberInput, TextArea, SearchInput, CheckboxGroup, DatePicker) | 5 |
| 3 | Feedback (Alert, Snackbar, Notification, Popover) | 4 |
| 4 | Navigation (Breadcrumbs, Pagination, Steps) | 3 |
| 5 | Layout (Drawer, BottomSheet, Resizable) | 3 |
| 6 | Data Display (Statistic, Descriptions, Timeline, Comment) | 4 |
| 7 | Advanced Input (Autocomplete, Transfer, TreeView, ColorPicker) | 4 |
| 8 | Media (ImageComponent, FileUpload, QRCode) | 3 |
| 9 | Interactive (Rating, Tour, FloatButton, SpeedDial) | 4 |
| 10 | Utility (Anchor, Affix, BackToTop, Watermark, ConfigProvider, CopyButton) | 6 |
| 11 | Low Priority (VirtualList, InfiniteScroll, Responsive, Accessibility, KeyboardShortcuts, DragDrop, ContextMenu, Menu, SkeletonVariants, CodeBlock, Markdown, FormValidation) | 12 |

### 🧪 Test Coverage

**300+ test cases** dalam 16 file test:

| File Test | Jumlah Test |
|---|---|
| Batch1ComponentsTest.kt | 38 |
| Batch2To11ComponentsTest.kt | 50+ |
| ComponentInteractionTest.kt | 73 |
| ConcurrentStressTest.kt | 26 |
| TaichiAotIntegrationTest.kt | 25 |
| AdvancedFeaturesTest.kt | 5 |
| ConcurrentExtremeStressTest.kt | 4 |
| ExtendedComponentsTest.kt | 1 |
| LogicParityTest.kt | 5 |
| ProFeaturesTestSuite.kt | 3 |
| PythonicApiParityTest.kt | 1 |
| RealWorldStressTest.kt | 1 |
| TaichiAotNativePipelineTest.kt | 1 |
| TaichiAotParityTest.kt | 2 |
| UiParityHarnessTest.kt | 3 |
| UltimateAuditorStressTest.kt | 5 |

---

## 🏗️ Arsitektur

```
resources/LibraryKotlin/
├── GenericUILibrary.kt          # Facade exports (semua 85+ komponen)
├── components/                  # 80+ UI components
├── theme/                       # Light + Dark themes
├── animations/                  # 7 animation files
├── domain/                      # 10 subdirectories
├── tests/                       # 16 test files, 300+ test cases
├── tokens/                      # Design tokens JSON
└── build.gradle.kts
```

---

## 🎯 Cara Penggunaan

### Import Semua Komponen
```kotlin
import org.pixelrefine.genericui.*
```

### Theme Provider
```kotlin
GenericThemeProvider(theme = DarkTheme) {
    Button(text = "Click Me", variant = Variant.Primary, onClick = { ... })
}
```

### Pythonic 1-Line API (60+ aliases)
```kotlin
// Original
toast("Proses selesai!", Variant.Success)
auto_cull(images, buffers, 4000, 3000)

// New (Batch 1-11)
h1("Heading 1")
slider(value = 0.5f, on_change = { /* ... */ })
tooltip("Help text") { Button("Help") }
divider()
avatar(initials = "JD")
chip("Filter", selected = true)
search_input(value = "", on_change = { /* ... */ })
alert(title = "Success", variant = Variant.Success)
drawer(visible = true, on_dismiss = { /* ... */ })
statistic(value = "1.2K", label = "Total Users", trend = StatTrend.Up)
rating(value = 4.5f, on_change = { /* ... */ })
file_upload(on_file_selected = { /* ... */ })
back_to_top(visible = true, on_click = { /* ... */ })
markdown("# Hello World")
code_block(code = "fun main() {}", language = "kotlin")
validated_input(value = "", on_change = { /* ... */ }, config = ValidationConfig(...))
```

### Taichi AOT Processing
```kotlin
TaichiAot.init(arch = "cuda")
val gpuBuffer = TaichiAot.upload(buffer, width, height)
val blurred = TaichiAot.gaussian_blur(gpuBuffer, ksize = Pair(5, 5))
TaichiAot.destroy()
```

---

## 📋 Persyaratan Build

- Kotlin 2.x + Compose Multiplatform plugin
- JDK 17+
- Gradle 8.x
- Target: Desktop (JVM) + Android

---

## 🔗 Tautan Terkait

- [API Documentation](API_DOCUMENTATION.md) - Panduan API lengkap
- [Design Document](DESIGN.md) - Rancangan port dari PySide6
- [Design Tokens](tokens/design_tokens.json) - Token desain JSON
- [AI Governance](../../ai_governance/) - Aturan dan protokol AI agent
- [LibraryKotlin Fixes Report](../../ai_governance/LIBRARY_KOTLIN_FIXES.md) - Laporan perbaikan bug dan fitur
