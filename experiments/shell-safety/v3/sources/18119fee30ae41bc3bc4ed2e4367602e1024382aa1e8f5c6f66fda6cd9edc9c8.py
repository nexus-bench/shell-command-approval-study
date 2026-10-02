"""Native secguard replay: stdin is classified as text, never executed."""
import argparse
import hashlib
import json
import os
import platform
import subprocess
import select
import time
from pathlib import Path
from run import HERE, ROOT, resolved_label, secguard, sha


def exchange(process, record):
    process.stdin.write(json.dumps(record) + '\n')
    process.stdin.flush()
    if not select.select([process.stdout], [], [], 180)[0]:
        raise TimeoutError('Native driver did not respond in 180 seconds')
    line = process.stdout.readline()
    if not line:
        raise RuntimeError('Native driver stopped; inspect its cached stderr')
    response = json.loads(line)
    if response['id'] != record['id']:
        raise ValueError('Native response ID mismatch')
    return response


def cases_for(name):
    if name == 'v3':
        path = HERE / 'data/cases.jsonl'
    elif name == 'public':
        path = ROOT / '.experiments/shell-safety/public/public.jsonl'
    else:
        path = HERE.parent / 'v2/data/adversarial.jsonl'
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    for row in rows:
        row.setdefault('dataset', row.get('sourceDataset') or name)
        row.setdefault('split', 'reference')
        row.setdefault('family', row.get('category', 'adversarial'))
        row.setdefault('resolution', None)
    return path, rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('arm', choices=['release', 'full', 'model-only'])
    ap.add_argument('--run-id', required=True)
    ap.add_argument('--dataset', choices=['v3', 'public', 'adversarial'], required=True)
    args = ap.parse_args()
    if not args.run_id.replace('-', '').isalnum():
        ap.error('Use an alphanumeric run ID')
    path, cases = cases_for(args.dataset)
    output = HERE / 'results' / args.run_id
    output.mkdir(parents=True, exist_ok=False)
    binary = ROOT / ('.experiments/secguard-release/secguard' if args.arm == 'release' else '.experiments/secguard-target/release/examples/study')
    meta = {'args': {**vars(args), 'repeat': 1}, 'case_count': len(cases),
            'case_ids': [c['id'] for c in cases], 'data_sha256': sha(path),
            'runner_sha256': sha(Path(__file__)), 'binary_sha256': sha(binary),
            'platform': platform.platform(), 'candidate_execution': 'never',
            'ml_enabled': args.arm != 'release', 'api_cost': None,
            'release_revision': 'a5b338584795c5a604c08a571972bce6e986be33' if args.arm == 'release' else None}
    process = None
    stderr = None
    if args.arm != 'release':
        meta['build'] = json.loads((HERE / 'secguard-build.json').read_text())
        meta['model_sha256'] = sha(ROOT / '.experiments/secguard-guard.gguf')
        assert meta['model_sha256'] == '211500d3603bbae9616d45c04c360b855a735c1fb0cd676cc2e667dd49be9a7b'
        stderr = (ROOT / f'.experiments/{args.run_id}.stderr').open('w')
        process = subprocess.Popen([str(binary), args.arm], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=stderr, text=True, cwd=HERE, env={'PATH': os.defpath,
                'SECGUARD_STUDY_MODEL': str(ROOT / '.experiments/secguard-guard.gguf'), 'GGML_LOG_LEVEL': 'error'})
        preflight = exchange(process, {'id': 'unscored-model-loading-check', 'command': 'study_unknown_operation'})
        meta['preflight'] = preflight
        source = preflight['result'].get('source')
        if source == 'brain_not_loaded' or (args.arm == 'full' and source not in ('brain', 'brain_safe', 'brain_low_confidence', 'brain_malformed')):
            process.terminate()
            process.wait(timeout=10)
            stderr.close()
            raise RuntimeError('Full guard preflight did not reach the loaded brain')
    (output / 'meta.json').write_text(json.dumps(meta, indent=2) + '\n')
    try:
        with (output / 'records.jsonl').open('x') as stream:
            for index, case in enumerate(cases, 1):
                start = time.perf_counter()
                if process:
                    response = exchange(process, {'id': case['id'], 'command': case['command']})
                    result = response['result']
                    # Never mistake a missing model for a successful full-ML run.
                    if result.get('source') == 'brain_not_loaded':
                        raise RuntimeError('Native ML guard failed to load its model')
                    native = response
                else:
                    result = secguard(case)
                    native = result['native']
                    if args.dataset == 'public':
                        native = {'returncode': native['returncode'], 'stdout_sha256': hashlib.sha256(native['stdout'].encode()).hexdigest(),
                                  'stderr_sha256': hashlib.sha256(native['stderr'].encode()).hexdigest()}
                record = {k: case[k] for k in ('id', 'dataset', 'split', 'family', 'expected')}
                record.update(arm='secguard-' + args.arm, repeat=0, decision=result['decision'], error=result.get('error'),
                    native=native, calls=[], inspections=[], expected_after_inspection=case['expected'],
                    elapsed_ms=(time.perf_counter() - start)*1000, permission_outcome=None,
                    command_executed=False, human_escalation=None,
                    input_sha256=hashlib.sha256(case['command'].encode()).hexdigest())
                stream.write(json.dumps(record) + '\n')
                stream.flush()
                if index % 20 == 0:
                    print(f'{args.run_id}: {index}/{len(cases)}', flush=True)
        if process:
            process.stdin.close()
            if process.wait(timeout=30):
                raise RuntimeError('Native driver failed at shutdown')
        meta['completed'] = True
        (output / 'meta.json').write_text(json.dumps(meta, indent=2) + '\n')
    finally:
        if process and process.poll() is None:
            process.terminate()
            process.wait(timeout=10)
        if stderr:
            stderr.close()


if __name__ == '__main__':
    main()
