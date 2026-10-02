"""Audit saved corpus, coverage, labels and evidence-resolution claims."""
import collections
import hashlib
import json
from pathlib import Path
from run import HERE, resolved_label

data = HERE / 'data/cases.jsonl'
freeze = json.loads((HERE / 'data/freeze.json').read_text())
assert hashlib.sha256(data.read_bytes()).hexdigest() == freeze['sha256']
cases = {c['id']: c for c in map(json.loads, data.read_text().splitlines())}
assert len(cases) == freeze['count'] == 120
checked = 0
for path in (HERE / 'results').glob('*/records.jsonl'):
    meta = json.loads((path.parent / 'meta.json').read_text())
    if not meta.get('completed'):
        print(f'Incomplete run excluded: {path.parent.name}')
        continue
    rows = list(map(json.loads, path.read_text().splitlines()))
    expected = collections.Counter((i, r) for i in meta['case_ids']
        for r in range(meta['args'].get('repeat', 1)))
    assert collections.Counter((r['id'], r['repeat']) for r in rows) == expected, path
    for row in rows:
        assert row['command_executed'] is False, path
        assert row['permission_outcome'] is None, path
        assert row['human_escalation'] is None, path
        if row.get('error'):
            assert row['decision'] is None, path
        if row['id'] in cases:
            case = cases[row['id']]
            assert row['expected'] == case['expected'], path
            assert row['expected_after_inspection'] == resolved_label(case, row['inspections']), path
        checked += 1
print(f'Validated {checked} saved decisions; corpus hash and case coverage match.')
