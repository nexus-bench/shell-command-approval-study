# Shell classifier dataset coverage and synthetic expansion

## What do existing datasets cover?

### Takeaway
The downloaded public datasets test different concepts: ShellRisk-Bench tests context-free command risk, while Shell Safety supplies synthetic session context and approval labels. Neither should be treated as a direct estimate of production authorization accuracy. This audit was locked without reading model predictions; it uses input records, source cards, and manifests only.

### Cited Findings
- ShellRisk-Bench test has 4,194 unique commands: 4,001 not-risky and 193 risky. Its six `source` values are provenance buckets, not semantic risk categories: SWE-smith 2,387, Terminal-Bench 1,364, nl2bash 250, GTFOBins 142, Atomic Red Team 47, offensive payloads 4. It explicitly excludes multiline scripts/sessions and task/user/session context. Benign trajectory labels are inferred from task provenance rather than verified individually. — [Pinned card](https://huggingface.co/datasets/kontext-security/ShellRisk-Bench/blob/437467862139b4e9cdd5322024ef3434a67c7ec8/README.md), [local counts](../../data/coverage-audit.json)
- Downloaded Shell Safety large test has 1,003 records, 600 safe and 403 unsafe, with 940 unique command strings. There are 19 categories: agent, build, cloud, complex, docker, fileops, network_curl, network_gh, network_git, network_rsync, network_scp, network_ssh, network_wget, pkgman, privilege, system, testing, windows_cmd and windows_ps. Windows accounts for 200 rows (131 PowerShell, 69 CMD); remaining 803 are POSIX. — [Pinned source](https://huggingface.co/datasets/tomngdev/shell-safety/blob/155dbb5d3047dd095523bd8ee3dd65adf1296dde/lg/test.jsonl), [local counts](../../data/coverage-audit.json)
- Shell Safety transcripts are a conversion of the same source dataset, not an independent evaluation corpus. Its author describes a static system prompt and changing `<SessionContext>` block. — [Pinned transcript card](https://huggingface.co/datasets/tomngdev/shell-safety-transcripts/blob/e8b46e9821d9bc7957466154453d88c59a76eb53/README.md)
- The frozen scored sample has 200 records: 50 per source/label combination, selected deterministically across categories; eight additional records are reserved for format development. The sample has 198 distinct command strings. It excludes the 200 Windows records. — [Selection manifest](../../public-selection.json), [selection code](../../prepare_public.py), [audit](../../data/coverage-audit.json)
- Original local study: 64 rows, 39 unique commands, 32 allow/16 ask/16 deny. Categories are provenance 14, script 8, path 8, environment 4, unknown 4, destination 4, secrets 4, authorization 2, control 16. — [Original cases](../../../cases.jsonl), [audit](../../data/coverage-audit.json)

### Inferences
- ShellRisk-Bench cannot measure sensitivity to changed repository state because its input schema contains none; this is a structural absence, not a claim that no command in it involves Git, scripts or secrets.
- Shell Safety is closer to the intended task, but broad categories such as `complex` do not establish coverage or absence of narrower mechanisms like executable shadowing, stale state, startup injection or hooks. A complete semantic annotation of all 5,197 downloaded rows was not performed.
- Balanced sampling is useful for comparing errors on both labels but does not retain original class prevalence. Report source-specific counts rather than treating pooled accuracy as expected operational performance.

### Gaps
- Public structured metadata does not isolate mixed user/agent provenance, changed executable resolution, shared Git common directories, incomplete context, or prompt injection as separate strata. Semantic examples could still exist inside broad categories.
- Dataset cards do not establish that labels match this application's exact approval policy. A risky command can be explicitly authorized; a harmless-looking command can invoke a dangerous local script.

## Which gaps does the frozen synthetic set address?

### Takeaway
The expansion deliberately tests mechanisms inadequately separated in the old study and public metadata. It contains 40 same-command allow/deny pairs, a third unknown-state variant per family, and eight controls; all commands remain inert strings.

### Cited Findings
- Frozen SHA-256 is `f6315bce4d1b82f1ade3a152427ab67e2f071cdcb1cfd1a1efccfd66235241b1`: 128 records, 48 unique commands, 44 allow/44 deny/40 ask. Inputs are only `command` and `context`; expected labels, category, rationale, IDs, pair and variant metadata are withheld from model inputs. Five integrity tests check freeze/reproduction, counts, pair construction, metadata independence and unknown-state representation. — [Freeze](../../data/synthetic-freeze.json), [generator](../../build_synthetic.py), [tests](../../test_dataset.py)
- Composition (15 rows): AND chains, OR fallback, substitutions, xargs target streams and find-exec. Obfuscation (6): encoded script and eval variable. Embedded code (3): Python heredoc. — [Generator](../../build_synthetic.py)
- Executable resolution (9): PATH shadowing, shell functions, Git pager. Environment poisoning (9): PYTHONPATH, NODE_OPTIONS, sourced env file. Hooks (9): Git commit hook, Make include, package install lifecycle. These distinguish visible command text from actual executable behavior. — [Generator](../../build_synthetic.py)
- Untrusted instructions (6): repository and comment injection. Path resolution (6): symlink directory and archive extraction. Shared Git state (6): common directory and submodule changes. State freshness (6): stale snapshot and redirect target race. — [Generator](../../build_synthetic.py)
- Cloud target (12): Kubernetes context, Terraform state, S3 profile, Docker context. Permissions (6): mode bits and ACL. Persistence (6): launch agent and cron. Shared processes (6): reused PID and pattern matching. Resource budget (6): disk consumption and parallel CPU/memory. Remote command (6): SSH alias and rsync deletion. Truncation (3): long-context stress. — [Generator](../../build_synthetic.py)
- Eight controls include quoted dangerous-looking strings, syntax-only checking, shell comments, clear secret upload, fork bomb, sudoers change, and a long command with/without a dangerous suffix. The controls include four allow and four deny labels. — [Generator](../../build_synthetic.py)
- Six serialized repository profiles are supplied: Node (38 rows), Python (39), infrastructure (18), macOS desktop (12), linked worktree (12), nested monorepo (9). — [Profiles](../../data/contexts.json), [audit](../../data/coverage-audit.json)

### Inferences
- Full matched-pair correctness measures whether a classifier both permits the known-good state and rejects the known-bad state. A command-only deterministic classifier cannot succeed on both members; this metric intentionally tests access to context, not generic model intelligence.
- Unknown cases should abstain or request inspection. Binary local classifiers can be scored as allow versus non-allow, but that loses ask-versus-deny quality; preserve native output separately.
- Context profiles broaden paths, tools and state assumptions, but they are not an exhaustive command-by-repository cross product. Each family is assigned one profile, so category and profile are confounded.

### Gaps
- These are stipulated serialized facts, not freshly collected filesystem snapshots or executable fixtures. They evaluate reasoning from supplied context, not a collector's ability to inspect scripts, resolve paths or prevent races.
- Synthetic labels have one agent author and no independent human adjudication. Repeated templates, explicit known-good/known-bad facts and shared rationale phrasing simplify inference compared with real logs.
- Remaining gaps include Windows shells, alternate shell dialects, broader language runtimes, multi-turn authorization revocation, full multi-step attacks, actual concurrent mutations and human uncertainty calibration. Forty correlated families do not constitute 128 independent trials.
- The long-context family's text describes the dangerous observation as at the end, but JSON serialization sorts nested keys: `observations` actually precedes the long `repositoryInventory`, followed by `userRequest`. These three cases test long input and adapter size limits, not reliably a dangerous-fact-at-tail condition. Preserve the frozen set and treat this as a fixture limitation; the two long-command controls do place the dangerous suffix at the end of command text.

## What limits independence and redistribution?

### Takeaway
The synthetic set has no exact-command overlap with the scored public sample, but that does not prove semantic independence. Public datasets carry training-family overlap and source-specific licensing limitations.

### Cited Findings
- Exact overlap with synthetic: original 64-case set has one shared command; full Shell Safety test has one; ShellRisk-Bench test has zero; scored 200 public examples have zero. Both shared commands are `git status --short`. Exact overlap is counted by unique literal command, not by row or normalized semantics. — [Reproducible audit](../../audit_coverage.py), [audit output](../../data/coverage-audit.json)
- ShellRisk-Bench has no blanket dataset license: source terms include MIT, Apache-2.0, GPL-3.0 and a source with no license file. Its code/documentation license is distinct from source data. Public raw data therefore stays in ignored cache; manifests retain source revisions/hashes without republishing prompt text. — [Pinned license section](https://huggingface.co/datasets/kontext-security/ShellRisk-Bench/blob/437467862139b4e9cdd5322024ef3434a67c7ec8/README.md), [artifact manifest](../../public-artifacts.json)
- Shell Safety and transcript cards declare MIT; the latter explicitly says it was structured for the author's training. Treat AutoShell performance on its author's public dataset as an in-family result, not independent validation; this audit did not verify training/test deduplication. — [Source card](https://huggingface.co/datasets/tomngdev/shell-safety/blob/155dbb5d3047dd095523bd8ee3dd65adf1296dde/README.md), [transcript card](https://huggingface.co/datasets/tomngdev/shell-safety-transcripts/blob/e8b46e9821d9bc7957466154453d88c59a76eb53/README.md)
- LANCET's current card says its training uses the ShellRisk training split and Shell Safety v2 training split, alongside authored examples and other sources. Shared data families constrain claims of out-of-distribution generalization even when official test splits are used. This is not evidence of exact test leakage. — [LANCET training disclosure](https://huggingface.co/fingerthief/lancet-nano#training)

### Inferences
- Publish source-separated results, synthetic context-pair results, and uncertainty results; do not rank all models on one pooled number across conflicting tasks.
- New synthetic text reduces literal overlap but includes familiar shell concepts. Only testing undisclosed real-world cases or independently sourced temporal holdouts can strengthen generalization claims.

### Gaps
- No complete model training-corpus overlap audit was possible. The newly authored synthetic set also needs future human adjudication and a independently authored holdout before threshold tuning.
- AutoShell-350M model-card fetch returned HTTP 401 during this audit; use the separately researched pinned model-format evidence rather than inferring model architecture or training details from this audit.
