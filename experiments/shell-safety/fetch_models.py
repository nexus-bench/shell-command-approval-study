"""Download public study artifacts only; no tokens or remote code execution."""
import hashlib
import json
import pathlib
import urllib.request

ROOT = pathlib.Path('.experiments/shell-safety')
REPOS = ['tomngdev/AutoShell-350M-GGUF', 'tomngdev/AutoShell-0.8B-GGUF',
         'tomngdev/AutoShell-350M', 'tomngdev/AutoShell-0.8B',
         'fingerthief/lancet-nano', 'P0u4a/ModernBERT-bash-classifier']

def get(url):
    with urllib.request.urlopen(url, timeout=120) as response:
        return response.read()

if __name__ == '__main__':
    ROOT.mkdir(parents=True, exist_ok=True)
    manifest = pathlib.Path(__file__).parent / 'results/artifacts.json'
    records = json.loads(manifest.read_text()) if manifest.exists() else []
    if not records:
        for repo in REPOS:
            try:
                info = json.loads(get('https://huggingface.co/api/models/' + repo))
                record = {'repo': repo, 'revision': info['sha'], 'files': [x['rfilename'] for x in info['siblings']]}
            except Exception as exc:
                record = {'repo': repo, 'error': str(exc)}
            records.append(record)
            print(json.dumps(record), flush=True)
    (ROOT / 'availability.json').write_text(json.dumps(records, indent=2) + '\n')
    for record in records:
        if 'error' in record:
            continue
        repo = record['repo']
        pinned = {a['file']: a for a in record.get('artifacts', [])}
        if manifest.exists():
            selected = list(pinned)
        elif repo.endswith('GGUF'):
            selected = [f for f in record['files'] if 'Q8_0' in f and f.endswith('.gguf')]
        elif repo == 'fingerthief/lancet-nano':
            selected = [f for f in record['files'] if f.startswith('bundle/')]
        else:
            selected = []
        artifacts = []
        for name in selected:
            path = ROOT / repo.split('/')[-1] / name
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                print('Downloading ' + repo + '/' + name, flush=True)
                data = get(f'https://huggingface.co/{repo}/resolve/{record["revision"]}/{name}')
                if name in pinned and hashlib.sha256(data).hexdigest() != pinned[name]['sha256']:
                    raise ValueError('Downloaded artifact hash mismatch: ' + name)
                path.write_bytes(data)
            artifact = {'file': name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes': path.stat().st_size}
            if name in pinned and artifact != pinned[name]:
                raise ValueError('Cached artifact mismatch: ' + str(path))
            artifacts.append(artifact)
        record['artifacts'] = artifacts
        (ROOT / 'availability.json').write_text(json.dumps(records, indent=2) + '\n')
