@echo off
setlocal

:: 1. Tentukan path Taichi
set TAICHI_C_API_DIR=e:\APP Developer\Pixel Refine\venv\Lib\site-packages\taichi\_lib\c_api
set TAICHI_INC=%TAICHI_C_API_DIR%\include
set TAICHI_LIB=%TAICHI_C_API_DIR%\lib

:: 2. Output Directory
set OUT_DIR=aot_dll
if not exist "%OUT_DIR%" mkdir "%OUT_DIR%"

echo [Build] Starting Ultra-Optimized Taichi Generic AOT Engine Build...

:: PGO Support (Manual Cycle)
:: Step 1: build_taichi_aot_engine.bat gen
:: Step 2: run tests
:: Step 3: build_taichi_aot_engine.bat use

set PGO_MODE=%1
set PGO_FLAGS=
if "%PGO_MODE%"=="gen" (
    set PGO_FLAGS=-fprofile-generate
    echo [PGO] Generating Profile Data...
)
if "%PGO_MODE%"=="use" (
    set PGO_FLAGS=-fprofile-use
    echo [PGO] Using Profile Data...
)

:: 3. Kompilasi dengan Flag Agresif
:: -O3: Optimasi level maksimal
:: -mavx2 -mfma: Gunakan instruksi vektor hardware
:: -ffast-math: Optimasi floating point agresif
:: -flto: Link Time Optimization (seluruh program)
:: -static: Link statis untuk dependensi GCC
echo [Build] Compiling taichi_aot_engine.dll with AVX2/FMA/LTO...
g++ -shared -o taichi_aot_engine.dll ^
    taichi_aot_engine.cpp ^
    -O3 -march=native -std=c++20 -ffast-math -flto ^
    -mavx2 -mfma ^
    -static -static-libgcc -static-libstdc++ ^
    %PGO_FLAGS% ^
    -I"%TAICHI_INC%" ^
    -L"%TAICHI_LIB%" ^
    -ltaichi_c_api

if %errorlevel% neq 0 (
    echo [Error] Kompilasi gagal.
    exit /b %errorlevel%
)

:: Copy to aot_dll
echo [Build] Copying DLLs to %OUT_DIR%
copy /y "taichi_aot_engine.dll" "%OUT_DIR%\"

echo [Success] Ultra-Optimized Taichi Generic AOT Engine DLL generated successfully!
exit /b 0
