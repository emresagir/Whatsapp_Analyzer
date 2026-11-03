"""Tests for the Windows app pieces: resource paths (source and frozen), console, launcher, dashboard start-up."""
import io
import shutil
import socket
import sys
from pathlib import Path

import pytest

import app
from wa_analyzer import paths
from wa_analyzer.console import utf8_console

ROOT = Path(__file__).resolve().parent.parent
FAKE = Path(__file__).parent / "fake_chats"


@pytest.fixture(scope="module")
def fake():
    if not (FAKE / "truth.json").exists():
        from make_fake_chats import main
        main(FAKE)
    return FAKE


def test_resources_from_source():
    assert not paths.is_frozen()
    assert paths.resource_dir() == ROOT
    for f in [("dashboard.py",), ("wa_analyzer", "lexicon.json"), ("wa_analyzer", "lexicon_tr.json")]:
        assert paths.resource(*f).is_file()


def test_lexicons_load_from_resources():
    from wa_analyzer.lexicon_engine import DEFAULT_LEXICONS, WordClassifier
    assert all(p.is_file() for p in DEFAULT_LEXICONS)
    assert WordClassifier().explain("seni seviom")


def test_frozen_paths(monkeypatch, tmp_path):
    bundle, install = tmp_path / "_internal", tmp_path / "WhatsAppAnalyzer"
    bundle.mkdir()
    (install / "chats").mkdir(parents=True)
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(bundle), raising=False)
    monkeypatch.setattr(sys, "executable", str(install / "WhatsAppAnalyzer.exe"))
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path / "home"))
    (tmp_path / "home" / "Downloads").mkdir(parents=True)
    assert paths.is_frozen()
    assert paths.resource("dashboard.py") == bundle / "dashboard.py"
    assert paths.app_dir() == install
    dirs = paths.chat_search_dirs()
    assert dirs[:2] == [(install / "chats").resolve(), install.resolve()]
    assert (tmp_path / "home" / "Downloads").resolve() in dirs
    assert (tmp_path / "home" / "Documents").resolve() not in dirs  # missing folders are skipped
    assert len(dirs) == len(set(dirs))


def test_utf8_console(monkeypatch):
    raw = io.BytesIO()
    monkeypatch.setattr(sys, "stdout", io.TextIOWrapper(raw, encoding="cp1252"))
    monkeypatch.setattr(sys, "stderr", None)  # windowed .exe: no console at all
    utf8_console()
    print("Sıla 💬 ağ")
    sys.stdout.flush()
    assert raw.getvalue().decode("utf-8").strip() == "Sıla 💬 ağ"


def test_free_port():
    port = app.free_port(0)
    with socket.socket() as s:
        s.bind((app.HOST, port))
    with socket.socket() as busy:
        busy.bind((app.HOST, 0))
        busy.listen()
        taken = busy.getsockname()[1]
        assert app.free_port(taken) != taken


def test_streamlit_argv():
    argv = app.streamlit_argv("dashboard.py", 8600)
    assert argv[:3] == ["streamlit", "run", "dashboard.py"]
    assert "--global.developmentMode=false" in argv
    assert "--server.address=127.0.0.1" in argv
    assert "--server.port=8600" in argv
    assert "--browser.gatherUsageStats=false" in argv


def test_launcher_explain(capsys):
    assert app.main(["--explain", "seni seviom aşkm"]) == 0
    assert "seni seviom" in capsys.readouterr().out


def test_launcher_report(fake, tmp_path):
    chat = tmp_path / "Sıla ğ chat.zip"  # non-ASCII file name, zip export
    shutil.copy(fake / "pair_ios_export.zip", chat)
    out = tmp_path / "report.html"
    assert app.main([str(chat), "-o", str(out), "--no-stats"]) == 0
    html = out.read_text(encoding="utf-8")
    assert len(html) > 100_000 and "plotly" in html.lower()


def test_dashboard_runs(fake, tmp_path, monkeypatch):
    pytest.importorskip("streamlit")
    from streamlit.testing.v1 import AppTest
    shutil.copy(fake / "pair_android_24h_dmy.txt", tmp_path / "WhatsApp Chat with Test.txt")
    monkeypatch.setattr(paths, "chat_search_dirs", lambda: [tmp_path])  # never pick up real chats
    at = AppTest.from_file(str(ROOT / "dashboard.py"), default_timeout=300)
    at.run()
    assert not at.exception, at.exception
    assert at.sidebar.selectbox[0].value.endswith("WhatsApp Chat with Test.txt")
    assert at.title[0].value == "Test"
    assert len(at.tabs) >= 4
