"""Audit dataset structure and exact overlap without reading predictions."""
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def summary(data):
    return {"rows": len(data), "unique_commands": len({r["command"] for r in data}),
            "labels": dict(sorted(Counter(r["expected"] for r in data).items())),
            "categories": dict(sorted(Counter(r["category"] for r in data).items()))}


def audit():
    synthetic = rows(HERE / "data/synthetic.jsonl")
    old = rows(HERE.parent / "cases.jsonl")
    public = rows(ROOT / ".experiments/shell-safety/public/public-all.jsonl")
    selected = rows(ROOT / ".experiments/shell-safety/public/public.jsonl")
    commands = {r["command"] for r in synthetic}
    datasets = defaultdict(list)
    for row in public:
        datasets[row["sourceDataset"]].append(row)
    result = {"scope": "Structure and exact command strings only; no model predictions read",
              "synthetic_sha256": hashlib.sha256((HERE / "data/synthetic.jsonl").read_bytes()).hexdigest(),
              "synthetic": summary(synthetic), "original": summary(old),
              "public": {name: summary(data) for name, data in sorted(datasets.items())},
              "public_selected": summary(selected),
              "synthetic_context_profiles": dict(sorted(Counter(r["contextProfile"] for r in synthetic).items())),
              "exact_overlap_unique_commands": {},
              "limitations": "Exact strings do not detect semantic paraphrases or undisclosed model training overlap."}
    for name, data in {"original": old, "public_selected": selected, **datasets}.items():
        result["exact_overlap_unique_commands"][name] = len(commands & {r["command"] for r in data})
    return result


if __name__ == "__main__":
    output = HERE / "data/coverage-audit.json"
    output.write_text(json.dumps(audit(), indent=2, sort_keys=True) + "\n")
    print(output)
