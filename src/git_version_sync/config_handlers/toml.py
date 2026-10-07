import re
from pathlib import Path
from typing import Tuple
from packaging.version import Version

try:
    import tomllib
except ImportError:
    import tomli as tomllib

from .base import BaseConfigParser


class TomlConfigParser(BaseConfigParser):

    def __init__(self, config_path: Path):
        super().__init__(config_path)
        # Variasi lokasi key yang umum di format TOML
        self.possible_keys: list[Tuple[str, ...]] = [
            ("project", "version"),             # PEP 621 (pyproject.toml standar)
            ("tool", "poetry", "version"),      # Poetry
            ("package", "version"),             # Cargo.toml (Rust)
            ("git-version-sync", "version"),    # Custom tool scope
            ("app", "version"),                 # Custom app scope
            ("metadata", "version"),            # Metadata scope
            ("version",),                       # Generic root level
        ]

    @staticmethod
    def _get_value_by_keys(data: dict, keys: Tuple[str, ...]):
        curr = data
        for k in keys:
            if isinstance(curr, dict) and k in curr:
                curr = curr[k]
            else:
                return None
        return curr

    def get_version(self) -> Version:
        content = self.config_path.read_text(encoding="utf-8")
        data = tomllib.loads(content)

        # Search matched key depends on possible_keys priority list
        for keys in self.possible_keys:
            val = self._get_value_by_keys(data, keys)
            if val and isinstance(val, str):
                return Version(val)

        raise RuntimeError(f"Version field not found in {self.config_path.name}")

    def update_version(self, new_version: Version) -> None:
        content = self.config_path.read_text(encoding="utf-8")
        data = tomllib.loads(content)

        # Search key that used in the file
        target_keys = None
        for keys in self.possible_keys:
            val = self._get_value_by_keys(data, keys)
            if val and isinstance(val, str):
                target_keys = keys
                break

        if not target_keys:
            raise RuntimeError(f"Failed to locate version key to update in {self.config_path.name}")

        # Update using Regex Section TOML
        if len(target_keys) == 1:
            # Root level (e.g. version = "1.0.0")
            pattern = r'^(version\s*=\s*["\']).*?(["\'])'
            replacement = rf'\g<1>{new_version}\g<2>'
        else:
            # Nested section level (e.g. [project] -> version = "1.0.0")
            section_header = r"\[" + r"\.".join(re.escape(k) for k in target_keys[:-1]) + r"\]"
            key_name = re.escape(target_keys[-1])

            # Regex to matching key = "val" only on right section
            pattern = rf'({section_header}[\s\S]*?^\s*{key_name}\s*=\s*["\']).*?(["\'])'
            replacement = rf'\g<1>{new_version}\g<2>'

        new_content, count = re.subn(pattern, replacement, content, count=1, flags=re.MULTILINE)
        if count == 0:
            raise RuntimeError(f"Failed to update version in {self.config_path.name}")

        self.config_path.write_text(new_content, encoding="utf-8")