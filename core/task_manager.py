from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from apscheduler.schedulers.background import BackgroundScheduler

from config import settings
from utils.helpers import load_json, save_json
from utils.logger import get_logger


logger = get_logger(__name__)


@dataclass
class Task:
    id: str
    title: str
    command: str
    created_at: str
    due_at: str | None = None
    recurring: str | None = None
    completed: bool = False
    completed_at: str | None = None


class TaskManager:
    def __init__(self) -> None:
        self.scheduler = BackgroundScheduler(daemon=True)
        self.scheduler.start()
        self._tasks: list[Task] = [Task(**t) for t in load_json(settings.tasks_file, [])]

    def _persist(self) -> None:
        save_json(settings.tasks_file, [asdict(t) for t in self._tasks])

    def create(self, title: str, command: str = "", due_at: str | None = None, recurring: str | None = None) -> Task:
        task = Task(
            id=str(uuid4()),
            title=title,
            command=command,
            created_at=datetime.now(UTC).isoformat(),
            due_at=due_at,
            recurring=recurring,
        )
        self._tasks.append(task)
        self._persist()
        logger.info("Created task id=%s title=%s", task.id, title)
        return task

    def list(self, show_completed: bool = True) -> list[Task]:
        if show_completed:
            return list(self._tasks)
        return [t for t in self._tasks if not t.completed]

    def complete(self, task_id: str) -> Task:
        task = self._find(task_id)
        task.completed = True
        task.completed_at = datetime.now(UTC).isoformat()
        self._persist()
        logger.info("Completed task id=%s", task.id)
        return task

    def delete(self, task_id: str) -> None:
        task = self._find(task_id)
        self._tasks.remove(task)
        self._persist()
        logger.info("Deleted task id=%s", task.id)

    def history(self) -> list[dict[str, Any]]:
        return [asdict(t) for t in self._tasks if t.completed]

    def _find(self, task_id: str) -> Task:
        for task in self._tasks:
            if task.id == task_id:
                return task
        raise KeyError(f"Task not found: {task_id}")
