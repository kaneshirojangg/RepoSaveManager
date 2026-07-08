"""Filesystem helpers for folder-level save and backup operations."""

from __future__ import annotations

import shutil
from contextlib import suppress
from pathlib import Path
from uuid import uuid4


def ensure_directory(directory_path: Path) -> Path:
    directory_path.mkdir(parents=True, exist_ok=True)
    return directory_path


def folder_exists(folder_path: Path) -> bool:
    return folder_path.exists() and folder_path.is_dir()


def remove_folder(folder_path: Path) -> None:
    if folder_exists(folder_path):
        shutil.rmtree(folder_path)


def copy_folder_atomic(source_path: Path, destination_path: Path) -> Path:
    if not folder_exists(source_path):
        raise FileNotFoundError(f"Source folder does not exist: {source_path}")

    ensure_directory(destination_path.parent)
    temporary_path = destination_path.parent / f".{destination_path.name}.tmp-{uuid4().hex}"

    try:
        shutil.copytree(source_path, temporary_path)
        if folder_exists(destination_path):
            shutil.rmtree(destination_path)
        shutil.move(str(temporary_path), str(destination_path))
        return destination_path
    except Exception:
        with suppress(Exception):
            if temporary_path.exists():
                shutil.rmtree(temporary_path)
        raise


def mirror_folder(source_path: Path, destination_path: Path) -> Path:
    return copy_folder_atomic(source_path, destination_path)


def folders_have_same_file_names(source_path: Path, destination_path: Path) -> bool:
    if not folder_exists(source_path) or not folder_exists(destination_path):
        return False

    source_entries = sorted(path.name for path in source_path.iterdir())
    destination_entries = sorted(path.name for path in destination_path.iterdir())
    return source_entries == destination_entries
