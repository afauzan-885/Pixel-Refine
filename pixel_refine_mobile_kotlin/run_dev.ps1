# Development run - setara `python main_desktop.py` untuk mobile Kotlin.
# Menjalankan aplikasi desktop (viewport 360x640) TANPA packaging APK.
# Setelah build pertama, gradle kompilasi inkremental (cepat).
$build = "D:\development_build"
$env:JAVA_HOME = "$build\jdk17\jdk-17.0.20+8"
$env:ANDROID_HOME = "$build\android-sdk"
$env:GRADLE_USER_HOME = "$build\.gradle"
$env:Path = "$env:JAVA_HOME\bin;$build\gradle-8.10.2\bin;$env:Path"
Set-Location $PSScriptRoot
Write-Host "[Pixel Refine Mobile] Dev run - gradle :composeApp:run"
gradle :composeApp:run
