"""Compare a tagged secguard replay with the preserved first run."""
import argparse
import collections
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / 'results'


def read(dataset, tag):
    stem = f'secguard-{tag}-{dataset}' if tag else f'secguard-{dataset}'
    rows = [json.loads(line) for line in (RESULTS / f'{stem}.jsonl').read_text().splitlines()]
    meta = json.loads((RESULTS / f'{stem}.meta.json').read_text())
    assert len(rows) == meta['count'], stem
    return rows, meta


def counts(rows):
    return {
        'labels': dict(sorted(collections.Counter(row.get('label') for row in rows).items())),
        'approved_by_expected': {
            label: [sum(bool(row['allow']) for row in rows if row['expected'] == label),
                    sum(row['expected'] == label for row in rows)]
            for label in sorted({row['expected'] for row in rows})
        },
        'errors': sum(row.get('error') is not None for row in rows),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tag', default='reference-gpu-bf16')
    args = ap.parse_args()
    output = {'tag': args.tag, 'datasets': {}, 'changed_decisions': []}
    for dataset in ('public', 'v2', 'adversarial'):
        original, original_meta = read(dataset, '')
        replay, replay_meta = read(dataset, args.tag)
        assert original_meta['dataset_sha256'] == replay_meta['dataset_sha256'], dataset
        assert [(row['id'], row['input_sha256']) for row in original] == [
            (row['id'], row['input_sha256']) for row in replay], dataset
        output['datasets'][dataset] = {
            'n': len(original),
            'dataset_sha256': original_meta['dataset_sha256'],
            'original': counts(original),
            'replay': counts(replay),
        }
        for before, after in zip(original, replay):
            if (before.get('allow'), before.get('label'), before.get('error')) != (
                    after.get('allow'), after.get('label'), after.get('error')):
                output['changed_decisions'].append({'dataset': dataset, 'id': before['id'],
                                                    'before': before.get('label'), 'after': after.get('label')})
    (RESULTS / 'secguard-recheck-summary.json').write_text(json.dumps(output, indent=2) + '\n')
    print(f"Compared {sum(v['n'] for v in output['datasets'].values())} cases; "
          f"{len(output['changed_decisions'])} changed decisions")


if __name__ == '__main__':
    main()
