# agent-notes: { ctx: "task model and validators", deps: ["datetime", "dataclasses"], state: active, last: "sato@2026-04-07" }
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

VALID_STATUSES = {"todo", "in-progress", "done"}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_status(raw_status: str) -> str:
    status = raw_status.strip().lower()
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {raw_status}. Allowed: todo, in-progress, done")
    return status


def normalize_due_at(raw_due_at: str) -> str:
    value = raw_due_at.strip()
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"

    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    utc_value = parsed.astimezone(timezone.utc).replace(microsecond=0)
    return utc_value.isoformat().replace("+00:00", "Z")


def due_at_for_display(utc_due_at: str) -> str:
    value = utc_due_at
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"

    parsed = datetime.fromisoformat(value)
    local_dt = parsed.astimezone()
    return local_dt.replace(microsecond=0).isoformat()


@dataclass
class Task:
    id: int
    title: str
    description: str
    status: str
    due_at: str
    estimate_minutes: int
    created_at: str
    updated_at: str

    @classmethod
    def from_dict(cls, payload: dict) -> "Task":
        return cls(
            id=int(payload["id"]),
            title=str(payload["title"]),
            description=str(payload.get("description", "")),
            status=normalize_status(str(payload["status"])),
            due_at=normalize_due_at(str(payload["due_at"])),
            estimate_minutes=int(payload["estimate_minutes"]),
            created_at=str(payload["created_at"]),
            updated_at=str(payload["updated_at"]),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "due_at": self.due_at,
            "estimate_minutes": self.estimate_minutes,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
