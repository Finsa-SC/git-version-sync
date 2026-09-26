from abc import ABC, abstractmethod
from pathlib import Path
from packaging.version import Version

class BaseConfigParser(ABC):
    def __init__(self, config_path: Path):
        self.config_path = config_path

    @abstractmethod
    def get_version(self) -> Version:
        ...

    @abstractmethod
    def update_version(self, new_version: Version) -> None:
        ...