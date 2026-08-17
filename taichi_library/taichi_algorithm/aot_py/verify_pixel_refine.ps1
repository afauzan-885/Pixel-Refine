[CmdletBinding()]
param(
    [switch]$SkipBuild,
    [int]$VulkanDevice = 1,
    [switch]$SkipLargeRemap
)

$ErrorActionPreference = "Stop"
$project = (Resolve-Path (Join-Path $PSScriptRoot "../../..")).Path
$repo = Join-Path $project "test_algorithm/taichi_upstream/stable-v1.7.4-development"
$python = Join-Path $project "venv/Scripts/python.exe"
$wheelVenv = Join-Path $repo "build/wheel-test-venv/Scripts/python.exe"

if (-not (Test-Path $python)) { throw "Python venv tidak ditemukan: $python" }
if (-not (Test-Path $repo)) { throw "Checkout Taichi tidak ditemukan: $repo" }

$env:PYTHONPATH = $project
$env:PIXEL_REFINE_AOT_DEVICE = [string]$VulkanDevice
$env:PIXEL_REFINE_AOT_AUTOSCAN = "1"

if (-not $SkipBuild) {
    Push-Location $repo
    try { cmd /c build_pixel_refine_wheel.bat
          if ($LASTEXITCODE -ne 0) { throw "Build wheel gagal ($LASTEXITCODE)" } }
    finally { Pop-Location }
}

$wheel = Get-ChildItem (Join-Path $repo "dist/taichi-*.whl") |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1
if ($null -eq $wheel) { throw "Wheel Taichi tidak ditemukan di $repo/dist" }

& $python -m pip install --force-reinstall --no-deps $wheel.FullName
if ($LASTEXITCODE -ne 0) { throw "Instalasi wheel ke venv gagal" }

& $python (Join-Path $PSScriptRoot "test_wheel_backends.py")
& $python (Join-Path $PSScriptRoot "test_aot_artifact_determinism.py")
if ($LASTEXITCODE -ne 0) { throw "Determinisme artefak gagal ($LASTEXITCODE)" }

function Invoke-Comprehensive([string]$Backend) {
    $env:PIXEL_REFINE_AOT_ARCH = $Backend
    if ($Backend -eq "cpu") { $env:PIXEL_REFINE_AOT_DEVICE = "0" }
    else { $env:PIXEL_REFINE_AOT_DEVICE = [string]$VulkanDevice }
    & $python (Join-Path $PSScriptRoot "tests/test_comprehensif.py")
    if ($LASTEXITCODE -ne 0) { throw "Suite komprehensif $Backend gagal ($LASTEXITCODE)" }
}

Invoke-Comprehensive "cpu"
& $python (Join-Path $PSScriptRoot "test_normalize_aot.py")
& $python (Join-Path $PSScriptRoot "test_gamma_proxy_aot.py")
if ($LASTEXITCODE -ne 0) { throw "Normalize/gamma CPU suite gagal ($LASTEXITCODE)" }
Invoke-Comprehensive "vulkan"
& $python (Join-Path $PSScriptRoot "test_normalize_aot.py")
& $python (Join-Path $PSScriptRoot "test_gamma_proxy_aot.py")
if ($LASTEXITCODE -ne 0) { throw "Normalize/gamma Vulkan suite gagal ($LASTEXITCODE)" }

# Optical-flow artifacts are Vulkan-only in the current AOT set.
$env:PIXEL_REFINE_AOT_ARCH = "vulkan"
$env:PIXEL_REFINE_AOT_DEVICE = [string]$VulkanDevice
& $python (Join-Path $PSScriptRoot "test_optical_flow_aot.py")
if ($LASTEXITCODE -ne 0) { throw "Optical-flow AOT suite gagal ($LASTEXITCODE)" }

if (-not $SkipLargeRemap) {
    $env:PIXEL_REFINE_AOT_ARCH = "cpu"
    $env:PIXEL_REFINE_AOT_DEVICE = "0"
    & $python (Join-Path $PSScriptRoot "test_remap_memory.py")
    if ($LASTEXITCODE -ne 0) { throw "Remap 12MP accuracy/memory gate gagal ($LASTEXITCODE)" }
}

$env:PIXEL_REFINE_AOT_ARCH = "cpu"
$env:PIXEL_REFINE_AOT_DEVICE = "0"
& $python (Join-Path $PSScriptRoot "test_aot_cpu_lifecycle.py")
if ($LASTEXITCODE -ne 0) { throw "Lifecycle CPU gagal ($LASTEXITCODE)" }
& $python (Join-Path $PSScriptRoot "test_aot_backend_parity.py") --compare --compare-backend vulkan --device $VulkanDevice
if ($LASTEXITCODE -ne 0) { throw "Parity CPU/Vulkan gagal ($LASTEXITCODE)" }

Write-Host "VERIFICATION PASSED: wheel=$($wheel.Name), vulkan_device=$VulkanDevice" -ForegroundColor Green
