# agent-notes: { ctx: "task service operations", deps: ["src/todo_cli/models.py", "src/todo_cli/storage.py"], state: active, last: "sato@2026-04-07" }
from __future__ import annotations

from todo_cli.models import Task, normalize_due_at, normalize_status, utc_now_iso
from todo_cli.storage import TaskStorage


class TaskService:
    def __init__(self, storage: TaskStorage) -> None:
        self.storage = storage

    def add_task(self, title: str, due_at: str, estimate_minutes: int, description: str = "") -> Task:
        if estimate_minutes <= 0:
            raise ValueError("estimate_minutes must be > 0")

        tasks = self.storage.load_tasks()
        new_id = max((task.id for task in tasks), default=0) + 1
        now = utc_now_iso()

        task = Task(
            id=new_id,
            title=title.strip(),
            description=description.strip(),
            status="todo",
            due_at=normalize_due_at(due_at),
            estimate_minutes=int(estimate_minutes),
            created_at=now,
            updated_at=now,
        )
        tasks.append(task)
        self.storage.save_tasks(tasks)
        return task

    def list_tasks(self) -> list[Task]:
        tasks = self.storage.load_tasks()
        return sorted(tasks, key=lambda task: (task.due_at, task.id))

    def get_task(self, task_id: int) -> Task:
        for task in self.storage.load_tasks():
            if task.id == task_id:
                return task
        raise ValueError(f"Task not found: {task_id}")

    def update_task(
        self,
        task_id: int,
        title: str | None = None,
        due_at: str | None = None,
        estimate_minutes: int | None = None,
        description: str | None = None,
    ) -> Task:
        tasks = self.storage.load_tasks()
        updated = None

        for index, task in enumerate(tasks):
            if task.id != task_id:
                continue

            if title is not None:
                task.title = title.strip()
            if due_at is not None:
                task.due_at = normalize_due_at(due_at)
            if estimate_minutes is not None:
                if estimate_minutes <= 0:
                    raise ValueError("estimate_minutes must be > 0")
                task.estimate_minutes = int(estimate_minutes)
            if description is not None:
                task.description = description.strip()

            task.updated_at = utc_now_iso()
            tasks[index] = task
            updated = task
            break

        if updated is None:
            raise ValueError(f"Task not found: {task_id}")

        self.storage.save_tasks(tasks)
        return updated

    def delete_task(self, task_id: int) -> None:
        tasks = self.storage.load_tasks()
        kept = [task for task in tasks if task.id != task_id]
        if len(kept) == len(tasks):
            raise ValueError(f"Task not found: {task_id}")
        self.storage.save_tasks(kept)

    def set_status(self, task_id: int, status: str) -> Task:
        normalized = normalize_status(status)
        tasks = self.storage.load_tasks()
        updated = None

        for index, task in enumerate(tasks):
            if task.id != task_id:
                continue
            task.status = normalized
            task.updated_at = utc_now_iso()
            tasks[index] = task
            updated = task
            break

        if updated is None:
            raise ValueError(f"Task not found: {task_id}")

        self.storage.save_tasks(tasks)
        return updated
