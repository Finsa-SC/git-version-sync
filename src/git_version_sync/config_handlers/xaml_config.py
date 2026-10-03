import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, Tuple
from packaging.version import Version

from .base import BaseConfigParser


class XmlConfigParser(BaseConfigParser):

    def __init__(self, config_path: Path):
        super().__init__(config_path)
        self.priority_xpaths = [
            # 1. Maven project version: <project><version>
            "./{*}version",
            # 2. Generic root version: <root><version>
            "./version",
            # 3. Maven parent fallback: <project><parent><version>
            "./{*}parent/{*}version",
            # 4. Android / Generic AppManifest: <manifest>/<widget>/<package>
            "./{*}metadata/{*}version",
        ]

    def _parse_tree(self) -> ET.ElementTree:
        try:
            return ET.parse(self.config_path)
        except ET.ParseError as e:
            raise RuntimeError(f"Failed to parse XML file {self.config_path.name}: {e}") from e

    def _strip_ns(self, tag: str) -> str:
        return tag.split("}")[-1] if "}" in tag else tag

    def _find_version_element(self, tree: ET.ElementTree) -> Tuple[ET.Element, str]:
        root = tree.getroot()

        # Trying to search by priority XPaths
        for xpath in self.priority_xpaths:
            elem = root.find(xpath)
            if elem is not None and elem.text and elem.text.strip():
                return elem, elem.text.strip()

        # Fallback: Search tag 'version' which is a DIRECT CHILD of the root only
        for child in root:
            if self._strip_ns(child.tag) == "version" and child.text and child.text.strip():
                return child, child.text.strip()

        # Last fallback: Iterate all of tree, avoid tag inside <dependencies>, <plugins>, or <dependencyManagement>
        skip_parents = {"dependency", "plugin", "dependencyManagement", "dependencies", "plugins"}

        for parent in root.iter():
            if self._strip_ns(parent.tag) in skip_parents:
                continue
            for child in parent:
                if self._strip_ns(child.tag) == "version" and child.text and child.text.strip():
                    return child, child.text.strip()

        raise KeyError(f"Could not find a valid project '<version>' tag in {self.config_path.name}")

    def get_version(self) -> Version:
        tree = self._parse_tree()
        _, raw_version = self._find_version_element(tree)
        version_str = raw_version.lstrip("v")
        return Version(version_str)

    def update_version(self, new_version: Version) -> None:
        # Keeping built-in namespace Maven/XML to prevent broke while saving
        xml_str = self.config_path.read_text(encoding="utf-8")
        if 'xmlns="' in xml_str:
            # Extract default namespace to re-register
            import re
            match = re.search(r'xmlns="([^"]+)"', xml_str)
            if match:
                ET.register_namespace("", match.group(1))

        tree = self._parse_tree()
        elem, raw_version = self._find_version_element(tree)

        new_val = f"v{new_version}" if raw_version.startswith("v") else str(new_version)
        elem.text = new_val

        # Trim the indentation when Python 3.9+
        if hasattr(ET, "indent"):
            ET.indent(tree, space="  ")

        tree.write(
            self.config_path,
            encoding="utf-8",
            xml_declaration=True
        )