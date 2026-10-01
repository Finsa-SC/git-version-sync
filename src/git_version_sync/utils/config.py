from pathlib import Path

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
        for file_name in DEFAULT_CONFIG_FILES:
            config_path = git_path / file_name
            if config_path.exists():
                return config_path
        raise ValueError(
            "No supported config file found in repository root.\n"
            "hint: Please specify the config file manually using '--config <path>' if you use a custom setup."
        )