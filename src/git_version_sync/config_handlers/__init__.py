from pathlib import Path

from .base import BaseConfigParser
from .toml import TomlConfigParser
from .json_config import JsonConfigParser

def get_config_parser(config_path: Path) -> BaseConfigParser:
    name = config_path.name.lower()

    if ".toml" in name:
        return TomlConfigParser(config_path)
    elif ".json" in name:
        return JsonConfigParser(config_path)
    else:
        raise RuntimeError(f"Unsupported configuration file type {config_path.name}")