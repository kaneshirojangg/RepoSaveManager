"""Watchdog-backed monitoring for Repo save folder creation and deletion."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from queue import Queue
from threading import Event, Thread
from typing import Any

from src.managers.backup_manager import BackupManager
from src.managers.restore_manager import RestoreManager
from src.managers.save_manager import SaveManager
from src.services.logger_service import get_logger

try:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer
except ImportError:  # pragma: no cover - runtime fallback when watchdog is unavailable
    FileSystemEventHandler = object  # type: ignore[misc,assignment]
    Observer = None  # type: ignore[assignment]


@dataclass(slots=True)
class MonitorEvent:
    event_type: str
    folder_id: str
    path: str
    timestamp: str
    payload: dict[str, Any]


class _RepoSaveWatchHandler(FileSystemEventHandler):
    def __init__(self, manager: "MonitorManager") -> None:
        self.manager = manager

    def on_created(self, event) -> None:  # type: ignore[override]
        if getattr(event, "is_directory", False):
            folder_path = Path(getattr(event, "src_path", ""))
            if folder_path.name:
                self.manager.queue_event("created", folder_path.name, folder_path)

    def on_deleted(self, event) -> None:  # type: ignore[override]
        if getattr(event, "is_directory", False):
            folder_path = Path(getattr(event, "src_path", ""))
            if folder_path.name:
                self.manager.queue_event("deleted", folder_path.name, folder_path)


class MonitorManager:
    def __init__(
        self,
        save_manager: SaveManager,
        backup_manager: BackupManager,
        restore_manager: RestoreManager,
    ) -> None:
        self.save_manager = save_manager
        self.backup_manager = backup_manager
        self.restore_manager = restore_manager
        self.logger = get_logger(self.__class__.__name__)
        self._observer = None
        self._running = False
        self._queue: Queue[MonitorEvent] = Queue()
        self._stop_event = Event()
        self._monitor_thread: Thread | None = None

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def event_queue(self) -> Queue[MonitorEvent]:
        return self._queue

    def start(self, save_root: str | Path) -> bool:
        if Observer is None:
            self.logger.warning("watchdog is not installed; monitoring cannot start.")
            return False

        if self._running:
            return True

        root_path = Path(save_root).expanduser().resolve()
        if not root_path.exists() or not root_path.is_dir():
            raise FileNotFoundError(f"Save root does not exist: {root_path}")

        self._observer = Observer()
        self._observer.schedule(_RepoSaveWatchHandler(self), str(root_path), recursive=False)
        self._observer.start()
        self._stop_event.clear()
        self._running = True
        self.logger.info("Monitoring started for %s", root_path)
        return True

    def stop(self) -> None:
        if self._observer is not None:
            self._observer.stop()
            self._observer.join(timeout=5)
            self._observer = None
        self._running = False
        self._stop_event.set()
        self.logger.info("Monitoring stopped")

    def queue_event(self, event_type: str, folder_id: str, path: Path, **payload: Any) -> None:
        self._queue.put(
            MonitorEvent(
                event_type=event_type,
                folder_id=folder_id,
                path=str(path),
                timestamp=datetime.now().isoformat(timespec="seconds"),
                payload=payload,
            )
        )

    def drain_events(self) -> list[MonitorEvent]:
        events: list[MonitorEvent] = []
        while not self._queue.empty():
            events.append(self._queue.get_nowait())
        return events

    def process_event(self, event: MonitorEvent) -> dict[str, Any]:
        if event.event_type == "created":
            self.logger.info("Save folder created: %s", event.folder_id)
            return {"action": "refresh", "folder_id": event.folder_id}

        if event.event_type == "deleted":
            record = self.backup_manager.get_record(event.folder_id)
            if record is None:
                self.logger.info("Deletion detected without backup record: %s", event.folder_id)
                return {"action": "missing_backup", "folder_id": event.folder_id}
            return {
                "action": "prompt_restore",
                "folder_id": event.folder_id,
                "record": record,
            }

        return {"action": "ignored", "folder_id": event.folder_id}
