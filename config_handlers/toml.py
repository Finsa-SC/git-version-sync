import re
from packaging.version import Version

from base import BaseConfigParser

class TomlConfigParser(BaseConfigParser):
    def get_version(self) -> Version:
        content = self.config_path.read_text(encoding="utf-8")

        match = re.search(r'^\s*version\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
        if not match:
            raise RuntimeError(f"Version field not found in {self.config_path.name}")
        return Version(match.group(1))

    def update_version(self, new_version: Version) -> None:
        content = self.config_path.read_text(encoding="utf-8")

        pattern = r'^(version\s*=\s*["\']).*?(["\'])'
        replacement = rf'\g<1>{new_version}\g<2>'

        new_content, count = re.subn(pattern, replacement, content, count=1, flags=re.MULTILINE)
        if count == 0:
            raise RuntimeError(f"Failed to update version in {self.config_path.name}")

        self.config_path.write_text(new_content, encoding="utf-8")