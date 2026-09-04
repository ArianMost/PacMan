#!/usr/bin/env python3
"""Pac-Man entry point.

Usage:
    python3 pac-man.py config.json
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.game.game import main  # noqa: E402


def _usage_error(message: str) -> int:
    print(f"error: {message}", file=sys.stderr)
    print("usage: python3 pac-man.py <config.json>", file=sys.stderr)
    return 1


def run() -> int:
    if len(sys.argv) != 2:
        return _usage_error("exactly one argument is required (the config file)")

    config_path = sys.argv[1]
    if not config_path.lower().endswith(".json"):
        return _usage_error("the config file must have a .json extension")

    return main(config_path)


if __name__ == "__main__":
    sys.exit(run())
