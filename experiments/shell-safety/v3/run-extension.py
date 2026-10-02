"""Run the remaining declared arms serially; never execute candidate commands."""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
commands = [
    ['run.py', 'two-stage', '--dataset', 'evidence-v3', '--run-id', 'two-stage-v3'],
    ['run.py', 'inspect', '--dataset', 'evidence-v3', '--run-id', 'inspect-v3'],
    ['run.py', 'inspect', '--dataset', 'evidence-v3', '--split', 'dev', '--limit', '6', '--repeat', '3', '--run-id', 'inspect-consistency'],
]
for arm, name in [('full', 'full'), ('model-only', 'native-model')]:
    for dataset in ['v3', 'public', 'adversarial']:
        commands.append(['run-secguard.py', arm, '--dataset', dataset,
                         '--run-id', f'secguard-{name}-{dataset}'])
for command in commands:
    subprocess.run([sys.executable, str(HERE / command[0]), *command[1:]], check=True)
subprocess.run([sys.executable, str(HERE / 'score.py')], check=True)
