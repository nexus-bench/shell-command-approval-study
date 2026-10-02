# Public shell safety datasets

## Which corpora are usable for this study?

### Takeaway
Two downloaded public test sets provide complementary coverage: ShellRisk-Bench evaluates command risk without context; Shell Safety supplies synthetic session state and a matching training-format transcript. The frozen evaluation samples 100 cases from each, balanced by source label rather than production prevalence.

### Cited Findings
- ShellRisk-Bench publishes 4,194 test commands (193 risky, 4,001 not risky), assembled from six sources. Benign labels follow source task intent; risky labels follow security collection purpose. Multiline sessions are excluded. Its authors explicitly distinguish risk from authorization. — [Dataset card](https://huggingface.co/datasets/kontext-security/ShellRisk-Bench)
- ShellRisk keeps upstream licenses; downloaded material remains in ignored cache. Versioned selection IDs, source revisions, hashes, and predictions reconstruct this experiment without republishing the command text. — [License/provenance](https://github.com/kontext-security/shellrisk-bench/blob/main/DATASETS.md); local `public-artifacts.json`, `fetch_public.py`
- Shell Safety transcripts are converted from Shell Safety with a static system prompt and variable SessionContext, distributed under MIT. Their first two messages are model inputs; the third contains the label and is removed. — [Transcript card](https://huggingface.co/datasets/tomngdev/shell-safety-transcripts); local `prepare_public.py`
- Downloads pin dataset revisions `437467862139b4e9cdd5322024ef3434a67c7ec8`, `155dbb5d3047dd095523bd8ee3dd65adf1296dde`, and `e8b46e9821d9bc7957466154453d88c59a76eb53`, respectively. Every downloaded file has a SHA256 lock. — local `public-artifacts.json`

### Inferences
- Balanced sampling measures sensitivity and false approvals more legibly than the highly imbalanced full ShellRisk test distribution, but aggregate accuracy is not comparable to its published full-test headline.
- Round-robin source/category sampling deliberately emphasizes rare categories. It does not estimate naturally occurring command prevalence.

### Gaps
- Public benchmarks are not clean independent validation of these models: LANCET names ShellRisk and Shell Safety training sources; AutoShell links its training dataset to Shell Safety transcripts. Exact row/template overlap with model training is unknown. — [LANCET model card](https://huggingface.co/fingerthief/lancet-nano); [AutoShell model card](https://huggingface.co/tomngdev/AutoShell-0.8B)
- The study uses a frozen subset, not all downloaded test rows. See the selection manifest for every selected source index and command hash.
