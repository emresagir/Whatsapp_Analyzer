# PyInstaller recipe for the Windows app ("Lite": report + statistics + dashboard, no local AI).
#
#   pip install -r requirements.txt -r requirements-dashboard.txt -r requirements-build.txt
#   pyinstaller whatsapp_analyzer.spec --noconfirm
#
# Result: dist/WhatsAppAnalyzer/WhatsAppAnalyzer.exe  (zip the whole dist/WhatsAppAnalyzer folder to share it).
# A folder build (not --onefile) starts much faster and triggers far fewer antivirus false alarms.
# PyInstaller cannot cross-compile: build on Windows to get a Windows .exe (see .github/workflows/build-windows.yml).
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata

datas = [
    ("dashboard.py", "."),                       # streamlit runs it as a script file
    ("wa_analyzer/lexicon.json", "wa_analyzer"),
    ("wa_analyzer/lexicon_tr.json", "wa_analyzer"),
]
datas += collect_data_files("streamlit")         # web frontend (static/), config defaults
datas += collect_data_files("plotly")            # plotly.min.js for the report, templates
datas += collect_data_files("lifelines")
for pkg in ("streamlit", "plotly", "pandas", "numpy", "scipy", "scikit-learn", "lifelines", "networkx", "joblib",
            "altair", "pyarrow"):
    try:
        datas += copy_metadata(pkg)              # packages that look up their own version at runtime
    except Exception:
        pass

hiddenimports = (
    ["dashboard"]                                # analysed for its imports (it is loaded by streamlit at runtime)
    + collect_submodules("wa_analyzer")
    + collect_submodules("streamlit")
    + collect_submodules("lifelines")
)

# Local AI is not part of the app: these are several GB and only imported when AI commands run.
excludes = ["torch", "torchvision", "torchaudio", "transformers", "sentence_transformers", "sentencepiece",
            "tensorflow", "keras", "jax", "shap", "numba", "llvmlite", "IPython", "jupyter", "notebook",
            "matplotlib", "tkinter", "pytest"]

a = Analysis(
    ["app.py"],
    pathex=["."],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="WhatsAppAnalyzer",
    console=True,      # the console window shows the address and stops the app when closed
    upx=False,
    icon=None,
)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name="WhatsAppAnalyzer")
