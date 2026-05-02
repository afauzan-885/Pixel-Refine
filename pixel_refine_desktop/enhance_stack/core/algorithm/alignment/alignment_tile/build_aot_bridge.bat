@echo off
setlocal

:: 1. Tentukan path Taichi (Manual venv path sesuai request)
set TAICHI_C_API_DIR=e:\APP Developer\Pixel Refine\venv\Lib\site-packages\taichi\_lib\c_api
set TAICHI_INC=%TAICHI_C_API_DIR%\include
set TAICHI_LIB=%TAICHI_C_API_DIR%\lib

:: 2. Output Directory
set OUT_DIR=..\..\..\..\..\ui\data

echo [Build] Starting Modular AOT Build...

:: 3. Kompilasi Preprocessing
echo [Build] Compiling preprocessing_aot.dll...
g++ -shared -o preprocessing_aot.dll ^
    preprocessing_aot.cpp ^
    -O3 -march=native -std=c++20 -ffast-math ^
    -I"%TAICHI_INC%" ^
    -L"%TAICHI_LIB%" ^
    -ltaichi_c_api

:: 4. Kompilasi Compute Flow
echo [Build] Compiling compute_flow_aot.dll...
g++ -shared -o compute_flow_aot.dll ^
    compute_flow_aot.cpp ^
    -O3 -march=native -std=c++20 -ffast-math ^
    -I"%TAICHI_INC%" ^
    -L"%TAICHI_LIB%" ^
    -ltaichi_c_api

:: 5. Kompilasi Warp
echo [Build] Compiling warp_aot.dll...
g++ -shared -o warp_aot.dll ^
    warp_aot.cpp ^
    -O3 -march=native -std=c++20 -ffast-math ^
    -I"%TAICHI_INC%" ^
    -L"%TAICHI_LIB%" ^
    -ltaichi_c_api

if %errorlevel% neq 0 (
    echo [Error] Kompilasi gagal.
    pause
    exit /b %errorlevel%
)

:: Copy to ui/data if it exists
if exist "%OUT_DIR%" (
   echo [Build] Copying DLLs to %OUT_DIR%
   copy /y "preprocessing_aot.dll" "%OUT_DIR%\"
   copy /y "compute_flow_aot.dll" "%OUT_DIR%\"
   copy /y "warp_aot.dll" "%OUT_DIR%\"
)

echo [Success] Semantic Modular DLLs generated successfully!
exit /b 0
