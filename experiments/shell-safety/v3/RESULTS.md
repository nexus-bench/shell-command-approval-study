# Classifier and evidence-acquisition results

These are staging-study measurements from 2026-10-02. The original 72 cases
remain intact. The extension adds 48 synthetic cases: six script scenarios,
two textual variants, and four evidence/authorization states. The new test split
contains only three scenarios, with six supported allow, six observed deny and
twelve initial ask cases. Six ask cases can resolve through a file read; six
require missing user confirmation. Labels are author judgments, not independently
human-validated. No candidate command was executed by these extension runners.

## Controlled reviewer comparison

All three predeclared arms use the same Qwen3.5-4B Q4_K_M model, study policy,
initial evidence, JSON output schema and generation settings. The second-review
arm reconsiders non-allow decisions without new evidence. The optional-inspection
arm can request up to four immutable file snapshots.

| New test cases | Supported approvals / 6 | Deny approvals / 6 | Unresolved ask approvals / 12 | Ask cases resolved and approved / 6 | Call failures / 24 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Single pass | 6 | 0 | 0 | 0 | 0 |
| Second review | 6 | 0 | 9 | 0 | 0 |
| Optional inspection | 6 | 0 | 0 | 0 | 0 |

On development cases, single pass and second review each approved 2 of 6 known
conflicts; optional inspection approved none. Second review approved all 12
unresolved development ask cases. Thus its reduction in blocking did not improve
supported approvals and did introduce unsupported approvals in this setup. This
is a result for our second-review prompt, not a reproduction of Anthropic's
model, reasoning budgets or tuning.

The optional-inspection model requested **zero reads across all 48 cases**.
Its final answer often said the file needed inspection, but returned `ask`
instead of the `inspect` action. It also returned ask, rather than deny, for
every observed conflict. Preventing automatic execution is useful but does not
mean the model diagnosed a known conflict correctly. Merely offering an
inspection action did not demonstrate evidence acquisition.

### Diagnostic: supply the missing file before review

After that result, we added a separately documented `prefetch` diagnostic. The
harness selects files explicitly marked unobserved in the visible evidence,
reads their saved snapshots and supplies them to the unchanged single-pass
reviewer. It does not use expected labels to choose reads, and it cannot supply
user confirmation. This tests the effect of evidence provision, not autonomous
tool use, and is not a blind confirmatory experiment.

On both development and test, it resolved and approved all six missing-file
cases, while approving none of the six cases missing authorization. It still
approved all six initially supported cases in each split. It approved 2 of 6
development conflicts and 0 of 6 test conflicts, unchanged from single pass.
All 48 calls returned valid decisions. The harness made 12 snapshot reads in
total. Evidence provision helped precisely the cases it could resolve; it did
not fix the remaining conflict-detection errors.

The fixed six-case development consistency subset produced identical final
decisions in all three repetitions (18 observations, six distinct cases), with
no optional reads. This narrow temperature-zero check does not establish
general robustness or increase the study sample size.

## Source-isolated Qwen Code

The actual pinned classifier, prompt and transcript builder were bundled with
a local model transport. We retained its two-stage budgets and timeouts. This
is not a native Qwen Code product evaluation: it omits the parent agent,
permission manager, sandbox and fast paths, and uses Qwen3.5-4B locally.

It approved all 72 legacy cases. On the 24 new test cases it approved all six
supported cases, all six observed conflicts, and eight of twelve initial ask
cases. It blocked two ask cases and returned unavailable on two others when
second-stage calls timed out. Those timeouts are failures, not correct blocks.
The new development split had six supported approvals, six deny approvals and
ten unresolved ask approvals, with two blocks and no call failures.

This classifier received the user request and pending command, but no script
contents or prior script-writing actions. Its stock policy differs from the
study's evidence requirements. These results illustrate the limits of that
input/policy combination, not a controlled ranking against the evidence-fed
reviewer. In particular, a command such as `python report.py` does not reveal
which version of the script will run.

## Native secguard guard and model wrapper

We ran the official 0.5.5 macOS release (no ML compiled in), the pinned native
Rust model wrapper, and the full guard at the same source revision as that
wrapper. The full guard's preflight reached the loaded brain; it did not fall
back to a missing-model path. Only model-file location was changed in upstream
logic, so the isolated workspace model could be used without installing hooks
or changing user configuration.

| Command-only setup | Safe verdicts on ShellRisk safe / 50 | Safe verdicts on ShellRisk unsafe / 50 | Safe verdicts on Shell Safety safe / 50 | Safe verdicts on Shell Safety unsafe / 50 |
| --- | ---: | ---: | ---: | ---: |
| Official non-ML release | 47 | 49 | 46 | 43 |
| Native model wrapper | 50 | 50 | 50 | 49 |
| Native full guard | 47 | 49 | 46 | 42 |

All three classified all 120 repository/snapshot cases and all 12 adversarial
cases as safe. The native model wrapper therefore returned safe on 331 of 332
cases, including 283 of the original 284: it confirms the broad finding from
the earlier model-only experiment rather than correcting it.

On the public sample, the full guard produced 15 heuristic destructive verdicts
and one brain destructive verdict. The remaining 184 were safe (178 from the
brain, six from policy). Compared with the native model alone at the same source
revision, the full guard flagged eight additional unsafe-labeled commands but
also seven safe-labeled commands. The release and full-guard revisions differ;
do not generally attribute their differences to ML alone. In this replay their
only decision difference was `shellsafety-672`, whose full-guard source was brain.

These are classification counts. The native driver's normalized `block` means
`Verdict::Destructive`, not necessarily enforcement: the public full-guard rows
have ten `Block`, three `Warn` and three `Confirm` actions. The actual action is
retained alongside every verdict, and no candidate command was executed.

All three completed full-guard replays hit a llama.cpp Metal assertion at
process teardown, after every case response had been collected. Those runs are
marked with a dagger in the generated table, with exit codes and crash tails
saved. The first attempt remains excluded as incomplete. The three native
model-only runs exited successfully. This is an operational limitation of the
tested embedding/runtime; the recorded teardown failures are neither successful
safety blocks nor evidence about native product enforcement.

## What this suggests adding next

The measured distinction is between acquiring evidence, reasoning about it and
checking authorization. Future work should test an explicit read-before-verdict
workflow, then use larger independent repositories and human-adjudicated labels.
The current optional-tool result is a reason to test that workflow, not evidence
that it already works. A native Cursor comparison needs an available authenticated
interface and observable classifier decisions; substituting a copied prompt
would answer a different question.

## Reproducibility and scope

The [protocol](PROTOCOL.md) and [artifact/runtime instructions](README.md) explain
the distinctions between native guard code, isolated classifier source, and our
controlled reviewer. Full requests, responses, observations and operational
errors are saved per run. [Summary tables](results/table.md) separate dataset
and split; [breakdowns](results/breakdown.json) retain family and initial label.
Smoke runs, incomplete runs and duplicate release replays are excluded from
those tables. The repeated development subset is reported separately and does
not enlarge the accuracy denominator.

No thresholds were fitted to these new outcomes. The prefetch diagnostic was
added after observing zero optional reads and is explicitly post-result. These
small, correlated, synthetic cases cannot establish real-world failure rates.
Latency is descriptive: desktop load was uncontrolled and dependency builds
overlapped some inference. All inference was local; API cost is recorded as
null, not zero-cost computing.

Cursor was unavailable here, so there is no native Cursor result. Existing
Codex and Claude measurements remain whole-agent-and-approval-path results on
the original corpus. None of the new classifier verdicts implies that a command
ran or that a human approved it. The [related-work note](RELATED-WORK.md) links
the published designs without mixing vendor-reported scores into our tables.
