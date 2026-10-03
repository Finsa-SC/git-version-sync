# Examples

## Single-Config Project

**Scenario:** Node.js project with only `package.json`

```bash
# Check version
$ git-version-sync check
Version is synchronized (v1.14.0)

# Bump interactively
$ git-version-sync bump
Detected 3 'feat' commit(s)
Suggested bump: minor (v1.14.0 -> v1.15.0)
Apply this version bump? [Y/n]: y

Updated package.json to v1.15.0
Committed changes: 'bump version to v1.15.0'
Created Git tag v1.15.0

Success bump version to v1.15.0
```

## Multi-Config Project

**Scenario:** Full-stack project with `package.json`, `pyproject.toml`, `docker-compose.yaml`

### Before bump
```
📁 project/
├── package.json (version: 1.14.0)
├── pyproject.toml (version: 1.14.0)
├── docker-compose.yaml (version: 1.14.0)
└── .git/tags → v1.14.0
```

### Run bump
```bash
$ git-version-sync bump minor
Detected 2 'feat' commit(s)
Suggested bump: minor (v1.14.0 -> v1.15.0)
Apply this version bump? [Y/n]: y

Updated package.json to v1.15.0
Updated pyproject.toml to v1.15.0
Updated docker-compose.yaml to v1.15.0
Committed changes: 'bump version to v1.15.0'
Created Git tag v1.15.0

Success bump version to v1.15.0
```

### After bump
```
📁 project/
├── package.json (version: 1.15.0) ✓
├── pyproject.toml (version: 1.15.0) ✓
├── docker-compose.yaml (version: 1.15.0) ✓
└── .git/tags → v1.15.0 ✓

All configs in sync!
```

**Key:** All files updated atomically in single operation. No partial state.

## GitHub Release

### Basic release
```bash
$ git-version-sync bump minor -p -r
Success bump version to v1.15.0
Pushed commit and tag to remote
Created GitHub Release v1.15.0

# Changelog auto-generated:
## What's Changed

### Features
- feat(api): add caching layer
- feat(cli): new --verbose flag

### Fixes
- fix(db): connection timeout issue

**Full Changelog**: https://github.com/user/repo/compare/v1.14.0...v1.15.0
```

### Release with custom notes
```bash
$ git-version-sync bump minor -p -r "Performance improvements and bug fixes"
Success bump version to v1.15.0
Pushed commit and tag
Created GitHub Release v1.15.0 with custom notes
```

### Draft release (for review)
```bash
$ git-version-sync bump minor -p -r -d
Success bump version to v1.15.0
Pushed commit and tag
Created GitHub Release v1.15.0 (DRAFT)

# Review on GitHub, then publish manually
```

## Dry-Run Preview

Test bump before applying:

```bash
$ git-version-sync bump minor --dry-run
Detected 2 'feat' commit(s)
Suggested bump: minor (v1.14.0 -> v1.15.0)

Would update package.json to v1.15.0 (DRY RUN)
Would update docker-compose.yaml to v1.15.0 (DRY RUN)
Would commit: 'bump version to v1.15.0' (DRY RUN)
Would create Git tag v1.15.0 (DRY RUN)

Dry run complete (no changes made)
```

Then run for real if looks good:
```bash
$ git-version-sync bump minor
```

## Protected Branch Handling

Auto-recovery on protected branch:

```bash
# Attempt bump with push
$ git-version-sync bump minor -p

Updated configs locally
Committed changes
Created Git tag locally
Pushing to remote...

[!] Error: remote: error: GH006: Protected branch
Auto-rolling back...
→ Reverted config changes
→ Deleted local tag
→ Undo? [y/N]: y

Successfully undone
```

**Result:** Zero partial state. Either fully complete or fully rolled back.

## Undo & Rollback

Undo last bump:

```bash
$ git-version-sync undo
Are you sure you want to undo v1.15.0? [y/N]: y
Reset last git commit
Reverted package.json version to v1.14.0
Reverted docker-compose.yaml version to v1.14.0
Deleted local tag v1.15.0

Successfully undone
```

Undo specific version with remote cleanup:

```bash
$ git-version-sync undo v1.14.2 -r -f
Successfully undone v1.14.2 (local and remote deleted)
```

## Custom Config File

Use non-standard config:

```bash
# Bump with custom file
$ git-version-sync bump patch --config my-version.json

# Or
$ git-version-sync --config my-version.json bump patch
```

## Offline Mode

Check without network:

```bash
$ git-version-sync check --no-fetch
Version is synchronized (v1.14.0)
```

No remote fetch, works offline.
