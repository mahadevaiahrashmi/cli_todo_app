# agent-notes: { ctx: "json storage repository", deps: ["json", "pathlib", "tempfile"], state: active, last: "sato@2026-04-07" }
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from todo_cli.models import Task

SCHEMA_VERSION = 1


class TaskStorage:
    def __init__(self, data_file: str) -> None:
        self.data_path = Path(data_file)

    def load_tasks(self) -> list[Task]:
        payload = self._read_payload()
        return [Task.from_dict(item) for item in payload["tasks"]]

    def save_tasks(self, tasks: list[Task]) -> None:
        payload = {
            "schema_version": SCHEMA_VERSION,
            "tasks": [task.to_dict() for task in tasks],
        }
        self._atomic_write(payload)

    def _read_payload(self) -> dict:
        if not self.data_path.exists():
            return {"schema_version": SCHEMA_VERSION, "tasks": []}

        content = self.data_path.read_text(encoding="utf-8")
        payload = json.loads(content)

        if payload.get("schema_version") != SCHEMA_VERSION:
            raise ValueError("Unsupported schema version in data file")

        tasks = payload.get("tasks")
        if not isinstance(tasks, list):
            raise ValueError("Invalid tasks payload")

        return payload

    def _atomic_write(self, payload: dict) -> None:
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(prefix="todo-cli-", suffix=".tmp", dir=str(self.data_path.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, indent=2)
                handle.write("\n")
            os.replace(tmp_path, self.data_path)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
