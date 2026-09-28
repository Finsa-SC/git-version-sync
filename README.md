# git-version-sync

   [![PyPI - Version](https://img.shields.io/pypi/v/git-version-sync)](https://pypi.org/project/git-version-sync/)
   [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A command-line tool to synchronize semantic versions between Git tags and project configuration files.

**Links:** [Repository](https://github.com/Finsa-SC/git-version-sync) · [PyPI](https://pypi.org/project/git-version-sync/) · [Issues](https://github.com/Finsa-SC/git-version-sync/issues)

## Features

- **Check** version status and consistency between Git tags and project configuration
- **Sync** version discrepancies with flexible sync directions
- **Bump** versions following semantic versioning (major, minor, patch, auto)
- **Push** commits and tags to remote repository
- **Undo** version bumps with optional remote cleanup
- **Auto-detect** configuration files (pyproject.toml, package.json, Cargo.toml, and more)
- **GitHub Release** integration for automated release creation
- **Dry-run mode** to preview changes before execution
- **Flexible config flag** - specify config file anywhere in command
- **Custom annotations** for Git tags
- **Force mode** for bypassing version mismatches

## Installation

### Requirements
- Python >= 3.10
- Git

### Via PyPI (Recommended)

```bash
pip install git-version-sync
```

Or with pipx for isolated installation:

```bash
pipx install git-version-sync
```

### From Source

```bash
git clone https://github.com/Finsa-SC/git-version-sync.git
cd git-version-sync
pip install -e .
```

## Supported Configuration Files

The tool automatically detects and supports multiple configuration file formats:

| Format | File Names | Projects |
|--------|-----------|----------|
| TOML | `pyproject.toml`, `Cargo.toml` | Python, Rust |
| JSON | `package.json` | Node.js, JavaScript |
| YAML | `*.yaml`, `*.yml` | DevOps, Multi-purpose |
| INI/CFG | `setup.cfg`, `*.cfg`, `*.ini` | Python (legacy) |
| XML | `*.xml` | Java, Enterprise |

**Auto-detection order:** pyproject.toml → package.json → Cargo.toml → *.yaml → setup.cfg → *.xml

The first file found will be used. You can also specify a custom config file with the `--config` flag.

## Usage

### Global Options

- `-c, --config PATH` - Path to a custom configuration file (works anywhere in the command)
- `-v, --version` - Display version information

### Check Command

Verify version consistency between Git tags and project configuration:

```bash
git-version-sync check
git-version-sync --config package.json check
git-version-sync check --config package.json
```

**Options:**
- `--no-fetch` - Skip fetching tags from remote repository

### Sync Command

Synchronize versions when discrepancies are detected:

```bash
git-version-sync sync
```

**Options (mutually exclusive):**
- `--to-git` - Force config version to match the highest Git tag
- `--to-config` - Force Git tag to match the version in project config

### Bump Command

Increment the version in configuration file and create a corresponding Git tag:

```bash
git-version-sync bump [major|minor|patch|auto]
```

**Arguments:**
- `part` - Version part to increment (major, minor, patch, auto). Optional - runs interactive mode if omitted.

**Modes:**
- **Interactive** (no argument) - Suggests bump type based on commit analysis and asks for confirmation
- **Auto** - Automatically detects version bump without confirmation
- **Manual** (major/minor/patch) - Explicitly specify version bump

**Options:**
- `-f, --force` - Force bump even if version mismatch occurs
- `-p, --push` - Automatically push commit and tag to remote
- `-m, --message MESSAGE` - Custom annotation message for the Git tag
- `-r, --release [NOTES]` - Create a GitHub release for the bumped version (requires 'gh' CLI)
- `-d, --draft` - Save the GitHub release as a draft (requires `--release`)
- `-n, --dry-run` - Perform a dry run without making any actual changes

### Push Command

Push the active branch and Git tags to remote repository:

```bash
git-version-sync push
```

**Arguments:**
- `tags` - Specific tag(s) to push (e.g., `v1.0.0 v1.0.1`). If empty, pushes active version tag.

**Options:**
- `-a, --all` - Push all local tags to remote

### Undo Command

Undo/rollback the last version bump and delete its corresponding Git tag:

```bash
git-version-sync undo
```

**Arguments:**
- `target` - Specific tag/version to undo (e.g., `v1.6.0`). Default: latest tag.

**Options:**
- `-r, --remote` - Also delete the target tag from remote repository
- `-f, --force` - Bypass confirmation prompts

## Examples

### Check current version status
```bash
$ git-version-sync check
Version is synchronized with highest local tag (v1.12.0)
```

### Check without fetching from remote
```bash
$ git-version-sync check --no-fetch
Version is synchronized with highest local tag (v1.12.0)
```

### Check with custom config file (flexible positioning)
```bash
$ git-version-sync --config package.json check
$ git-version-sync check --config package.json
```

### Bump with interactive mode (no argument)
```bash
$ git-version-sync bump
Detected feature addition in recent commits
Suggested bump: minor (v1.12.0 -> v1.13.0)
Apply this version bump? [Y/n]: y
Success bump version to v1.13.0
```

### Bump with auto-detection
```bash
$ git-version-sync bump auto
Success bump version to v1.13.0
```

### Bump patch version explicitly
```bash
$ git-version-sync bump patch
Success bump version to v1.12.1
```

### Bump minor version with custom message
```bash
$ git-version-sync bump minor -m "Add new features"
Success bump version to v1.13.0
```

### Bump patch version with push and GitHub release
```bash
$ git-version-sync bump patch -p -r "Bug fixes and improvements"
Success bump version to v1.12.1
Pushing commit and tag to remote...
Created GitHub Release v1.12.1
```

### Bump major version as draft release
```bash
$ git-version-sync bump major -p -r -d
Success bump version to v2.0.0
Pushing commit and tag to remote...
Created GitHub Release v2.0.0 (draft)
```

### Dry-run preview before bumping
```bash
$ git-version-sync bump minor -m "Release" -p --dry-run
Updated project config to v1.13.0 (DRY RUN)
Committed changes: 'bump version to v1.13.0' (DRY RUN)
Created Git tag v1.13.0 (DRY RUN)
Pushed commit and tag to remote (DRY RUN)

Success bump version to v1.13.0 (DRY RUN - no changes made)
```

### Push to remote
```bash
$ git-version-sync push
Pushing branch and tags to remote...
```

### Push specific tags
```bash
$ git-version-sync push v1.12.0 v1.12.1
Pushing specified tags to remote...
```

### Push all local tags
```bash
$ git-version-sync push -a
Pushing all local tags to remote...
```

### Undo latest version bump
```bash
$ git-version-sync undo
Are you sure you want to undo v1.12.1? (y/n): y
Successfully undone version bump
```

### Undo specific version and delete from remote
```bash
$ git-version-sync undo v1.12.1 -r -f
Successfully undone v1.12.1 and deleted from remote
```

### Display version
```bash
$ git-version-sync --version
git-version-sync 1.12.0
```

## Dependencies

- `packaging>=26.3` - For version parsing and comparison
- `pytest>=9.1.1` - Testing framework
- `pytest-mock>=3.15.1` - Mocking library for tests

## License

MIT - See LICENSE file for details

## Author

Finsa-SC