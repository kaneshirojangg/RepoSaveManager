# TODO

- [ ] Update Windows packaging so the extracted zip shows `Repo Save Manager.exe` in the top-level extracted folder.
  - [ ] Inspect current `build-windows-exe.sh` packaging layout.
  - [ ] Modify zip step to re-root the dist folder so exe lands at extraction root.
  - [ ] (Optional) Add a post-build verification that the zip contains the expected exe at the correct path.
- [ ] Re-run `./build-windows-exe.sh` and verify resulting zip contents/extracted layout.

