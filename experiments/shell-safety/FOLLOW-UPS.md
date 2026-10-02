# Study follow-ups

These checks are open. The published counts remain as measured until a check is completed and documented.

- [x] **Recheck the secguard model-only setup.** The pinned model hash, prompt tokens, and upstream-style Metal/BF16 settings were checked. A fresh 284-case replay changed no decisions; [see the methods and saved outputs](additional/SECGUARD-RECHECK.md). The result describes this model-only path, not the full guard.
- [ ] **Check secguard's native Rust wrapper and full guard separately.** Its policy and heuristic layers were outside the model-only comparison. Do not apply the model-only counts to that complete tool.
- [ ] **Rerun the six Node startup cases per native provider.** First use the [preflight](extension/NATIVE-FULL.md#node-startup-rerun-preflight) to prove that `NODE_OPTIONS` reaches the exact candidate command while the agent process starts without it. Run only the Node family in disposable fixtures with fake credentials and blocked network access. Inspect candidate proposals, tool returns, and file effects separately. Recompute the native comparison only after those checks pass.
- [ ] **Get independent human labels.** The [72-case review sheet](CASE-REVIEW.md) lists the cases and the authors' labels. Collect independent judgments before treating the labels as a validated benchmark.
