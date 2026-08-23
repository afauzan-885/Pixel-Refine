# Development run - setara `python main_desktop.py` untuk mobile Kotlin.
# Menjalankan aplikasi desktop (viewport 360x640) TANPA packaging APK.
# Setelah build pertama, gradle kompilasi inkremental (cepat).
$build = $env:PIXEL_REFINE_MOBILE_TOOLCHAIN_ROOT
if ($build) {
    $env:JAVA_HOME = Join-Path $build "jdk17"
    $env:ANDROID_HOME = Join-Path $build "android-sdk"
    $env:GRADLE_USER_HOME = Join-Path $build ".gradle"
    $gradleBin = Join-Path $build "gradle-8.10.2\bin"
    $env:Path = "$gradleBin;$env:Path"
} else {
    Write-Host "[Pixel Refine Mobile] Menggunakan JAVA_HOME, ANDROID_HOME, dan gradle dari environment/PATH."
}
Set-Location $PSScriptRoot
Write-Host "[Pixel Refine Mobile] Dev run - gradle :composeApp:run"
gradle :composeApp:run
