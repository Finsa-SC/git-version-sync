from pathlib import Path

from .base import BaseConfigParser
from .toml import TomlConfigParser
from .json_config import JsonConfigParser
from .yaml_config import YamlConfigParser

def get_config_parser(config_path: Path) -> BaseConfigParser:
    if config_path.suffix == ".toml":
        return TomlConfigParser(config_path)
    elif config_path.suffix == ".json":
        return JsonConfigParser(config_path)
    elif config_path.suffix in [".yaml", ".yml"]:
        return YamlConfigParser(config_path)
    else:
        raise RuntimeError(f"Unsupported configuration file type {config_path.name}")