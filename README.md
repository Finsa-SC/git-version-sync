# git-version-sync

[![PyPI - Version](https://img.shields.io/pypi/v/git-version-sync)](https://pypi.org/project/git-version-sync/)
[![npm - Version](https://img.shields.io/npm/v/git-version-sync)](https://www.npmjs.com/package/git-version-sync)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A CLI tool to synchronize semantic versions between Git tags and project configuration files.

**Links:** [Repository](https://github.com/Finsa-SC/git-version-sync) · [PyPI](https://pypi.org/project/git-version-sync/) · [npm](https://www.npmjs.com/package/git-version-sync) · [Issues](https://github.com/Finsa-SC/git-version-sync/issues)

## Quick Start

```bash
# Install (choose one)
pip install git-version-sync        # Python/PyPI
npm install -g git-version-sync     # Node.js/npm

# Use it
cd your-project
git-version-sync bump               # Interactive bump
git-version-sync bump -p -r         # Bump + push + release
```

## Features

- **Check** version status and consistency
- **Sync** version discrepancies between config and Git tags
- **Bump** versions (major, minor, patch, auto) with semantic versioning
- **Push** to remote with optional GitHub releases
- **Undo** version bumps with automatic rollback on error
- **Auto-detect** multiple config files (pyproject.toml, package.json, Cargo.toml, docker-compose.yaml, and more)
- **Auto-generate** changelog from conventional commits
- **Multi-config** support - bump multiple files atomically
- **Protected branches** aware with automatic rollback
- **Dry-run** mode to preview before executing

## Documentation

| Topic | Link |
|-------|------|
| **Installation** | [PyPI, npm, from source](./docs/installation.md) |
| **Configuration** | [Supported files, auto-detection](./docs/configuration.md) |
| **Usage** | [Commands reference](./docs/usage.md) |
| **Examples** | [Single-config, multi-config, GitHub releases](./docs/examples.md) |
| **Troubleshooting** | [Common issues and solutions](./docs/troubleshooting.md) |

## Common Commands

```bash
# Check version status
git-version-sync check

# Bump and preview
git-version-sync bump --dry-run

# Bump + push to remote
git-version-sync bump minor -p

# Bump + push + create GitHub release
git-version-sync bump minor -p -r "New features"

# Undo last bump
git-version-sync undo
```

## License

MIT - See [LICENSE](LICENSE) file for details

## Author

[Finsa-SC](https://github.com/Finsa-SC)
