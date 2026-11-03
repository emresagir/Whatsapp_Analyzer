"""Entry point of the packaged app (WhatsAppAnalyzer.exe). Also works from source:  python app.py

  WhatsAppAnalyzer.exe                       start the dashboard and open it in the browser
  WhatsAppAnalyzer.exe CHAT.txt [options]    write the HTML report (same options as: python -m wa_analyzer)

The dashboard only listens on this computer (127.0.0.1); nothing is sent anywhere.
"""
from __future__ import annotations

import multiprocessing
import socket
import sys
import threading
import time
import webbrowser

from wa_analyzer.console import utf8_console
from wa_analyzer.paths import resource

HOST = "127.0.0.1"


def free_port(preferred: int = 8501) -> int:
    """The preferred port if it is free, otherwise any free port."""
    for port in (preferred, 0):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((HOST, port))
            except OSError:
                continue
            return s.getsockname()[1]
    raise RuntimeError("no free port")


def open_when_ready(url: str, port: int, timeout: float = 60.0) -> None:
    """Open the browser as soon as the server accepts connections (in the background)."""
    def wait():
        end = time.time() + timeout
        while time.time() < end:
            try:
                with socket.create_connection((HOST, port), timeout=0.5):
                    webbrowser.open(url)
                    return
            except OSError:
                time.sleep(0.3)
    threading.Thread(target=wait, daemon=True).start()


def streamlit_argv(script: str, port: int) -> list[str]:
    return [
        "streamlit", "run", script,
        "--global.developmentMode=false",       # required when frozen, otherwise --server.port is refused
        f"--server.address={HOST}",              # local only
        f"--server.port={port}",
        "--server.headless=true",                # no first-run e-mail prompt; we open the browser ourselves
        "--server.fileWatcherType=none",
        "--server.runOnSave=false",
        "--browser.gatherUsageStats=false",      # no telemetry
        "--theme.base=light",
    ]


def run_dashboard(open_browser: bool = True) -> int:
    from streamlit.web import cli as stcli

    script = resource("dashboard.py")
    if not script.exists():
        print(f"dashboard.py not found in {script.parent}", file=sys.stderr)
        return 1
    port = free_port()
    url = f"http://{HOST}:{port}"
    print("WhatsApp Analyzer is running on this computer only.")
    print(f"Open {url} in your browser if it does not open by itself.")
    print("Close this window to stop the app.\n")
    if open_browser:
        open_when_ready(url, port)
    sys.argv = streamlit_argv(str(script), port)
    return stcli.main()


def main(argv: list[str] | None = None) -> int:
    utf8_console()
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] not in ("--dashboard", "--no-browser"):
        from wa_analyzer.__main__ import main as cli_main
        return cli_main(argv) or 0
    return run_dashboard(open_browser="--no-browser" not in argv) or 0


if __name__ == "__main__":
    multiprocessing.freeze_support()  # needed by joblib/scikit-learn worker processes in the frozen .exe
    sys.exit(main())
