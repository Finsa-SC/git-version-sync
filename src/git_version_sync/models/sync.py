from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class SyncRequest:
    to_git      : bool = False
    to_config   : bool = False
    config_name : Path|None = None
    no_prefix   : bool = False
    remote_name : str = "origin"