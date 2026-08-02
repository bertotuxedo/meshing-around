#!/usr/bin/env python3
"""Container healthcheck for the long-running Meshing Around process."""

from __future__ import annotations

import configparser
import os
from pathlib import Path


CONFIG_PATH = Path(
    os.getenv("MESHING_AROUND_RUNTIME_CONFIG", "/run/meshing-around/config.ini")
)


def bot_process_running() -> bool:
    proc = Path("/proc")
    if not proc.exists():
        return True
    for entry in proc.iterdir():
        if not entry.name.isdigit():
            continue
        try:
            command = (entry / "cmdline").read_bytes().replace(b"\0", b" ")
        except (OSError, PermissionError):
            continue
        if b"mesh_bot.py" in command or b"pong_bot.py" in command:
            return True
    return False


def config_is_valid() -> bool:
    parser = configparser.ConfigParser(interpolation=None)
    try:
        with CONFIG_PATH.open("r", encoding="utf-8") as handle:
            parser.read_file(handle)
    except (OSError, configparser.Error):
        return False
    return parser.has_section("interface") and bool(
        parser.get("interface", "type", fallback="").strip()
    )


if __name__ == "__main__":
    raise SystemExit(0 if config_is_valid() and bot_process_running() else 1)
