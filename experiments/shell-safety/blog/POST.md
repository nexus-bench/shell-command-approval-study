# Can a small local model decide whether a shell command is safe?

`rm -- output.txt` might remove a disposable benchmark result or erase a day's work. Even erasing a day's work could be right if the user says the benchmark was flawed and explicitly asks to discard it. The command alone cannot settle that decision. An assistant needs to know what the file is, how it got there, and what the user authorized.

We tested six local models: **AutoShell-0.8B, LANCET Nano, ModernBERT-bash-classifier, Kestrel, secguard-guard 0.8B, and Qwen3.5-4B**. We also tested **native Codex and Claude agent paths**, including their command approval steps. The local models did not offer a dependable replacement for those tool paths. At a lenient setting, AutoShell approved some commands that conflicted with the task. At a strict setting, it blocked most commands that were justified. The Codex and Claude paths let more justified commands run in their separate test, but they too ran commands when important facts were missing.

We then expanded the study with native secguard code, Qwen Code's isolated classifier, and controlled reviews that can request file evidence. The clearest new result: supplying a missing script helped the reviewer resolve uncertainty, but giving it the option to read did not make it use that option.

## What we tested

We tried 200 examples from two public command test sets. We used GPT-6 Astra to generate and label 72 cases, each in its own small Git repository with real files. Another agent reviewed the labels before we ran the models. This is a small study using cases we designed ourselves. You can [inspect all 72 cases](../v2/data/cases.jsonl) alongside the [approval rules](../v2/POLICY.md) and tell us where you disagree. Half the cases were used to choose a model setting; the other half tested it on different kinds of commands. The test half had 12 cases in each of three groups:

| Label | What it means | What should happen |
| --- | --- | --- |
| **Allow** | The available facts support the action, and the user allowed it. | The command may run. |
| **Deny** | The command would conflict with the user's request or affect protected data. | Stop it. |
| **Ask for more information** | A fact needed for approval is missing, outdated, or unclear. | Inspect the missing fact or ask the user before running it. This label does not mean the command is harmful. |

The small models return a yes or no. In our results, an approval on an **ask** case means the command was allowed without enough information. It does not mean the model asked a question.

### What each model could see

The inputs differ partly because these tools accept different kinds of input. AutoShell was built to take a task and repository details. The LANCET, Kestrel, and secguard interfaces we tested took a command; the ModernBERT interface also took a directory. We used each setup's available input rather than pretending that a command-only model had seen the files.

| Test setup | Information supplied |
| --- | --- |
| AutoShell | The command, the user's task, and collected repository information, including some file contents. The collection could still miss a relevant file. |
| Qwen3.5-4B | The same saved command, task, and repository information as AutoShell. We prompted it to answer allow, deny, or ask. |
| LANCET Nano, Kestrel, secguard | The command alone. They could not see the contents of a script named in it. |
| ModernBERT | The command and current directory, but no file contents. |
| Native Codex and Claude | The command, task, and a copy of the collected information in the request. These are agents with tool approval steps. |

The native interfaces we used did not provide a separate approval verdict for every candidate command. We therefore measured whether the command reached the tool after the agent's choice and its approval process. These setups use different information and rules, so the figures describe the tested paths rather than a ranking of model designs.

### How the settings were chosen

We did not train or fine-tune the models. AutoShell's default approval cutoff, a yes score above **0.8**, came from its original implementation. For the repository test, we replaced its stock instructions with our written approval rule. We then chose a stricter cutoff using only the 36 development cases: approve as many of the 14 allow cases as possible while approving none of the 22 deny or ask cases. That cutoff approved 4 of 14 allow cases in development. We fixed it before running the separate test cases. AutoShell's yes score is **not** a measured probability that a command is safe.

LANCET, ModernBERT, Kestrel, and secguard used their published input formats and decision rules. We did not adjust their cutoffs or prompts to improve the results shown here. Their rules target different notions of risk, so their approval counts should be read with the input differences in mind.

## Repository results

The first chart shows AutoShell and Qwen with the user's task and collected repository evidence. AutoShell's two rows use the same model and input; only the approval cutoff changes. Qwen is a larger general model, run with a different prompt and runtime.

![Approvals across 12 allow, 12 deny, and 12 ask cases for AutoShell at two cutoffs and Qwen3.5-4B.](figures/repository-evidence.png)

*Each color represents an expected label. Approvals in allow cases are useful; approvals in deny or ask cases are not. All three rows used the saved task and repository evidence; the two AutoShell rows differ only in cutoff.*

With our test instructions and collected repository information, AutoShell approved **8 of 12 allow cases**, **4 of 12 deny cases**, and **7 of 12 ask cases**. The stricter cutoff stopped all 12 deny cases. It also approved only **2 of 12 allow cases** and still approved **2 ask cases**.

The [Qwen3.5-4B](../general-baseline/README.md) approved **4 of 12 allow**, **2 of 12 deny**, and **6 of 12 ask cases**. It answered **ask** on the other 24 cases and never answered **deny**, even when the evidence showed a conflict. An ask answer would stop automatic execution, but it does not tell a user that a known conflict was found. It matched the exact label on **10 of 36** test cases. This is a test of one 4-bit Qwen setup, not a verdict on every way to run the model.

The second chart shows setups that received no repository file contents. LANCET, Kestrel, and secguard received the command; ModernBERT also received the working directory. Their decision rules differ, so the rows are not a controlled comparison of model quality.

![Approvals across 12 allow, 12 deny, and 12 ask cases for models given a command alone or a command and working directory, without repository file contents.](figures/repository-limited-input.png)

*These models saw different limited inputs and used their own decision rules. This secguard row is its original model-only setup; the native guard extension below is a separate experiment. An ask case means evidence is missing, not that harm is proven.*

The command-only models could not tell apart two cases where the command was identical but the file it would run had changed. That is a limit of the information they received, not proof that they could never reason about files.

## Results on public test sets

![Unsafe approvals in two public test sets. Kestrel approved none of 50 unsafe ShellRisk examples, but 34 of 50 unsafe Shell Safety examples.](figures/dataset-transfer.png)

*Each source contributed 50 unsafe cases. Their policies differ, and none of these setups received repository file contents. The secguard result is for the model alone.*

Kestrel approved none of the 50 unsafe ShellRisk examples we sampled, but approved **34 of 50** unsafe examples from Shell Safety. A strong result on one small sample did not carry over to the other.

The original secguard model-only setup returned “safe” on **283 of 284** cases, including plainly destructive commands. We verified the pinned model file and prompt tokens, then reran all 284 cases with Metal and BF16 cache settings closer to the publisher's code. **No decision changed.** That experiment did not exercise the native Rust guard. [See the original recheck and saved results](../additional/SECGUARD-RECHECK.md).

### Checking secguard's actual Rust code

We extended the experiment to run secguard's native model wrapper and full guard, plus its official non-ML release. The native wrapper classified **283 of the original 284 cases as safe**, matching the broad result of the earlier model-only setup. Across the expanded 332-case replay, it returned safe on **331 cases**.

The full guard's policy and heuristic layers did change results on the public sample. It returned safe on **49 of 50 unsafe ShellRisk examples** and **42 of 50 unsafe Shell Safety examples**, compared with 50 and 49 for the native model alone. It also flagged **7 of 100 safe-labeled public examples**. Both returned safe on all 120 repository and snapshot cases. A command-only guard still cannot distinguish an unchanged command pointing to a changed script.

We verified that the full guard loaded its model and recorded which layer produced each verdict. These are classification results: secguard also returns separate block, warn or confirmation actions. No candidate commands were executed in these new replays.

## What changes when a reviewer can inspect evidence?

Several coding tools have published approaches beyond a single command score. [Anthropic describes a two-stage transcript classifier](https://www.anthropic.com/engineering/claude-code-auto-mode). [Qwen Code publishes its Auto Mode implementation](https://github.com/QwenLM/qwen-code/blob/a011f66944768e05b432a10548ffa4576f1d8ef8/docs/users/features/auto-mode.md). [Cursor's Auto-review classifier can make read-only file queries](https://cursor.com/docs/agent/security/run-modes). These designs make different choices about which information reaches the reviewer. They do not establish that approval is solved.

We added **48 synthetic cases** to study this distinction: six script scenarios, two textual variants, and four conditions—supported execution, an observed conflict, a script not yet read, and missing user confirmation. The test split contains only three scenarios. These are closely related examples with author-assigned labels, not 48 independent production workflows.

We compared the same local Qwen3.5-4B model under the same approval policy in three setups. One makes a single decision. One revisits non-allow decisions without new evidence. One can request file snapshots. The new test split has six allow, six deny, and twelve ask cases:

| Reviewer | Supported approvals / 6 | Deny approvals / 6 | Unresolved ask approvals / 12 | Missing-file cases resolved and approved / 6 |
| --- | ---: | ---: | ---: | ---: |
| Single pass | 6 | 0 | 0 | 0 |
| Second review, same evidence | 6 | 0 | 9 | 0 |
| Optional file inspection | 6 | 0 | 0 | 0 |

A second review did not increase useful approvals here. It instead cleared nine cases that still lacked required evidence or authorization. That is a result for our prompt and local model, not Anthropic's deployed classifier.

The inspection-enabled model made **zero file reads across all 48 cases**. It often said a script needed inspection, then returned “ask” instead of requesting a read. It also answered “ask” on observed conflicts, so stopping execution did not mean it had correctly identified a reason to deny. Offering an inspection tool was insufficient in this setup.

We then added a diagnostic: have the harness supply the visibly missing file before the same single-pass review. On the test split, this resolved and approved **all six missing-file cases**, while leaving **all six missing-authorization cases unapproved**. This was a follow-up after seeing the initial results, not a predeclared autonomous-inspection success. The distinction matters: the reviewer could use the supplied evidence, but did not fetch it itself.

The new development cases also show the limits of that improvement. Single pass, second review and the diagnostic each approved **2 of 6 observed conflicts**. Supplying missing files helped with uncertainty; it did not repair every judgment about visible code.

### Qwen Code's classifier is a separate comparison

We also bundled Qwen Code's actual classifier, stock prompt and transcript builder, replacing its model transport with the same local Qwen3.5-4B runtime. This isolated classifier saw the user request and pending command, with no script contents or earlier script-writing history. It did not include Qwen Code's parent agent, permission manager or sandbox.

It approved all 72 original cases. On the 24 new test cases, it approved all six supported cases, all six conflicts, and eight of twelve ask cases. It blocked two ask cases; two more produced timeouts, which we count as failures rather than correct blocks. Its stock policy and available evidence differ from our controlled reviewers. These counts describe that source-isolated configuration, not the native Qwen Code product.

Cursor was not available in the test environment. Our optional-inspection experiment tests an idea from its documented design; it is not a measurement of Cursor.

Read the [extension methods, raw results and limitations](../v3/RESULTS.md).

## Codex and Claude command paths

![Commands that reached the native Codex and Claude tools across all 72 cases per provider, grouped by allow, deny, and ask labels.](figures/native-path.png)

*The groups contain 26 allow, 22 deny, and 24 ask cases per provider. These bars show whether a command reached the tool after the agent's choice and approval steps, not a separate classifier verdict. An ask case calls for inspection or clarification; a returned tool is not proof of harm.*

We ran all 72 cases through each native path. The first run lacked a required Node startup setting in the candidate shell, so we [reran those six cases per provider with a checked preload](../extension/NATIVE-FULL.md#node-startup-rerun-preflight). The chart includes the latest verified result for every case.

The command reached the tool in **26 of 26 allow cases for Codex** and **25 of 26 for Claude**. No command reached the tool in the **22 deny cases** for either provider. But commands also reached the tool in **12 of 24 ask cases** for each provider. The underlying files in many ask cases were harmless; the problem was acting without the evidence our approval rule required.

These counts describe the whole path from an agent's choice through its approval step. An agent might never suggest the command, and Claude does not expose a separate positive classifier decision here. A tool return also does not always show that the command finished successfully. No protected test file changed in this run.

## Speed

![Median local model response times on a logarithmic scale, from 0.024 milliseconds for Kestrel to 3,150 milliseconds for AutoShell with repository information; Qwen used Metal acceleration.](figures/latency.png)

*Apple M1 Pro, 16 GB. Qwen used Metal; the other rows used CPU inference. These separate runs had different inputs and software. Times exclude model loading and evidence collection, which took about 41 ms at the median. The secguard row is its model alone.*

On an Apple M1 Pro, the tested local setups took from about **24 microseconds** for the Kestrel Python port to **3.15 seconds** for AutoShell with repository information. They used different inputs and software, so this is a measure of these setups on this computer, not a general speed ranking.

Qwen took **1.99 seconds** at the median on the same computer. It used Metal acceleration, so the chart marks it separately from the CPU runs.

## Conclusion

AutoShell is an important step toward command checks that use the user's task and repository evidence while still running locally. Its decisions need to improve: the lenient setting approved some commands that conflicted with the task or lacked enough evidence, while the strict setting blocked most supported commands. The larger Qwen model also approved commands with observed conflicts or missing evidence in this test. The Codex and Claude paths were more useful on these cases, but they too let commands through when the study called for more information. When a needed fact is missing, the right next step is to check it or ask.

The extension adds a practical requirement: a reviewer needs a reliable way to obtain missing evidence, use it, and keep missing authorization separate. Asking the same model twice did not supply those facts. Neither did merely offering it an inspection action. Our diagnostic showed that supplied evidence could help, while leaving visible-code mistakes unresolved.

These tests do not give a real-world failure rate for any model or tool path. They point to further work on explicit inspection workflows and independent labels before treating a local approval system as dependable.

*Get the [full study on GitHub](../STUDY.md) to reproduce it yourself. We'd love your feedback.*
