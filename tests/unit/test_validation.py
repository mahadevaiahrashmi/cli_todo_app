# agent-notes: { ctx: "unit validation tests", deps: ["src/todo_cli/models.py"], state: active, last: "tara@2026-04-07" }
import unittest

from todo_cli.models import normalize_due_at, normalize_status


class ValidationTests(unittest.TestCase):
    def test_normalize_status_accepts_known_values(self) -> None:
        self.assertEqual(normalize_status("todo"), "todo")
        self.assertEqual(normalize_status("In-Progress"), "in-progress")

    def test_normalize_status_rejects_unknown_value(self) -> None:
        with self.assertRaises(ValueError):
            normalize_status("blocked")

    def test_normalize_due_at_outputs_utc(self) -> None:
        out = normalize_due_at("2026-04-20T10:00:00+02:00")
        self.assertTrue(out.endswith("Z"))
        self.assertEqual(out, "2026-04-20T08:00:00Z")

    def test_normalize_due_at_matrix(self) -> None:
        cases = [
            ("2026-04-20T08:00:00Z", "2026-04-20T08:00:00Z"),
            ("2026-04-20T10:00:00+02:00", "2026-04-20T08:00:00Z"),
            ("2026-04-20T03:00:00-05:00", "2026-04-20T08:00:00Z"),
            ("2026-04-20T08:00:00", "2026-04-20T08:00:00Z"),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                self.assertEqual(normalize_due_at(raw), expected)

    def test_normalize_due_at_rejects_invalid_value(self) -> None:
        with self.assertRaises(ValueError):
            normalize_due_at("not-a-date")


if __name__ == "__main__":
    unittest.main()
