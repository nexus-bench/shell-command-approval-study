"""Local models only. Never executes case commands. Incremental reproducible output."""
import argparse,hashlib,importlib.util,inspect,json,platform,time,urllib.request,urllib.error
from pathlib import Path
HERE=Path(__file__).parent
spec=importlib.util.spec_from_file_location('prior',HERE.parent/'run_eval.py')
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
def native_context(context):
    lines=[]
    for key,value in context.items():
        if key=='agentTouchedFiles' and isinstance(value,list):value=', '.join(value)
        elif key=='gitStatus' and isinstance(value,dict):
            value='\n'+'\n'.join(prefix+p for field,prefix in [('modified',' M '),('staged','M  '),('untracked','?? ')] for p in value.get(field,[]))
        elif not isinstance(value,str):value=json.dumps(value,ensure_ascii=False)
        lines.append(f'{key}: {value}')
    return '\n'.join(lines)
def transcript_fields(case):
    content=case['nativeMessages'][1]['content']
    prefix='<SessionContext>\n'
    suffix='\n</SessionContext>\n\n'+case['command']
    if content=='\n\n'+case['command']:return {}
    assert content.startswith(prefix) and content.endswith(suffix)
    body=content[len(prefix):-len(suffix)]
    fields={}
    while body:
        if body.startswith('gitStatus:\n'):
            fields['gitStatus']=body[len('gitStatus:\n'):];break
        line,_,body=body.partition('\n')
        key,sep,value=line.partition(': ')
        assert sep and key in ('gitRemote','agentTouchedFiles') and key not in fields
        fields[key]=value
    reconstructed='\n'.join(k+(':\n' if k=='gitStatus' else ': ')+v for k,v in fields.items())
    assert prefix+reconstructed+suffix==content
    return fields
def messages(case,arm):
    if arm=='autoshell-format-only':
        fields=transcript_fields(case)
        if not fields:return case['nativeMessages']
        body='\n'.join(k+': '+json.dumps(v,ensure_ascii=False) for k,v in fields.items())
        return [case['nativeMessages'][0],{'role':'user','content':'<SessionContext>\n'+body+'\n</SessionContext>\n\n'+case['command']}]
    if arm=='autoshell-native' and 'nativeMessages' in case:return case['nativeMessages']
    if arm=='autoshell-native':
        content='<SessionContext>\n'+native_context(case['context'])+'\n</SessionContext>\n\n'+case['command']
        return [{'role':'system','content':prior.SYSTEM},{'role':'user','content':content}]
    return prior.messages(case,'autoshell-command' if arm=='autoshell-command' else 'autoshell-context')
def fingerprint(rows,arm,redact):
    def digest(value):return hashlib.sha256(value).hexdigest()
    # Hash actual serialized inputs, not this whole orchestration file.
    inputs=[{'command':r['command']} if arm=='lancet' else messages(r,arm) for r in rows]
    return dict(inputs_sha256=digest(json.dumps(inputs,sort_keys=True,ensure_ascii=False).encode()),
                parser_sha256=digest(inspect.getsource(prior.parse_auto).encode()),
                artifacts_manifest_sha256=digest((HERE.parent/'results/artifacts.json').read_bytes()),
                declared_server_settings={'context':4096,'parallel':1,'threads':4,'gpu_layers':0,'port':18765},
                generation={'max_tokens':1,'temperature':0,'seed':20260930,'top_logprobs':20,'cache_prompt':False},
                redacted=redact)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('dataset');ap.add_argument('arm',choices=['lancet','autoshell-command','autoshell-native','autoshell-expanded','autoshell-format-only']);ap.add_argument('--output',required=True);ap.add_argument('--redact',action='store_true');ap.add_argument('--resume',action='store_true');args=ap.parse_args()
    payload=Path(args.dataset).read_bytes();rows=[json.loads(x) for x in payload.splitlines()]
    identity=fingerprint(rows,args.arm,args.redact)
    start=time.perf_counter()
    if args.arm=='lancet':
        spec=importlib.util.spec_from_file_location('lancet_runtime',prior.CACHE/'lancet-nano/bundle/classify.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);model=m.LancetNano(prior.CACHE/'lancet-nano/bundle/model',threads=4)
        def score(case):
            raw=model.score(case['command']);return dict(allow=raw['classification']=='not_flagged',safe_score=1-raw['score'] if raw['score'] is not None else None,error=raw['reason'] if raw['score'] is None else None,response=raw,request={'command':case['command']})
    else:
        def score(case):
            request=dict(model='autoshell',messages=messages(case,args.arm),max_tokens=1,temperature=0,seed=20260930,logprobs=True,top_logprobs=20,cache_prompt=False)
            req=urllib.request.Request('http://127.0.0.1:18765/v1/chat/completions',data=json.dumps(request).encode(),headers={'Content-Type':'application/json'})
            try:
                with urllib.request.urlopen(req,timeout=120) as response:raw=json.load(response)
            except urllib.error.HTTPError as exc:
                raw=json.loads(exc.read())
                return dict(allow=False,safe_score=None,error=f'http-{exc.code}',request=request,response=raw)
            return prior.parse_auto(raw)|dict(request=request,response=raw)
    load_ms=(time.perf_counter()-start)*1000
    output=Path(args.output);output.parent.mkdir(parents=True,exist_ok=True)
    completed=0
    if output.exists():
        if not args.resume:raise RuntimeError('Refusing to overwrite existing results')
        previous=json.loads(output.with_suffix('.meta.json').read_text())
        assert previous['arm']==args.arm and previous['dataset_sha256']==hashlib.sha256(payload).hexdigest()
        if previous.get('fingerprint')!=identity:
            raise RuntimeError('Resume requires matching input/parser/artifact/settings fingerprint; historical runs without it require a separate audited recovery')
        saved=[json.loads(x) for x in output.read_text().splitlines()]
        assert [x['id'] for x in saved]==[x['id'] for x in rows[:len(saved)]]
        completed=len(saved)
    metadata=dict(arm=args.arm,dataset_sha256=hashlib.sha256(payload).hexdigest(),fingerprint=identity,count=len(rows),python=platform.python_version(),platform=platform.platform(),load_ms=load_ms,timestamp_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
    if completed:
        previous.setdefault('resumes',[]).append(metadata|dict(completed_before_resume=completed))
        metadata=previous
    output.with_suffix('.meta.json').write_text(json.dumps(metadata,indent=2)+'\n')
    for command in ['ls','pwd']:
        warmup={'command':command,'context':{}}
        if args.arm=='autoshell-format-only':
            warmup['nativeMessages']=[{'role':'system','content':prior.SYSTEM},{'role':'user','content':'<SessionContext>\ngitRemote: github.com\nagentTouchedFiles: \ngitStatus:\n\n</SessionContext>\n\n'+command}]
        score(warmup)
    with output.open('a' if completed else 'w') as stream:
        for i,case in enumerate(rows[completed:],start=completed):
            start=time.perf_counter();prediction=score(case);elapsed=(time.perf_counter()-start)*1000
            if args.redact:
                prediction['request_sha256']=hashlib.sha256(json.dumps(prediction.pop('request'),sort_keys=True).encode()).hexdigest()
            record={k:case.get(k) for k in ['id','sourceDataset','expected','category','pair','contextProfile','contrastGroup']}|prediction|dict(elapsed_ms=elapsed)
            stream.write(json.dumps(record,ensure_ascii=False)+'\n');stream.flush()
            if (i+1)%20==0:print(f'{args.arm} {i+1}/{len(rows)}',flush=True)
if __name__=='__main__':main()
