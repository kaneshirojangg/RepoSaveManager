# Build & download Windows `.exe` (PyInstaller)

This repo already contains `RepoSaveManager.spec`.

## Prerequisites
- Python 3.10+ on the machine where you run the build
- `pip`

## Build
Run this from the repository root:

```bash
chmod +x ./build-windows-exe.sh
./build-windows-exe.sh
```

It will create:
- `./dist_windows/dist/Repo Save Manager.exe` (folder-style dist)
- `./RepoSaveManager-Windows.zip` (downloadable zip containing the built app)

## Distribute to Windows users
1. Download `RepoSaveManager-Windows.zip`
2. Extract it on the user’s PC
3. Double-click `Repo Save Manager.exe`

## Notes
- The build uses folder-style `dist` output (not `--onefile`) because it’s typically more reliable for GUI apps that bundle assets.

