"""Freeze deterministic public samples before model inference. Commands are data."""
import hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
import pyarrow.parquet as pq
HERE=Path(__file__).parent
CACHE=Path('.experiments/shell-safety/public')
def sha(x):return hashlib.sha256(x.encode()).hexdigest()
def load():
    out=[]
    for i,r in enumerate(pq.read_table(CACHE/'ShellRisk-Bench/data/test-00000-of-00001.parquet').to_pylist()):
        out.append(dict(id='shellrisk-'+r['id'],sourceDataset='shellrisk',sourceIndex=i,command=r['command'],context={},expected='allow' if r['label']=='not_risky' else 'deny',originalLabel=r['label'],category=r['source'],pair=None,shell='bash'))
    source=[json.loads(x) for x in (CACHE/'shell-safety/lg/test.jsonl').read_text().splitlines()]
    transcripts=[json.loads(x) for x in (CACHE/'shell-safety-transcripts/lg/test.jsonl').read_text().splitlines()]
    assert len(source)==len(transcripts)
    for i,(r,t) in enumerate(zip(source,transcripts)):
        assert t['messages'][1]['content'].endswith('\n\n'+r['command'])
        assert t['messages'][2]['content']==('yes' if r['safe'] else 'no')
        out.append(dict(id=f'shellsafety-{i}',sourceDataset='shellsafety',sourceIndex=i,command=r['command'],context=r['session_context'],nativeMessages=t['messages'][:2],expected='allow' if r['safe'] else 'deny',originalLabel=r['safe'],category=r['category'],pair=None,shell=r['shell']))
    return out
def select(rows,n):
    buckets=defaultdict(list)
    for r in rows:buckets[r['category']].append(r)
    for b in buckets.values():b.sort(key=lambda r:sha('20260930:'+r['id']))
    chosen=[]
    while len(chosen)<n:
        for k in sorted(buckets):
            if buckets[k] and len(chosen)<n:chosen.append(buckets[k].pop(0))
    return chosen
def main():
    rows=load();selected=[];dev=[]
    for dataset in ['shellrisk','shellsafety']:
        for label in ['allow','deny']:
            eligible=[r for r in rows if r['sourceDataset']==dataset and r['expected']==label and r['shell'] in ('bash','posix')]
            candidates=select(eligible,52);dev+=candidates[:2];selected+=candidates[2:]
    for name,data in [('public',selected),('public-format-dev',dev),('public-all',rows),('public-shellsafety',[r for r in selected if r['sourceDataset']=='shellsafety'])]:
        (CACHE/(name+'.jsonl')).write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in data))
    manifest={'selection':'Per dataset/label: POSIX/Bash only; SHA256(seed:id) within category, round-robin sorted categories; first 2 reserved format development, next 50 scored. No score-based filtering.', 'seed':20260930,'publicSha256':hashlib.sha256((CACHE/'public.jsonl').read_bytes()).hexdigest(),'rows':[{k:r[k] for k in ('id','sourceDataset','sourceIndex','expected','category')}|{'commandSha256':sha(r['command'])} for r in selected], 'developmentIds':[r['id'] for r in dev], 'fullCounts':dict(Counter(r['sourceDataset']+'|'+r['shell']+'|'+str(r['originalLabel'])+'|'+r['category'] for r in rows))}
    (HERE/'public-selection.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(len(rows),len(selected),len(dev))
if __name__=='__main__':main()
