# Installation

## Requirements

- **Python >= 3.10** (for PyPI)
- **Node.js >= 14** (for npm)
- **Git** installed and configured

## Via PyPI (Python)

### Using pip

```bash
pip install git-version-sync
```

### Using pipx (isolated environment)

```bash
pipx install git-version-sync
```

### Verify installation

```bash
git-version-sync --version
```

## Via npm (Node.js)

### Global installation

```bash
npm install -g git-version-sync
```

### Local project installation

```bash
npm install --save-dev git-version-sync
npx git-version-sync bump
```

### Verify installation

```bash
git-version-sync --version
```

## From Source

```bash
git clone https://github.com/Finsa-SC/git-version-sync.git
cd git-version-sync
pip install -e .
```

Then verify:

```bash
git-version-sync --version
```

## Troubleshooting Installation

### Command not found

**Issue:** `git-version-sync: command not found`

**Solution:**
- PyPI: Ensure pip directory in PATH: `python -m git_version_sync --version`
- npm: Try `npx git-version-sync --version`
- pipx: Reinstall with `pipx install --force git-version-sync`

### Permission denied

**Issue:** Permission denied when installing with pip

**Solution:**
```bash
pip install --user git-version-sync
# or use pipx
pipx install git-version-sync
```

### Version mismatch

**Issue:** Multiple installations causing conflicts

**Solution:**
```bash
# Uninstall all
pip uninstall git-version-sync
npm uninstall -g git-version-sync

# Reinstall once
pip install git-version-sync
```
