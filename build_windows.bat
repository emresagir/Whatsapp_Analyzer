@echo off
rem Build the Windows app on a Windows computer:  build_windows.bat
rem Result: dist\WhatsAppAnalyzer-windows.zip  (unzip anywhere, run WhatsAppAnalyzer.exe)
setlocal
cd /d "%~dp0"

py -3 -m venv .venv-build 2>nul || python -m venv .venv-build
call .venv-build\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt -r requirements-dashboard.txt -r requirements-build.txt || exit /b 1
pyinstaller whatsapp_analyzer.spec --noconfirm --clean || exit /b 1

rem quick check: the packaged CLI must start
dist\WhatsAppAnalyzer\WhatsAppAnalyzer.exe --explain "seni seviom" || exit /b 1

powershell -NoProfile -Command "Compress-Archive -Path dist\WhatsAppAnalyzer -DestinationPath dist\WhatsAppAnalyzer-windows.zip -Force"
echo.
echo Built: dist\WhatsAppAnalyzer-windows.zip
endlocal
