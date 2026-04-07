# agent-notes: { ctx: "integration CLI workflow tests", deps: ["src/todo_cli/main.py"], state: active, last: "tara@2026-04-07" }
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


class TodoCliFlowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.data_file = Path(self.tmpdir.name) / "tasks.json"
        self.env = os.environ.copy()
        self.env["PYTHONPATH"] = str(Path.cwd() / "src")

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "python3",
                "-m",
                "todo_cli.main",
                "--data-file",
                str(self.data_file),
                *args,
            ],
            check=False,
            capture_output=True,
            text=True,
            env=self.env,
        )

    def test_crud_and_status_workflow(self) -> None:
        add = self.run_cli(
            "add",
            "--title",
            "Pay rent",
            "--due-at",
            "2026-04-20T09:00:00+00:00",
            "--estimate-minutes",
            "30",
            "--description",
            "April payment",
        )
        self.assertEqual(add.returncode, 0, add.stderr)
        self.assertIn("Created task #1", add.stdout)

        list_out = self.run_cli("list")
        self.assertEqual(list_out.returncode, 0, list_out.stderr)
        self.assertIn("Pay rent", list_out.stdout)
        self.assertIn("todo", list_out.stdout)

        status = self.run_cli("status", "--id", "1", "--status", "in-progress")
        self.assertEqual(status.returncode, 0, status.stderr)

        show = self.run_cli("show", "--id", "1")
        self.assertEqual(show.returncode, 0, show.stderr)
        self.assertIn("in-progress", show.stdout)
        self.assertIn("estimate_minutes: 30", show.stdout)

        update = self.run_cli(
            "update",
            "--id",
            "1",
            "--title",
            "Pay rent and utilities",
            "--estimate-minutes",
            "45",
        )
        self.assertEqual(update.returncode, 0, update.stderr)

        show2 = self.run_cli("show", "--id", "1")
        self.assertEqual(show2.returncode, 0, show2.stderr)
        self.assertIn("Pay rent and utilities", show2.stdout)
        self.assertIn("estimate_minutes: 45", show2.stdout)

        delete = self.run_cli("delete", "--id", "1")
        self.assertEqual(delete.returncode, 0, delete.stderr)

        empty = self.run_cli("list")
        self.assertEqual(empty.returncode, 0, empty.stderr)
        self.assertIn("No tasks found", empty.stdout)

    def test_invalid_status_returns_nonzero(self) -> None:
        add = self.run_cli(
            "add",
            "--title",
            "Bad status test",
            "--due-at",
            "2026-04-20T09:00:00+00:00",
            "--estimate-minutes",
            "20",
        )
        self.assertEqual(add.returncode, 0, add.stderr)

        bad = self.run_cli("status", "--id", "1", "--status", "blocked")
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("Invalid status", bad.stderr)

    def test_persistence_file_has_schema(self) -> None:
        add = self.run_cli(
            "add",
            "--title",
            "Persist me",
            "--due-at",
            "2026-04-20T09:00:00+00:00",
            "--estimate-minutes",
            "10",
        )
        self.assertEqual(add.returncode, 0, add.stderr)

        data = json.loads(self.data_file.read_text(encoding="utf-8"))
        self.assertEqual(data["schema_version"], 1)
        self.assertEqual(len(data["tasks"]), 1)

    def test_due_at_matrix_persists_as_utc(self) -> None:
        cases = [
            ("2026-04-20T08:00:00Z", "2026-04-20T08:00:00Z"),
            ("2026-04-20T10:00:00+02:00", "2026-04-20T08:00:00Z"),
            ("2026-04-20T03:00:00-05:00", "2026-04-20T08:00:00Z"),
            ("2026-04-20T08:00:00", "2026-04-20T08:00:00Z"),
        ]

        for raw_due, expected_due in cases:
            with self.subTest(raw_due=raw_due):
                add = self.run_cli(
                    "add",
                    "--title",
                    f"Case {raw_due}",
                    "--due-at",
                    raw_due,
                    "--estimate-minutes",
                    "15",
                )
                self.assertEqual(add.returncode, 0, add.stderr)

        data = json.loads(self.data_file.read_text(encoding="utf-8"))
        persisted_dues = [task["due_at"] for task in data["tasks"]]
        self.assertEqual(persisted_dues, [case[1] for case in cases])

    def test_invalid_due_at_returns_nonzero(self) -> None:
        bad = self.run_cli(
            "add",
            "--title",
            "Bad due date",
            "--due-at",
            "definitely-not-iso",
            "--estimate-minutes",
            "20",
        )
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("Invalid isoformat string", bad.stderr)

    def test_non_positive_estimate_returns_nonzero(self) -> None:
        zero = self.run_cli(
            "add",
            "--title",
            "Zero estimate",
            "--due-at",
            "2026-04-20T09:00:00+00:00",
            "--estimate-minutes",
            "0",
        )
        self.assertNotEqual(zero.returncode, 0)
        self.assertIn("estimate_minutes must be > 0", zero.stderr)

    def test_missing_task_id_returns_nonzero(self) -> None:
        miss_show = self.run_cli("show", "--id", "999")
        self.assertNotEqual(miss_show.returncode, 0)
        self.assertIn("Task not found", miss_show.stderr)

        miss_update = self.run_cli("update", "--id", "999", "--title", "Nope")
        self.assertNotEqual(miss_update.returncode, 0)
        self.assertIn("Task not found", miss_update.stderr)


if __name__ == "__main__":
    unittest.main()
