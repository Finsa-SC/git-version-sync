import json
from pathlib import Path
from typing import Any, Tuple, Optional
from packaging.version import Version

from .base import BaseConfigParser


class JsonConfigParser(BaseConfigParser):
    # JSON files that prohibit prefix 'v'
    STRICT_NO_PREFIX_FILES = {"package.json", "package-lock.json", "composer.json"}

    def __init__(self, config_path: Path):
        super().__init__(config_path)
        self.possible_keys: list[Tuple[str, ...]] = [
            # Node.js / NPM / Composer / Generic Root
            ("version",),

            # OpenAPI / Swagger JSON
            ("info", "version"),

            # App / Project Scopes
            ("git-version-sync", "version"),
            ("project", "version"),
            ("package", "version"),
            ("app", "version"),

            # Metadata Scope
            ("metadata", "version"),
        ]

    @staticmethod
    def _get_by_path(data: dict[str, Any], path: Tuple[str, ...]) -> Optional[Any]:
        curr = data
        for key in path:
            if isinstance(curr, dict) and key in curr:
                curr = curr[key]
            else:
                return None
        return curr

    @staticmethod
    def _set_by_path(data: dict[str, Any], path: Tuple[str, ...], value: Any) -> bool:
        curr = data
        for key in path[:-1]:
            if isinstance(curr, dict) and key in curr:
                curr = curr[key]
            else:
                return False

        target_key = path[-1]
        if isinstance(curr, dict) and target_key in curr:
            curr[target_key] = value
            return True
        return False

    def get_version(self) -> Version:
        data = json.loads(self.config_path.read_text(encoding="utf-8"))

        for path in self.possible_keys:
            val = self._get_by_path(data, path)
            if val is not None:
                # Always remove prefix 'v'
                clean_val = str(val).lstrip('v')
                return Version(clean_val)

        raise KeyError(f"No valid version field found in {self.config_path.name}")

    def update_version(self, new_version: Version) -> None:
        content = self.config_path.read_text(encoding="utf-8")
        data = json.loads(content)

        version_str = str(new_version)

        # if not a strict file, and old file have prefix 'v', keep the original style
        if self.config_path.name.lower() not in self.STRICT_NO_PREFIX_FILES:
            current_raw_val = None
            for path in self.possible_keys:
                val = self._get_by_path(data, path)
                if val is not None:
                    current_raw_val = str(val)
                    break

            # if old version start with 'v', adding back 'v'
            if current_raw_val and current_raw_val.startswith('v'):
                version_str = f"v{version_str}"

        # Update value to data JSON
        updated = False
        for path in self.possible_keys:
            if self._get_by_path(data, path) is not None:
                self._set_by_path(data, path, version_str)
                updated = True
                break

        if not updated:
            raise KeyError(f"Could not find a valid version key to update in {self.config_path.name}")

        new_content = json.dumps(data, indent=2) + "\n"
        self.config_path.write_text(new_content, encoding="utf-8")