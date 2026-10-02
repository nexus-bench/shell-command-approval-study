"""Download pinned public artifacts into the ignored cache and verify hashes."""
import json, urllib.request
from run import HERE, CACHE, sha

SOURCES = {
    'lib.rs': ('random1st/secguard','d45bbb55c30c767bb0c1fb07885a69bb11365836','crates/secguard-brain/src/lib.rs'),
    'brain.rs': ('random1st/secguard','d45bbb55c30c767bb0c1fb07885a69bb11365836','crates/secguard-guard/src/brain.rs'),
    **{name:('kontext-security/kontext','8a0096c658167f29b1ee4927e812ff316e9d84c8',path) for name,path in {
        'svm.go':'internal/guard/riskclassifier/svm.go',
        'normalize.go':'internal/guard/riskclassifier/normalize.go',
        'golden.jsonl':'internal/guard/riskclassifier/testdata/golden.jsonl',
        'svm.json.gz':'internal/guard/riskclassifier/model/svm.json.gz',
        'export_portable.py':'scripts/riskclassifier/export_portable.py',
    }.items()},
}

def main():
    from huggingface_hub import snapshot_download
    manifest = json.loads((HERE/'artifacts.json').read_text())
    for name, model in manifest['models'].items():
        snapshot_download(model['repo'], revision=model['revision'], local_dir=CACHE/name, ignore_patterns=['training_args.bin'])
    (CACHE/'source').mkdir(exist_ok=True)
    for name,(repo,revision,path) in SOURCES.items():
        with urllib.request.urlopen(f'https://raw.githubusercontent.com/{repo}/{revision}/{path}',timeout=60) as r:
            (CACHE/'source'/name).write_bytes(r.read())
    for name, expected in manifest['files'].items():
        assert sha((CACHE/name).read_bytes()) == expected['sha256'], name
    print('All pinned artifact hashes verified.')

if __name__ == '__main__':
    main()
