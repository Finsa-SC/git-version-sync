# Configuration Files

## Supported Formats

| Format | File Names | Projects |
|--------|-----------|----------|
| TOML | `pyproject.toml`, `Cargo.toml` | Python, Rust |
| JSON | `package.json`, `composer.json` | Node.js, PHP |
| YAML | `pubspec.yaml`, `docker-compose.yaml` | Dart, Docker |
| INI/CFG | `setup.cfg`, `*.cfg`, `*.ini` | Python (legacy) |
| XML | `pom.xml`, `*.xml`, `*.xaml` | Java, .NET |

## Auto-detection

Tool automatically detects and manages versions in **all found files** simultaneously.

### Detection Order

Scans in this order:
1. `pyproject.toml` (Python)
2. `Cargo.toml` (Rust)
3. `package.json` (Node.js)
4. `setup.cfg` (Python legacy)
5. `pubspec.yaml` (Dart)
6. `pom.xml` (Java)
7. `composer.json` (PHP)
8. `docker-compose.yaml` (Docker)

**Important:** All found files are managed together, not just the first one.

### Example: Multi-config Project

```
📁 project/
├── package.json          → Detected ✓
├── pyproject.toml        → Detected ✓
├── docker-compose.yaml   → Detected ✓
└── .git/tags/v1.14.0     → All in sync ✓
```

When you bump, all three files update to same version.

## Specify Custom Config

Use `--config` flag (works anywhere in command):

```bash
git-version-sync --config my-config.json bump
git-version-sync bump --config my-config.json
```

## Version Format Handling

Tool automatically detects version prefix requirements:

### With 'v' prefix (Git tags style)
```toml
# pyproject.toml
version = "v1.14.0"

# docker-compose.yaml
APP_VERSION: "v1.14.0"
```

### Without prefix (npm style)
```json
{
  "version": "1.14.0"
}
```

**Tool auto-detects and handles both formats.** No configuration needed.

## Configuration Examples

### Python (pyproject.toml)
```toml
[project]
name = "my-package"
version = "1.14.0"
```

### Node.js (package.json)
```json
{
  "name": "my-package",
  "version": "1.14.0"
}
```

### Rust (Cargo.toml)
```toml
[package]
name = "my-package"
version = "1.14.0"
```

### Docker (docker-compose.yaml)
```yaml
version: '3.8'
services:
  app:
    environment:
      APP_VERSION: "1.14.0"
```

### Java (pom.xml)
```xml
<project>
  <version>1.14.0</version>
</project>
```

### PHP (composer.json)
```json
{
  "version": "1.14.0"
}
```
