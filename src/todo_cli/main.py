# agent-notes: { ctx: "cli entrypoint and commands", deps: ["argparse", "src/todo_cli/service.py"], state: active, last: "sato@2026-04-07" }
from __future__ import annotations

import argparse
import sys

from todo_cli.models import due_at_for_display
from todo_cli.service import TaskService
from todo_cli.storage import TaskStorage


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="todo-cli")
    parser.add_argument("--data-file", default=".todo-cli/tasks.json", help="Path to local task file")

    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="Add a task")
    add.add_argument("--title", required=True)
    add.add_argument("--due-at", required=True)
    add.add_argument("--estimate-minutes", required=True, type=int)
    add.add_argument("--description", default="")

    sub.add_parser("list", help="List tasks")

    show = sub.add_parser("show", help="Show a task")
    show.add_argument("--id", required=True, type=int)

    update = sub.add_parser("update", help="Update fields of a task")
    update.add_argument("--id", required=True, type=int)
    update.add_argument("--title")
    update.add_argument("--due-at")
    update.add_argument("--estimate-minutes", type=int)
    update.add_argument("--description")

    delete = sub.add_parser("delete", help="Delete a task")
    delete.add_argument("--id", required=True, type=int)

    status = sub.add_parser("status", help="Update task status")
    status.add_argument("--id", required=True, type=int)
    status.add_argument("--status", required=True)

    return parser


def render_task_line(task) -> str:
    return (
        f"[{task.id}] {task.title} | {task.status} | "
        f"due: {due_at_for_display(task.due_at)} | "
        f"estimate: {task.estimate_minutes}m"
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    service = TaskService(TaskStorage(args.data_file))

    try:
        if args.command == "add":
            task = service.add_task(args.title, args.due_at, args.estimate_minutes, args.description)
            print(f"Created task #{task.id}")
            return 0

        if args.command == "list":
            tasks = service.list_tasks()
            if not tasks:
                print("No tasks found")
                return 0
            for task in tasks:
                print(render_task_line(task))
            return 0

        if args.command == "show":
            task = service.get_task(args.id)
            print(f"id: {task.id}")
            print(f"title: {task.title}")
            print(f"description: {task.description}")
            print(f"status: {task.status}")
            print(f"due_at: {due_at_for_display(task.due_at)}")
            print(f"estimate_minutes: {task.estimate_minutes}")
            return 0

        if args.command == "update":
            task = service.update_task(
                args.id,
                title=args.title,
                due_at=args.due_at,
                estimate_minutes=args.estimate_minutes,
                description=args.description,
            )
            print(f"Updated task #{task.id}")
            return 0

        if args.command == "delete":
            service.delete_task(args.id)
            print(f"Deleted task #{args.id}")
            return 0

        if args.command == "status":
            task = service.set_status(args.id, args.status)
            print(f"Updated task #{task.id} status to {task.status}")
            return 0

        parser.print_help()
        return 1
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
