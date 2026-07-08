#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$SCRIPT_DIR"
INSTALL_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/RepoSaveManager"
BIN_DIR="${XDG_BIN_HOME:-$HOME/.local/bin}"
DESKTOP_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
ICON_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor/256x256/apps"

mkdir -p "$INSTALL_DIR" "$BIN_DIR" "$DESKTOP_DIR" "$ICON_DIR"

cp -a "$SOURCE_DIR"/. "$INSTALL_DIR"/

rm -rf \
  "$INSTALL_DIR/.git" \
  "$INSTALL_DIR/__pycache__" \
  "$INSTALL_DIR/src/__pycache__" \
  "$INSTALL_DIR/src/ui/__pycache__" \
  "$INSTALL_DIR/src/managers/__pycache__" \
  "$INSTALL_DIR/src/models/__pycache__" \
  "$INSTALL_DIR/src/services/__pycache__" \
  "$INSTALL_DIR/src/utils/__pycache__"

python3 -m venv "$INSTALL_DIR/.venv"
"$INSTALL_DIR/.venv/bin/python" -m pip install --upgrade pip >/dev/null
"$INSTALL_DIR/.venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt"

cat > "$BIN_DIR/repo-save-manager" <<EOF
#!/usr/bin/env bash
exec "$INSTALL_DIR/.venv/bin/python" -m src "\$@"
EOF
chmod +x "$BIN_DIR/repo-save-manager"

cp "$INSTALL_DIR/assets/images/reposavemanager.png" "$ICON_DIR/reposavemanager.png"

cat > "$DESKTOP_DIR/RepoSaveManager.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Repo Save Manager
Comment=Manage R.E.P.O. save folder backups and restores
Exec=$BIN_DIR/repo-save-manager
Path=$INSTALL_DIR
Terminal=false
StartupNotify=true
Categories=Utility;
Icon=$ICON_DIR/reposavemanager.png
EOF
chmod +x "$DESKTOP_DIR/RepoSaveManager.desktop"

if [ -d "$HOME/Desktop" ]; then
  cp "$DESKTOP_DIR/RepoSaveManager.desktop" "$HOME/Desktop/RepoSaveManager.desktop"
  chmod +x "$HOME/Desktop/RepoSaveManager.desktop"
fi

echo "Repo Save Manager installed to $INSTALL_DIR"
echo "Desktop launcher created at $DESKTOP_DIR/RepoSaveManager.desktop"
