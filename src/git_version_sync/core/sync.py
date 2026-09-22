from .bump import bump_config_version, bump_git_tag
from .check import get_config_tag, get_local_tags, parse_highest_verion

def do_sync(to_git: bool=False, to_config: bool=False) -> str:
    config_tag = get_config_tag()
    local_tags = get_local_tags()
    highest_local_tag = parse_highest_verion(local_tags)

    if config_tag == highest_local_tag:
        return f"Already in sync at v({config_tag})"

    if to_git:
        if highest_local_tag:
            bump_config_version(highest_local_tag)
            return f"Synced config version to match Git tag v{highest_local_tag}"
        else:
            raise RuntimeError("No git tag found on local.")

    elif to_config and highest_local_tag:
        bump_git_tag(config_tag, message=f"Sync git tag to v{config_tag}")
        return f"Synced Git tag to match config version v{config_tag}"

    else:
        if highest_local_tag:
            target_version = max(config_tag, highest_local_tag)
        else:
            target_version = config_tag

        if highest_local_tag and highest_local_tag > config_tag:
            bump_config_version(target_version)
        else:
            bump_git_tag(target_version)

        return f"Synced workspace to highest version v{target_version}"