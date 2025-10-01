# Plugin Manager

Simple plugin manager for board plugins. Each plugin is a separate git repository that gets cloned into `src/boards/plugins/`.

## Quick Start

```bash
# List installed plugins
python plugins.py list

# Add a new plugin
python plugins.py add wvu-score https://github.com/user/wvu-score.git --ref v1.2.0

# Install/update all plugins from plugins.json
python plugins.py sync

# Remove a plugin (preserves config.json if --keep-config is used)
python plugins.py rm clock --keep-config

# Enable verbose logging
python plugins.py --verbose sync
```

## Configuration Files

- **`plugins.json`** - Source of truth for which plugins to install (committed to git)
- **`plugins.lock.json`** - Auto-generated lock file with exact commit SHAs (for reproducibility)

## Gitignore

Add to `.gitignore`:
```
src/boards/plugins/*
!src/boards/plugins/.gitkeep
plugins.lock.json
```

This prevents plugin code from being committed to your app repo while tracking which plugins should be installed.
