#!/usr/bin/env python3
"""
Barebones Plugin Manager for NHL LED Scoreboard

Manages board plugins as separate git repositories. Each plugin is cloned,
copied into src/boards/plugins/<name>, and tracked in plugins.lock.json
for reproducible installs.

Usage:
    python plugins.py add NAME URL [--ref REF]
    python plugins.py rm NAME [--keep-config]
    python plugins.py list
    python plugins.py sync
"""

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional

# Environment overrides for flexibility
PLUGINS_DIR = Path(os.getenv("PLUGINS_DIR", "src/boards/plugins"))
PLUGINS_JSON = Path(os.getenv("PLUGINS_JSON", "plugins.json"))
PLUGINS_LOCK = Path(os.getenv("PLUGINS_LOCK", "plugins.lock.json"))

logger = logging.getLogger(__name__)


def load_json(path: Path) -> dict:
    """Load JSON file, returning empty dict if not found."""
    if not path.exists():
        return {}
    try:
        with open(path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {path}: {e}")
        sys.exit(1)


def save_json_atomic(path: Path, data: dict):
    """Save JSON atomically using temp file + rename."""
    tmp_path = path.with_suffix(".tmp")
    with open(tmp_path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")  # trailing newline
    tmp_path.replace(path)


def check_git_available():
    """Ensure git is installed and available."""
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("Git is not installed or not in PATH. Please install git.")
        sys.exit(1)


def run_git(args: List[str], cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
    """Run a git command, returning CompletedProcess for inspection."""
    cmd = ["git"] + args
    logger.debug(f"Running: {' '.join(cmd)} (cwd={cwd})")
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def clone_plugin(url: str, ref: Optional[str], tmp_dir: Path) -> Optional[str]:
    """
    Clone a git repo into tmp_dir and optionally checkout a ref.
    Returns the resolved commit SHA, or None on failure.
    """
    # Clone with depth 1 for speed
    result = run_git(["clone", "--depth", "1", url, str(tmp_dir)])
    if result.returncode != 0:
        logger.error(f"Failed to clone {url}")
        logger.error(result.stderr)
        return None

    # If a ref is specified, fetch and checkout
    if ref:
        # Unshallow first to allow checking out arbitrary refs
        logger.debug(f"Fetching ref: {ref}")
        result = run_git(["fetch", "--depth", "1", "origin", ref], cwd=tmp_dir)
        if result.returncode != 0:
            logger.warning(f"Could not fetch ref '{ref}', using default branch")
        else:
            result = run_git(["checkout", ref], cwd=tmp_dir)
            if result.returncode != 0:
                logger.error(f"Failed to checkout ref '{ref}'")
                logger.error(result.stderr)
                return None

    # Get resolved commit SHA
    result = run_git(["rev-parse", "HEAD"], cwd=tmp_dir)
    if result.returncode != 0:
        logger.error("Failed to get commit SHA")
        return None

    commit_sha = result.stdout.strip()
    logger.debug(f"Resolved commit: {commit_sha}")
    return commit_sha


def copy_plugin_files(src: Path, dest: Path):
    """
    Copy plugin files from src to dest, excluding .git directory.
    Removes dest first if it exists to avoid stale files.
    """
    # Remove destination if it exists
    if dest.exists():
        logger.debug(f"Removing existing plugin at {dest}")
        shutil.rmtree(dest)

    # Copy files, ignoring .git
    def ignore_git(directory, contents):
        return [".git"] if ".git" in contents else []

    shutil.copytree(src, dest, ignore=ignore_git)
    logger.debug(f"Copied plugin files to {dest}")


def validate_plugin(plugin_path: Path) -> bool:
    """
    Check if plugin folder contains expected files.
    Returns True if valid, False with warning if suspicious.
    """
    expected_files = ["board.py", "__init__.py", "config.sample.json"]
    found = any((plugin_path / f).exists() for f in expected_files)

    if not found:
        logger.warning(
            f"Plugin at {plugin_path} doesn't contain expected files "
            f"({', '.join(expected_files)}). May not work correctly."
        )
        return False
    return True


def install_plugin(name: str, url: str, ref: Optional[str]) -> Optional[Dict]:
    """
    Install or update a single plugin.
    Returns lock entry dict on success, None on failure.
    """
    logger.info(f"Installing plugin '{name}' from {url}")

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # Clone and get commit SHA
        commit_sha = clone_plugin(url, ref, tmp_path)
        if not commit_sha:
            return None

        # Copy to plugins directory
        plugin_dest = PLUGINS_DIR / name
        PLUGINS_DIR.mkdir(parents=True, exist_ok=True)
        copy_plugin_files(tmp_path, plugin_dest)

        # Validate plugin structure
        validate_plugin(plugin_dest)

        logger.info(f"✓ Plugin '{name}' installed successfully (commit: {commit_sha[:7]})")

        # Return lock entry
        return {
            "name": name,
            "url": url,
            "ref": ref or "default",
            "commit": commit_sha,
        }


def cmd_add(args):
    """Add or update a plugin in plugins.json and install it."""
    check_git_available()

    # Load current plugins.json
    plugins_data = load_json(PLUGINS_JSON)
    if "plugins" not in plugins_data:
        plugins_data["plugins"] = []

    # Remove existing entry if present
    plugins_data["plugins"] = [
        p for p in plugins_data["plugins"] if p["name"] != args.name
    ]

    # Add new entry
    new_entry = {"name": args.name, "url": args.url}
    if args.ref:
        new_entry["ref"] = args.ref
    plugins_data["plugins"].append(new_entry)

    # Save plugins.json
    save_json_atomic(PLUGINS_JSON, plugins_data)
    logger.info(f"Added '{args.name}' to {PLUGINS_JSON}")

    # Install the plugin
    lock_entry = install_plugin(args.name, args.url, args.ref)
    if not lock_entry:
        logger.error(f"Failed to install plugin '{args.name}'")
        sys.exit(1)

    # Update lock file
    lock_data = load_json(PLUGINS_LOCK)
    if "locked" not in lock_data:
        lock_data["locked"] = []

    # Remove existing lock entry
    lock_data["locked"] = [p for p in lock_data["locked"] if p["name"] != args.name]
    lock_data["locked"].append(lock_entry)

    save_json_atomic(PLUGINS_LOCK, lock_data)
    logger.info(f"Updated {PLUGINS_LOCK}")


def cmd_rm(args):
    """Remove a plugin from plugins.json and delete its files."""
    # Load plugins.json
    plugins_data = load_json(PLUGINS_JSON)
    if "plugins" not in plugins_data:
        plugins_data["plugins"] = []

    # Remove from plugins.json
    original_count = len(plugins_data["plugins"])
    plugins_data["plugins"] = [p for p in plugins_data["plugins"] if p["name"] != args.name]

    if len(plugins_data["plugins"]) == original_count:
        logger.warning(f"Plugin '{args.name}' not found in {PLUGINS_JSON}")
    else:
        save_json_atomic(PLUGINS_JSON, plugins_data)
        logger.info(f"Removed '{args.name}' from {PLUGINS_JSON}")

    # Remove from lock
    lock_data = load_json(PLUGINS_LOCK)
    if "locked" in lock_data:
        lock_data["locked"] = [p for p in lock_data["locked"] if p["name"] != args.name]
        save_json_atomic(PLUGINS_LOCK, lock_data)

    # Delete plugin files
    plugin_path = PLUGINS_DIR / args.name
    if plugin_path.exists():
        # Optionally preserve config.json
        config_backup = None
        if args.keep_config:
            config_path = plugin_path / "config.json"
            if config_path.exists():
                config_backup = config_path.read_text()
                logger.info(f"Preserving config.json for '{args.name}'")

        shutil.rmtree(plugin_path)
        logger.info(f"Deleted plugin directory: {plugin_path}")

        # Restore config if requested
        if config_backup:
            plugin_path.mkdir(parents=True, exist_ok=True)
            (plugin_path / "config.json").write_text(config_backup)
            logger.info(f"Restored config.json to {plugin_path}")
    else:
        logger.warning(f"Plugin directory not found: {plugin_path}")


def cmd_list(args):
    """List all plugins with their status."""
    plugins_data = load_json(PLUGINS_JSON)
    lock_data = load_json(PLUGINS_LOCK)

    plugins = plugins_data.get("plugins", [])
    locked = {p["name"]: p for p in lock_data.get("locked", [])}

    if not plugins:
        print("No plugins configured in plugins.json")
        return

    # Print table header
    print(f"{'NAME':<20} {'STATUS':<12} {'COMMIT':<10}")
    print("-" * 45)

    for plugin in plugins:
        name = plugin["name"]
        plugin_path = PLUGINS_DIR / name
        status = "present" if plugin_path.exists() else "missing"
        commit = locked.get(name, {}).get("commit", "")[:7] if status == "present" else "-"

        print(f"{name:<20} {status:<12} {commit:<10}")


def cmd_sync(args):
    """Sync all plugins from plugins.json."""
    check_git_available()

    plugins_data = load_json(PLUGINS_JSON)
    plugins = plugins_data.get("plugins", [])

    if not plugins:
        logger.warning(f"No plugins configured in {PLUGINS_JSON}")
        return

    logger.info(f"Syncing {len(plugins)} plugin(s)...")

    lock_entries = []
    failed = []

    for plugin in plugins:
        name = plugin["name"]
        url = plugin["url"]
        ref = plugin.get("ref")

        lock_entry = install_plugin(name, url, ref)
        if lock_entry:
            lock_entries.append(lock_entry)
        else:
            failed.append(name)

    # Update lock file with all successful installs
    lock_data = {"locked": lock_entries}
    save_json_atomic(PLUGINS_LOCK, lock_data)

    # Summary
    print()
    logger.info(f"✓ Sync complete: {len(lock_entries)} installed, {len(failed)} failed")
    if failed:
        logger.error(f"Failed plugins: {', '.join(failed)}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Manage board plugins for NHL LED Scoreboard")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Add command
    add_parser = subparsers.add_parser("add", help="Add or update a plugin")
    add_parser.add_argument("name", help="Plugin name (folder name)")
    add_parser.add_argument("url", help="Git repository URL")
    add_parser.add_argument("--ref", help="Git ref (tag, branch, or SHA)")
    add_parser.set_defaults(func=cmd_add)

    # Remove command
    rm_parser = subparsers.add_parser("rm", help="Remove a plugin")
    rm_parser.add_argument("name", help="Plugin name to remove")
    rm_parser.add_argument("--keep-config", action="store_true", help="Preserve config.json when removing")
    rm_parser.set_defaults(func=cmd_rm)

    # List command
    list_parser = subparsers.add_parser("list", help="List all plugins")
    list_parser.set_defaults(func=cmd_list)

    # Sync command
    sync_parser = subparsers.add_parser("sync", help="Install/update all plugins from plugins.json")
    sync_parser.set_defaults(func=cmd_sync)

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")

    # Execute command
    args.func(args)


if __name__ == "__main__":
    main()
