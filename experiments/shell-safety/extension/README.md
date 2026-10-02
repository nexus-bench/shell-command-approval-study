# Shell classifier study: public datasets and repository state

See the [reviewed fixture follow-up](../v2/README.md) and [historical errata](../v2/ERRATA.md),
including the invalid Node `--version` preload scenario. Original data/results are preserved.

Read the [study report](reports/Shell%20classifier%20dataset%20expansion.md).
This extends the [original 64-case study](../README.md) without changing its data
or predictions. Research only; application approval behavior is unchanged.

## Artifacts

- [Protocol](LOCAL-PROTOCOL.md), [download lock](public-artifacts.json),
  [public sample selection](public-selection.json).
- [Frozen synthetic set](data/synthetic.jsonl), [repository profiles](data/contexts.json),
  [freeze manifest](data/synthetic-freeze.json), [coverage audit](data/coverage-audit.json).
- [Source research and coverage notes](research_notes/Shell%20classifier%20dataset%20expansion/).
- [Generated results table](results/local-table.md), [detailed summary](results/local-summary.json),
  per-example JSONL predictions and run metadata in [results](results/).
- [Native smoke evidence](results/native-smoke.json) and [exact native setup](native-setup.json).
- [Paired native approval-path pilot](NATIVE-PILOT.md) using the same command against
  a regular file and a symlink to user notes.
- [Full native end-to-end sweep](NATIVE-FULL.md) across the 72 frozen v2 cases,
  with per-case outcomes and separate counts for proposals, reviews and tools.

Public commands stay in ignored `.experiments/shell-safety/public/` because source
licenses differ. Their revisions, source row IDs, command hashes, request hashes,
and prediction outputs are versioned here. Synthetic inputs are fully included.
No evaluation command is executed; the native smoke executes only a harmless
marker write in disposable fixtures.

## Reproduce

Run from the repository root. First follow the original study's model download
and pinned Python environment setup. Add the Parquet reader, verify/download
the pinned public data, and reconstruct the exact sample:

```sh
uv pip install --python .experiments/shell-safety/venv/bin/python -r experiments/shell-safety/extension/requirements.txt
.experiments/shell-safety/venv/bin/python experiments/shell-safety/extension/fetch_public.py
.experiments/shell-safety/venv/bin/python experiments/shell-safety/extension/prepare_public.py
python3 experiments/shell-safety/extension/audit_coverage.py
```

Preserve the supplied `results` directory before making a fresh run. `run_local.py`
refuses to overwrite predictions. It accepts `--resume` only for an exact prefix
with a matching experiment fingerprint; older historical files lack that fingerprint.
`run_remaining.py` skips complete arms by exact IDs, so it is a recovery helper,
not a command that repeats an already completed study.

Start the CPU server in a separate terminal:

```sh
llama-server -m .experiments/shell-safety/AutoShell-0.8B-GGUF/AutoShell-0.8B-Q8_0.gguf --host 127.0.0.1 --port 18765 -c 4096 -np 1 -t 4 -ngl 0 --no-warmup
```

For a fresh run with the old result files moved aside, run these sequentially:

```sh
.experiments/shell-safety/venv/bin/python experiments/shell-safety/extension/run_local.py .experiments/shell-safety/public/public-format-dev.jsonl autoshell-native --redact --output experiments/shell-safety/extension/results/public-format-dev-autoshell-native.jsonl
.experiments/shell-safety/venv/bin/python experiments/shell-safety/extension/run_local.py .experiments/shell-safety/public/public.jsonl lancet --redact --output experiments/shell-safety/extension/results/public-lancet.jsonl
.experiments/shell-safety/venv/bin/python experiments/shell-safety/extension/run_local.py .experiments/shell-safety/public/public.jsonl autoshell-command --redact --output experiments/shell-safety/extension/results/public-autoshell-command.jsonl
.experiments/shell-safety/venv/bin/python experiments/shell-safety/extension/run_remaining.py
python3 experiments/shell-safety/extension/summarize_local.py
python3 experiments/shell-safety/extension/render_tables.py
python3 experiments/shell-safety/extension/analyze_errors.py
python3 -m unittest discover -s experiments/shell-safety/extension -p 'test_*.py'
python3 -m unittest discover -s experiments/shell-safety -p 'test_*.py'
```

Stop the CPU server with Ctrl-C. Model dependencies and weights remain ignored.
The bundled LANCET runtime can create `:memory:.ses` in the working directory;
that telemetry file is not study data.

Native probes require subscription authentication and separate pinned dependencies.
Their reproduction commands and interpretation limits are in the
[native research note](research_notes/Shell%20classifier%20dataset%20expansion/native_classifiers.md).
Do not substitute corpus commands into that execution harness.
