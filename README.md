# Shell command approval study

This is a public copy of the study behind [“Can a small local model decide whether a shell command is safe?”](https://nexus-website.nexusbench.workers.dev/blog/shell-classifier/). It contains the test cases, saved results, methods, figures, and scripts. The cases use synthetic repositories and fake credentials.

Start with the [study index](experiments/shell-safety/STUDY.md). You can [inspect all 72 repository cases](experiments/shell-safety/v2/data/cases.jsonl) against the [approval rules](experiments/shell-safety/v2/POLICY.md). The [open follow-ups](experiments/shell-safety/FOLLOW-UPS.md) include a secguard guard verification and a corrected Node startup rerun.

The published counts describe these test setups. They do not estimate real-world failure rates. The six Node startup cases per native provider remain outside the effect comparison until the prepared rerun is completed and checked.

The Python requirements are in the study directories. Local model files are downloaded separately using the documented artifact lists; they are not included here. Native Codex and Claude reruns require your own subscription sign-ins. The native scripts operate only on generated disposable fixtures. Review the scripts and use fake credentials before running them.

This copy comes from the study at source revision `dc9dc4694abf01fbabd97f23a209fb752ca3fff1`, with two experiment helper modules and public feedback links included here. The source repository itself is private; this copy contains the study files needed for inspection and reproduction.
