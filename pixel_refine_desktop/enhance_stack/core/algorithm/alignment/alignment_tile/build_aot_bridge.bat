@echo off
setlocal

:: 1. Tentukan path Taichi (Manual venv path sesuai request)
set TAICHI_C_API_DIR=e:\APP Developer\Pixel Refine\venv\Lib\site-packages\taichi\_lib\c_api
set TAICHI_INC=%TAICHI_C_API_DIR%\include
set TAICHI_LIB=%TAICHI_C_API_DIR%\lib

:: 2. Nama File
set SRC=alignment_aot.cpp
set DLL=preprocessing_aot.dll
set OUT_DIR=..\..\..\..\..\ui\data

echo [Build] Compiling %SRC% to %DLL%...

:: 3. Kompilasi menggunakan g++ (Optimal Flags)
g++ -shared -o %DLL% ^
    -DALIGNMENT_AOT_EXPORTS ^
    %SRC% ^
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
   echo [Build] Copying %DLL% to %OUT_DIR%
   copy /y "%DLL%" "%OUT_DIR%\"
)

echo [Success] %DLL% berhasil dibuat!
exit /b 0
