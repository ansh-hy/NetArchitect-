import json
from pathlib import Path

PRESET_DIR = Path(__file__).resolve().parent.parent / "config"


def list_presets():
    return ["campus_lan", "metro_man", "global_wan"]


def load_preset(name: str) -> dict:
    if name not in list_presets():
        raise ValueError(f"Unknown preset: {name}")
    path = PRESET_DIR / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))
