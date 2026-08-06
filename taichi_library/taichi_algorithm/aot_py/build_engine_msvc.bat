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
  set "OUTPUT_DIR=%PROJECT_ROOT%\taichi_library\taichi_algorithm\aot_py\aot_dll\cpu"
)
if /I "%~1"=="vulkan" (
  rem Keep Vulkan/OpenGL desktop bridge ABI-matched to the isolated
  rem vulkan_x86_64_windows target, never the historical pr-vk cache.
  set "TAICHI_LIB=%PROJECT_ROOT%\test_algorithm\aot_targets\build\vulkan_x86_64_windows\out"
  set "OUTPUT_DIR=%PROJECT_ROOT%\taichi_library\taichi_algorithm\aot_py\aot_dll\vulkan"
)
if /I "%~1"=="opengl" (
  rem OpenGL desktop bridge is built against the OpenGL-only profile.  Its
  rem context is selected by the active WGL/EGL/ICD policy at runtime.
  set "TAICHI_LIB=%PROJECT_ROOT%\test_algorithm\aot_targets\build\opengl_x86_64_windows\out"
  set "OUTPUT_DIR=%PROJECT_ROOT%\taichi_library\taichi_algorithm\aot_py\aot_dll\opengl"
)
if /I "%~1"=="cuda" (
  rem CUDA target is configured in the isolated target harness.  The bridge
  rem must link the matching C-API import library; never fall back to a Vulkan
  rem or CPU DLL with a different ABI.
  set "TAICHI_LIB=%PROJECT_ROOT%\test_algorithm\aot_targets\build\cuda_x86_64_windows_nvidia\out"
  set "OUTPUT_DIR=%PROJECT_ROOT%\taichi_library\taichi_algorithm\aot_py\aot_dll\cuda"
)
set "OUTPUT=%OUTPUT_DIR%\taichi_aot_engine.dll"
set "ENGINE_DEFS="
if /I "%~1"=="cuda" set "ENGINE_DEFS=/DPIXEL_REFINE_AOT_DISABLE_OPENGL_INTEROP"
if /I "%~1"=="cpu" set "ENGINE_DEFS=/DPIXEL_REFINE_AOT_DISABLE_OPENGL_INTEROP"

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

cl.exe /nologo /LD /O2 /EHsc /std:c++20 /arch:AVX2 %ENGINE_DEFS% ^
  /Fo"%OUTPUT_DIR%\taichi_aot_engine.obj" ^
  /I"%TAICHI_INC%" ^
  /I"%TAICHI_ROOT%\external\glad\include" ^
  "%SCRIPT_DIR%\taichi_aot_engine.cpp" ^
  /link /OUT:"%OUTPUT%" /LIBPATH:"%TAICHI_LIB%" ^
  /IMPLIB:"%OUTPUT_DIR%\taichi_aot_engine.lib" ^
  taichi_c_api.lib windowscodecs.lib advapi32.lib gdi32.lib user32.lib ole32.lib uuid.lib
if errorlevel 1 exit /b %errorlevel%
rem Target-qualified builds place the bridge beside the import library.  Keep
rem the historical source-tree path as a compatibility fallback for the old
rem CPU/Vulkan profiles.
if exist "%TAICHI_LIB%\taichi_c_api.dll" (
  copy /y "%TAICHI_LIB%\taichi_c_api.dll" "%OUTPUT_DIR%\taichi_c_api.dll" >nul
) else if exist "%TAICHI_ROOT%\build\taichi_c_api.dll" (
  copy /y "%TAICHI_ROOT%\build\taichi_c_api.dll" "%OUTPUT_DIR%\taichi_c_api.dll" >nul
) else (
  echo ERROR: matching taichi_c_api.dll was not found beside the selected import library.
  exit /b 5
)
exit /b %errorlevel%
