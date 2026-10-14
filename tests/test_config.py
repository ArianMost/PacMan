import json
from pathlib import Path
from src.config.config_loader import load_config

def test_missing_file(tmp_path: Path) -> None:
    config = load_config(str(tmp_path / "does_not_exist.json"))
    assert config.lives == 3
    assert len(config.levels) >= 1

def test_comments_stripped(tmp_path: Path) -> None:
    new_path = tmp_path / "config.json"
    new_path.write_text(
        """
        {
            # this is a comment
            "lives": 7,
            # "pacgum": 40
            "pacgum": 30
        }
        """
    )
    config = load_config(str(new_path))
    assert config.lives == 7
    assert config.pacgum == 30

def test_invalid_values(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"lives": -2, "pacgum": "gasfd"}))
    config = load_config(str(path))
    assert config.lives > 0
    assert config.pacgum > 0

def test_unknown_keys(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"qqq": 123, "lives": 5}))
    config = load_config(str(path))
    assert config.lives == 5

def test_malformed_json(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text("{ not valid json file!")
    config = load_config(str(path))
    assert config.lives == 3

def test_levels_keys(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"levels": [{"width": 21, "height": 14}]}))
    config = load_config(str(path))
    assert len(config.levels) == 1
    assert config.levels[0].width == 21
    assert config.levels[0].height == 14
