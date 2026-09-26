import json
from packaging.version import Version

from .base import BaseConfigParser

class JsonConfigParser(BaseConfigParser):
    def get_version(self) -> Version:
        data = json.loads(self.config_path.read_text(encoding="utf-8"))

        if "version" not in data:
            raise KeyError(f"'version' field missing in {self.config_path.name}")
        return Version(data["version"])

    def update_version(self, new_version: Version) -> None:
        content = self.config_path.read_text(encoding="utf-8")
        data = json.loads(content)
        data['version'] = f"v{new_version}"

        new_content = json.dumps(data, indent=2) + "\n"
        self.config_path.write_text(new_content, encoding="utf-8")