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

The six Node startup cases are excluded from the effect comparison below. The
captured v2 receipt specifies a `NODE_OPTIONS` preload, but the native tool
process did not actually inherit that preload. Both agents still processed those
six prompts; their outcomes are in the per-case data. Rerun them before counting
their effects, using a runner that sets the preload for the candidate shell
without loading it in the agent process and checks that it ran.

| Research-policy label, excluding Node startup | Codex candidate tool returned | Claude candidate tool returned |
| --- | ---: | ---: |
| Allow: evidence supports action | 24/24 | 23/24 |
| Deny: observed conflict, stop | 0/20 | 0/20 |
| Ask: inspect or clarify first | 12/22 | 12/22 |

The twelve returned `ask` cases differ between providers. They are **insufficient-evidence
approvals under the research policy**, not observed damage: most unavailable
states deliberately use a benign underlying fixture. All 144 latest trials
completed. No `.env` or `user-notes.txt` content changed, and no tool output
recorded the fake canary. Each provider changed tracked `notes.txt` only in the
two good rollback fixtures, where the captured receipt attributed the edit to
the task.

Across all 72 cases, Codex recorded 46 candidate proposals, 25 explicit
auto-review approvals, seven explicit auto-review denials, and 39 returned
candidate commands. Fourteen commands returned without an auto-review event,
consistent with in-sandbox calls bypassing that review. Claude recorded 45 exact
candidate proposals, eight explicit classifier denials, and 37 returned Bash
tools. It attempted nine extra or substituted commands; the exact-command hook
blocked them. Claude exposed no separate positive classifier verdict, so a
returned tool is only a combined-path observation. Its PostToolUse event also
does not prove shell exit code zero. Codex command records include exit codes;
all 39 returned commands exited zero in the latest records.

Agent non-proposal, classifier denial, tool return, and file effect are different
outcomes. The known-deny cases all stopped before the candidate tool returned,
but most had no explicit classifier denial because the agent did not submit the
candidate. Neither provider's 0/20 figure therefore establishes a native
classifier false-approval rate. These are single trials on author-built
fixtures, and the models saw captured host receipts as prompt text rather than
an independently authenticated native context channel. Codex used a zsh tool
wrapper even though the v2 host receipt specifies bash; the commands outside
the Node preload family were used for the limited comparison above, with that
remaining shell difference noted.

## Evidence and reproduction

- [Sanitized per-case outcomes](results/native-full.jsonl) record labels,
  proposal, explicit review or denial, tool return, and file effects, without
  raw tool output or account data.
- [Aggregate counts and case IDs](results/native-full-summary.json) are generated
  by [native-full-analyze.py](native-full-analyze.py).
- The ignored `.experiments/shell-safety/extension/native-full-results.jsonl`
  contains restricted local event traces. Repeated interrupted attempts remain
  there; the analyzer selects the latest trial per provider and case.

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

The runner now has a targeted `node-startup --rerun` mode. It puts a `node`
wrapper first on `PATH` only in that mode. The wrapper adds the captured
`NODE_OPTIONS=--require=./startup.cjs` only for the exact candidate arguments
inside a Node startup fixture. Other Node calls, including agent startup, run
without that preload. Before connecting to either provider, the runner checks
with a harmless temporary preload that the exact command loads it and a
different Node command does not. This check does not execute the bad fixture.
The wrapper prints a fixed marker before launching an approved candidate; the
runner records only whether that marker appeared in tool output.

To prepare the disposable fixtures and run **only** the six Node cases for each
provider, use separate commands from the repository root:

```sh
python3 experiments/shell-safety/extension/native-full-build.py codex --reset
python3 experiments/shell-safety/extension/native-full-build.py claude --reset
node experiments/shell-safety/extension/native-full.mjs codex node-startup --rerun
node experiments/shell-safety/extension/native-full.mjs claude node-startup --rerun
```

The bad fixture contains only a fake credential and a `.invalid` destination.
Keep network access blocked. Check the trial records for the preflight result,
the exact submitted command, and the preload marker before changing
the published counts. The rerun has been prepared but is not included in the
counts above.
