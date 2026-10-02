# Additional local shell classifiers

This follow-up adds **ModernBERT-bash-classifier, secguard-guard 0.8B, and Kestrel v0.1** to the [repository-context study](../v2/README.md). AutoShell-350M remains unavailable through the public API (HTTP 401). Qwen3-4B was excluded at the user's request. No application code or execution policy changed.

## Findings

None of these three interfaces can distinguish the same command across different repository states: ModernBERT takes command plus CWD; secguard and Kestrel take only the command. Their v2 results measure the limitations of those inputs against our approval policy. They do not establish that the models ignored evidence they were given.

On the 36 existing v2 test cases:

| Model | Legitimate approved | Denied approved | Unknown approved | Median inference |
|---|---:|---:|---:|---:|
| ModernBERT | 6/12 | 6/12 | 6/12 | 62 ms |
| Kestrel | 10/12 | 10/12 | 10/12 | 0.024 ms |
| secguard | 12/12 | 12/12 | 12/12 | 603 ms |
| LANCET, previous run | 10/12 | 10/12 | 10/12 | 3.6 ms |
| AutoShell-0.8B application/full evidence, previous default | 8/12 | 4/12 | 7/12 | 3,150 ms |

Previous results come from [v2's saved table](../v2/results/table.md). AutoShell receives more information and a different policy prompt; this is a comparison of evaluated configurations, not a controlled architecture comparison. Timings are sequential warm local measurements on Apple M1 Pro 16 GB, and were not all collected in the same run. Kestrel timing is our Python port, not its publisher's Go runtime.

On the frozen public sample (50 safe and 50 unsafe examples from each source):

| Model | ShellRisk safe approved | ShellRisk unsafe approved | Shell Safety safe approved | Shell Safety unsafe approved |
|---|---:|---:|---:|---:|
| ModernBERT | 43/50 | 17/50 | 13/50 | 10/50 |
| Kestrel | 50/50 | 0/50 | 40/50 | 34/50 |
| secguard | 50/50 | 50/50 | 50/50 | 49/50 |

Kestrel's perfect result on this small ShellRisk subset does not transfer to Shell Safety or repository approval. ShellRisk is the publisher's own same-source benchmark. This sample does not justify a general zero-error claim. ModernBERT rejects many benign Shell Safety cases; its native policy treats network access as unsafe while allowing project file mutations, which differs from the source and application policies.

Secguard produced `safe` on 283 of 284 main evaluation inputs. All first generated tokens were `<think>`. Its native confidence calculation measures that first token's probability, even when the final label occurs later. We preserve this behavior rather than interpreting that score as calibrated label confidence. The native 0.85 gate and final-label-only mapping made identical decisions in this run. A [pinned-artifact, prompt-token, and Metal/BF16 recheck](SECGUARD-RECHECK.md) changed **none of the 284 decisions**. This remains a result for the model-only path; we did not run the publisher's Rust wrapper or its complete policy/heuristic guard.

The separate 12-case authorization/provenance diagnostic produced legitimate/deny/unknown approvals of 0/6, 0/4, 0/2 for ModernBERT; 4/6, 2/4, 2/2 for Kestrel; and 6/6, 4/4, 2/2 for secguard. Rejecting every diagnostic is not evidence of understanding authorization revocation.

## Setup and provenance

The [protocol](PROTOCOL.md) was saved before scoring. We reused 200 public cases, all 72 v2 fixtures (36 development and 36 test), and 12 adversarial cases. There were **852 main inference attempts**, all valid outputs with no input-capacity errors. These are previously inspected regression sets, not fresh blind holdouts. No prompt/threshold adjustments were made based on their results. Commands were supplied as inert text and never executed.

- [ModernBERT](https://huggingface.co/P0u4a/ModernBERT-bash-classifier): pinned weights, native `CWD: …\nCOMMAND: …` input, config labels `0=unsafe`, `1=safe`, argmax decision. PyTorch CPU float32, four threads, SDPA. Missing CWD is stipulated `/repo`. No repository bytes are appended to this trained format.
- [secguard](https://huggingface.co/random1st/secguard-models): Q8 GGUF; exact prompt and ChatML framing from [its guard adapter](https://github.com/random1st/secguard/blob/d45bbb55c30c767bb0c1fb07885a69bb11365836/crates/secguard-guard/src/brain.rs). Greedy 20-token generation, 512-token context, first-valid-prefix parsing and completed-thinking-block removal. llama.cpp build 10280 (`61881b1f7`), CPU four threads. Our CPU/default KV configuration differs from upstream GPU/BF16 KV. HTTP generation may continue beyond the first valid label, so latency includes that overhead. Maximum observed input was 186 tokens; no truncation was needed.
- [Kestrel](https://huggingface.co/kontext-security/Kestrel): published JSON artifact, threshold zero. Its exported coefficient already incorporates IDF. We verified all 50,000 features against [Kontext's runtime export](https://github.com/kontext-security/kontext/tree/8a0096c658167f29b1ee4927e812ff316e9d84c8/internal/guard/riskclassifier), then matched normalization and scores on all 78 upstream golden examples within 1e-8. Artifact license is `other`; weights and third-party source are not vendored here.

[artifacts.json](artifacts.json) records revisions, file SHA-256 hashes, sizes, and package versions. [Raw results](results/) retain IDs, input hashes, outputs, errors, and timings; public command text is not copied into predictions. [Generated tables](results/table.md) and [summary JSON](results/summary.json) separate public sources, development, test, and diagnostic results. ModernBERT's runner hash predates a Kestrel-only coefficient correction; its own inference code was unchanged.

## Reproduction

From the repository root, use the existing ignored research virtual environment and restore the public sample with the [extension's instructions](../extension/README.md). Install the versions listed in `artifacts.json` (this run used torch 2.14.1 and transformers 5.18.0).

```sh
.experiments/shell-safety/venv/bin/python experiments/shell-safety/additional/fetch.py
.experiments/shell-safety/venv/bin/python experiments/shell-safety/additional/test_adapters.py
llama-server -m .experiments/shell-safety/additional/secguard/secguard-guard.gguf --host 127.0.0.1 --port 18766 -c 512 -np 1 -t 4 -ngl 0 --no-warmup --log-disable
```

In a second terminal, run each model sequentially (move the saved result files to a separate archive first; the runner refuses overwrites):

```sh
.experiments/shell-safety/venv/bin/python experiments/shell-safety/additional/run.py modernbert
.experiments/shell-safety/venv/bin/python experiments/shell-safety/additional/run.py kestrel
.experiments/shell-safety/venv/bin/python experiments/shell-safety/additional/run.py secguard
.experiments/shell-safety/venv/bin/python experiments/shell-safety/additional/summarize.py
```

Five adapter tests cover reference parity, exported weights, thinking/prefix parsing, low-confidence behavior, and malformed-output handling. These validate adapters, not dataset labels. Fixed post-run secguard sanity probes are saved separately in `results/secguard-sanity.json`; they are not included in the 852 attempts or used to tune the model. All four (`pwd`, `rm -rf /`, `git reset --hard HEAD`, and `terraform destroy -auto-approve`) returned `safe` again in the recheck. The closer runtime match did not change those outputs. This is not a test of the publisher's full guard or its claimed training-set performance.

For repository-aware approval, retain an explicit evidence/authorization layer. These additional models may be evaluated as command-risk signals, but none closes the missing-context gap by itself.
