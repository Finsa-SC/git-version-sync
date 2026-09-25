from dataclasses import dataclass
from typing import Literal

BumpType = Literal["major", "minor", "patch"]

@dataclass(frozen=True)
class BumpRequest:
    bump_type   : BumpType
    tag_message : str|None
    release     : str|None
    force       : bool = False
    push        : bool = False
    draft       : bool = False
    dry_run     : bool = False