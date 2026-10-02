"""Replay saved decisions and verify the completed study, without inference."""
import hashlib
import json
import unittest
from pathlib import Path

import run_local
import summarize_local
import render_tables
import analyze_errors

HERE = Path(__file__).parent


class ResultsTests(unittest.TestCase):
    def test_complete_matrix_and_labels(self):
        public = json.loads((HERE / 'public-selection.json').read_text())['rows']
        synthetic = [json.loads(x) for x in (HERE / 'data/synthetic.jsonl').read_text().splitlines()]
        for corpus, cases in [('public', public), ('synthetic', synthetic)]:
            for arm in ['lancet', 'autoshell-command', 'autoshell-native', 'autoshell-expanded']:
                path = HERE / 'results' / f'{corpus}-{arm}.jsonl'
                rows = [json.loads(x) for x in path.read_text().splitlines()]
                self.assertEqual([(r['id'], r['expected']) for r in rows],
                                 [(r['id'], r['expected']) for r in cases])
                for row in rows:
                    if corpus == 'public':
                        self.assertNotIn('request', row)
                        self.assertEqual(len(row['request_sha256']), 64)
                    if arm != 'lancet' and not str(row.get('error')).startswith('http-'):
                        parsed = run_local.prior.parse_auto(row['response'])
                        for key in ('allow', 'safe_score', 'error'):
                            self.assertEqual(parsed[key], row[key])
                    elif arm == 'lancet':
                        self.assertEqual(row['allow'], row['response']['classification'] == 'not_flagged')
                    else:
                        self.assertFalse(row['allow'])

    def test_summary_reproduces(self):
        self.assertEqual(summarize_local.summarize(),
                         json.loads((HERE / 'results/local-summary.json').read_text()))

    def test_analysis_reproduces(self):
        self.assertEqual(analyze_errors.analyze(), json.loads((HERE / 'results/error-analysis.json').read_text()))
        summary = json.loads((HERE / 'results/local-summary.json').read_text())
        self.assertEqual(render_tables.render(summary), (HERE / 'results/detailed-tables.md').read_text())

    def test_format_control_lossless(self):
        case = {'command': 'git status', 'nativeMessages': [
            {'role': 'system', 'content': run_local.prior.SYSTEM},
            {'role': 'user', 'content': '<SessionContext>\ngitRemote: github.com\nagentTouchedFiles: a, b\ngitStatus:\n M a\n?? b\n</SessionContext>\n\ngit status'}]}
        fields = run_local.transcript_fields(case)
        self.assertEqual(fields, {'gitRemote': 'github.com', 'agentTouchedFiles': 'a, b', 'gitStatus': ' M a\n?? b'})
        output = run_local.messages(case, 'autoshell-format-only')
        body = output[1]['content'].split('<SessionContext>\n')[1].split('\n</SessionContext>')[0]
        self.assertEqual({line.split(': ', 1)[0]: json.loads(line.split(': ', 1)[1])
                          for line in body.splitlines()}, fields)
        self.assertEqual(output[0], case['nativeMessages'][0])

    def test_format_control_same_examples(self):
        native = [json.loads(x) for x in (HERE / 'results/public-autoshell-native.jsonl').read_text().splitlines()]
        control = [json.loads(x) for x in (HERE / 'results/public-autoshell-format-only.jsonl').read_text().splitlines()]
        self.assertEqual([(r['id'], r['expected']) for r in control],
                         [(r['id'], r['expected']) for r in native if r['sourceDataset'] == 'shellsafety'])
        for row in control:
            self.assertEqual(run_local.prior.parse_auto(row['response'])['allow'], row['allow'])

    def test_synthetic_input_fingerprints(self):
        raw = (HERE / 'data/synthetic.jsonl').read_bytes()
        cases = [json.loads(x) for x in raw.splitlines()]
        for arm in ['lancet', 'autoshell-command', 'autoshell-native', 'autoshell-expanded']:
            meta = json.loads((HERE / 'results' / f'synthetic-{arm}.meta.json').read_text())
            self.assertEqual(meta['dataset_sha256'], hashlib.sha256(raw).hexdigest())
            self.assertEqual(meta['fingerprint'], run_local.fingerprint(cases, arm, False))

    def test_public_request_hashes_when_downloads_present(self):
        cache = Path('.experiments/shell-safety/public/public.jsonl')
        if not cache.exists():
            self.skipTest('Download pinned public inputs to verify redacted request hashes')
        cases = {r['id']: r for r in map(json.loads, cache.read_text().splitlines())}
        for arm in ['lancet', 'autoshell-command', 'autoshell-native', 'autoshell-expanded', 'autoshell-format-only']:
            path = HERE / 'results' / f'public-{arm}.jsonl'
            for row in map(json.loads, path.read_text().splitlines()):
                case = cases[row['id']]
                if arm == 'lancet':
                    request = {'command': case['command']}
                else:
                    request = dict(model='autoshell', messages=run_local.messages(case, arm),
                                   max_tokens=1, temperature=0, seed=20260930,
                                   logprobs=True, top_logprobs=20, cache_prompt=False)
                self.assertEqual(row['request_sha256'],
                                 hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest())


if __name__ == '__main__':
    unittest.main()
