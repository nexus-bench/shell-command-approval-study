"""Run remaining frozen local arms sequentially; dataset text is never executed."""
import subprocess
import sys
import json
from pathlib import Path

HERE = Path(__file__).parent

for corpus, dataset, arms in [
    ('public', '.experiments/shell-safety/public/public.jsonl', ['autoshell-native', 'autoshell-expanded']),
    ('synthetic', str(HERE / 'data/synthetic.jsonl'), ['lancet', 'autoshell-command', 'autoshell-native', 'autoshell-expanded']),
    ('public', '.experiments/shell-safety/public/public-shellsafety.jsonl', ['autoshell-format-only']),
]:
    for arm in arms:
        output = HERE / 'results' / f'{corpus}-{arm}.jsonl'
        if output.exists():
            saved = [json.loads(line) for line in output.read_text().splitlines()]
            expected = [json.loads(line) for line in Path(dataset).read_text().splitlines()]
            if [r['id'] for r in saved] == [r['id'] for r in expected]:
                print(f'Skipping complete {output.name}', flush=True)
                continue
        command = [sys.executable, str(HERE / 'run_local.py'), dataset, arm,
                   '--output', str(output)]
        if output.exists():
            command.append('--resume')
        if corpus == 'public':
            command.append('--redact')
        subprocess.run(command, check=True)
