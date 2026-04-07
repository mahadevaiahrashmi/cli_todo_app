<!-- agent-notes: { ctx: "todo cli usage guide", deps: ["src/todo_cli/main.py", "tests/"], state: active, last: "diego@2026-04-07" } -->
# Todo CLI

Single-user Python command-line todo application.

Built with Codex GPT-5.3.

## Features

- Create, read, update, and delete tasks
- Track status: `todo`, `in-progress`, `done`
- Store both `due date/time` and `estimated duration`
- Local JSON persistence with atomic writes

## Quick Start

Run commands directly from source:

```bash
PYTHONPATH=src python3 -m todo_cli.main --help
```

Use a local data file path:

```bash
PYTHONPATH=src python3 -m todo_cli.main --data-file .todo-cli/tasks.json list
```

## Command Examples

Add a task:

```bash
PYTHONPATH=src python3 -m todo_cli.main --data-file .todo-cli/tasks.json add \
  --title "Pay rent" \
  --due-at "2026-04-20T09:00:00+00:00" \
  --estimate-minutes 30 \
  --description "April payment"
```

List tasks:

```bash
PYTHONPATH=src python3 -m todo_cli.main --data-file .todo-cli/tasks.json list
```

Show one task:

```bash
PYTHONPATH=src python3 -m todo_cli.main --data-file .todo-cli/tasks.json show --id 1
```

Update fields:

```bash
PYTHONPATH=src python3 -m todo_cli.main --data-file .todo-cli/tasks.json update \
  --id 1 \
  --title "Pay rent and utilities" \
  --estimate-minutes 45
```

Change status:

```bash
PYTHONPATH=src python3 -m todo_cli.main --data-file .todo-cli/tasks.json status --id 1 --status in-progress
```

Delete:

```bash
PYTHONPATH=src python3 -m todo_cli.main --data-file .todo-cli/tasks.json delete --id 1
```

## Tests

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py' -v
```
