@echo off
setlocal EnableExtensions

set "SCRIPT_DIR=%~dp0."
set "PROJECT_ROOT=%~dp0..\..\.."
set "TAICHI_ROOT=%PROJECT_ROOT%\test_algorithm\taichi_upstream\stable-v1.7.4-development"
set "VSDEVCMD=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\Common7\Tools\VsDevCmd.bat"
set "TAICHI_INC=%TAICHI_ROOT%\c_api\include"
set "TAICHI_LIB=%TAICHI_ROOT%\build\pr-msvc"
set "OUTPUT_DIR=%TAICHI_ROOT%\build\pr-bridge"
if /I "%~1"=="vulkan" (
  set "TAICHI_LIB=%TAICHI_ROOT%\build\pr-vk"
  set "OUTPUT_DIR=%TAICHI_ROOT%\build\pr-vk-bridge"
)
set "OUTPUT=%OUTPUT_DIR%\taichi_aot_engine.dll"

if not exist "%VSDEVCMD%" (
  echo ERROR: Visual Studio 2022 Build Tools were not found.
  exit /b 2
)
if not exist "%TAICHI_INC%\taichi\cpp\taichi.hpp" (
  echo ERROR: Taichi C-API headers were not found at %TAICHI_INC%.
  exit /b 3
)
if not exist "%TAICHI_LIB%\taichi_c_api.lib" (
  echo ERROR: Build taichi_c_api with pixel_refine_native_tests.bat first.
  exit /b 4
)

call "%VSDEVCMD%" -arch=x64 -host_arch=x64
if errorlevel 1 exit /b %errorlevel%
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

cl.exe /nologo /LD /O2 /EHsc /std:c++20 /arch:AVX2 ^
  /Fo"%OUTPUT_DIR%\taichi_aot_engine.obj" ^
  /I"%TAICHI_INC%" ^
  "%SCRIPT_DIR%\taichi_aot_engine.cpp" ^
  /link /OUT:"%OUTPUT%" /LIBPATH:"%TAICHI_LIB%" ^
  /IMPLIB:"%OUTPUT_DIR%\taichi_aot_engine.lib" ^
  taichi_c_api.lib windowscodecs.lib ole32.lib uuid.lib
if errorlevel 1 exit /b %errorlevel%
copy /y "%TAICHI_ROOT%\build\taichi_c_api.dll" "%OUTPUT_DIR%\taichi_c_api.dll" >nul
exit /b %errorlevel%
