# Published approaches and what this extension compares

Checked 2026-10-02. Product descriptions are evidence about design, not results
on our fixtures. None establishes that command approval is solved generally.

| Source | Published approach | Study treatment |
| --- | --- | --- |
| [Anthropic: How we built Claude Code auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode) | A fast filter escalates flagged actions to a reasoning stage. The classifier keeps user messages and tool calls, excluding assistant prose and tool outputs. | Existing Claude whole-path measurements remain separate. The controlled second-review arm tests the general idea, not Anthropic's classifier. |
| [Qwen Code Auto Mode](https://github.com/QwenLM/qwen-code/blob/a011f66944768e05b432a10548ffa4576f1d8ef8/docs/users/features/auto-mode.md) | Open classifier source, transcript projection, two-stage review, and permission fast paths. | Import the actual pinned classifier and transcript code; substitute a documented local model transport. Exclude product fast paths and label the arm source-isolated. |
| [Cursor Run Modes](https://cursor.com/docs/agent/security/run-modes) | Auto-review combines allowlisting, sandboxing and a backend classifier. The classifier can inspect files using read-only tools. Cursor explicitly describes it as fallible. | Native arm unavailable in this environment. The controlled inspection arm tests evidence acquisition using immutable snapshots; it is not a Cursor reproduction. |
| [secguard source](https://github.com/random1st/secguard/tree/d45bbb55c30c767bb0c1fb07885a69bb11365836) | Policy and heuristic checks precede an optional local model. | Run the native full guard and native model wrapper separately, plus the older official non-ML release. Retain phase and model-loading evidence. |

Anthropic reports that its second stage lowers false positives on internal
traffic from 8.5% to 0.4%, while false negatives on 52 curated overeager actions
rise from 6.6% to 17%. Those are publisher-reported results on different data,
models and policies; do not place them in our measured-results tables. They
motivate measuring both useful approvals and unsafe approvals rather than a
single accuracy number.

The staged extension therefore separates reproducible wrapper checks,
source-isolated classification, controlled evidence acquisition, and future
whole-product tests. A product's prompt copied into another model does not
establish that product's performance.
