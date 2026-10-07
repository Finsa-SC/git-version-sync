from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class UndoRequest:
    undo_tag    : str
    force       : bool = False
    config_name : Path|None = None
    remote_name : str = "origin"