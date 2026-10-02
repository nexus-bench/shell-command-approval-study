"""Regenerate count-based tables. No cross-policy pooled accuracy."""
import collections, json, statistics
from run import HERE

def metric(rows, key='allow'):
    out = {}
    for label in ['allow','deny','ask']:
        subset = [r for r in rows if r['expected']==label]
        out[label] = [sum(bool(r.get(key)) for r in subset),len(subset)]
    out['errors'] = sum(bool(r.get('error')) for r in rows)
    times = sorted(r['elapsed_ms'] for r in rows)
    out['p50_ms'] = statistics.median(times)
    out['p95_ms'] = times[min(len(times)-1, int(.95*len(times)))]
    return out

def main():
    summary = {}
    for model in ['modernbert','kestrel','secguard']:
        for dataset in ['public','v2','adversarial']:
            rows = [json.loads(x) for x in (HERE/f'results/{model}-{dataset}.jsonl').read_text().splitlines()]
            groups = collections.defaultdict(list)
            for row in rows:
                group = row['sourceDataset'] if dataset=='public' else row['split'] if dataset=='v2' else 'diagnostic'
                groups[group].append(row)
            for key in (['allow','label_allow'] if model=='secguard' else ['allow']):
                for group, values in groups.items():
                    summary[f'{model}/{key}/{dataset}/{group}'] = metric(values,key)
    (HERE/'results/summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    lines = ['| Model / decision / set | Safe or legitimate approved | Deny approved | Unknown approved | Errors | p50 / p95 ms |',
             '|---|---:|---:|---:|---:|---:|']
    for name,m in summary.items():
        counts = ['/'.join(map(str,m[label])) for label in ['allow','deny','ask']]
        lines.append(f'| {name} | '+ ' | '.join(counts)+ f" | {m['errors']} | {m['p50_ms']:.2f} / {m['p95_ms']:.2f} |")
    (HERE/'results/table.md').write_text('\n'.join(lines)+'\n')
    print('\n'.join(lines))

if __name__ == '__main__':
    main()
