# Usage

## Global Options

```bash
git-version-sync [-h] [-v] COMMAND [OPTIONS]
```

| Option | Description |
|--------|------------|
| `-v, --version` | Display version |
| `-h, --help` | Show help |

> **Note:** `--config` and `--remote` are **not** global options. They belong to each command and must be written **after** the command name:
>
> ```bash
> git-version-sync check --remote upstream     # OK
> git-version-sync --remote upstream check     # error: rejected by the parser
> ```

## Common Command Options

Available on every command (`check`, `sync`, `bump`, `push`, `undo`):

| Option | Description |
|--------|------------|
| `-c, --config PATH` | Use a custom config file (e.g. `pyproject.toml`, `Cargo.toml`, `package.json`) |
| `-R, --remote [REMOTE]` | Target Git remote. If the flag is used without a name, `origin` is used |

## Local vs Remote Behavior

Commands work **locally by default**. A command only touches the remote when it needs to, or when you ask it to with `--remote`.

| Command | Without `--remote` | With `--remote` |
|---------|--------------------|-----------------|
| `check` | Reads remote tags (read-only, nothing is downloaded) | Same, against the remote you name |
| `sync` | Local only: compares config with local tags | Checks the remote's highest tag, then fetches tags if safe |
| `push` | Pushes to `origin` | Pushes to the remote you name |
| `undo` | Deletes the tag locally only | Also deletes the tag on the remote |

## Commands

### Check

Verify version consistency between Git tags and configuration. `check` only **reports**; it never changes files or tags.

```bash
git-version-sync check
```

**Options:**
- `--no-fetch` - Skip contacting the remote (offline mode)

**Examples:**

```bash
# Everything in sync
$ git-version-sync check
Version (1.14.0) is synchronized with local tag 'v1.14.0'.

# A newer tag exists on the remote
$ git-version-sync check
Version (2.10.0) is synchronized with local tag 'v2.10.0'.

New tag(s) found on remote (origin):
  - v2.11.0

Warning: Local version is behind remote.
Hint: Remote has newer tags/commits. Run 'git pull' (or 'git fetch --tags') before pushing local changes.

# Local tags that have not been pushed yet
$ git-version-sync check
Version (2.9.0) is synchronized with local tag 'v2.9.0'.

Pending Remote Sync (origin):
  - v2.7.0
  - v2.8.0
  - v2.9.0

# Check with custom config
$ git-version-sync check --config package.json

# Check offline
$ git-version-sync check --no-fetch
```

> Versions are compared numerically, so `v2.10.0` is higher than `v2.9.1`.

---

### Sync

Synchronize version discrepancies between config and Git.

```bash
git-version-sync sync
```

**Options:**

| Option | Description |
|--------|------------|
| `--to-git` | Update config to match the highest Git tag *(mutually exclusive with `--to-config`)* |
| `--to-config` | Update Git tag to match the config version *(mutually exclusive with `--to-git`)* |
| `-R, --remote [REMOTE]` | Also take the remote's highest tag into account (default remote: `origin`) |

**Local sync (default):** compares config files with the local tags only. No network access.

**Remote sync (`--remote`):** before changing any file, the tool:

1. Reads the highest tag on the remote (read-only).
2. If that tag already exists locally, there is nothing new to bring in.
3. Otherwise it checks that the commit the tag points to is part of your current branch's history. If it is not, `sync` stops with an error and **nothing is fetched or modified**.
4. If the check passes, it fetches the tags and updates the config.

**Examples:**

```bash
# Local sync
$ git-version-sync sync
Already in sync at (v2.10.0)

# Sync with the remote
$ git-version-sync sync --remote
Synced package.json version to match v2.12.0.
Synced docker-compose.yaml version to match v2.12.0.

Synced workspace to highest version v2.12.0.

# Remote has a newer tag, but you haven't pulled its commit yet
$ git-version-sync sync --remote
Error: Commit 'c8d32f3' associated with tag 'v2.11.0' is not integrated into your current branch.
Hint: Please run 'git pull' or merge the target branch before syncing version.

# Sync using a specific direction
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

Push Git tags to a remote.

```bash
git-version-sync push [TAGS...]
```

**Arguments:**
- *(none)* - Push the current version tag
- `TAG1 TAG2 ...` - Push specific tags

**Options:**

| Option | Description |
|--------|------------|
| `-a, --all` | Push all local tags that are not on the remote yet |
| `-r, --release [NOTES]` | Create GitHub release |
| `-R, --remote [REMOTE]` | Target remote (default: `origin`) |

**Rules:**
- Tags you name must exist locally. If **any** of them does not, the whole command is cancelled and **nothing is pushed**.
- Tags that already exist on the remote are reported and skipped; this is not an error.
- `--all` cannot be combined with explicit tags.

**Examples:**

```bash
# Push current tag
$ git-version-sync push
Pushing tag(s) to remote: v1.15.0
Pushed: v1.15.0 -> origin.

# Tag is already on the remote
$ git-version-sync push v1.14.0
Already on origin: v1.14.0

# Push all unpushed tags
$ git-version-sync push -a

# A tag does not exist locally: nothing is pushed
$ git-version-sync push v1.14.0 v9.9.9
Error: Tag(s) not found locally: v9.9.9
Nothing was pushed.

# Mixing --all with tags is rejected
$ git-version-sync push v1.14.0 --all
usage: git-version-sync push [-h] [-c PATH] [-R [REMOTE]] [-a] [-r [NOTES]] [tags ...]
git-version-sync push: error: --all cannot be combined with explicit tags.

# Push to a different remote
$ git-version-sync push v1.15.0 --remote upstream

# Push with release
$ git-version-sync push -r "Stable release"
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
| `-R, --remote [REMOTE]` | Also delete the tag from the remote (default: `origin`) |
| `-f, --force` | Skip confirmation |

**Examples:**

```bash
# Undo latest (interactive), local only
$ git-version-sync undo
Undo v1.15.0? [y/N]: y
Done

# Undo specific tag and delete it from origin too
$ git-version-sync undo v1.14.2 -R -f

# Delete from a specific remote
$ git-version-sync undo v1.14.2 -R upstream -f
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success, or nothing to do (e.g. "Already on origin") |
| `1` | The tool reported an error (remote not found, tag not found, sync refused, ...) |
| `2` | Invalid command-line arguments |
| `130` | Interrupted by the user (Ctrl+C) |

Error messages are written to **stderr**, so they stay separate from normal output when piped. This makes the tool safe to use in scripts and CI:

```bash
git-version-sync push v1.15.0 && echo "tag published"
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