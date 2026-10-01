import yaml
from pathlib import Path
from packaging.version import Version
from typing import Any

from .base import BaseConfigParser

class YamlConfigParser(BaseConfigParser):
    def __init__(self, config_path: Path):
        super().__init__(config_path)
        self._data = self._load_yaml()
        self.possible_keys = [
            ("git-version-sync", "version"),  # Tool scope: git-version-sync.version
            ("tool", "git-version-sync", "version"),  # Standard CLI scope
            ("package", "version"),  # Package scope
            ("project", "version"),
        ]

    def _load_yaml(self) -> dict[str, Any]:
        with self.config_path.open('r', encoding="utf-8") as file:
            content = yaml.safe_load(file)

        if isinstance(content, dict):
            return content
        return {}

    def _find_version_key_path(self) -> tuple[tuple[str, ...], Any]:
        for key_path in self.possible_keys:
            current = self._data
            for k in key_path:
                if isinstance(current, dict) and k in current:
                    current = current[k]
                else:
                    current = None
                    break

            if current is not None:
                return key_path, current

        raise KeyError(
            f"Could not find a valid 'version' key in {self.config_path.name}. "
            "Expected 'version: X.Y.Z' or under a section like 'git-version-sync.version'."
        )

    def get_version(self) -> Version:
        _, raw_version = self._find_version_key_path()

        version_str = str(raw_version).strip().lstrip("v")
        return Version(version_str)

    def update_version(self, new_version: Version) -> None:
        key_path, _ = self._find_version_key_path()

        current = self._data
        for k in key_path[:-1]:
            current = current[k]

        last_key = key_path[-1]
        current[last_key] = f"v{new_version}" if isinstance(current[last_key], str) and current[last_key].startswith('v') else str(new_version)

        with self.config_path.open('w', encoding="utf-8") as file:
            yaml.safe_dump(self._data, file, sort_keys=False)
