@echo off
setlocal
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\Common7\Tools\VsDevCmd.bat" -arch=x64 -host_arch=x64
if errorlevel 1 exit /b %errorlevel%
pushd "%~dp0..\..\..\test_algorithm\taichi_upstream\stable-v1.7.4-development"
cmake --build build\pr-vk --target taichi_c_api -j8
set "RESULT=%ERRORLEVEL%"
popd
exit /b %RESULT%
