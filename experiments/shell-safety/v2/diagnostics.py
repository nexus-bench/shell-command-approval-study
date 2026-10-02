"""Score reviewed diagnostics and a small deterministic replay after threshold lock."""
import hashlib
import json
import time
from pathlib import Path

import analyze
import run

HERE=Path(__file__).parent


def main():
    assert (HERE/'results/thresholds.json').exists()
    target=HERE/'results/adversarial.jsonl'
    if target.exists():raise RuntimeError('Preserve existing diagnostic outputs')
    rows=[json.loads(x) for x in (HERE/'data/adversarial.jsonl').read_text().splitlines()]
    with target.open('w') as stream:
        for case in rows:
            start=time.perf_counter()
            prediction=run.predict(case,'app-full')
            out={k:case[k] for k in ['id','family','variant','expected']}
            out.update(prediction,elapsed_ms=(time.perf_counter()-start)*1000,rule_allow=analyze.rule(case,'full'))
            stream.write(json.dumps(out)+'\n');stream.flush()
            print(out['id'],out['allow'],flush=True)
    original={r['id']:r for r in analyze.load('test','app-full')}
    # First ID per family, chosen without looking at predictions.
    selected={}
    for case in sorted((r for r in run.rows() if r['split']=='test'),key=lambda r:r['id']):
        selected.setdefault(case['family'],case)
    replay=[]
    for case in selected.values():
        start=time.perf_counter();prediction=run.predict(case,'app-full')
        replay.append({'id':case['id'],'original_allow':original[case['id']]['allow'],
                       'original_error':original[case['id']]['error'],
                       'original_score':original[case['id']]['safe_score'],**prediction,
                       'elapsed_ms':(time.perf_counter()-start)*1000})
    (HERE/'results/replay.json').write_text(json.dumps(replay,indent=2)+'\n')
    (HERE/'results/diagnostic-lock.json').write_text(json.dumps({
        'adversarial_sha256':hashlib.sha256((HERE/'data/adversarial.jsonl').read_bytes()).hexdigest(),
        'policy_sha256':hashlib.sha256((HERE/'POLICY.md').read_bytes()).hexdigest(),
        'thresholds_sha256':hashlib.sha256((HERE/'results/thresholds.json').read_bytes()).hexdigest(),
        'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'capacity':4096},indent=2)+'\n')


if __name__=='__main__':main()
