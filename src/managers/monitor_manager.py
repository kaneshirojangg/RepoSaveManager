"""Watchdog-backed monitoring for Repo save folder creation, deletion, and
in-place progress changes (auto-backup)."""

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


def _resolved(path: Path) -> Path:
    """Resolve a path defensively.

    Path.resolve() can raise on some platforms/edge cases (e.g. a path that
    disappears mid-resolve). Falls back to the original path rather than
    blowing up an event-handling callback.
    """
    try:
        return path.resolve()
    except OSError:
        return path


class _RepoSaveWatchHandler(FileSystemEventHandler):
    def __init__(self, manager: "MonitorManager", watch_root: Path) -> None:
        self.manager = manager
        # Pre-resolve once up front so every comparison below is cheap.
        self.watch_root = _resolved(watch_root)

    def _is_direct_child_of_watch_root(self, candidate_parent: Path) -> bool:
        # NOTE: this used to compare `candidate_parent == self.watch_root`
        # directly. watchdog hands back whatever raw src_path the OS gives
        # it, which is not guaranteed to be resolved/normalized the same
        # way self.watch_root was (case differences, short-path forms,
        # trailing separators, symlinked AppData redirects on Windows,
        # etc.). A single mismatch there meant this comparison silently
        # failed for *every* event, so queue_event() was never called and
        # auto-backup never had a chance to run. Resolving both sides
        # before comparing fixes that.
        return _resolved(candidate_parent) == self.watch_root

    def on_created(self, event) -> None:  # type: ignore[override]
        # Only a brand-new top-level REPO_SAVE_xxx folder counts as "created" —
        # not files appearing inside an existing save folder.
        if not getattr(event, "is_directory", False):
            return
        folder_path = Path(getattr(event, "src_path", ""))
        if folder_path.name and self._is_direct_child_of_watch_root(folder_path.parent):
            self.manager.queue_event("created", folder_path.name, folder_path)

    def on_deleted(self, event) -> None:  # type: ignore[override]
        # Only the whole save folder being removed counts as a deletion —
        # not an individual file being removed from inside it.
        if not getattr(event, "is_directory", False):
            return
        folder_path = Path(getattr(event, "src_path", ""))
        if folder_path.name and self._is_direct_child_of_watch_root(folder_path.parent):
            self.manager.queue_event("deleted", folder_path.name, folder_path)

    def on_modified(self, event) -> None:  # type: ignore[override]
        # We care about the save *file* changing (new progress written),
        # not the folder's own modification timestamp ticking.
        if getattr(event, "is_directory", False):
            return
        src_path = Path(getattr(event, "src_path", ""))
        folder_path = src_path.parent
        # Only react to files that live directly inside one of the
        # top-level REPO_SAVE_xxx folders being watched.
        if folder_path.name and self._is_direct_child_of_watch_root(folder_path.parent):
            self.manager.queue_event("modified", folder_path.name, folder_path)


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
        self._watch_root: Path | None = None

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

        self._watch_root = root_path
        self._observer = Observer()
        # recursive=True so we also see modifications to the save files that
        # live *inside* each REPO_SAVE_xxx folder, not just top-level folder
        # creation/deletion. The handler itself filters events back down to
        # only what's relevant (see _RepoSaveWatchHandler above).
        self._observer.schedule(_RepoSaveWatchHandler(self, root_path), str(root_path), recursive=True)
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
        self._watch_root = None
        self._stop_event.set()
        self.logger.info("Monitoring stopped")

    def queue_event(self, event_type: str, folder_id: str, path: Path, **payload: Any) -> None:
        self.logger.debug("Queuing monitor event: %s for %s (%s)", event_type, folder_id, path)
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
        raw_events: list[MonitorEvent] = []
        while not self._queue.empty():
            raw_events.append(self._queue.get_nowait())
        return self._collapse_modified_events(raw_events)

    @staticmethod
    def _collapse_modified_events(events: list[MonitorEvent]) -> list[MonitorEvent]:
        """Collapse a burst of "modified" events for the same folder down to
        just the most recent one.

        Auto-backup creation has been removed; monitoring no longer performs
        any work for "modified" events. This method remains defensive to keep
        the event queue small if monitoring is still active.
        """
        seen_modified_ids: set[str] = set()
        collapsed: list[MonitorEvent] = []
        for evt in reversed(events):
            if evt.event_type == "modified":
                if evt.folder_id in seen_modified_ids:
                    continue
                seen_modified_ids.add(evt.folder_id)
            collapsed.append(evt)
        collapsed.reverse()
        return collapsed


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

        # Auto-backups on file modifications were removed.
        if event.event_type == "modified":
            return {"action": "ignored", "folder_id": event.folder_id}

        return {"action": "ignored", "folder_id": event.folder_id}

