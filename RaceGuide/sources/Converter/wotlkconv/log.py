"""Minimal levelled logging with optional ANSI colour.

Kept dependency-free and separate from :mod:`logging` so that the CLI can stay
quiet by default and still emit structured per-file diagnostics.
"""

from __future__ import annotations

import os
import sys
import threading

QUIET = 0
ERROR = 1
WARN = 2
INFO = 3
DEBUG = 4

_LEVEL_NAMES = {
    "quiet": QUIET,
    "error": ERROR,
    "warn": WARN,
    "info": INFO,
    "debug": DEBUG,
}

_lock = threading.Lock()
_level = INFO
_use_colour = sys.stderr.isatty() and os.environ.get("NO_COLOR") is None

_COLOURS = {
    ERROR: "\033[31m",
    WARN: "\033[33m",
    INFO: "\033[0m",
    DEBUG: "\033[90m",
}
_RESET = "\033[0m"
_PREFIX = {ERROR: "error", WARN: "warn", INFO: "info", DEBUG: "debug"}


def set_level(level: int | str) -> None:
    global _level
    if isinstance(level, str):
        try:
            level = _LEVEL_NAMES[level.lower()]
        except KeyError:
            raise ValueError(f"unknown log level {level!r}") from None
    _level = level


def set_colour(enabled: bool) -> None:
    global _use_colour
    _use_colour = enabled


def _emit(level: int, msg: str) -> None:
    if level > _level:
        return
    prefix = _PREFIX[level]
    line = f"{_COLOURS[level]}{prefix}:{_RESET} {msg}" if _use_colour else f"{prefix}: {msg}"
    with _lock:
        print(line, file=sys.stderr, flush=True)


def error(msg: str) -> None:
    _emit(ERROR, msg)


def warn(msg: str) -> None:
    _emit(WARN, msg)


def info(msg: str) -> None:
    _emit(INFO, msg)


def debug(msg: str) -> None:
    _emit(DEBUG, msg)
