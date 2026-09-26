from pathlib import Path


def get_config_path(config_name: Path|None=None) -> Path:
    from git_version_sync.core.git import get_git_path

    git_path = get_git_path()
    if config_name:
        config_path = git_path / config_name

        if config_path.exists():
            return config_path
        else:
            raise RuntimeError(f"Config file not found: {config_path}")

    else:
        if (config_path := git_path / "pyproject.toml").exists():
            return config_path

        elif (config_path := git_path / "Cargo.toml").exists():
            return config_path

        elif (config_path := git_path / "package.json").exists():
            return config_path

        else:
            raise RuntimeError(f"No supported config file found")