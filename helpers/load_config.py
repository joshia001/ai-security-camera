import yaml
from typing import Dict


def load_config(filepath: str) -> Dict:
    try:
        with open(filepath, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError("Invalid config file path. Check and try again.")
