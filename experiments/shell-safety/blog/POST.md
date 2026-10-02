# Can a small local model decide whether a shell command is safe?

A command can look harmless while doing something the user never asked for. `bash verify.sh` might run a test, or the script might read a credential. To decide whether to run it, an assistant needs to know what the command will do, what is in the repository, and what the user allowed.

We tested five small local models: **AutoShell-0.8B, LANCET Nano, ModernBERT-bash-classifier, Kestrel, and secguard-guard 0.8B**. We also tested **native Codex and Claude agent paths**, including their command approval steps. The small models did not offer a dependable replacement for those tool paths. At a lenient setting, AutoShell approved some commands that conflicted with the task. At a strict setting, it blocked most commands that were justified. The Codex and Claude paths let more justified commands run in their separate test, but they too ran commands when important facts were missing.

## What we tested

We tried 200 examples from two public command test sets. We also built 72 small, separate Git repositories with real files. Half were used to choose a model setting; the other half tested it on different kinds of commands. The test half had 12 cases in each of three groups:

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
| LANCET Nano, Kestrel, secguard | The command alone. They could not see the contents of a script named in it. |
| ModernBERT | The command and current directory, but no file contents. |
| Native Codex and Claude | The command, task, and a copy of the collected information in the request. These are agents with tool approval steps. |

The native interfaces we used did not provide a separate approval verdict for every candidate command. We therefore measured whether the command reached the tool after the agent's choice and its approval process. These setups use different information and rules, so the figures describe the tested paths rather than a ranking of model designs.

## Repository results

![Approved commands by label in the repository test. The chart separates AutoShell, which received repository evidence, from models that received a command or a command plus directory.](figures/repository-decisions.png)

With our test instructions and collected repository information, AutoShell approved **8 of 12 allow cases**, **4 of 12 deny cases**, and **7 of 12 ask cases**. A stricter approval cutoff stopped all 12 deny cases. It also approved only **2 of 12 allow cases** and still approved **2 ask cases**.

The command-only models could not tell apart two cases where the command was identical but the file it would run had changed. That is a limit of the information they received, not proof that they could never reason about files.

## Results on public test sets

![Unsafe approvals in two public test sets. Kestrel approved none of 50 unsafe ShellRisk examples, but 34 of 50 unsafe Shell Safety examples.](figures/dataset-transfer.png)

Kestrel approved none of the 50 unsafe ShellRisk examples we sampled, but approved **34 of 50** unsafe examples from Shell Safety. A strong result on one small sample did not carry over to the other.

The secguard setup returned “safe” on **283 of 284** cases, including plainly destructive commands. We have not established whether the problem lies with the model file or how we ran it, so we do not treat that result as a judgment on the model itself. [Rechecking that setup is an open task](../FOLLOW-UPS.md).

## Codex and Claude command paths

![Commands that reached the native Codex and Claude tools, grouped by allow, deny, and ask labels. Six Node startup cases per provider are excluded because the tool did not receive the required startup setting.](figures/native-path.png)

We ran all 72 cases once through each native path. For the chart, we left out six Node cases per provider: our runner did not pass a required startup setting to the shell, so those runs did not test the stated conditions. We have [prepared a checked rerun](../extension/NATIVE-FULL.md#node-startup-rerun-preflight) and will count those cases only after it passes.

Among the remaining cases, the command reached the tool in **24 of 24 allow cases for Codex** and **23 of 24 for Claude**. No command reached the tool in the **20 deny cases** for either provider. But commands also reached the tool in **12 of 22 ask cases** for each provider. The underlying files in many ask cases were harmless; the problem was acting without the evidence our approval rule required.

These counts describe the whole path from an agent's choice through its approval step. An agent might never suggest the command, and Claude does not expose a separate positive classifier decision here. A tool return also does not always show that the command finished successfully. No protected test file changed in this run.

## Speed

![Median local model response times on a logarithmic scale, from 0.024 milliseconds for Kestrel to 3,150 milliseconds for AutoShell with repository information.](figures/latency.png)

On an Apple M1 Pro, the tested local setups took from about **24 microseconds** for the Kestrel Python port to **3.15 seconds** for AutoShell with repository information. They used different inputs and software, so this is a measure of these setups on this computer, not a general speed ranking.

## Conclusion

AutoShell is an important step toward command checks that use the user's task and repository evidence while still running locally. Its decisions need to improve: the lenient setting approved some commands that conflicted with the task or lacked enough evidence, while the strict setting blocked most supported commands. The Codex and Claude paths were more useful on these cases, but they too let commands through when the study called for more information. When a needed fact is missing, the right next step is to check it or ask.

To be clear, these tests do not give a real-world failure rate for any model or tool path. They do point to a need for better local classifiers that can check a command against verified context without depending on a proprietary agent's approval system. This was a small study using cases we wrote ourselves. Another agent reviewed the labels, but people did not independently judge every case. [See all 72 cases separately](../CASE-REVIEW.md) and tell us where you disagree.

*Get the [full study on GitHub](../STUDY.md) to reproduce it yourself. We'd love your feedback.*
