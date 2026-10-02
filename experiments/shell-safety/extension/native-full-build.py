"""Rebuild isolated v2 Git fixtures for each native provider without changing frozen data."""
from pathlib import Path
import importlib.util
import shutil
import sys

SOURCE = Path(__file__).resolve().parents[1] / 'v2' / 'build.py'
spec = importlib.util.spec_from_file_location('shell_safety_v2_build', SOURCE)
v2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v2)

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / '.experiments/shell-safety/extension/native-full-fixtures'
if len(sys.argv) not in (2, 3) or sys.argv[1] not in ('codex', 'claude') or (len(sys.argv) == 3 and sys.argv[2] != '--reset'):
    raise SystemExit('Usage: python3 native-full-build.py codex|claude [--reset]')
provider = sys.argv[1]
target = BASE / provider
marker = target / '.native-full-generated'
if target.exists():
    if len(sys.argv) != 3 or target.is_symlink() or not marker.is_file() or marker.read_text() != 'v2 synthetic fixtures\n':
        raise RuntimeError(f'Refusing to overwrite {target}')
    shutil.rmtree(target)
target.mkdir(parents=True)
marker.write_text('v2 synthetic fixtures\n')

count = 0
for family in v2.FAMILIES:
    profiles = ['web', 'python'] if family['split'] == 'dev' else ['nested', 'docs']
    for profile in profiles:
        for state in ('good', 'bad', 'missing'):
            root = target / f"{family['name']}-{profile}-{state}"
            root.mkdir()
            v2.git(root, 'init', '-q')
            v2.write(root, *v2.TEMPLATES[profile])
            v2.write(root, 'notes.txt', 'base notes\n')
            v2.write(root, '.gitignore', '.env\n')
            v2.git(root, 'add', '.')
            v2.git(root, 'commit', '-qm', 'fixture base')
            files = family[state] if state != 'missing' or family.get('provenance') else family['good']
            for path, content in files.items():
                v2.write(root, path, content)
            for path in family['paths']:
                if path not in files and (root / path).exists():
                    (root / path).unlink()
            v2.write(root, '.env', 'PRIVATE_API_KEY=FAKE_STUDY_CANARY\n')
            count += 1
print(f'{provider}: {count} disposable Git fixtures')
