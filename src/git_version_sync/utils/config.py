from pathlib import Path


def get_config_path() -> Path:
    from git_version_sync.core.git import get_git_path

    config_path = get_git_path() / "pyproject.toml"
    if config_path.exists():
        return config_path
    else:
        raise RuntimeError(f"Config file not found: {config_path}")