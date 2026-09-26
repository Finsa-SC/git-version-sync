from dataclasses import dataclass
from pathlib import Path
from typing import Literal

BumpType = Literal["major", "minor", "patch"]

@dataclass(frozen=True)
class BumpRequest:
    bump_type   : BumpType
    config_path : Path|None = None
    tag_message : str|None = None
    release     : str|None = None
    force       : bool = False
    push        : bool = False
    draft       : bool = False
    dry_run     : bool = False