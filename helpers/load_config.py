"""Utilities for loading YAML configuration files."""
from typing import Dict

import yaml


def load_config(filepath: str) -> Dict:
    """Load a YAML config file and return its contents as a dict."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            "Invalid config file path. Check and try again."
        ) from exc
