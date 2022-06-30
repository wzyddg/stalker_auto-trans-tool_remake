@echo off
setlocal EnableDelayedExpansion
color 1e
cd /d %0\..
set WORKDIR=%CD%
set MYTEMP=%WORKDIR%\~temp
set MYDATA=%WORKDIR%\Data
set OUTDIR=%WORKDIR%\gamedata
for /f "tokens=2 delims=:" %%i in ('chcp') do set /a CP=%%i
if exist "%MYDATA%\strings_%CP%.txt" (
set STRTXT=%MYDATA%\strings_%CP%.txt
) else (
set STRTXT=%MYDATA%\strings.txt
)
for /f "tokens=*" %%i in ('cscript /nologo /E:JScript "%MYDATA%\strings.js" "%STRTXT%" 29') do title %%i
for /f "eol=; tokens=1,* delims==" %%i in (config.ini) do set %%i=%%j
set CFGERR=
if NOT DEFINED LANG set CFGERR=y
if NOT DEFINED GAME set CFGERR=y
if /i "%GAME%" EQU "SoC" (
set FONTGEN_ARGB=xxxx
set FONTGEN_BPP=32
set NVDXT_FORMAT=-32 u8888
set CONFIGS=%OUTDIR%\config
) else if /i "%GAME%" EQU "STCS" (
set FONTGEN_ARGB=xxxx
set FONTGEN_BPP=32
set NVDXT_FORMAT=-32 u8888
set CONFIGS=%OUTDIR%\configs
) else if /i "%GAME%" EQU "CoP" (
set FONTGEN_ARGB=1xxx
set FONTGEN_BPP=8
set NVDXT_FORMAT=-8 A8
set CONFIGS=%OUTDIR%\configs
) else set CFGERR=y
if DEFINED CFGERR (
cscript /nologo /E:JScript "%MYDATA%\strings.js" "%STRTXT%" 28
pause
exit
)
for /f "tokens=*" %%i in ('cscript /nologo /E:JScript "%MYDATA%\strings.js" "%STRTXT%" 1') do set FontName=%%i
set FontFile=msyh.ttf
cls
cscript /nologo /E:JScript "%MYDATA%\strings.js" "%STRTXT%" 2
pause>nul
cls
if not exist "%WORKDIR%\xmlfiles\*.xml" (
cscript /nologo /E:JScript "%MYDATA%\strings.js" "%STRTXT%" 3
pause
exit
)

if exist "%OUTDIR%" (
cscript /nologo /E:JScript "%MYDATA%\strings.js" "%STRTXT%" 5
pause
exit
)
if exist "%MYTEMP%" (
cscript /nologo /E:JScript "%MYDATA%\strings.js" "%STRTXT%" 6
rd /s /q "%MYTEMP%">nul 2>&1
if %ERRORLEVEL% NEQ 0 (
cscript /nologo /E:JScript "%MYDATA%\strings.js" "%STRTXT%" 7
pause
exit
)
)
mkdir "%MYTEMP%">nul 2>&1
attrib +h "%MYTEMP%"
cscript /nologo /E:JScript "%MYDATA%\strings.js" "%STRTXT%" 8
mkdir "%MYTEMP%\txtfiles">nul 2>&1
for /r "%WORKDIR%\xmlfiles" %%I in (*.xml) do (
"%MYDATA%\ExportXmlText.exe" "%%~fI" "%MYTEMP%\txtfiles\%%~nI.txt"
if !ERRORLEVEL! NEQ 0 (
echo %%~nI.xml
cscript /nologo /E:JScript "%MYDATA%\strings.js" "%STRTXT%" 9
pause
exit
)
)
copy "%MYDATA%\_ascii_char.txt" "%MYTEMP%\txtfiles\_ascii_char.txt">nul 2>&1
if %ERRORLEVEL% NEQ 0 (
cscript /nologo /E:JScript "%MYDATA%\strings.js" "%STRTXT%" 10
pause
exit
)
cd "%MYTEMP%\txtfiles"
"%MYDATA%\CharAdder.exe" .*?\.txt "%MYTEMP%\Char.txt">nul
if %ERRORLEVEL% NEQ 0 (
cscript /nologo /E:JScript "%MYDATA%\strings.js" "%STRTXT%" 11
pause
exit
)
cd "%WORKDIR%"
rd /s /q "%MYTEMP%\txtfiles">nul 2>&1
if not exist "%MYTEMP%\Char.txt" (
cscript /nologo /E:JScript "%MYDATA%\strings.js" "%STRTXT%" 12
pause
exit
)
cscript /nologo /E:JScript "%MYDATA%\strings.js" "%STRTXT%" 13
start "FontGen" /min "%MYDATA%\FontGen" /argb:%FONTGEN_ARGB% /add:"%MYTEMP%\Char.txt",%FontName%,0,11,15,15,0,0,0,0,0,0 /bpp:%FONTGEN_BPP% /save:"%MYTEMP%\ui_font_11_%LANG%.fd"
start "FontGen" /min "%MYDATA%\FontGen" /argb:%FONTGEN_ARGB% /add:"%MYTEMP%\Char.txt",%FontName%,0,13,16,16,0,0,0,0,0,0 /bpp:%FONTGEN_BPP% /save:"%MYTEMP%\ui_font_13_%LANG%.fd"
start "FontGen" /min "%MYDATA%\FontGen" /argb:%FONTGEN_ARGB% /add:"%MYTEMP%\Char.txt",%FontName%,0,15,19,19,0,0,0,0,0,0 /bpp:%FONTGEN_BPP% /save:"%MYTEMP%\ui_font_15_%LANG%.fd"
"%MYDATA%\FontGen" /x2 /argb:%FONTGEN_ARGB% /add:"%MYTEMP%\Char.txt",%FontName%,0,16,20,20,0,0,0,0,0,0 /bpp:%FONTGEN_BPP% /save:"%MYTEMP%\ui_font_16_%LANG%.fd"
start "FontGen" /min "%MYDATA%\FontGen" /x2 /argb:%FONTGEN_ARGB% /add:"%MYTEMP%\Char.txt",%FontName%,0,17,22,22,0,0,0,0,0,0 /bpp:%FONTGEN_BPP% /save:"%MYTEMP%\ui_font_17_%LANG%.fd"
start "FontGen" /min "%MYDATA%\FontGen" /x2 /argb:%FONTGEN_ARGB% /add:"%MYTEMP%\Char.txt",%FontName%,0,18,23,23,0,0,0,0,0,0 /bpp:%FONTGEN_BPP% /save:"%MYTEMP%\ui_font_18_%LANG%.fd"
start "FontGen" /min "%MYDATA%\FontGen" /x2 /argb:%FONTGEN_ARGB% /add:"%MYTEMP%\Char.txt",%FontName%,0,20,25,25,0,0,0,0,0,0 /bpp:%FONTGEN_BPP% /save:"%MYTEMP%\ui_font_20_%LANG%.fd"
"%MYDATA%\FontGen" /x2 /argb:%FONTGEN_ARGB% /add:"%MYTEMP%\Char.txt",%FontName%,0,21,26,26,0,0,0,0,0,0 /bpp:%FONTGEN_BPP% /save:"%MYTEMP%\ui_font_21_%LANG%.fd"
start "FontGen" /min "%MYDATA%\FontGen" /x2 /argb:%FONTGEN_ARGB% /add:"%MYTEMP%\Char.txt",%FontName%,0,23,29,29,0,0,0,0,0,0 /bpp:%FONTGEN_BPP% /save:"%MYTEMP%\ui_font_23_%LANG%.fd"
"%MYDATA%\FontGen" /x2 /argb:%FONTGEN_ARGB% /add:"%MYTEMP%\Char.txt",%FontName%,0,25,31,31,0,0,0,0,0,0 /bpp:%FONTGEN_BPP% /save:"%MYTEMP%\ui_font_25_%LANG%.fd"
if not exist "%MYTEMP%\ui_font_23_%LANG%.fd" ping -n 6 127.0.0.1>nul 2>&1
if not exist "%MYTEMP%\ui_font_11_%LANG%.fd" (
cscript /nologo /E:JScript "%MYDATA%\strings.js" "%STRTXT%" 14
pause
exit
)
del /f "%MYTEMP%\Char.txt">nul 2>&1
cscript /nologo /E:JScript "%MYDATA%\strings.js" "%STRTXT%" 15
for /r "%MYTEMP%" %%i in (*.fd) do (
"%MYDATA%\FD2INI.exe" "%%i" && del "%%i" || cscript /nologo /E:JScript "%MYDATA%\strings.js" "%STRTXT%" 16 && pause && exit
)
cscript /nologo /E:JScript "%MYDATA%\strings.js" "%STRTXT%" 17
for /r "%MYTEMP%" %%i in (*.bmp) do (
"%MYDATA%\BmpCuter.exe" "%%i"
if !ERRORLEVEL! NEQ 0 (
cscript /nologo /E:JScript "%MYDATA%\strings.js" "%STRTXT%" 18
pause
exit
)
)
cscript /nologo /E:JScript "%MYDATA%\strings.js" "%STRTXT%" 19
"%MYDATA%\nvdxt.exe" -file "%MYTEMP%\*.bmp" -outdir "%MYTEMP%" -nomipmap %NVDXT_FORMAT% >nul
if %ERRORLEVEL% NEQ 0 (
cscript /nologo /E:JScript "%MYDATA%\strings.js" "%STRTXT%" 20
pause
exit
)
del /f /q "%MYTEMP%\*.bmp">nul 2>&1
cscript /nologo /E:JScript "%MYDATA%\strings.js" "%STRTXT%" 21
mkdir "%OUTDIR%">nul 2>&1
mkdir "%CONFIGS%\text\%LANG%">nul 2>&1
mkdir "%OUTDIR%\textures\ui">nul 2>&1
move "%MYTEMP%\*.dds" "%OUTDIR%\textures\ui\">nul
if %ERRORLEVEL% NEQ 0 (
cscript /nologo /E:JScript "%MYDATA%\strings.js" "%STRTXT%" 22
pause
exit
)
move "%MYTEMP%\*.ini" "%OUTDIR%\textures\ui\">nul
if %ERRORLEVEL% NEQ 0 (
cscript /nologo /E:JScript "%MYDATA%\strings.js" "%STRTXT%" 23
pause
exit
)
rd /s /q "%MYTEMP%">nul 2>&1
copy "%WORKDIR%\xmlfiles\*.xml" "%CONFIGS%\text\%LANG%\">nul
if %ERRORLEVEL% NEQ 0 (
cscript /nologo /E:JScript "%MYDATA%\strings.js" "%STRTXT%" 24
pause
exit
)
copy "%MYDATA%\fonts_%GAME%.ltx" "%CONFIGS%\fonts.ltx">nul
if %ERRORLEVEL% NEQ 0 (
cscript /nologo /E:JScript "%MYDATA%\strings.js" "%STRTXT%" 25
pause
exit
)
for /f "delims= eol=" %%i in ('type "%MYDATA%\localization_%GAME%.ltx"') do (
set str=%%i
set "str=!str:#LANG#=%LANG%!"
echo !str!>>"%CONFIGS%\localization.ltx"
)
if %ERRORLEVEL% NEQ 0 (
cscript /nologo /E:JScript "%MYDATA%\strings.js" "%STRTXT%" 26
pause
exit
)
cscript /nologo /E:JScript "%MYDATA%\strings.js" "%STRTXT%" 27
pause