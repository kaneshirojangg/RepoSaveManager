#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/RepoSaveManager"
BIN_FILE="${XDG_BIN_HOME:-$HOME/.local/bin}/repo-save-manager"
DESKTOP_FILE="${XDG_DATA_HOME:-$HOME/.local/share}/applications/RepoSaveManager.desktop"
ICON_FILE="${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor/256x256/apps/reposavemanager.png"

rm -f "$BIN_FILE" "$DESKTOP_FILE" "$ICON_FILE"
rm -rf "$INSTALL_DIR"

if [ -f "$HOME/Desktop/RepoSaveManager.desktop" ]; then
  rm -f "$HOME/Desktop/RepoSaveManager.desktop"
fi

echo "Repo Save Manager removed."
