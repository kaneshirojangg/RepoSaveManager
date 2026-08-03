# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None


def _existing_datas(entries: list[tuple[str, str]]) -> list[tuple[str, str]]:
    collected: list[tuple[str, str]] = []
    for source, target in entries:
        if os.path.exists(source):
            collected.append((source, target))
    return collected

a = Analysis(
    ['launch.py'],
    pathex=[],
    binaries=[],
    datas=_existing_datas([
        ('assets', 'assets'),
        ('config', 'config'),
        ('data', 'data'),
        ('logs', 'logs'),
        ('backups', 'backups'),
    ]),
    hiddenimports=['customtkinter', 'watchdog'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Repo Save Manager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/images/reposavemanager.png',
)
