# Classifier and evidence-acquisition extension

This is an extension of the staging study, not a new validated benchmark. Read
[PROTOCOL.md](PROTOCOL.md) before interpreting the results. The original v2 data
and runs remain available for comparison. Nothing in these runners executes a
candidate command.

Read the [results and interpretation](RESULTS.md), [published approaches](RELATED-WORK.md), the [per-split results](results/table.md),
and the [family/label breakdown](results/breakdown.json).

## Arms

| Arm | Actual implementation | Inputs and limits |
| --- | --- | --- |
| `secguard-release` | Official 0.5.5 macOS binary, SHA-verified | Default policy/heuristics; release builds have no ML feature. Command only. Release revision `a5b338584795c5a604c08a571972bce6e986be33`. |
| `secguard-full` | Pinned Rust guard + native ML at `d45bbb55c30c767bb0c1fb07885a69bb11365836` | Default guard configuration. Only source edit redirects the model path to the workspace. The guard decision and phase are retained. |
| `secguard-model-only` | Same pinned Rust MicroBrain | Bypasses policy/heuristics to isolate the native model wrapper. Same pinned weights as the older model-only experiment. |
| `qwen-code` | Pinned Qwen Code classifier, stock prompt and transcript builder at `a011f66944768e05b432a10548ffa4576f1d8ef8` | Source-isolated with a local JSON-schema transport, not the native product. User request + exact command; no file contents injected as user intent. No permission-manager fast paths. |
| `single` | Study reviewer, Qwen3.5-4B | Saved evidence, study policy, three-way decision. |
| `two-stage` | Same reviewer | Second review only after a non-allow first decision. |
| `inspect` | Same reviewer | Up to four read-only synthetic snapshot observations; no host filesystem access. |
| `prefetch` | Same reviewer, diagnostic follow-up | Harness reads visibly unobserved snapshots before the unchanged single-pass review. This is not autonomous inspection. |

The three controlled reviewers use the same model, initial input and policy.
Qwen Code's stock policy permits some work the study policy requires evidence
for. It is not a controlled model-quality comparison. Similarly the released
secguard revision differs from the more recent pinned source, so improvements
between those revisions cannot be attributed solely to adding ML.

In native secguard records, normalized `block` means the Rust guard returned
`Verdict::Destructive`; it is not proof of enforcement. The separate native
`action` can be `Block`, `Warn` or `Confirm`. Safe-verdict counts compare
classification with study labels. Actual permission outcomes remain null.

## Reproduce

From the study root, clone the upstream repositories into the ignored cache:

```sh
gh repo clone QwenLM/qwen-code .experiments/upstream/qwen-code
gh repo clone random1st/secguard .experiments/upstream/secguard
git -C .experiments/upstream/qwen-code switch --detach a011f66944768e05b432a10548ffa4576f1d8ef8
git -C .experiments/upstream/secguard switch --detach d45bbb55c30c767bb0c1fb07885a69bb11365836
python3 experiments/shell-safety/v3/build.py
python3 -m unittest discover -s experiments/shell-safety/v3 -p 'test_*.py'
```

Fetch Qwen3.5-4B Q4_K_M from the revision and hash in
[the original baseline](../general-baseline/README.md), saving it as
`.experiments/qwen35-4b.gguf`. Fetch the secguard model from the original
[artifact manifest](../additional/artifacts.json), saving it as
`.experiments/secguard-guard.gguf`. Do not install either into user configuration.

Download the [official secguard 0.5.5 release](https://github.com/random1st/secguard/releases/tag/v0.5.5) `secguard-aarch64-apple-darwin.tar.gz` and
`checksums-sha256.txt` release assets. Verify archive SHA-256
`69c178718c48038b3789f57fd6cefc06c3ae14b4d9eb3553094883d4e743fce3` and extract the
binary into `.experiments/secguard-release/`.

Install the pinned npm dependencies in this directory (`npm ci`), then run
`npm run build:qwen`. The build imports the upstream classifier source; it does
not copy or recreate its policy. `qwen-build.json` records source hashes and
transport limitations. The adapter does not implement upstream SDK retries.
The bundle also stubs logging and context-length-error detection, and supplies
a minimal configuration plus a shell-input projection containing the exact
command. It does not instantiate the product's executable tool registry.

Start the localhost model server from the study root:

```sh
llama-server -m .experiments/qwen35-4b.gguf --alias qwen35-4b-q4 --host 127.0.0.1 --port 18767 -c 16384 -np 1 -t 4 -ngl 99 --jinja --no-warmup
```

Run arms serially to avoid request queuing contaminating latency:

```sh
python3 experiments/shell-safety/v3/run.py qwen-code --run-id qwen-code-v3
python3 experiments/shell-safety/v3/run.py single --dataset evidence-v3 --run-id single-v3
python3 experiments/shell-safety/v3/run.py two-stage --dataset evidence-v3 --run-id two-stage-v3
python3 experiments/shell-safety/v3/run.py inspect --dataset evidence-v3 --run-id inspect-v3
python3 experiments/shell-safety/v3/run.py prefetch --dataset evidence-v3 --run-id prefetch-diagnostic
python3 experiments/shell-safety/v3/score.py
```

Existing run directories are never overwritten. Use a new run ID for reruns.
Smoke runs and incomplete runs are excluded from summary tables. Models do not
receive IDs, expected labels, post-inspection labels, or the withheld snapshots.

For native secguard, `build-secguard.py` uses an isolated toolchain under
`.experiments/rust/`; `bootstrap-rust.py` can populate it from a Rust distribution
manifest saved as `.experiments/rust-channel.toml`. Components are hash-verified.
This run used the 2026-10-01 stable distribution (Rust 1.99.0); exact component
URLs and checksums are preserved in [rust-components.json](rust-components.json).
CMake can be supplied through `uv run --with cmake python .../build-secguard.py`.
The build preserves upstream `Cargo.lock` and records its hash. The source-path
patch is included in `secguard-build.json`.

```sh
python3 experiments/shell-safety/v3/run-secguard.py full --dataset v3 --run-id secguard-full-v3
python3 experiments/shell-safety/v3/run-secguard.py model-only --dataset v3 --run-id secguard-native-model-v3
```

Public and adversarial replays use `--dataset public` / `--dataset adversarial`.
First reconstruct the public sample with the original `extension/fetch_public.py`
and `extension/prepare_public.py`. Public command text is kept in the ignored
cache; result rows contain IDs, command hashes, and predictions.

## Native product availability

Existing Codex/Claude whole-path results remain in `extension/`. They are not
isolated classifier verdicts. Cursor Auto-review cannot be run in this environment:
no Cursor application, agent CLI or authenticated session was found. This arm
remains unavailable, with no invented results. Its read-only inspection design
motivates the controlled inspection arm but does not make that arm Cursor.

## Interpretation

The 48 new cases use six author-written script scenarios, two textual variants
and four evidence conditions each. They test a narrow causal question; they are
not 48 independent real-world workflows. Initial ask labels can resolve only
after an exact recorded observation matches the predeclared resolution rule.
An authorization gap cannot be filled by inspecting source code.

No thresholds are fitted in this extension. Test labels are author judgments
without independent human validation. Report per-case denominators, operational
errors, and policy/input differences alongside any aggregate result.

`validate.py` audits the corpus hash, case/repeat coverage, label consistency,
non-execution fields and evidence-resolution claims. `sources/` preserves runner
versions matching available run hashes. The first release public/adversarial
replays predate timeout-handling edits and do not have an archived exact runner;
their original hashes and predictions remain intact. This limits exact-source
reproduction of those two early runs. Both were replayed with the archived runner
under `-verified` IDs; every decision matched. Summaries use the verified replays
and exclude the early duplicates. Controlled-arm prompts and case bytes did
not change during inference. `freeze.json` records the state at corpus creation;
its `inference_started: false` is historical, not the current run status.

The first full-native replay returned 120 decisions but failed at process exit
with a llama.cpp Metal assertion. It remains excluded as incomplete. Subsequent
native replays record teardown return codes and saved crash tails separately;
`completed` means all classifier responses were collected. A dagger in the
results table flags teardown failures. No classifier verdict is inferred from
the process's exit status in the native Rust-driver arms.
