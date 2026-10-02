"""Render source-separated and context-sensitive metrics from saved predictions."""
import json
from pathlib import Path

HERE = Path(__file__).parent


def render(summary):
    arms = ['lancet', 'autoshell-command', 'autoshell-native', 'autoshell-expanded']
    lines = ['### Public source results', '',
             '| Source / arm | Unsafe allowed ↓ | Legitimate allowed ↑ | Accuracy | p50 / p95 ms |',
             '|---|---:|---:|---:|---:|']
    for source in ['shellrisk', 'shellsafety']:
        for arm in arms + (['autoshell-format-only'] if source == 'shellsafety' else []):
            m = summary['public-' + arm]['sourceDataset'][source]
            lines.append(f"| {source} / {arm} | {m['unsafe_approvals']}/{m['intervention_n']} | {m['legitimate_approvals']}/{m['safe_n']} | {100*m['correct']/m['n']:.0f}% | {m['p50_ms']:.1f} / {m['p95_ms']:.1f} |")
    lines += ['', '### Synthetic challenge results', '',
              '| Arm | Deny allowed / 44 ↓ | Unknown allowed / 40 ↓ | Legitimate allowed / 44 ↑ | Both-correct pairs / 40 ↑ | Runtime/parser errors | p50 / p95 ms |',
              '|---|---:|---:|---:|---:|---:|---:|']
    for arm in arms:
        record = summary['synthetic-' + arm]
        m = record['overall']
        lines.append(f"| {arm} | {record['expected']['deny']['unsafe_approvals']} | {record['expected']['ask']['unsafe_approvals']} | {m['legitimate_approvals']} | {m['pairs_correct']} | {m['errors']} | {m['p50_ms']:.1f} / {m['p95_ms']:.1f} |")
    lines += ['', '### Repository profiles', '',
              'Each cell is **unsafe approvals / intervention cases; legitimate approvals / allow cases**.',
              'These profiles have different command families; they are not controlled repository rankings.', '',
              '| Profile | LANCET | AutoShell command | AutoShell native | AutoShell expanded |',
              '|---|---|---|---|---|']
    for profile in sorted(summary['synthetic-lancet']['contextProfile']):
        cells = []
        for arm in arms:
            m = summary['synthetic-' + arm]['contextProfile'][profile]
            cells.append(f"{m['unsafe_approvals']}/{m['intervention_n']}; {m['legitimate_approvals']}/{m['safe_n']}")
        lines.append('| ' + profile + ' | ' + ' | '.join(cells) + ' |')
    return '\n'.join(lines) + '\n'


if __name__ == '__main__':
    summary = json.loads((HERE / 'results/local-summary.json').read_text())
    output = render(summary)
    (HERE / 'results/detailed-tables.md').write_text(output)
    print(output)
