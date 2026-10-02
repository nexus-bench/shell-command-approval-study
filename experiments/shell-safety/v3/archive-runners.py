"""Keep exact runner revisions referenced by saved runs."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
current = (HERE / 'run.py').read_text()
previous = current.replace(
    'observed = {i["path"] for i in inspections if "content" in i and\n                i == inspect(case, i["path"])}',
    'observed = {i["path"] for i in inspections if "content" in i}')
sources = [current, previous, (HERE / 'run-secguard.py').read_text()]
archive = HERE / 'sources'
archive.mkdir(exist_ok=True)
for source in sources:
    digest = hashlib.sha256(source.encode()).hexdigest()
    (archive / f'{digest}.py').write_text(source)
for path in (HERE / 'results').glob('*/meta.json'):
    meta = json.loads(path.read_text())
    digest = meta['runner_sha256']
    if not (archive / f'{digest}.py').exists():
        print(f'Historical runner source not archived: {path.parent.name} ({digest})')
print('Archived available runner revisions; original metadata remains unchanged.')
