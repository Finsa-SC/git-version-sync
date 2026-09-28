import xml.etree.ElementTree as ET
from pathlib import Path
from packaging.version import Version

from .base import BaseConfigParser

class XmlConfigParser(BaseConfigParser):
    def __init__(self, config_path: Path):
        super().__init__(config_path)
        self.target_tags = [
            "version",
            "{http://maven.apache.org/POM/4.0.0}version"
        ]

    def _parse_tree(self) -> ET.ElementTree:
        try:
            return ET.parse(self.config_path)
        except ET.ParseError as e:
            raise RuntimeError(f"Failed to parse XML file {self.config_path.name}: {e}") from e

    def _find_version_element(self, tree: ET.ElementTree) -> tuple[ET.Element, str]:
        root = tree.getroot()

        for tag in self.target_tags:
            elem = root.find(tag)
            if elem is not None and elem.text:
                return elem, elem.text.strip()

        for elem in root.iter():
            tag_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
            if tag_name == "version" and elem.text:
                return elem, elem.text.strip()

        raise KeyError(
            f"Could not find a valid '<version>' tag in {self.config_path.name}."
        )

    def get_version(self) -> Version:
        tree = self._parse_tree()
        _, raw_version = self._find_version_element(tree)
        version_str = raw_version.lstrip("v")
        return Version(version_str)

    def update_version(self, new_version: Version) -> None:
        tree = self._parse_tree()
        elem, raw_version = self._find_version_element(tree)

        new_val = f"v{new_version}" if raw_version.startswith("v") else str(new_version)
        elem.text = new_val

        if hasattr(ET, "indent"):
            ET.indent(tree, space="  ")

        tree.write(
            self.config_path,
            encoding="utf-8",
            xml_declaration=True
        )