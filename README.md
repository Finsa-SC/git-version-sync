# git-version-sync

A command-line tool to synchronize semantic versions between Git tags and `pyproject.toml`.

## Features

- **Check** version status and consistency between Git tags and `pyproject.toml`
- **Sync** version discrepancies with flexible sync directions
- **Bump** versions following semantic versioning (major, minor, patch)
- **Auto Push** option to push commits and tags directly to remote
- **Custom annotations** for Git tags
- **Force mode** for bypassing version mismatches

## Installation

### Requirements
- Python >= 3.11
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
git clone <repository-url>
cd git-version-sync
pip install -e .
```

## Usage

### Check Command

Verify version consistency between Git tags and `pyproject.toml`:

```bash
git-version-sync check
```

**Options:**
- `--fetch` - Fetch remote tags before checking

### Sync Command

Synchronize versions when discrepancies are detected:

```bash
git-version-sync sync
```

**Options (mutually exclusive):**
- `--to-git` - Force `pyproject.toml` version to match the highest Git tag
- `--to-config` - Force Git tag to match `pyproject.toml` version

### Bump Command

Increment the version in `pyproject.toml` and create a corresponding Git tag:

```bash
git-version-sync bump {major|minor|patch}
```

**Options:**
- `-f, --force` - Force bump even if version mismatch occurs
- `-p, --push` - Automatically push commit and tag to remote
- `-m, --message MESSAGE` - Custom annotation message for the Git tag

## Examples

### Check current version status
```bash
$ git-version-sync check
Version is synchronized with highest local tag (v1.0.0)
```

### Bump patch version
```bash
$ git-version-sync bump patch
Success bump version to v1.0.1
```

### Bump minor version with custom message and auto-push
```bash
$ git-version-sync bump minor -m "Add new features" -p
Success bump version to v1.1.0
Pushing commit and tag to remote...
```

### Bump major version with force flag
```bash
$ git-version-sync bump major -f
Success bump version to v2.0.0
```

### Sync to Git tags
```bash
$ git-version-sync sync --to-git
Successfully synced version to match highest tag
```

## Dependencies

- `packaging>=26.3` - For version parsing and comparison

## License

See LICENSE file for details.

## Author

Finsa-SC