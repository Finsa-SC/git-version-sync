from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class SyncRequest:
    to_git      : bool = False
    to_config   : bool = False
    config_name : Path|None = None
    remote_name : str = "origin"