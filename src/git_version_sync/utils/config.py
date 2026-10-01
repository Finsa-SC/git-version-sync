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

def get_list_config_path(config_name: Path | None=None) -> list[Path]:
    from git_version_sync.core.git import get_git_path

    git_path = get_git_path()
    if config_name:
        config_path = git_path / config_name

        if config_path.exists():
            return [config_path]
        else:
            raise RuntimeError(f"Config file not found: {config_path}")

    else:
        found_config = []
        for file in git_path.iterdir():
            file_name = file.name
            config_path = git_path / file_name

            if file_name in DEFAULT_CONFIG_FILES and config_path.exists():
                found_config.append(config_path)

        if found_config:
            return found_config

        raise ValueError(
            "No supported config file found in repository root.\n"
            "hint: Please specify the config file manually using '--config <path>' if you use a custom setup."
        )

if __name__ == "__main__":
    print(get_list_config_path())