# Troubleshooting

## Version Mismatch

**Error:**
```
Version mismatch detected!
  Config: v1.14.0
  Git   : v1.13.0
```

**Cause:** Git tag and config file are out of sync.

**Solutions:**

1. **Sync automatically** (use highest version):
   ```bash
   git-version-sync sync
   ```

2. **Sync to Git tag** (config becomes v1.13.0):
   ```bash
   git-version-sync sync --to-git
   ```

3. **Sync to config** (Git tag becomes v1.14.0):
   ```bash
   git-version-sync sync --to-config
   ```

4. **Force bump anyway**:
   ```bash
   git-version-sync bump minor --force
   ```

---

## Network Error

**Error:**
```
Network error: Network is unreachable. Unable to fetch remote tags.
```

**Cause:** Internet disconnected or Git remote unreachable.

**Solutions:**

1. **Check connectivity**:
   ```bash
   git remote -v
   git fetch origin
   ```

2. **Work offline** (skip network check):
   ```bash
   git-version-sync check --no-fetch
   git-version-sync bump --force
   ```

3. **Try again** (when network available):
   ```bash
   git-version-sync check
   ```

---

## Protected Branch Error

**Error:**
```
[!] Error: remote: error: GH006: Protected branch update failed
[!] Auto-rolling back...
```

**Cause:** GitHub branch protection requires PR review before pushing.

**Info:** Tool automatically rolled back to prevent partial state. This is expected behavior.

**Solutions:**

1. **Create draft release** (safer, for review):
   ```bash
   git-version-sync bump minor -r -d
   # Review on GitHub, then publish
   ```

2. **Bump without push** (then create PR):
   ```bash
   git-version-sync bump minor
   git push -u origin version-bump
   # Create PR for review
   ```

3. **Get push permission** (if you have permission):
   ```bash
   # Ask repository admin for push access to main/dev
   git-version-sync bump minor -p
   ```

---

## Config File Not Found

**Error:**
```
No supported config files found
```

**Cause:** No supported config file in current directory.

**Solutions:**

1. **Specify custom config**:
   ```bash
   git-version-sync --config my-config.json bump
   ```

2. **Create config file**:
   ```bash
   # Example: Node.js
   echo '{"version": "1.0.0"}' > package.json
   
   # Example: Python
   echo '[project]
   version = "1.0.0"' > pyproject.toml
   
   git-version-sync bump
   ```

3. **Verify current directory**:
   ```bash
   pwd
   ls -la
   ```

---

## GitHub Release Missing (gh CLI)

**Error:**
```
GitHub Release creation requires 'gh' CLI to be installed
```

**Cause:** GitHub CLI (`gh`) not installed or not authenticated.

**Solutions:**

1. **Install GitHub CLI**:
   ```bash
   # macOS
   brew install gh
   
   # Ubuntu/Debian
   sudo apt install gh
   
   # Windows
   choco install gh
   
   # Or from source
   https://github.com/cli/cli#installation
   ```

2. **Authenticate with GitHub**:
   ```bash
   gh auth login
   # Choose: GitHub.com, HTTPS, Paste token, Y
   ```

3. **Verify installation**:
   ```bash
   gh --version
   gh auth status
   ```

4. **Try again**:
   ```bash
   git-version-sync bump minor -r
   ```

---

## No Commits Since Last Version

**Error:**
```
No commits found since v1.14.0
Cannot determine version bump
```

**Cause:** No new commits since last tag.

**Solutions:**

1. **Specify version explicitly** (no auto-detect):
   ```bash
   git-version-sync bump patch
   ```

2. **Check git history**:
   ```bash
   git log v1.14.0..HEAD
   ```

3. **Create commits first**:
   ```bash
   git commit -m "feat: new feature"
   git-version-sync bump
   ```

---

## Config File Not Recognized

**Error:**
```
Unable to parse version from config file
```

**Cause:** Config file format not supported or version not found.

**Solutions:**

1. **Check supported formats**:
   See [Configuration Files](./configuration.md)

2. **Verify version key in file**:
   ```bash
   # pyproject.toml
   grep "version" pyproject.toml
   
   # package.json
   grep "version" package.json
   
   # docker-compose.yaml
   grep "APP_VERSION" docker-compose.yaml
   ```

3. **Ensure valid format**:
   - JSON must be valid JSON
   - YAML must be valid YAML
   - TOML must be valid TOML

4. **Specify custom config**:
   ```bash
   git-version-sync --config path/to/file bump
   ```

---

## Permission Denied

**Error:**
```
Permission denied: Unable to write to config file
```

**Cause:** File permissions restrict writing.

**Solutions:**

1. **Check file permissions**:
   ```bash
   ls -la config-file
   ```

2. **Fix permissions**:
   ```bash
   chmod 644 package.json
   chmod 644 pyproject.toml
   ```

3. **Check directory permissions**:
   ```bash
   # Ensure write permission to directory
   chmod 755 .
   ```

---

## Command Not Found

**Error:**
```
git-version-sync: command not found
```

**Cause:** Installation incomplete or PATH not updated.

**Solutions:**

1. **Verify installation**:
   ```bash
   pip show git-version-sync       # PyPI
   npm list -g git-version-sync    # npm
   ```

2. **Try full path**:
   ```bash
   python -m git_version_sync --version
   npx git-version-sync --version
   ```

3. **Reinstall**:
   ```bash
   # PyPI
   pip install --force-reinstall git-version-sync
   
   # npm
   npm install -g git-version-sync
   
   # pipx
   pipx install --force git-version-sync
   ```

4. **Check PATH**:
   ```bash
   echo $PATH
   ```

---

## Undoing Wrong Undo

**Error:**
```
Accidentally undid the wrong bump
```

**Solution:**

Git history is preserved. Check reflog:

```bash
git reflog
# Find the commit you want to restore

git reset --hard <commit-hash>
git tag v1.15.0  # Recreate tag if needed
```

Then:
```bash
git push origin main --force-with-lease
git push origin v1.15.0
```

---

## Conflicting Tags

**Error:**
```
Tag already exists: v1.15.0
```

**Cause:** Tag already created locally or remotely.

**Solutions:**

1. **Delete local tag**:
   ```bash
   git tag -d v1.15.0
   git-version-sync bump
   ```

2. **Delete remote tag**:
   ```bash
   git push origin --delete v1.15.0
   git-version-sync bump -p
   ```

3. **Force tag**:
   ```bash
   git tag -f v1.15.0
   git push origin -f v1.15.0
   ```

---

## Getting Help

Still stuck? Try:

1. **Check help**:
   ```bash
   git-version-sync --help
   git-version-sync bump --help
   ```

2. **Verify setup**:
   ```bash
   git-version-sync check
   git log --oneline -5
   git tag -l
   ```

3. **Open issue**:
   - [GitHub Issues](https://github.com/Finsa-SC/git-version-sync/issues)
   - Include output of `git-version-sync check`
   - Include error message
   - Describe what you're trying to do
