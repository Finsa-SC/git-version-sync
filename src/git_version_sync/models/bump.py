from dataclasses import dataclass
from typing import Literal

BumpType = Literal["major", "minor", "patch"]

@dataclass(frozen=True)
class BumpRequest:
    bump_type   : BumpType
    tag_message : str|None
    force       : bool
    push        : bool
    release     : str|None