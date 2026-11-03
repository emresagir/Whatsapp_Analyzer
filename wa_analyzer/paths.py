"""Where things are, both when running from source and inside the packaged Windows app (PyInstaller).

  * resource_dir(): folder that holds the bundled files (dashboard.py, wa_analyzer/lexicon*.json).
    From source this is the project folder; in the packaged app it is PyInstaller's _MEIPASS folder.
  * app_dir(): folder the user sees: the project folder, or the folder that contains the .exe.
  * chat_search_dirs(): folders the dashboard scans for chat exports.
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent


def is_frozen() -> bool:
    """True inside the packaged app (PyInstaller)."""
    return bool(getattr(sys, "frozen", False))


def resource_dir() -> Path:
    if is_frozen():
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    return PROJECT_DIR


def resource(*parts: str) -> Path:
    return resource_dir().joinpath(*parts)


def app_dir() -> Path:
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return PROJECT_DIR


def chat_search_dirs() -> list[Path]:
    """Folders to look for exports in: app folder, its chats/ folder, Downloads, Documents, Desktop, home."""
    home = Path.home()
    dirs = [app_dir() / "chats", app_dir(), home / "Downloads", home / "Documents", home / "Desktop", home]
    out: list[Path] = []
    for d in dirs:
        try:
            d = d.resolve()
        except OSError:
            continue
        if d not in out and d.is_dir():
            out.append(d)
    return out
