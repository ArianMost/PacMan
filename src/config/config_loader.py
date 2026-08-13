import json
from pathlib import Path
import sys
from typing import Any
from config import Config

def load_config(config_file: str) -> Config:
    config_text = ""

    try:
        file_path = Path(config_file)
        config_text = file_path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"[config] warning: could not read config file '{config_file}' ({e}) using defaults", file=sys.stderr)
        config_text = ""


    config_data: dict[str, Any] = {}
    if config_text.strip():
        try:
            cleaned_config = _remove_comments(config_text)
            parsed = json.loads(cleaned_config)
            
            if isinstance(parsed, dict):
                config_data = parsed
            else:
                print(f"[config] warning: config root is not a JSON object; using defaults", file=sys.stderr)
        except json.JSONDecodeError as e:
            print(f"[config] warning: malformed JSON in config file ({e}); using defaults", file=sys.stderr)
