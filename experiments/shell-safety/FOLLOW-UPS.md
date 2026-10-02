# Study follow-ups

These checks track the staging study. Prior measured runs remain available when an extension adds or corrects a comparison.

- [x] **Recheck the secguard model-only setup.** The pinned model hash, prompt tokens, and upstream-style Metal/BF16 settings were checked. A fresh 284-case replay changed no decisions; [see the methods and saved outputs](additional/SECGUARD-RECHECK.md). The result describes this model-only path, not the full guard.
- [x] **Check secguard's native Rust wrapper and full guard separately.** The [extension](v3/RESULTS.md#native-secguard-guard-and-model-wrapper) replays both paths, proves model loading, and preserves native action/phase details. Full-guard Metal teardown assertions are recorded separately; native model-only runs exit successfully.
- [x] **Compare source-isolated Qwen Code and controlled reviewer designs.** The [120-case corpus and new reviewer runs](v3/RESULTS.md) distinguish stock policy/input differences, second review, optional inspection and a post-result prefetch diagnostic.
- [ ] **Run native Cursor Auto-review when available.** No application, agent CLI or authenticated session was available here. Do not present the controlled inspection experiment as Cursor performance.
- [ ] **Test an explicit read-before-verdict workflow on independent repositories.** Optional inspection made no reads; deterministic evidence provision helped the resolvable cases. The diagnostic is not proof of autonomous inspection.
- [x] **Rerun the six Node startup cases per native provider.** The [preflight and targeted rerun](extension/NATIVE-FULL.md#node-startup-rerun-preflight) checked the startup setting in the candidate shell, then verified the returned commands and file effects. The native chart now includes all 72 cases per provider.
- [ ] **Get independent human labels.** GPT-6 Astra generated and labeled the [72 case records](v2/data/cases.jsonl); another agent reviewed the labels. Collect independent human judgments before treating the labels as a validated benchmark.
