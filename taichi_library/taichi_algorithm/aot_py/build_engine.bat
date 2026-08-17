@echo off
setlocal
rem Deprecated compatibility wrapper. The supported Windows bridge build is
rem build_engine_msvc.bat and uses Visual Studio 2022/LLVM20; this wrapper
rem intentionally has no GCC/MinGW/MSYS2 fallback.
call "%~dp0build_engine_msvc.bat" %*
exit /b %errorlevel%
