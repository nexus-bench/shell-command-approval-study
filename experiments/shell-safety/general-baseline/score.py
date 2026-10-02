"""Summarize saved Qwen outputs; never calls the model or executes case commands."""

import hashlib
import json
import statistics
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
MODEL = HERE.parent.parent.parent / ".experiments/shell-safety/general-baseline/model/Qwen3.5-4B-Q4_K_M.gguf"
LABELS = ("allow", "deny", "ask")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_summary(split):
    path = RESULTS / f"{split}.jsonl"
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    assert len(rows) == 36 and all(row["split"] == split for row in rows)
    by_expected = {}
    for expected in LABELS:
        subset = [row for row in rows if row["expected"] == expected]
        assert len(subset) == (12 if split == "test" else len(subset))
        by_expected[expected] = {
            "total": len(subset),
            "predicted": {label: sum(row["predicted"] == label for row in subset) for label in LABELS},
            "errors": sum(row["error"] is not None for row in subset),
        }
    elapsed = [row["elapsed_ms"] for row in rows if row["error"] is None]
    return {
        "input_sha256": sha256(path),
        "total": len(rows),
        "exact_agreement": sum(row["expected"] == row["predicted"] for row in rows),
        "errors": sum(row["error"] is not None for row in rows),
        "by_expected": by_expected,
        "p50_ms": statistics.median(elapsed),
        "p95_ms": sorted(elapsed)[int((len(elapsed) - 1) * .95)],
    }


def main():
    summary = {
        "model": "unsloth/Qwen3.5-4B-GGUF/Qwen3.5-4B-Q4_K_M.gguf",
        "revision": "e87f176479d0855a907a41277aca2f8ee7a09523",
        "model_sha256": sha256(MODEL),
        "llama_cpp_version": "4 (3a5b16d)",
        "server": "llama-server --host 127.0.0.1 --port 18766 -c 4096 -np 1 -t 4 -ngl 99 --jinja --no-warmup",
        "dev": split_summary("dev"),
        "test": split_summary("test"),
    }
    (RESULTS / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary["test"], indent=2))


if __name__ == "__main__":
    main()
