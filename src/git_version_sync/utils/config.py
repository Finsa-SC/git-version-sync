from pathlib import Path
from packaging.version import Version

from git_version_sync.exception import GitVersionSyncError
from .colors import Color

DEFAULT_CONFIG_FILES = [
    "pyproject.toml",
    "Cargo.toml",
    "package.json",
    "setup.cfg",
    "pubspec.yaml",
    "pom.xml",
    "composer.json",
    "docker-compose.yaml"
]

def get_config_version(config_name: Path | None=None) -> dict[Path, Version]:
    from git_version_sync.core.check import get_config_tag
    from git_version_sync.core.git import get_git_path

    git_path = get_git_path()

    # The --config argument is filled
    if config_name:
        config_path = git_path / config_name

        if config_path.exists():
            return {config_path: get_config_tag(config_path)}
        else:
            raise GitVersionSyncError(f"Config file not found: {config_path}")

    # Search all config file in git path
    else:
        found_config = {}
        for file in git_path.iterdir():
            file_name = file.name
            config_path = git_path / file_name

            if file_name in DEFAULT_CONFIG_FILES and config_path.exists():
                found_config[config_path] = get_config_tag(config_path)

        if found_config:
            return found_config

        raise GitVersionSyncError(
            "No supported config file found in repository root.\n"
            f"{Color.BLUE}Hint: Please specify the config file manually using '--config <path>' if you use a custom setup."
        )