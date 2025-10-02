# Plugin Manager

Simple plugin manager for board plugins. Each plugin is a separate git repository that gets cloned into `src/boards/plugins/`.

## Quick Start

```bash
# First time setup: copy the example configuration
cp plugins.json.example plugins.json

# List installed plugins
python plugins.py list

# Install all plugins from your configuration
python plugins.py sync

# Add a new plugin - plugin name is auto-detected from __plugin_id__
python plugins.py add https://github.com/user/wvu-score.git --ref v1.2.0

# Add with custom name override (advanced)
python plugins.py add https://github.com/user/wvu-score.git --name wvu_score

# Remove a plugin (preserves user files if --keep-config is used)
python plugins.py rm nfl_board --keep-config

# Enable verbose logging
python plugins.py --verbose sync
```

## Configuration Files

- **`plugins.json.example`** - Template with recommended plugins (committed to git)
- **`plugins.json`** - Your customized plugin list (gitignored - won't conflict on pulls)
- **`plugins.lock.json`** - Auto-generated lock file with exact commit SHAs (gitignored)

## User File Preservation

The plugin manager automatically preserves user-modified files during updates and removals. This includes:

### Default Preserved Patterns
If a plugin doesn't specify `__preserve_files__`, these patterns are preserved by default:
- `config.json`
- `*.csv`
- `data/*`
- `custom_*`

### Custom Preservation (Plugin Authors)
Plugin authors can specify custom files to preserve in their `__init__.py`:

```python
# In your plugin's __init__.py
__preserve_files__ = [
    "config.json",
    "custom_holidays.csv",
    "data/*.json",
    "user_settings.txt"
]
```

### How It Works
- **On update** (`sync` or `add`): User files are backed up, plugin is updated, then user files are restored
- **On removal** (`rm --keep-config`): Specified files are preserved in the plugin directory after removal
- Supports glob patterns for flexible file matching
- Works recursively in subdirectories (e.g., `data/*`)

### Examples
```bash
# Update plugin but keep user's config.json and CSV files
python plugins.py sync

# Remove plugin but preserve all user-modified files
python plugins.py rm holiday_countdown --keep-config

# Force fresh install (no preservation)
# First remove without preserving, then re-add
python plugins.py rm holiday_countdown
python plugins.py add holiday_countdown https://github.com/user/holiday-countdown.git
```

## How It Works

### Plugin Naming (Important!)
- Each plugin **must** define `__plugin_id__` in its `__init__.py`
- This ensures consistent folder names across all installations
- Example: `__plugin_id__ = "nfl_board"`
- The plugin manager auto-detects this ID when you run `add`
- Users cannot accidentally misconfigure plugin names

### First Time Setup
1. Clone the repo - it includes `plugins.json.example` with recommended plugins
2. Copy `plugins.json.example` to `plugins.json` (or let `add` create it)
3. Run `python plugins.py sync` to install all plugins

### Customizing Your Setup
- `plugins.json` is gitignored, so your customizations won't conflict when you `git pull`
- `add` and `rm` commands automatically create/update your `plugins.json`
- The lock file pins exact commits for reproducibility
- Plugin names are auto-detected from `__plugin_id__` for consistency

### Developer Workflow
- Update `plugins.json.example` to change recommended plugins for all users
- Individual users' `plugins.json` won't be affected by your changes
- Similar to `config/config.json.sample` pattern already used in this project
- **Always include `__plugin_id__` in your plugin's `__init__.py`**

## Creating a Plugin

### Required Files
Your plugin repo must contain:
- `__init__.py` - Plugin metadata (including **`__plugin_id__`**)
- `board.py` - Board class inheriting from `BoardBase`
- `config.sample.json` - Sample configuration

### Minimal __init__.py Example
```python
"""
My Custom Board Plugin
"""

# REQUIRED: Canonical folder name for installation
__plugin_id__ = "my_custom_board"

# Optional metadata
__version__ = "1.0.0"
__description__ = "My custom board for displaying data"
__board_name__ = "My Custom Board"
__author__ = "Your Name"

# Optional: Additional dependencies
__requirements__ = []

# Optional: Files to preserve during updates
__preserve_files__ = [
    "config.json",
    "custom_data.csv"
]
```

### Plugin ID Rules
- Must be a valid Python module name (lowercase, underscores only)
- Should match your local folder structure expectations
- Examples: `nfl_board`, `holiday_countdown`, `wvu_score`
- **NOT**: `NFL-Board`, `holiday countdown`, `wvu.score`

## Gitignore

Already configured in `.gitignore`:
```
src/boards/plugins/*
!src/boards/plugins/.gitkeep
plugins.json
plugins.lock.json
```

This prevents plugin code and user customizations from being committed while tracking recommended plugins via `plugins.json.example`.
