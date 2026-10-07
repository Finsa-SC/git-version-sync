# Examples

## Single-Config Project

**Scenario:** Node.js project with only `package.json`

```bash
# Check version
$ git-version-sync check
Version (1.14.0) is synchronized with local tag 'v1.14.0'.

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

Undo last bump (local only):

```bash
$ git-version-sync undo
Are you sure you want to undo v1.15.0? [y/N]: y
Reset last git commit
Reverted package.json version to v1.14.0
Reverted docker-compose.yaml version to v1.14.0
Deleted local tag v1.15.0

Successfully undone
```

Undo a specific version and delete it from the remote too:

```bash
$ git-version-sync undo v1.14.2 -R -f
Successfully undone v1.14.2 (local and remote deleted)
```

## Staying in Sync with a Remote

**Scenario:** A teammate released `v2.11.0` and you want to catch up.

### 1. Peek first (nothing is changed)

```bash
$ git-version-sync check
Version (2.10.0) is synchronized with local tag 'v2.10.0'.

New tag(s) found on remote (origin):
  - v2.11.0

Warning: Local version is behind remote.
Hint: Remote has newer tags/commits. Run 'git pull' (or 'git fetch --tags') before pushing local changes.
```

`check` only reads the remote's tag list. It does not download anything or touch your files.

### 2. Get the code

```bash
$ git pull
```

### 3. Sync config files with the remote tag

```bash
$ git-version-sync sync --remote
Synced package.json version to match v2.11.0.
Synced docker-compose.yaml version to match v2.11.0.

Synced workspace to highest version v2.11.0.
```

### What if you skip step 2?

`sync --remote` refuses to run when the tag's commit is not part of your current branch. This prevents config files from claiming a version whose code you do not have yet:

```bash
$ git-version-sync sync --remote
Error: Commit 'c8d32f3' associated with tag 'v2.11.0' is not integrated into your current branch.
Hint: Please run 'git pull' or merge the target branch before syncing version.
```

Nothing is fetched and no file is modified when this happens, so you can safely `git pull` and run the command again.

> Plain `git-version-sync sync` (without `--remote`) is local only. It never contacts the remote.

## Pushing Tags

### Push the current tag

```bash
$ git-version-sync push
Pushing tag(s) to remote: v2.12.6
Pushed: v2.12.6 -> origin.
```

### Push several tags, or all unpushed ones

```bash
$ git-version-sync push v2.12.7 v2.12.8
$ git-version-sync push --all
```

### Tag is already on the remote

```bash
$ git-version-sync push v2.12.6
Already on origin: v2.12.6
```

### Typos are caught before anything is pushed

If any tag does not exist locally, the whole command is cancelled:

```bash
$ git-version-sync push v2.12.7 v9.9.9 v2t2
Error: Tag(s) not found locally: v9.9.9, v2t2
Nothing was pushed.
```

Here `v2.12.7` is **not** pushed either, so you never end up with a half-finished push.

### Push to another remote

```bash
$ git-version-sync push v2.12.7 --remote upstream

# Remote name does not exist
$ git-version-sync push v2.12.7 --remote test_remote
Remote 'test_remote' not found.
Hint: Add a remote using 'git remote add test_remote <url>'
```

## Custom Config File

Use non-standard config:

```bash
# Bump with custom file
$ git-version-sync bump patch --config my-version.json
```

Options belong to the command, so they go **after** the command name. This form is not valid:

```bash
$ git-version-sync --config my-version.json bump patch    # rejected by the parser
```

## Offline Mode

Check without network:

```bash
$ git-version-sync check --no-fetch
Version (1.14.0) is synchronized with local tag 'v1.14.0'.
```

No remote access, works offline.

## Using in Scripts and CI

Exit codes are reliable (`0` success, `1` tool error, `2` bad arguments, `130` Ctrl+C), and errors go to stderr:

```bash
# Fail the pipeline if config and tags disagree
git-version-sync check || exit 1

# Publish only if the tag push succeeded
git-version-sync push v1.15.0 && echo "tag published"
```

In `fish`, read the exit code with `$status` instead of `$?`.