# Study follow-ups

These checks are open. The published counts remain as measured until a check is completed and documented.

- [x] **Recheck the secguard model-only setup.** The pinned model hash, prompt tokens, and upstream-style Metal/BF16 settings were checked. A fresh 284-case replay changed no decisions; [see the methods and saved outputs](additional/SECGUARD-RECHECK.md). The result describes this model-only path, not the full guard.
- [ ] **Check secguard's native Rust wrapper and full guard separately.** Its policy and heuristic layers were outside the model-only comparison. Do not apply the model-only counts to that complete tool.
- [x] **Rerun the six Node startup cases per native provider.** The [preflight and targeted rerun](extension/NATIVE-FULL.md#node-startup-rerun-preflight) checked the startup setting in the candidate shell, then verified the returned commands and file effects. The native chart now includes all 72 cases per provider.
- [ ] **Get independent human labels.** GPT-6 Astra generated and labeled the [72 case records](v2/data/cases.jsonl); another agent reviewed the labels. Collect independent human judgments before treating the labels as a validated benchmark.
