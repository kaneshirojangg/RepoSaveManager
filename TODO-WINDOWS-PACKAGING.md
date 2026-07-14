# Windows Packaging (PyInstaller) - Checklist

- [ ] Ensure build produces `dist_windows/dist/<dist-folder>/Repo Save Manager.exe`.
- [ ] Ensure `RepoSaveManager-Windows.zip` is created and contains that `.exe` at the zip root when extracted.
- [ ] Add build-time validation: locate exe, fail if not found.
- [ ] Add packaging-time validation: verify zip contains `Repo Save Manager.exe`.
- [ ] (Optional) Update README so GitHub “Download zip” users know which artifact to download (release asset vs repo zip).

