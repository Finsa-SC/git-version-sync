# Usage

## Global Options

```bash
git-version-sync [OPTIONS] COMMAND
```

| Option | Description |
|--------|------------|
| `-c, --config PATH` | Use custom config file |
| `-v, --version` | Display version |
| `-h, --help` | Show help |

## Commands

### Check

Verify version consistency between Git tags and configuration.

```bash
git-version-sync check
```

**Options:**
- `--no-fetch` - Skip fetching from remote (offline mode)

**Examples:**

```bash
# Check current status
$ git-version-sync check
Version is synchronized (v1.14.0)

# Check with custom config
$ git-version-sync check --config package.json

# Check offline
$ git-version-sync check --no-fetch
```

---

### Sync

Synchronize version discrepancies between config and Git.

```bash
git-version-sync sync
```

**Options (mutually exclusive):**
- `--to-git` - Update config to match Git tag
- `--to-config` - Update Git tag to match config

**Examples:**

```bash
# Auto-sync (uses highest version)
$ git-version-sync sync
Config: v1.13.0
Git: v1.14.0
→ Syncing to v1.14.0

# Sync to specific direction
$ git-version-sync sync --to-config
```

---

### Bump

Increment version and create Git tag.

```bash
git-version-sync bump [PART]
```

**Arguments:**

| Argument | Behavior |
|----------|----------|
| *(none)* | Interactive - Suggests, asks confirmation |
| `auto` | Auto-detect, no confirmation |
| `major` | Bump major version (1.0.0 → 2.0.0) |
| `minor` | Bump minor version (1.0.0 → 1.1.0) |
| `patch` | Bump patch version (1.0.0 → 1.0.1) |

**Options:**

| Option | Description |
|--------|------------|
| `-f, --force` | Force bump despite version mismatch |
| `-p, --push` | Push to remote automatically |
| `-m, --message TEXT` | Custom annotation message |
| `-r, --release [NOTES]` | Create GitHub release |
| `-d, --draft` | Save release as draft |
| `-n, --dry-run` | Preview without applying |

**Examples:**

```bash
# Interactive (recommended)
$ git-version-sync bump
Detected 2 'feat' commit(s)
Suggested: minor (v1.14.0 → v1.15.0)
Apply? [Y/n]: y
Success

# Auto-detect
$ git-version-sync bump auto

# Manual with options
$ git-version-sync bump minor -p -r "New features"

# Dry-run preview
$ git-version-sync bump patch --dry-run
```

---

### Push

Push commits and tags to remote.

```bash
git-version-sync push [TAGS...]
```

**Arguments:**
- *(none)* - Push current version tag
- `TAG1 TAG2 ...` - Push specific tags

**Options:**

| Option | Description |
|--------|------------|
| `-a, --all` - Push all local tags |
| `-r, --release [NOTES]` | Create GitHub release |

**Examples:**

```bash
# Push current tag
$ git-version-sync push

# Push all tags
$ git-version-sync push -a

# Push with release
$ git-version-sync push -r "Stable release"

# Push specific tags
$ git-version-sync push v1.14.0 v1.15.0 -r
```

---

### Undo

Rollback last version bump.

```bash
git-version-sync undo [TARGET]
```

**Arguments:**
- *(none)* - Undo latest tag
- `TAG` - Undo specific tag (e.g., `v1.15.0`)

**Options:**

| Option | Description |
|--------|------------|
| `-r, --remote` | Also delete from remote |
| `-f, --force` | Skip confirmation |

**Examples:**

```bash
# Undo latest (interactive)
$ git-version-sync undo
Undo v1.15.0? [y/N]: y
Done

# Undo specific with remote cleanup
$ git-version-sync undo v1.14.2 -r -f
```

---

## Conventional Commits

Tool analyzes conventional commits to suggest version bumps:

| Format | Bump Type |
|--------|-----------|
| `feat:` | Minor (adds feature) |
| `fix:` | Patch (fixes bug) |
| `breaking:` or `BREAKING CHANGE:` | Major (breaking change) |
| `chore:`, `docs:`, `refactor:` | No bump |

**Example:**
```
commit 1: feat(api): add caching layer
commit 2: fix(db): connection timeout

$ git-version-sync bump
Detected 1 'feat', 1 'fix'
Suggested: minor (feature > fix)
```
