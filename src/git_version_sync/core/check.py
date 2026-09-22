from pathlib import Path
import subprocess

def get_git_path() -> Path:
    command = ["git", "rev-parse", "--show-toplevel"]
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True
    )

    return Path(result.stdout.strip())

