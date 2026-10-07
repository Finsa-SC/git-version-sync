from dataclasses import dataclass

@dataclass(frozen=True)
class PushRequest:
    tags        : list[str]
    push_all    : bool = False
    release     : str|None = None
    remote_name : str = 'origin'