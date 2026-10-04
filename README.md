# Shell command safety study

This is a public copy of the study behind [“Can a small local model decide whether a shell command is safe?”](https://nexus-website.nexusbench.workers.dev/blog/shell-classifier/). It contains the test cases, saved results, methods, figures, and scripts. The cases use synthetic repositories and fake credentials.

Start with the [study index](experiments/shell-safety/STUDY.md). You can [inspect all 72 repository cases](experiments/shell-safety/v2/data/cases.jsonl) against the [approval rules](experiments/shell-safety/v2/POLICY.md). The [open follow-ups](experiments/shell-safety/FOLLOW-UPS.md) include full secguard guard verification and independent human label review.

The published counts describe these test setups. They do not estimate real-world failure rates. The corrected Node startup rerun is complete; the native results include all 72 cases per provider, including the six verified Node cases.

The Python requirements are in the study directories. Local model files are downloaded separately using the documented artifact lists; they are not included here. Native Codex and Claude reruns require your own subscription sign-ins. The native scripts operate only on generated disposable fixtures. Review the scripts and use fake credentials before running them.

This copy comes from the study at source revision `dc9dc4694abf01fbabd97f23a209fb752ca3fff1`, with two experiment helper modules and public feedback links included here. The source repository itself is private; this copy contains the study files needed for inspection and reproduction.

## Verify saved results

From the repository root, these Python standard-library checks replay committed results without downloading models, executing candidate commands, or contacting a provider:

```sh
python3 -m unittest discover -s experiments/shell-safety -p 'test_*.py'
python3 -m unittest discover -s experiments/shell-safety/v2 -p 'test_*.py'
python3 -m unittest discover -s experiments/shell-safety/extension -p 'test_*.py'
python3 -m unittest discover -s experiments/shell-safety/additional -p 'test_*.py'
```

The extension public-request hash check and two Kestrel parity checks skip when their pinned downloads are absent. Follow the [public-data setup](experiments/shell-safety/extension/README.md) and [additional-model setup](experiments/shell-safety/additional/README.md) to enable those checks. A skipped check is not a verified result.

## Rerun experiments

Use a separate checkout to preserve the published outputs. Setup and inference instructions are in the [repository study](experiments/shell-safety/v2/README.md#reproduce), [additional models](experiments/shell-safety/additional/README.md), [Qwen baseline](experiments/shell-safety/general-baseline/README.md#reproduce), and [native-agent experiment](experiments/shell-safety/extension/NATIVE-FULL.md#evidence-and-reproduction). Native runs require sign-ins and execute commands in generated fixtures; they are separate from the offline checks above.

This is an exploratory study with agent-generated labels, pending independent human review. See the [limitations and follow-ups](experiments/shell-safety/FOLLOW-UPS.md).

## License

Licensed under the [Apache License 2.0](LICENSE).
