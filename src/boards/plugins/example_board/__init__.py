"""
Example board module demonstrating the board system.

This board module shows how to create a simple board that displays text and uses configuration.
"""

# Board metadata using standard Python package conventions
__plugin_id__ = "example_board"  # Canonical folder name for installation (REQUIRED)
__version__ = "1.0.0"
__description__ = "Example board module for demonstration"
__board_name__ = "Example Board"
__author__ = "NHL LED Scoreboard"

# Board requirements (optional)
__requirements__ = []

# Minimum application version required (optional)
__min_app_version__ = "2025.9.0"

# Files to preserve during plugin updates/removals (optional)
# The plugin manager will preserve these files when updating or removing with --keep-config
# Supports glob patterns like *.csv, data/*, custom_*
# Default if not specified: ["config.json", "*.csv", "data/*", "custom_*"]
__preserve_files__ = [
    "config.json",
    # Add other user-modifiable files here, e.g.:
    # "custom_data.csv",
    # "data/*.json",
]