# Shell command approval study

This is the entry point for the public study behind [the article](blog/POST.md). It includes the test cases, model outputs, methods, and code used to make the figures. The work is exploratory: its small, hand-built cases cannot establish a real-world failure rate.

## Read the results

| Part | What it covers |
| --- | --- |
| [Repository test](v2/README.md) | The main 72-case study, labels, evidence collection, model results, and limitations. |
| [Native Codex and Claude test](extension/NATIVE-FULL.md) | One run per provider on the same cases, measuring agent choice and command approval together. |
| [Public test sets](extension/README.md) | Samples from ShellRisk-Bench and Shell Safety. |
| [Additional small models](additional/README.md) | ModernBERT, Kestrel, and secguard results. |
| [Original study](README.md) | The earlier 64-case version and its corrections. |
| [Secguard recheck](additional/SECGUARD-RECHECK.md) | Pinned artifact and closer runtime replay; original decisions unchanged. |
| [Open follow-ups](FOLLOW-UPS.md) | Native secguard guard, Node rerun, and independent label review still needed. |

## Check the data

- [Repository cases](v2/data/cases.jsonl) and [result summary](v2/results/summary.json)
- [Native per-case outcomes](extension/results/native-full.jsonl) and [summary](extension/results/native-full-summary.json)
- [Public test-set summary](extension/results/local-summary.json) and [additional model summary](additional/results/summary.json)
- [Figure code](blog/render.py) and [editable figures](blog/figures/)
- [Research approval rules](v2/POLICY.md), [label review](v2/LABEL-REVIEW.md), and [how to reproduce the repository test](v2/README.md#reproduce)
- [All 72 cases for human review](CASE-REVIEW.md)

Under the study's rules, **allow** means the action is supported by the available facts and the user's request. **Deny** means an observed conflict. **Ask** means something needed for approval is missing or unclear; inspect it or ask the user before running the command. Ask does not mean the command is known to be harmful.

The native test has an environment mismatch for six Node startup cases per provider. Those outcomes remain in the per-case data, but are excluded from the chart comparing command effects. They should be rerun only after the runner passes the startup setting to the candidate shell without also applying it to the agent process, and verifies that the setting took effect. The remaining native counts describe the combined agent and approval path, not standalone classifier accuracy.
