import json
import re
import sys
from pathlib import Path
from typing import Any

MAX_ENTRIES = 10
MAX_NAME_LENGTH = 10
_NAME_PATTERN = re.compile(r"^[A-Za-z0-9 ]+$")

class HighscoreEntry:
    def __init__(self, name: str, score: int) -> None:
        self.name = name
        self.score = score


class HighscoreStore:
    """Loads, validates, ranks, and persists highscore entries.
 
    Attributes:
        filename: Path to the JSON file entries are stored in.
        entries: In-memory list of `HighscoreEntry`, always kept sorted
            by score (highest first) and capped at `MAX_ENTRIES`.
    """
 
    def __init__(
        self,
        filename: str,
        entries: list[HighscoreEntry] | None = None
    ) -> None:
        self.filename = filename

        if entries is None:
            self.entries = []
        else:
            self.entries = entries

    @staticmethod
    def _validate_name(name: Any) -> str | None:
        """Normalize and validate a player name, or return None if invalid."""
        if not isinstance(name, str):
            return None
        candidate = name.strip()[:MAX_NAME_LENGTH]
        if not candidate or not _NAME_PATTERN.fullmatch(candidate):
            return None
        return candidate
 
    @staticmethod
    def _validate_score(score: Any) -> int | None:
        """Coerce and validate a score, or return None if invalid."""
        if isinstance(score, bool):  # bool is an int subclass -- reject it
            return None
        try:
            value = int(score)
        except (TypeError, ValueError):
            return None
        if value < 0:
            return None
        return value

    @classmethod
    def _parse_entry(cls, item: Any, index: int) -> HighscoreEntry | None:
        """Parse one raw JSON element into a `HighscoreEntry`, or None."""
        if not isinstance(item, dict):
            print(
                f"[highscore] warning: entry[{index}] is not an object, "
                f"skipping",
                file=sys.stderr,
            )
            return None
        name = cls._validate_name(item.get("name"))
        score = cls._validate_score(item.get("score"))
        if name is None or score is None:
            print(
                f"[highscore] warning: entry[{index}] has an invalid "
                f"name/score, skipping",
                file=sys.stderr,
            )
            return None
        return HighscoreEntry(name=name, score=score)

    def load(self) -> None:
        """(Re)load entries from `filename`, replacing the in-memory list.
 
        Call once at game start. If the file doesn't exist yet (first
        run) or is unreadable/corrupt, this quietly resets to an empty
        list instead of raising -- a broken highscore file must never
        prevent the game from starting.
        """
        path = Path(self.filename)
        if not path.exists():
            self.entries = []
            return
 
        try:
            raw_data = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            print(
                f"[highscore] warning: could not read '{self.filename}' "
                f"({exc}); starting with an empty highscore list",
                file=sys.stderr,
            )
            self.entries = []
            return
        except json.JSONDecodeError as exc:
            print(
                f"[highscore] warning: '{self.filename}' contains invalid "
                f"JSON ({exc}); starting with an empty highscore list",
                file=sys.stderr,
            )
            self.entries = []
            return
 
        if not isinstance(raw_data, list):
            print(
                f"[highscore] warning: '{self.filename}' does not contain "
                f"a JSON array; starting with an empty highscore list",
                file=sys.stderr,
            )
            self.entries = []
            return
 
        parsed = [
            entry
            for index, item in enumerate(raw_data)
            if (entry := self._parse_entry(item, index)) is not None
        ]
        parsed.sort(key=lambda e: e.score, reverse=True)
        self.entries = parsed[:MAX_ENTRIES]
