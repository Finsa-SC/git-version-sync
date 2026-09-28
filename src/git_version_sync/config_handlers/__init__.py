from pathlib import Path

from .base import BaseConfigParser
from .ini_config import IniConfigParser
from .toml import TomlConfigParser
from .json_config import JsonConfigParser
from .yaml_config import YamlConfigParser

def get_config_parser(config_path: Path) -> BaseConfigParser:
    suffix = config_path.suffix.lower()

    if suffix == ".toml":
        return TomlConfigParser(config_path)
    elif suffix == ".json":
        return JsonConfigParser(config_path)
    elif suffix in (".yaml", ".yml"):
        return YamlConfigParser(config_path)
    elif suffix in ('.ini', '.cfg'):
        return IniConfigParser(config_path)
    else:
        raise RuntimeError(f"Unsupported configuration file type {config_path.name}")