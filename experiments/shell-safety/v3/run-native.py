"""Native follow-ups after recording the first replay's teardown failure."""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for arm, name in [('full', 'full'), ('model-only', 'native-model')]:
    for dataset in ['v3', 'public', 'adversarial']:
        run_id = f'secguard-{name}-{dataset}-recorded'
        subprocess.run([sys.executable, str(HERE / 'run-secguard.py'), arm,
            '--dataset', dataset, '--run-id', run_id], check=True)
subprocess.run([sys.executable, str(HERE / 'score.py')], check=True)
