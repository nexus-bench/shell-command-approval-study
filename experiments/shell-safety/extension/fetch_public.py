"""Download pinned public datasets as inert bytes; never execute dataset commands."""
import hashlib,json,urllib.request
from pathlib import Path
ROOT=Path(__file__).parent
CACHE=Path('.experiments/shell-safety/public')
SOURCES=[('kontext-security/ShellRisk-Bench','437467862139b4e9cdd5322024ef3434a67c7ec8',['README.md','data/test-00000-of-00001.parquet']),('tomngdev/shell-safety','155dbb5d3047dd095523bd8ee3dd65adf1296dde',['README.md','lg/test.jsonl']),('tomngdev/shell-safety-transcripts','e8b46e9821d9bc7957466154453d88c59a76eb53',['README.md','lg/test.jsonl'])]
def main():
    manifest=[]
    lock=ROOT/'public-artifacts.json'
    expected={(r['repo'],r['file']):r['sha256'] for r in json.loads(lock.read_text())} if lock.exists() else {}
    for repo,revision,files in SOURCES:
        for filename in files:
            url=f'https://huggingface.co/datasets/{repo}/resolve/{revision}/{filename}'
            path=CACHE/repo.split('/')[-1]/filename
            path.parent.mkdir(parents=True,exist_ok=True)
            if not path.exists():path.write_bytes(urllib.request.urlopen(url,timeout=120).read())
            data=path.read_bytes()
            if expected and hashlib.sha256(data).hexdigest()!=expected[(repo,filename)]:
                raise RuntimeError('Artifact hash mismatch: '+str(path))
            manifest.append(dict(repo=repo,revision=revision,file=filename,url=url,path=str(path),bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
            print(str(path),len(data),flush=True)
    (ROOT/'public-artifacts.json').write_text(json.dumps(manifest,indent=2)+'\n')
if __name__=='__main__':main()
