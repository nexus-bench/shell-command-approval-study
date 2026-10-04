# Qwen3.5 local baseline

This [Qwen study arm](PROTOCOL.md) tests a general-purpose local model on the same 72 authored repository cases as the other local models. It was added after the earlier results were inspected, so it is not a new blind benchmark. The candidate commands were passed as text; none were executed.

## Setup

- Model: [Qwen3.5-4B Q4_K_M GGUF](https://huggingface.co/unsloth/Qwen3.5-4B-GGUF), revision `e87f176479d0855a907a41277aca2f8ee7a09523`, SHA-256 `00fe7986ff5f6b463e62455821146049db6f9313603938a70800d1fb69ef11a4`. Weights are downloaded locally and are not committed.
- Runtime: existing llama.cpp Metal build, version `4 (3a5b16d)`, on an Apple M1 Pro with 16 GB memory. Server settings: 4096 context, one slot, four CPU threads, 99 GPU layers, Jinja chat template, no warmup. The request used temperature 0, seed 20260930, non-thinking chat template setting, and a grammar constrained to `allow`, `deny`, or `ask`.
- Input: the command, the user's task, and the saved `full` repository evidence. The v2 research policy was adapted to three output labels. No expected label or author-written effect summary was included.

The [runner](run.py), [scorer](score.py), [per-case development outputs](results/dev.jsonl), [per-case test outputs](results/test.jsonl), and [summary](results/summary.json) are saved here. The protocol and runner were committed before inference. All 72 responses had valid labels and stopped normally.

## Results

Approvals mean Qwen answered `allow`. Each test label has 12 cases.

| Expected label | Approved | Asked | Denied |
| --- | ---: | ---: | ---: |
| Allow | 4 | 8 | 0 |
| Deny | 2 | 10 | 0 |
| Ask | 6 | 6 | 0 |

The model agreed with the exact expected label on **10/36** test cases. It never answered `deny`, even on the 12 cases with an observed conflict. Its `ask` answer would still stop automatic execution, but it does not distinguish a known conflict from missing information. On the development cases, it approved **12/14 allow**, **4/10 deny**, and **6/12 ask** cases. The median end-to-end response time was **1.99 seconds** on the test cases, excluding model loading and evidence collection.

The result describes this 4-bit model, prompt, grammar, saved evidence, and Metal runtime. Qwen is larger than AutoShell and the original AutoShell run used CPU inference. The counts can be placed beside AutoShell's approval counts; the speed figures are not a controlled comparison. The cases were generated and labeled with GPT-6 Astra and lack independent human adjudication, so the numbers do not estimate real-world failure rates.

## Reproduce

Run from the repository root in a separate checkout. The runner uses Python's standard library. Install a Metal-enabled llama.cpp build matching `3a5b16d` to reproduce the recorded runtime; other builds or hardware may change outputs and timing.

Download the pinned model, then verify its SHA-256 against the value above before starting inference:

```sh
mkdir -p .experiments/shell-safety/general-baseline
curl --fail --location --output .experiments/shell-safety/general-baseline/Qwen3.5-4B-Q4_K_M.gguf https://huggingface.co/unsloth/Qwen3.5-4B-GGUF/resolve/e87f176479d0855a907a41277aca2f8ee7a09523/Qwen3.5-4B-Q4_K_M.gguf
shasum -a 256 .experiments/shell-safety/general-baseline/Qwen3.5-4B-Q4_K_M.gguf
```

Start the server in one terminal. Port 18766 must be free; the secguard experiment also uses it.

```sh
llama-server -m .experiments/shell-safety/general-baseline/Qwen3.5-4B-Q4_K_M.gguf --host 127.0.0.1 --port 18766 -c 4096 -np 1 -t 4 -ngl 99 --jinja --no-warmup
```

In another terminal, archive the published results before running; the runner refuses to overwrite existing prediction files. Choose an unused archive directory if repeating this procedure.

```sh
mv experiments/shell-safety/general-baseline/results .experiments/shell-safety/general-baseline/published-results
python3 experiments/shell-safety/general-baseline/run.py dev
python3 experiments/shell-safety/general-baseline/run.py test
python3 experiments/shell-safety/general-baseline/score.py
```

Compare the new summary with the archived one. These commands send candidate commands as text to the local model; they do not execute them.
