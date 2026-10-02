"""Regenerate measured report section; analysis never triggers model inference."""
import json
import math
from pathlib import Path

import analyze

HERE=Path(__file__).parent
RESULTS=HERE/'results'


def render():
    summary=json.loads((RESULTS/'summary.json').read_text())
    thresholds=json.loads((RESULTS/'thresholds.json').read_text())['thresholds']
    lines=['### Development selection', '',
           '| Application arm | Locked threshold | Development legitimate approvals | Development deny/ask approvals |',
           '|---|---:|---:|---:|']
    for arm,point in thresholds.items():
        m=point['dev_metrics']
        lines.append(f"| {arm} | {point['threshold']:.12g} | {m['legitimate_approvals']}/{m['allow_n']} | {m['wrong_approved_n']} |")
    lines += ['', 'Threshold column means approve when the score is **greater than** the listed threshold.',
              'These thresholds were chosen without opening test predictions.', '',
              '### Held-out results under each input/policy label set', '',
              'Native full excludes two ambiguous test labels. Limited evidence has fewer allow labels.',
              'LANCET remains a risk-signal reference; its application labels do not redefine its native task.', '',
              'Oracle-only metrics are parent-label recovery with the command withheld, not operational approval safety.',
              'Rule/always-intervene latency was not measured (shown as —).', '',
              (RESULTS/'table.md').read_text().strip(), '',
              '### Common full-evidence application reference', '',
              'This table uses the same 12 allow / 12 deny / 12 ask reference for every arm.',
              'For limited collection, it exposes useful actions lost because evidence was not collected.',
              'The input-specific table above additionally counts unsupported approvals of actually benign cases.', '',
              '| Arm / operating point | Legitimate approved / 12 | Deny approved / 12 | Unknown approved / 12 |',
              '|---|---:|---:|---:|']
    for arm,entry in summary.items():
        for point in ['default','selected']:
            key='application_reference_'+point
            if key not in entry:continue
            m=entry[key]
            lines.append(f"| {arm} / {point} | {m['legitimate_approvals']} | {m['deny_approvals']} | {m['unknown_approvals']} |")
    lines += ['', '### Family-cluster uncertainty at selected thresholds', '',
              '| Arm | Legitimate recall, 95% bootstrap interval | Error fraction among approved actions, 95% interval |',
              '|---|---|---|']
    for arm,entry in summary.items():
        if 'cluster_bootstrap' not in entry:continue
        b=entry['cluster_bootstrap']
        def fmt(interval):
            return 'undefined' if interval is None else f'{100*interval[0]:.1f}%–{100*interval[1]:.1f}%'
        risk=fmt(b['approved_error_fraction_95_percentile']) if b['approving_family_n']>1 else 'Not informative: only one approving family'
        lines.append(f"| {arm} | {fmt(b['legitimate_recall_95_percentile'])} | {risk} |")
    lines += ['', 'Intervals resample all six held-out families with their members together (2,000 draws).',
              '`None` means no defined estimate; a [0, 0] interval with no observed errors is **not** a safety guarantee.',
              'Approval-error intervals omit bootstrap resamples with no approvals; their counts are saved in summary.json.', '',
              'When approvals occur in only one family, conditional risk resampling gives a spuriously',
              'precise point interval; the report suppresses its interpretation while retaining raw bootstrap values.', '',
              '### Separate adversarial diagnostics', '',
              '| Family | Expected allow / deny / ask | Default allowed | Selected allowed | Rule allowed |',
              '|---|---|---|---|---|']
    diagnostics=[json.loads(x) for x in (RESULTS/'adversarial.jsonl').read_text().splitlines()]
    threshold=thresholds['app-full']['threshold']
    for family in sorted({r['family'] for r in diagnostics}):
        group=[r for r in diagnostics if r['family']==family]
        counts=lambda key: ' / '.join(str(sum(bool(r[key]) for r in group if r['expected']==label)) for label in ['allow','deny','ask'])
        for r in group:r['selected']=analyze.decide(r,threshold)
        expected=' / '.join(str(sum(r['expected']==label for r in group)) for label in ['allow','deny','ask'])
        lines.append(f"| {family} | {expected} | {counts('allow')} | {counts('selected')} | {counts('rule_allow')} |")
    lines += ['', 'Allowed-count cells follow the same allow / deny / ask order. These 12 diagnostic cases',
              'reuse existing families and are excluded from calibration and the held-out headline metrics.', '',
              '### Positional and capacity stress', '',
              '| Size / position / expected | Prompt tokens | Default allowed | Selected allowed | Error | Model+HTTP ms |',
              '|---|---:|---|---|---|---:|']
    for r in map(json.loads,(RESULTS/'long-4096.jsonl').read_text().splitlines()):
        lines.append(f"| {r['size']} / {r['position']} / {r['expected']} | {r['prompt_tokens']} | {r['allow']} | {analyze.decide(r,threshold)} | {r['error']} | {r['elapsed_ms']:.1f} |")
    lines += ['', 'Positions are verified against actual serialized bytes; token counts come from llama.cpp.',
              'Overflow rejections reflect the configured 4096-token server, not an architectural model limit.',
              'No higher-capacity result is included in this run.', '', '### Collection and replay', '']
    timings=json.loads((HERE/'data/collection-timings.json').read_text())
    for mode in ['full','limited']:
        values=sorted(r[mode+'_ms'] for r in timings)
        lines.append(f"- {mode} collection: p50 {values[math.ceil(.5*len(values))-1]:.1f} ms, p95 {values[math.ceil(.95*len(values))-1]:.1f} ms, max {values[-1]:.1f} ms.")
    replay=json.loads((RESULTS/'replay.json').read_text())
    match=sum(r['allow']==r['original_allow'] for r in replay)
    selected_match=sum(analyze.decide(r,threshold)==analyze.decide({'allow':r['original_allow'],'safe_score':r['original_score'],'error':r['original_error']},threshold) for r in replay)
    lines.append(f'- One preselected case per test family replayed: {match}/{len(replay)} default decisions matched; this is not a repeated latency benchmark.')
    lines.append(f'- At the development-selected app-full threshold, {selected_match}/{len(replay)} replay decisions matched.')
    lines.append('- The prespecified first-ID replay selects deny-label cases; it does not establish stability of positive approvals or near-threshold decisions.')
    memory=json.loads((RESULTS/'runtime-sample.json').read_text())
    lines.append(f"- One server RSS sample during inference: {memory['rss_kib']/1024:.1f} MiB. This is neither peak memory nor a cold-start measurement.")
    return '\n'.join(lines)+'\n'


if __name__=='__main__':
    section=render()
    (RESULTS/'report-section.md').write_text(section)
    path=HERE/'README.md'
    text=path.read_text()
    begin='<!-- RESULTS -->';end='<!-- END_RESULTS -->'
    if end in text:
        left=text.split(begin)[0];right=text.split(end,1)[1]
        text=left+begin+'\n\n'+section+'\n'+end+right
    else:
        assert text.count(begin)==1
        text=text.replace(begin,begin+'\n\n'+section+'\n'+end)
    path.write_text(text)
    print('Updated measured report section')
