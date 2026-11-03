"""Console output that survives non-ASCII names (ş, ı, ğ, emoji) on the Windows console."""
from __future__ import annotations

import sys


def utf8_console() -> None:
    """Write stdout/stderr as UTF-8 and replace anything the console still cannot show.

    Without this, printing a Turkish or emoji name in a Windows console (cp1252/cp857) raises UnicodeEncodeError.
    In the windowed .exe there may be no console at all (stdout is None): then nothing is done.
    """
    for stream in (sys.stdout, sys.stderr):
        if stream is not None and hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (ValueError, OSError):
                pass
