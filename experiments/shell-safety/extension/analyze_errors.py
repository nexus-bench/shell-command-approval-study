"""Save identifiable failure and representation-change evidence without public text."""
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent


def load(name):
    return [json.loads(x) for x in (HERE / 'results' / (name + '.jsonl')).read_text().splitlines()]


def analyze():
    output = {'synthetic': {}, 'public_representation_changes': {}}
    for arm in ['lancet', 'autoshell-command', 'autoshell-native', 'autoshell-expanded']:
        rows = load('synthetic-' + arm)
        pairs = defaultdict(list)
        for row in rows:
            if row['pair']:
                pairs[row['pair']].append(row)
        output['synthetic'][arm] = {
            'deny_allowed': [r['id'] for r in rows if r['expected'] == 'deny' and r['allow']],
            'unknown_allowed': [r['id'] for r in rows if r['expected'] == 'ask' and r['allow']],
            'legitimate_intercepted': [r['id'] for r in rows if r['expected'] == 'allow' and not r['allow']],
            'errors': [{'id': r['id'], 'error': r['error']} for r in rows if r.get('error')],
            'pairs_correct': [key for key, group in pairs.items()
                              if len(group) == 2 and all(r['allow'] == (r['expected'] == 'allow') for r in group)],
        }
    native = {r['id']: r for r in load('public-autoshell-native')}
    for arm in ['autoshell-expanded', 'autoshell-format-only']:
        changes = []
        for row in load('public-' + arm):
            before = native[row['id']]
            if before['allow'] != row['allow']:
                changes.append({'id': row['id'], 'source': row['sourceDataset'],
                                'expected': row['expected'], 'native_allow': before['allow'],
                                'comparison_allow': row['allow'], 'native_score': before['safe_score'],
                                'comparison_score': row['safe_score']})
        output['public_representation_changes'][arm] = changes
    return output


if __name__ == '__main__':
    result = analyze()
    (HERE / 'results/error-analysis.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
