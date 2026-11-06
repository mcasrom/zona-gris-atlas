from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT / "config"


def load_yaml(name: str) -> dict[str, Any]:
    path = CONFIG_DIR / name
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return data or {}


def site() -> dict[str, Any]:
    return load_yaml("site.yaml")


def taxonomy() -> dict[str, Any]:
    return load_yaml("taxonomy.yaml")


def sources() -> dict[str, Any]:
    return load_yaml("sources.yaml")


def db_path() -> Path:
    return Path(os.environ.get("ZG_DB_PATH", ROOT / "data" / "zonagris.db"))


def data_dir() -> Path:
    return Path(os.environ.get("ZG_DATA_DIR", ROOT / "data"))


def cache_dir() -> Path:
    return Path(os.environ.get("ZG_CACHE_DIR", data_dir() / "raw"))


def user_agent() -> str:
    return os.environ.get(
        "ZG_USER_AGENT",
        "zona-gris-atlas/0.1 (+https://github.com/mcasrom/zona-gris-atlas)",
    )
