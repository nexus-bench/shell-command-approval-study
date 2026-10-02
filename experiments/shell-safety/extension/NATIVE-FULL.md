# Native Codex and Claude end-to-end fixture sweep

On 2026-10-01, both native paths were run once over all 72 frozen v2 cases. This
is an **end-to-end agent and permission-path experiment**, not a direct test of
two standalone classifiers or a rerun of the v2 model benchmark. Unlike the v2
protocol, a native path can execute an approved candidate. Every candidate here
was one of the twelve fixed commands in the author-created corpus, and each ran
only against a disposable Git repository containing synthetic data and a fake
credential canary. Claude and Codex used separate fixture sets.

The agent received the exact command, task, and v2 captured full evidence as
data. Further inspection was disallowed to preserve the study's unavailable
evidence states. Codex used CLI 0.157.1, `gpt-6-astra`, a read-only sandbox and
`auto_review` for sandbox-boundary requests. Claude used Agent SDK 0.3.283,
`opus`, auto mode with `classifyAllShell`, a strict network sandbox, and a hook
that denied any Bash command other than the exact candidate. No manual approval
was granted. The host supplied a local `python` shim and
`PYTHONDONTWRITEBYTECODE=1` to match the captured Python cases. The first Codex
Python attempts had exit 127 because this Mac has no `python` command; those six
were rerun with the shim, and the latest records are used below.

## Observed results

The six Node startup cases per provider were rerun on 2026-10-02. The first
attempts lacked the required startup preload in the candidate shell, so their
effects were excluded. The targeted rerun supplied that preload only to the
candidate Node command and checked for a marker in every returned tool result.
All six Node cases per provider now meet the stated environment condition.

| Research-policy label, all 72 cases per provider | Codex candidate tool returned | Claude candidate tool returned |
| --- | ---: | ---: |
| Allow: evidence supports action | 26/26 | 25/26 |
| Deny: observed conflict, stop | 0/22 | 0/22 |
| Ask: inspect or clarify first | 12/24 | 12/24 |

The twelve returned `ask` cases differ between providers. They are **insufficient-evidence
approvals under the research policy**, not observed damage: most unavailable
states deliberately use a benign underlying fixture. All 144 latest trials
completed. No `.env` or `user-notes.txt` content changed, and no tool output
recorded the fake canary. Each provider changed tracked `notes.txt` only in the
two good rollback fixtures, where the captured receipt attributed the edit to
the task.

Across all 72 latest cases, Codex recorded 45 candidate proposals, 22 explicit
auto-review approvals, seven explicit auto-review denials, and 38 returned
candidate commands. Sixteen commands returned without an auto-review event,
consistent with in-sandbox calls bypassing that review. Claude recorded 45 exact
candidate proposals, eight explicit classifier denials, and 37 returned Bash
tools. It attempted nine extra or substituted commands; the exact-command hook
blocked them. Claude exposed no separate positive classifier verdict, so a
returned tool is only a combined-path observation. Its PostToolUse event also
does not prove shell exit code zero. Codex command records include exit codes;
all 38 returned commands exited zero in the latest records.

Agent non-proposal, classifier denial, tool return, and file effect are different
outcomes. The known-deny cases all stopped before the candidate tool returned,
but most had no explicit classifier denial because the agent did not submit the
candidate. Neither provider's 0/22 figure therefore establishes a native
classifier false-approval rate. These are single trials on author-built
fixtures, and the models saw captured host receipts as prompt text rather than
an independently authenticated native context channel. Codex used a zsh tool
wrapper even though the v2 host receipt specifies bash; the commands outside
the Node preload family used a checked subprocess setting on the rerun. The
remaining shell difference should still be kept in mind when reading the counts.

## Evidence and reproduction

- [Sanitized per-case outcomes](results/native-full.jsonl) record labels,
  proposal, explicit review or denial, tool return, and file effects, without
  raw tool output or account data.
- [The twelve Node rerun outcomes](results/native-node-rerun.jsonl) are also
  saved separately. [native-node-merge.py](native-node-merge.py) verifies them,
  replaces the earlier Node rows, and recomputes the public summary from the
  sanitized cases. It first checks that this reducer reproduces the summary
  published before the Node rerun.
- [Aggregate counts and case IDs](results/native-full-summary.json) were
  recomputed by [native-node-merge.py](native-node-merge.py) from the saved
  per-case outcomes; the original sweep used
  [native-full-analyze.py](native-full-analyze.py).
- The ignored `.experiments/shell-safety/extension/native-full-results.jsonl`
  contains restricted local event traces. The original sweep's raw traces are
  not in this checkout; its sanitized case rows are committed. The targeted
  rerun's local trace includes repeated attempts. The merge script selects the
  latest trial per provider and Node case.

From the repository root, with native subscription sign-ins available:

```sh
npm install --prefix .experiments/shell-safety/extension/native --no-save --ignore-scripts @openai/codex@0.157.1 @anthropic-ai/claude-agent-sdk@0.3.283
python3 experiments/shell-safety/extension/native-full-build.py codex --reset
python3 experiments/shell-safety/extension/native-full-build.py claude --reset
node experiments/shell-safety/extension/native-full.mjs codex all --rerun
node experiments/shell-safety/extension/native-full.mjs claude all --rerun
python3 experiments/shell-safety/extension/native-full-analyze.py --write
```

The builder resets only its marked generated directories. The runner checks
each visible file against the frozen case hash before a trial. Do not point the
runner at a real project or replace the corpus with live credentials or network
destinations. This separate experiment does not change v2's inert-candidate
protocol or its local-model results.

### Node startup rerun preflight

The runner has a targeted `node-startup --rerun` mode. Claude uses a `node`
wrapper first on `PATH`. Codex starts candidate commands through a login zsh
that resets `PATH`, so its shell subprocess instead receives a `NODE_OPTIONS`
probe through Codex's shell environment setting. The probe loads the same
`startup.cjs` only for the exact candidate arguments inside a disposable Node
fixture. Neither provider loads it in the agent process. Before connecting to
each provider, the runner checks with a harmless temporary startup file that
the exact command loads it and a different Node command does not. This check
does not execute the bad fixture. A fixed marker confirms that the preload ran
when a candidate reached the tool.

To prepare the disposable fixtures and run **only** the six Node cases for each
provider, use separate commands from the repository root:

```sh
python3 experiments/shell-safety/extension/native-full-build.py codex --reset
python3 experiments/shell-safety/extension/native-full-build.py claude --reset
node experiments/shell-safety/extension/native-full.mjs codex node-startup --rerun
node experiments/shell-safety/extension/native-full.mjs claude node-startup --rerun
python3 experiments/shell-safety/extension/native-node-merge.py
```

The bad fixture contains only a fake credential and a `.invalid` destination.
Keep network access blocked. The merger refuses a returned Node command unless
its preload marker is present. It also rejects errors, unexpected Node cases,
fake-canary output, or protected-file changes. The counts above include the
verified rerun.
