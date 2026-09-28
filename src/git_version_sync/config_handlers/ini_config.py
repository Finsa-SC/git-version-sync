import configparser
from pathlib import Path
from packaging.version import Version
from base import BaseConfigParser

class IniConfigParser(BaseConfigParser):
    def __init__(self, config_path: Path):
        super().__init__(config_path)
        self.possible_sections = [
            ("metadata", "version"),       # Standard setup.cfg
            ("version", "version"),        # Section [version]
            ("git-version-sync", "version"),
            ("DEFAULT", "version"),        # Root / default
        ]

    def _load_ini(self) -> configparser.ConfigParser:
        config = configparser.ConfigParser()
        config.read(self.config_path, encoding="utf-8")
        return config

    def _find_version_key_path(self) -> tuple[str, str, str]:
        config = self._load_ini()
        for section, key in self.possible_sections:
            if config.has_section(section) and config.has_option(section, key):
                return section, key, config.get(section, key)
            if section == "DEFAULT" and config.has_option("DEFAULT", key):
                return "DEFAULT", key, config.get("DEFAULT", key)

        raise KeyError(f"Could not find a valid 'version' key in {self.config_path.name}.")

    def get_version(self) -> Version:
        _, _, raw_version = self._find_version_key_path()
        return Version(raw_version.strip().lstrip("v"))

    def update_version(self, new_version: Version) -> None:
        section, key, raw_version = self._find_version_key_path()
        config = self._load_ini()

        new_val = f"v{new_version}" if raw_version.startswith("v") else str(new_version)
        config.set(section, key, new_val)

        with self.config_path.open("w", encoding="utf-8") as file:
            config.write(file)