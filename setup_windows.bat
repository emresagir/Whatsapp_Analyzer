@echo off
rem Install from source on Windows (needs Python 3.10+ from python.org, "Add python.exe to PATH" ticked).
rem   setup_windows.bat          report + statistics + dashboard + local AI on CPU
rem   setup_windows.bat gpu      same, with the CUDA build of PyTorch (NVIDIA GPU)
rem   setup_windows.bat lite     report + statistics + dashboard only (no AI, much smaller)
setlocal
cd /d "%~dp0"

py -3 -m venv .venv 2>nul || python -m venv .venv
if errorlevel 1 (
    echo Could not create the environment. Install Python 3.10+ from https://www.python.org/downloads/
    exit /b 1
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt -r requirements-dashboard.txt || exit /b 1

if /i "%~1"=="lite" goto done
if /i "%~1"=="gpu" (
    pip install torch --index-url https://download.pytorch.org/whl/cu124 || exit /b 1
    set DEVICE=cuda
) else (
    pip install torch --index-url https://download.pytorch.org/whl/cpu || exit /b 1
    set DEVICE=cpu
)
pip install -r requirements-ai.txt || exit /b 1
echo.
python -m wa_analyzer.ai doctor --device %DEVICE%

:done
echo.
echo Done. In a new terminal, activate the environment with:  .venv\Scripts\activate
echo Then:  streamlit run dashboard.py      or      python -m wa_analyzer CHAT.txt --open
endlocal
