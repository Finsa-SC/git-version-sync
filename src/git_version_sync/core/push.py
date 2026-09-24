from .check import get_local_tags, get_remote_tags

def do_push(tags: list[str]):
    local_tags = get_local_tags()
    remote_tags = get_remote_tags()

