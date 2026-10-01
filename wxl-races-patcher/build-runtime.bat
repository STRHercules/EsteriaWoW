@echo off
setlocal
call "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvarsall.bat" x86
if errorlevel 1 exit /b %errorlevel%
cl.exe /nologo /std:c++17 /O2 /EHsc /LD "%~dp0DarkfallenCharacterSelect.cpp" /Fo"%~dp0DarkfallenCharacterSelect.obj" /link /OUT:"%~dp0darkfallen-character-select.next.dll" /IMPLIB:"%~dp0DarkfallenCharacterSelect.lib"
exit /b %errorlevel%
