@echo off
setlocal
call "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvarsall.bat" x86
if not "%errorlevel%"=="0" exit /b %errorlevel%
if "%~1"=="" exit /b 2
if not exist "%~1" mkdir "%~1"
cl.exe /nologo /std:c++20 /O2 /EHsc /MT /LD "%~dp0NativeAppearance.cpp" /Fo"%~1\NativeAppearance.obj" /link /DEF:"%~dp0NativeAppearance.def" /OUT:"%~1\EsteriaAppearance.dll" /IMPLIB:"%~1\EsteriaAppearance.lib"
if not "%errorlevel%"=="0" exit /b %errorlevel%
cl.exe /nologo /std:c++20 /O2 /EHsc /MT "%~dp0TestNativeAppearance.cpp" /Fo"%~1\TestNativeAppearance.obj" /link /OUT:"%~1\TestNativeAppearance.exe"
if not "%errorlevel%"=="0" exit /b %errorlevel%
"%~1\TestNativeAppearance.exe" "%~1\EsteriaAppearance.dll"
if not "%errorlevel%"=="0" exit /b %errorlevel%
cl.exe /nologo /std:c++20 /O2 /EHsc /MT "%~dp0TestHighmountainMaterials.cpp" /Fo"%~1\TestHighmountainMaterials.obj" /link /DYNAMICBASE:NO /BASE:0x04000000 /OUT:"%~1\TestHighmountainMaterials.exe"
if not "%errorlevel%"=="0" exit /b %errorlevel%
"%~1\TestHighmountainMaterials.exe" "%~1\EsteriaAppearance.dll"
if not "%errorlevel%"=="0" exit /b %errorlevel%
cl.exe /nologo /std:c++20 /O2 /EHsc /MT "%~dp0TestCustomizationChoices.cpp" /Fo"%~1\TestCustomizationChoices.obj" /link /DYNAMICBASE:NO /BASE:0x04000000 /OUT:"%~1\TestCustomizationChoices.exe"
if not "%errorlevel%"=="0" exit /b %errorlevel%
"%~1\TestCustomizationChoices.exe" "%~1\EsteriaAppearance.dll"
if not "%errorlevel%"=="0" exit /b %errorlevel%
cl.exe /nologo /std:c++20 /O2 /EHsc /MT "%~dp0TestCosmeticWings.cpp" /Fo"%~1\TestCosmeticWings.obj" /link /DYNAMICBASE:NO /BASE:0x04000000 /OUT:"%~1\TestCosmeticWings.exe"
if not "%errorlevel%"=="0" exit /b %errorlevel%
if exist "%~1\EsteriaCosmeticWings.bin" "%~1\TestCosmeticWings.exe" "%~1\EsteriaAppearance.dll"
exit /b %errorlevel%
