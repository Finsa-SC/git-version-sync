import subprocess
from pathlib import Path

def get_git_path() -> Path:
    command = ["git", "rev-parse", "--show-toplevel"]
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True
    )

    return Path(result.stdout.strip())

def get_config_path() -> Path:
    config_path = get_git_path() / "pyproject.toml"
    if config_path.exists():
        return config_path
    else:
        raise RuntimeError(f"Config file not found: {config_path}")