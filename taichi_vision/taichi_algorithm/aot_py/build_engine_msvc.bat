@echo off
setlocal EnableExtensions

set "SCRIPT_DIR=%~dp0."
set "PROJECT_ROOT=%~dp0..\..\.."
set "TAICHI_ROOT=%PROJECT_ROOT%\test_algorithm\taichi_upstream\stable-v1.7.4-development"
set "VSDEVCMD=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\Common7\Tools\VsDevCmd.bat"
set "TAICHI_INC=%TAICHI_ROOT%\c_api\include"
rem OpenGL and Vulkan are enabled together in the production pr-vk build.  The
rem old pr-msvc cache has both GPU backends disabled and cannot link this
rem bridge reliably, so use the feature-complete cache by default.
set "TAICHI_LIB=%TAICHI_ROOT%\build\pr-vk"
set "OUTPUT_DIR=%TAICHI_ROOT%\build\pr-vk-bridge"
if /I "%~1"=="cpu" (
  rem Use the isolated, target-qualified CPU runtime.  Linking the old
  rem source-tree pr-msvc cache can silently mix an older C-API ABI and hang
  rem during init when the x86_64 bridge loads beside fresh TCM artifacts.
  set "TAICHI_LIB=%PROJECT_ROOT%\test_algorithm\aot_targets\build\cpu_x86_64_windows\out"
  set "OUTPUT_DIR=%PROJECT_ROOT%\taichi_vision\taichi_algorithm\aot_py\aot_dll\cpu"
)
if /I "%~1"=="vulkan" (
  rem Keep Vulkan/OpenGL desktop bridge ABI-matched to the isolated
  rem vulkan_x86_64_windows target, never the historical pr-vk cache.
  set "TAICHI_LIB=%PROJECT_ROOT%\test_algorithm\aot_targets\build\vulkan_x86_64_windows\out"
  set "OUTPUT_DIR=%PROJECT_ROOT%\taichi_vision\taichi_algorithm\aot_py\aot_dll\vulkan"
)
if /I "%~1"=="opengl" (
  rem OpenGL desktop bridge is built against the OpenGL-only profile.  Its
  rem context is selected by the active WGL/EGL/ICD policy at runtime.
  set "TAICHI_LIB=%PROJECT_ROOT%\test_algorithm\aot_targets\build\opengl_x86_64_windows\out"
  set "OUTPUT_DIR=%PROJECT_ROOT%\taichi_vision\taichi_algorithm\aot_py\aot_dll\opengl"
)
if /I "%~1"=="cuda" (
  rem CUDA target is configured in the isolated target harness.  The bridge
  rem must link the matching C-API import library; never fall back to a Vulkan
  rem or CPU DLL with a different ABI.
  set "TAICHI_LIB=%PROJECT_ROOT%\test_algorithm\aot_targets\build\cuda_x86_64_windows_nvidia\out"
  set "OUTPUT_DIR=%PROJECT_ROOT%\taichi_vision\taichi_algorithm\aot_py\aot_dll\cuda"
)
rem Optional isolated validation override.  This is useful when a newer
rem LLVM/CUDA C-API build is being tested: it keeps the public bridge output
rem and the historical target cache untouched.
if defined PIXEL_REFINE_TAICHI_LIB set "TAICHI_LIB=%PIXEL_REFINE_TAICHI_LIB%"
if defined PIXEL_REFINE_BRIDGE_OUTPUT_DIR set "OUTPUT_DIR=%PIXEL_REFINE_BRIDGE_OUTPUT_DIR%"
set "OUTPUT=%OUTPUT_DIR%\taichi_aot_engine.dll"
set "ENGINE_DEFS="
if /I "%~1"=="cuda" set "ENGINE_DEFS=/DPIXEL_REFINE_AOT_DISABLE_OPENGL_INTEROP"
if /I "%~1"=="cpu" set "ENGINE_DEFS=/DPIXEL_REFINE_AOT_DISABLE_OPENGL_INTEROP"

rem The bridge contains an AVX2 fast path for host buffer conversion.  Keep
rem the historical AVX2 build as the default, but allow a baseline/SSE2 DLL
rem for older x86-64 CPUs.  The second argument (or environment variable)
rem selects the profile without changing the exported ABI:
rem   build_engine_msvc.bat cpu avx2       -> taichi_aot_engine.dll
rem   build_engine_msvc.bat cpu baseline   -> taichi_aot_engine_baseline.dll
set "BRIDGE_ISA=%PIXEL_REFINE_BRIDGE_ISA%"
if not "%~2"=="" set "BRIDGE_ISA=%~2"
if "%BRIDGE_ISA%"=="" set "BRIDGE_ISA=avx2"
set "BRIDGE_ARCH=/arch:AVX2"
set "BRIDGE_ISA_DEFS="
set "BRIDGE_SUFFIX="
if /I "%BRIDGE_ISA%"=="baseline" (
  set "BRIDGE_ARCH=/arch:SSE2"
  set "BRIDGE_ISA_DEFS=/DPIXEL_REFINE_AOT_BASELINE"
  set "BRIDGE_SUFFIX=_baseline"
) else if /I "%BRIDGE_ISA%"=="avx2" (
  rem Keep the optimized default profile.
) else (
  echo ERROR: unsupported bridge ISA "%BRIDGE_ISA%". Use avx2 or baseline.
  exit /b 6
)
set "OUTPUT=%OUTPUT_DIR%\taichi_aot_engine%BRIDGE_SUFFIX%.dll"

rem Link-time optimization keeps the exported C ABI unchanged while allowing
rem MSVC to inline the hot buffer-conversion and dispatch glue across this
rem translation unit.  Set PIXEL_REFINE_BRIDGE_NO_LTO=1 for a diagnostic build
rem with the older per-file optimizer only.
set "LTO_COMPILE=/GL"
set "LTO_LINK=/LTCG /OPT:REF /OPT:ICF"
if "%PIXEL_REFINE_BRIDGE_NO_LTO%"=="1" (
  set "LTO_COMPILE="
  set "LTO_LINK="
)

rem LLVM20's Windows static package is built with the static MSVC CRT.  Keep
rem the bridge on the same CRT by default; an explicitly DLL-CRT toolchain can
rem opt in with PIXEL_REFINE_BRIDGE_CRT=MD.
set "BRIDGE_CRT=%PIXEL_REFINE_BRIDGE_CRT%"
if "%BRIDGE_CRT%"=="" set "BRIDGE_CRT=MT"
if /I not "%BRIDGE_CRT%"=="MT" if /I not "%BRIDGE_CRT%"=="MD" (
  echo ERROR: unsupported bridge CRT "%BRIDGE_CRT%". Use MT or MD.
  exit /b 7
)
set "BRIDGE_CRT_FLAG=/%BRIDGE_CRT%"

if not exist "%VSDEVCMD%" (
  echo ERROR: Visual Studio 2022 Build Tools were not found.
  exit /b 2
)
if not exist "%TAICHI_INC%\taichi\cpp\taichi.hpp" (
  echo ERROR: Taichi C-API headers were not found at %TAICHI_INC%.
  exit /b 3
)
if not exist "%TAICHI_LIB%\taichi_c_api.lib" (
  echo ERROR: Matching taichi_c_api.lib was not found in "%TAICHI_LIB%".
  echo        Configure/build the MSVC CUDA profile before building this bridge.
  exit /b 4
)

call "%VSDEVCMD%" -arch=x64 -host_arch=x64
if errorlevel 1 exit /b %errorlevel%
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

cl.exe /nologo /LD /O2 %LTO_COMPILE% %BRIDGE_CRT_FLAG% /EHsc /std:c++20 %BRIDGE_ARCH% %ENGINE_DEFS% %BRIDGE_ISA_DEFS% ^
  /Fo"%OUTPUT_DIR%\taichi_aot_engine%BRIDGE_SUFFIX%.obj" ^
  /I"%TAICHI_INC%" ^
  /I"%TAICHI_ROOT%\external\glad\include" ^
  "%SCRIPT_DIR%\taichi_aot_engine.cpp" ^
  /link %LTO_LINK% /OUT:"%OUTPUT%" /LIBPATH:"%TAICHI_LIB%" ^
  /IMPLIB:"%OUTPUT_DIR%\taichi_aot_engine%BRIDGE_SUFFIX%.lib" ^
  taichi_c_api.lib windowscodecs.lib advapi32.lib gdi32.lib user32.lib ole32.lib uuid.lib
if errorlevel 1 exit /b %errorlevel%
rem Target-qualified builds place the bridge beside the import library.  Keep
rem the historical source-tree path as a compatibility fallback for the old
rem CPU/Vulkan profiles.
if exist "%TAICHI_LIB%\taichi_c_api.dll" (
  copy /y "%TAICHI_LIB%\taichi_c_api.dll" "%OUTPUT_DIR%\taichi_c_api.dll" >nul
) else if defined PIXEL_REFINE_TAICHI_C_API_DLL if exist "%PIXEL_REFINE_TAICHI_C_API_DLL%" (
  copy /y "%PIXEL_REFINE_TAICHI_C_API_DLL%" "%OUTPUT_DIR%\taichi_c_api.dll" >nul
) else if exist "%TAICHI_ROOT%\build\taichi_c_api.dll" (
  copy /y "%TAICHI_ROOT%\build\taichi_c_api.dll" "%OUTPUT_DIR%\taichi_c_api.dll" >nul
) else (
  echo ERROR: matching taichi_c_api.dll was not found beside the selected import library.
  exit /b 5
)
exit /b %errorlevel%
