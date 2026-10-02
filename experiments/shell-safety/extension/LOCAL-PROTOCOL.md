# Local extension protocol

Frozen before the 200-row inference sweep, 2026-09-30.

Use the original pinned LANCET v0.4.2 and AutoShell-0.8B Q8_0 artifacts,
original CPU settings (four threads; AutoShell one slot, 4096 tokens), and
unchanged thresholds. No commands in any corpus are executed.

Download pinned ShellRisk-Bench test and Shell Safety large test plus its
row-aligned transcript version. Keep downloaded text ignored because ShellRisk
retains multiple upstream licenses including absent and GPL terms. Check in IDs,
source revisions and hashes, selection logic, request hashes and model outputs.

From each dataset, select 50 allow and 50 intervention POSIX/Bash examples.
Within each label, cycle alphabetically through categories/source adapters;
within each category order SHA256('20260930:' + id). Reserve the first two
examples per dataset/label (8 total) for format development; score the next 50.
This deliberately overrepresents rare sources and categories. Report separate
source denominators, never pool public risk labels with synthetic authorization
labels as if identical. Full source category counts live in public-selection.json.

Compare LANCET supported command-only input with AutoShell command-only,
native transcript, and original JSON-lines context serialization. Public native
Shell Safety uses exactly the first two transcript messages, dropping the gold
assistant response. Public expanded input uses exactly the original structured
session_context. Native serialization normalizes remote URL to hostname in the
published transcript, so this comparison measures the complete published input
encoding, not an isolated whitespace experiment. ShellRisk has no context;
context arms use empty SessionContext (an empty-wrapper ablation).

Disjoint native-format development produced valid yes/no logprobs in 8/8 rows,
correct polarity on 7/8; the single error was rejection of a source-benign command.
No prompts or thresholds were tuned to improve that result. Synthetic native
format preserves all supplied extra state facts as an extension to the published
core keys; it is not claimed to be an exact training-distribution input.

Run all local inference arms sequentially. Two unscored warmups ('ls', 'pwd')
precede each arm. Persist raw outputs per example immediately; refuse overwrite.
Record dataset hash, runtime and wall time; timings remain descriptive one-sweep
measurements amid uncontrolled desktop activity. Exclude expected labels,
categories, rationale, pair IDs, and profile IDs from input.

ShellRisk is context-free risk, not authorization. Shell Safety tests overlap
the model authors' source distributions and may overlap training at command or
template level; do not describe either as a novel independent holdout. LANCET's
model card names ShellRisk training and Shell Safety v2 training. AutoShell card
names shell-safety-common (not currently discoverable) while the linked training
dataset is shell-safety-transcripts. Exact training-row membership is unknown.

## Prespecified representation-control amendment

Before scoring an additional arm, add `autoshell-format-only` on the already
selected 100 Shell Safety cases. Parse exactly the three published transcript
fields (remote hostname, touched-files string, complete status text), then
JSON-quote those same string values, preserving field order and the exact system
prompt and command. Reconstruct the original block to verify losslessness.
This isolates quoting/newline representation from URL normalization and field
selection. No examples, labels, thresholds, or source-native inputs change.
The initial native/expanded comparison remains a combined format/feature change.

## Interrupted-run provenance

The host interrupted the first command-only public sweep at 83 of 200 rows.
Recovery found no surviving inference processes, restarted the same declared
CPU server command, and appended the remaining 117 rows without rerunning the
83. Original metadata is retained and a resume event records the boundary.
At that time the runner recorded dataset hash and arm but not an experiment
fingerprint; therefore old server settings cannot be cryptographically proven
from those predictions. Future resume refuses missing or differing fingerprints
(serialized input stream, parser source, artifact lock, declared settings,
generation options, and redaction). Declared settings are not remote attestation.

A second host failure interrupted public expanded-context inference after 36 of
200 rows. Recovery again found no surviving study processes, restarted the same
CPU server, verified the new fingerprint, and appended the remaining 164 rows.
The complete public native-context arm was retained without rerunning it. A
recovery helper now skips complete arms and resumes only incomplete matching runs.
