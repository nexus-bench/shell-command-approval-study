"""Render a compact, human-reviewable index of the frozen repository cases."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "v2/data/cases.jsonl"
DEST = ROOT / "CASE-REVIEW.md"


def cell(value):
    return str(value).replace("|", "\\|").replace("\n", "<br>")


cases = [json.loads(line) for line in SOURCE.read_text().splitlines() if line]
assert len(cases) == 72

lines = [
    "# Review the 72 shell command cases",
    "",
    "These are the author-assigned labels, shown separately so readers can check them.",
    "A second agent reviewed the labels, but people have not independently judged every case.",
    "Use the [approval rules](v2/POLICY.md) and open each linked [full case](v2/data/cases.jsonl),",
    "including its file contents and captured environment, before deciding whether you agree.",
    "The short evidence column is only an index. It does not show every relevant fact.",
    "The `oracle` field in the raw data describes the author's intended effect; avoid reading it",
    "until after you make your own judgment if you want a blind review.",
    "",
    "**Allow** means the visible facts support running the command; **deny** means they show a conflict;",
    "**ask** means a fact needed for approval is missing or unclear.",
    "An ask label does not mean the underlying command is harmful.",
    "",
    "| Case | Author label | User's task | Candidate command | Visible file pointers | Your label |",
    "| --- | --- | --- | --- | --- | --- |",
]

for number, case in enumerate(cases, 1):
    files = ", ".join(
        f"{entry['path']} ({'unavailable' if entry.get('error') else 'shown'})"
        for entry in case["full"]["files"]
    ) or "none"
    lines.append(
        "| "
        + " | ".join(
            [
                f"[{cell(case['id'])}](v2/data/cases.jsonl#L{number})",
                cell(case["expected"]),
                cell(case["full"]["host"]["userRequest"]),
                f"`{cell(case['command']).replace('`', '&#96;')}`",
                cell(files),
                "_____",
            ]
        )
        + " |"
    )

lines += [
    "",
    "The [label review notes](v2/LABEL-REVIEW.md) record six changes made before model inference.",
    "If you disagree with a label, please include the case ID, your label, and the visible fact",
    "that supports it when you [send feedback](https://github.com/apucher/shell-command-approval-study/issues/new).",
    "",
]
DEST.write_text("\n".join(lines))
