# Shell command approval study

This is the reproducibility repository for the staging article [“Can a small local model decide whether a shell command is safe?”](https://nexus-website.nexusbench.workers.dev/blog/shell-classifier/). It contains the test cases, saved results, methods, figures, and scripts. The cases use synthetic repositories and fake credentials.

Start with the [study index](experiments/shell-safety/STUDY.md) and the [classifier/evidence extension](experiments/shell-safety/v3/README.md). The extension preserves the original 72 cases and adds 48 synthetic evidence conditions. You can inspect them against the [approval rules](experiments/shell-safety/v2/POLICY.md).

The measured counts describe these test setups, not real-world failure rates. The six Node startup cases per native provider have been rerun and checked; the native chart includes all 72 cases per provider. Independent human label review remains open.

The Python requirements are in the study directories. Local model files are downloaded separately using the documented artifact lists; they are not included here. Native Codex and Claude reruns require your own subscription sign-ins. The native scripts operate only on generated disposable fixtures. Review the scripts and use fake credentials before running them.

This copy comes from the study at source revision `dc9dc4694abf01fbabd97f23a209fb752ca3fff1`, with two experiment helper modules and public feedback links included here. The source repository itself is private; this copy contains the study files needed for inspection and reproduction.
