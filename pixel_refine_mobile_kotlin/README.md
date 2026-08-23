# Pixel Refine Mobile (Kotlin / Compose Multiplatform) — DEFAULT

Aplikasi mobile **Pixel Refine** versi resmi, ditulis dalam **Kotlin + Compose
Multiplatform** dengan gaya deklaratif, API komponen yang meniru Python
(nama & parameter sama), dan arsitektur **KISS**.

Ini **menggantikan versi Python lama** (`main_mobile.py` + `pixel_refine_mobile/`)
yang telah **dihapus** untuk menghindari duplikasi kode.

Target: **Android** (utama) + **Desktop** (Windows/Linux/macOS) untuk pengujian lokal.
(iOS bisa ditambahkan nanti sesuai `resources/GenericUILibraryKotlin/DESIGN.md`.)

---

## Struktur

```
pixel_refine_mobile_kotlin/
├── settings.gradle.kts / build.gradle.kts / gradle.properties
├── gradle/libs.versions.toml
├── local.properties                 # sdk.dir -> Android SDK (jangan commit)
└── composeApp/src/
    ├── commonMain/kotlin/org/pixelrefine/mobile/
    │   ├── App.kt                   # root + navigasi (mirror AppState)
    │   ├── model/Tool.kt            # Screen, Tool, TOOLS, SAMPLE_BATCHES, LANGUAGES
    │   └── ui/
    │       ├── HomeScreen.kt        # kartu tool (MFDenoiser/MFResolution/HDR/Panorama)
    │       ├── WorkspaceScreen.kt   # batch strip + tab algoritma + preview + progress
    │       └── SettingsScreen.kt    # Language / GPU / Dark Theme / About
    ├── androidMain/                 # MainActivity + AndroidManifest.xml
    └── desktopMain/                 # main() untuk run lokal 360x640

# Komponen UI & Tema terisolasi mandiri di:
resources/GenericUILibraryKotlin/    # Modul Gradle :generic-ui-kotlin
├── build.gradle.kts
├── tokens/design_tokens.json
└── src/commonMain/kotlin/org/pixelrefine/genericui/
    ├── theme/GenericTheme.kt        # Light/Dark design tokens
    └── components/                  # Button, Card, Container, Row, Col, Spacer, Switch, dll.
```

## Jalankan (Desktop — tanpa emulator)

Padanan `python main_desktop.py` untuk development: **kompilasi inkremental +
langsung jalankan** (tanpa packaging APK). Setelah build pertama, siklus dev cepat.

**Cara termudah (sekali klik / satu perintah):**
```powershell
cd pixel_refine_mobile_kotlin
.\run_dev.bat        # atau: powershell -File run_dev.ps1
```

Atau manual dengan toolchain yang disediakan oleh environment:
```powershell
$env:PIXEL_REFINE_MOBILE_TOOLCHAIN_ROOT="<toolchain-root>"
# Atau set JAVA_HOME, ANDROID_HOME, GRADLE_USER_HOME dan gradle pada PATH.
cd pixel_refine_mobile_kotlin
gradle :composeApp:run          # ← task dev run (bukan :composeApp:desktopRun)
```

> Catatan: gunakan `:composeApp:run`. `:composeApp:desktopRun` adalah task KMP
> *carrier* yang tidak punya mainClass (akan gagal). Untuk auto-restart saat file
> berubah (dev loop), tambahkan `--continuous`: `gradle :composeApp:run --continuous`.

## Build APK (Android)

Dengan Android SDK yang sudah terpasang (di `local.properties`):

```powershell
gradle :composeApp:assembleDebug
# APK: composeApp/build/outputs/apk/debug/composeApp-debug.apk
```

Atau buka folder ini di **Android Studio** → biarkan sinkronisasi → **Run ▶**.
Catatan: build APK memerlukan SDK Android lengkap (sudah disiapkan di
toolchain yang dikonfigurasi dengan platform android-35 + build-tools 35.0.0).
Toolchain build (JDK 17, Gradle, Android SDK, cache) tersentralisasi di
`PIXEL_REFINE_MOBILE_TOOLCHAIN_ROOT`; lihat
`ai_governance/knowledge/build-config/build-toolchain.md`.

## Konsistensi gaya (1:1)

- Semua warna/radius/spacing/font diambil 1:1 dari
  `resources/GenericUILibraryKotlin/tokens/design_tokens.json`
  (ekstraksi `resources/GenericUILibrary/theme.py`, tervalidasi 0 mismatch).
- Nama komponen & parameter meniru Python (`Button(text, variant, onClick)`,
  `Card(title)`, `Container(padding)`, `ProgressBar(value)`, dll).
- Tombol mobile = **solid variant + teks putih bold** (gaya `Button.to_qml()`);
  radius 5, kartu radius 8, border `borderColor` 1px.
