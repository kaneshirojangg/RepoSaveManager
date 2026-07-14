#!/usr/bin/env bash
set -euo pipefail

# Windows build helper (run under WSL or Linux machine that has Wine/Windows tooling).
# It generates PyInstaller dist/ output, then zips it for easy download.
#
# If you are building for Windows from Linux, you MUST have a cross-compilation / Windows
# toolchain available (or do the build directly on Windows). This script assumes you
# can run PyInstaller to produce a Windows exe.

APP_NAME="Repo Save Manager"
SPEC_PATH="./RepoSaveManager.spec"
OUT_DIR="./dist_windows"

rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR"

echo "[build] Cleaning old dist/ & build/ ..."
rm -rf dist build

echo "[build] Running PyInstaller ..."
python3 -m pip install -r requirements.txt
python3 -m pip install pyinstaller

# Folder dist output (more reliable than --onefile for packaging assets)
pyinstaller "$SPEC_PATH" --distpath "$OUT_DIR/dist" --workpath "$OUT_DIR/build" -y

EXE_PATH="$OUT_DIR/dist/Repo Save Manager.exe"
if [ ! -f "$EXE_PATH" ]; then
  # PyInstaller sometimes replaces spaces with underscores or uses the name differently.
  # Print directory listing for debugging.
  echo "[build] ERROR: expected exe not found at: $EXE_PATH"
  echo "[build] dist output:" 
  ls -la "$OUT_DIR/dist" || true
  exit 1
fi

echo "[package] Creating zip for download ..."
ZIP_PATH="./RepoSaveManager-Windows.zip"
rm -f "$ZIP_PATH"

# Zip the folder contents to avoid breaking relative paths inside the bundled app.
# The exe will be inside the zip root.
( cd "$OUT_DIR/dist" && zip -r "$(realpath --relative-to="$(pwd)" "$ZIP_PATH")" . )

echo "[done] Created: $ZIP_PATH"

