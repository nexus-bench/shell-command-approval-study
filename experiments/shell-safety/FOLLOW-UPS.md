# Study follow-ups

These checks are open. The published counts remain as measured until a check is completed and documented.

- [ ] **Recheck secguard.** Pin and verify the model file and its upstream version. Compare the prompt, token handling, and inference settings with the author's intended interface. Run a small set of clearly safe and clearly unsafe commands through a reference setup, then rerun the frozen cases without tuning on their labels. Keep the original 283/284 result visible and publish the corrected result, or explain why the setups differ. Until then, the reported behavior describes this setup, not the model in general.
- [ ] **Rerun the six Node startup cases per native provider.** First use the [preflight](extension/NATIVE-FULL.md#node-startup-rerun-preflight) to prove that `NODE_OPTIONS` reaches the exact candidate command while the agent process starts without it. Run only the Node family in disposable fixtures with fake credentials and blocked network access. Inspect candidate proposals, tool returns, and file effects separately. Recompute the native comparison only after those checks pass.
- [ ] **Get independent human labels.** The [72-case review sheet](CASE-REVIEW.md) lists the cases and the authors' labels. Collect independent judgments before treating the labels as a validated benchmark.
