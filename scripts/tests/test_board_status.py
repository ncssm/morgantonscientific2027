"""Tests for how scripts/board_status.py reads an issue's Stages checklist.

    python -m unittest discover scripts/tests
"""

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("board_status", ROOT / "scripts" / "board_status.py")
board_status = importlib.util.module_from_spec(spec)
sys.modules["board_status"] = board_status
spec.loader.exec_module(board_status)

STAGES = [
    "Handed off: layout editor assigned",
    "Conversion: PR opened with the draft label",
    "Checks: all checks green on the PR",
    "Author proof: the author has approved the Curvenote preview",
    "Copy edit: read-through done and the PR approved by the copy editor",
    "Merged: submitted to Curvenote",
]


def body(checked, received_all=True):
    """An issue description shaped like the New article form's output."""
    mark = "X" if received_all else " "
    lines = ["### Article title", "", "Caffeine and climbing", "", "### Received", "",
             f"- [{mark}] Intake form completed by the corresponding author",
             f"- [{mark}] ORCID for every author", "", "### Stages", ""]
    # GitHub writes [X] for boxes checked in the form and [x] for boxes clicked later.
    lines += [f"- [{'x' if i in checked else ' '}] {s}" for i, s in enumerate(STAGES)]
    return "\n".join(lines)


class ColumnTest(unittest.TestCase):
    def test_each_stage(self):
        expected = ["Conversion", "Conversion", "Author proof", "Copy edit", "Copy edit", "Submitted"]
        for i, column in enumerate(expected):
            with self.subTest(stage=STAGES[i]):
                self.assertEqual(board_status.column_for(body(set(range(i + 1)))), column)

    def test_nothing_checked_is_intake(self):
        self.assertEqual(board_status.column_for(body(set())), "Intake")

    def test_received_boxes_dont_count(self):
        self.assertEqual(board_status.column_for(body(set(), received_all=True)), "Intake")

    def test_unchecking_moves_back(self):
        # Checks was unchecked again after a failing push: back to Conversion.
        self.assertEqual(board_status.column_for(body({0, 1})), "Conversion")

    def test_furthest_stage_wins_even_with_gaps(self):
        self.assertEqual(board_status.column_for(body({0, 3})), "Copy edit")

    def test_no_checklist(self):
        self.assertEqual(board_status.column_for("An issue written by hand."), "Intake")
        self.assertEqual(board_status.column_for(None), "Intake")

    def test_capital_x(self):
        text = body(set()).replace("- [ ] Checks:", "- [X] Checks:")
        self.assertEqual(board_status.column_for(text), "Author proof")


if __name__ == "__main__":
    unittest.main()
