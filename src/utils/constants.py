"""Core application constants and filesystem paths."""

from __future__ import annotations

import os
from pathlib import Path


APP_NAME = "Repo Save Manager"
APP_SLUG = "RepoSaveManager"
APP_VERSION = "0.1.0"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
ASSETS_DIR = PROJECT_ROOT / "assets"
BACKUPS_DIR = PROJECT_ROOT / "backups"
LOGS_DIR = PROJECT_ROOT / "logs"
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"

_USERPROFILE = os.environ.get("USERPROFILE") or str(Path.home())

DEFAULT_SAVE_FOLDER = Path(
    os.path.join(
        _USERPROFILE,
        "AppData",
        "LocalLow",
        "semiwork",
        "Repo",
        "saves",
    )
)

DEFAULT_SETTINGS_PATH = CONFIG_DIR / "settings.json"
DEFAULT_BACKUP_DATABASE_PATH = DATA_DIR / "backup_database.json"
DEFAULT_LOG_FILE_PATH = LOGS_DIR / "application.log"
