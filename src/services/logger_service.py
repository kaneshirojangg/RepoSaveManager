"""Logging configuration for the application."""

from __future__ import annotations

import logging
from logging import Logger
from pathlib import Path

from src.utils.constants import APP_NAME, DEFAULT_LOG_FILE_PATH, LOGS_DIR


def configure_logger(log_file_path: Path = DEFAULT_LOG_FILE_PATH) -> Logger:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(APP_NAME)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False
    return logger


def get_logger(name: str = APP_NAME) -> Logger:
    parent_logger = configure_logger()
    return parent_logger.getChild(name) if name != APP_NAME else parent_logger
