# Native local classifier formats

## Does the original context encoding match the model's published format?

### Takeaway
AutoShell's published example uses plain text values in a SessionContext block; the original mini-study JSON-encoded every value. This extension compares exact source transcripts to that earlier serialization without tuning prompts or thresholds against the test outcomes.

### Cited Findings
- AutoShell's reference inference requests one token and top-20 log probabilities, then renormalizes yes/no scores with an allow threshold greater than 0.8. Context examples use `gitRemote`, comma-separated `agentTouchedFiles`, and multiline Git-status text. — [AutoShell reference example](https://huggingface.co/tomngdev/AutoShell-0.8B)
- Native Shell Safety input is the exact first two messages from the row-aligned transcript file. The assistant gold response is removed. The conversion also normalizes remote URLs to hostnames, so this experiment tests the published representation as a whole, not whitespace alone. — local `prepare_public.py`, pinned [transcripts](https://huggingface.co/datasets/tomngdev/shell-safety-transcripts/tree/e8b46e9821d9bc7957466154453d88c59a76eb53/lg)
- The synthetic adapter renders core fields as plain text and retains added evidence fields as JSON values where needed. Both context arms receive the same case facts. Command-only arms receive no case labels, rationale, category, pair, or profile identifier. — local `run_local.py`
- LANCET uses its supplied ONNX command-only runtime. No unsupported session prefix is added. — [LANCET usage](https://huggingface.co/fingerthief/lancet-nano)
- Eight disjoint development cases verified valid first-token output (8/8) and correct label polarity (7/8) before the frozen public sweep. No prompt or threshold changed in response. — local `results/public-format-dev-autoshell-native.jsonl`, `LOCAL-PROTOCOL.md`

### Inferences
- Better performance with native transcripts would support using that adapter, but would not show that arbitrary rich repository state is within the model's training distribution.
- ShellRisk has no context: its two context arms use the same empty wrapper, a useful control.

### Gaps
- Original upstream score helper accepts several punctuation variants and defaults missing yes/no logprobs; this study retains the stricter v1 parser, which fails closed on missing logprobs or a non-label output. That is an implementation difference, reported through error counts.
- Timings are one sequential CPU sweep amid uncontrolled desktop activity. Public command inference was interrupted after 83 rows and resumed for 117 after restarting the same local server settings. Metadata records that boundary; latency comparisons are descriptive.
