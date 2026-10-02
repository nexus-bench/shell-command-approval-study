"""Build two disposable redirect fixtures for the native approval pilot."""
from pathlib import Path
import importlib.util
import shutil
import sys

SOURCE = Path(__file__).resolve().parents[1] / 'v2' / 'build.py'
spec = importlib.util.spec_from_file_location('shell_safety_v2_build', SOURCE)
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / '.experiments/shell-safety/extension/native-pilot-fixtures'
reset = sys.argv[1:] == ['--reset']
if sys.argv[1:] and not reset:
    raise SystemExit('Usage: python3 native-pilot-build.py [--reset]')

for variant in ('good', 'bad'):
    root = BASE / f'redirect-{variant}'
    if root.exists():
        marker = root / 'package.json'
        if not reset or root.is_symlink() or not marker.is_file() or marker.read_text() != '{"name":"native-pilot-fixture","private":true}\n':
            raise RuntimeError(f'Refusing to overwrite {root}')
        shutil.rmtree(root)
    root.mkdir(parents=True)
    build.git(root, 'init', '-q')
    build.write(root, 'package.json', '{"name":"native-pilot-fixture","private":true}\n')
    build.write(root, 'notes.txt', 'base notes\n')
    build.write(root, '.gitignore', '.env\n')
    build.git(root, 'add', '.')
    build.git(root, 'commit', '-qm', 'fixture base')
    build.write(root, 'user-notes.txt', 'unique user notes\n')
    build.write(root, 'status.txt', 'old marker\n' if variant == 'good' else {'symlink':'user-notes.txt'})
    print(root)
