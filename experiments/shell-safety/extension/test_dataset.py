"""Integrity tests: frozen fixtures and label-free adapter inputs, no inference."""
import hashlib
import json
import unittest
from collections import Counter, defaultdict
from pathlib import Path
import build_synthetic
import run_local

HERE = Path(__file__).resolve().parent


class DatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (HERE / "data/synthetic.jsonl").read_bytes()
        cls.rows = [json.loads(line) for line in cls.raw.splitlines()]
        cls.freeze = json.loads((HERE / "data/synthetic-freeze.json").read_text())

    def test_freeze_and_reproduction(self):
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(), self.freeze["sha256"])
        self.assertEqual(self.rows, build_synthetic.build())
        for filename, key in [("data/contexts.json", "contexts_sha256"), ("build_synthetic.py", "generator_sha256")]:
            self.assertEqual(hashlib.sha256((HERE / filename).read_bytes()).hexdigest(), self.freeze[key])

    def test_counts_and_unique_ids(self):
        self.assertEqual(len(self.rows), 128)
        self.assertEqual(len({r["id"] for r in self.rows}), 128)
        self.assertEqual(dict(Counter(r["expected"] for r in self.rows)), {"allow": 44, "deny": 44, "ask": 40})
        self.assertEqual(len({r["category"] for r in self.rows}), 18)
        self.assertEqual(len({r["contextProfile"] for r in self.rows}), 6)

    def test_contrast_groups(self):
        groups = defaultdict(list)
        for row in self.rows:
            if row["contrastGroup"]:
                groups[row["contrastGroup"]].append(row)
        self.assertEqual(len(groups), 40)
        for group, members in groups.items():
            self.assertEqual({r["variant"] for r in members}, {"a", "b", "c"})
            self.assertEqual(len({r["command"] for r in members}), 1)
            self.assertEqual(len({r["context"]["userRequest"] for r in members}), 1)
            self.assertEqual({r["expected"] for r in members}, {"allow", "deny", "ask"})
            self.assertEqual([r["pair"] for r in members if r["variant"] == "c"], [None])
            self.assertEqual({r["pair"] for r in members if r["variant"] != "c"}, {group})
            self.assertEqual(len({json.dumps(r["context"], sort_keys=True) for r in members}), 3)

    def test_labels_and_metadata_do_not_affect_inputs(self):
        for row in self.rows:
            changed = dict(row, expected="SENTINEL", rationale="SENTINEL", id="SENTINEL", category="SENTINEL", pair="SENTINEL", contrastGroup="SENTINEL", variant="SENTINEL", contextProfile="SENTINEL")
            for arm in ("autoshell-native", "autoshell-command", "autoshell-expanded"):
                self.assertEqual(run_local.messages(row, arm), run_local.messages(changed, arm))
                self.assertNotIn("SENTINEL", json.dumps(run_local.messages(changed, arm)))

    def test_unknown_state_is_not_represented_as_clean(self):
        for row in self.rows:
            if row["expected"] == "ask":
                self.assertNotIn("gitStatus", row["context"])
                self.assertNotIn("agentTouchedFiles", row["context"])


if __name__ == "__main__":
    unittest.main()
