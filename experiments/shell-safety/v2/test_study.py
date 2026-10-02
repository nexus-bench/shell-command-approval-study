"""Verify fixture provenance, split isolation, label-free inputs and saved scoring."""
import hashlib
import json
import unittest
from pathlib import Path

import analyze
import run
import render_report

HERE=Path(__file__).parent


class StudyTests(unittest.TestCase):
    def test_freeze(self):
        lock=json.loads((HERE/'data/freeze.json').read_text())
        for filename,key in [('data/cases.jsonl','cases_sha256'),('build.py','builder_sha256'),('POLICY.md','policy_sha256')]:
            self.assertEqual(hashlib.sha256((HERE/filename).read_bytes()).hexdigest(),lock[key])

    def test_disjoint_families_profiles_and_repositories(self):
        cases=run.rows()
        self.assertEqual(len(cases),72)
        self.assertEqual(len({r['id'] for r in cases}),72)
        for field in ['family','profile','id']:
            self.assertFalse({r[field] for r in cases if r['split']=='dev'} & {r[field] for r in cases if r['split']=='test'})
        for family in {r['family'] for r in cases}:
            group=[r for r in cases if r['family']==family]
            self.assertEqual(len(group),6)
            self.assertEqual(len({r['profile'] for r in group}),2)
            self.assertEqual(len({r['command'] for r in group}),1)

    def test_no_labels_or_summaries_in_raw_inputs(self):
        for case in run.rows():
            changed=dict(case,expected='SENTINEL',limitedExpected='SENTINEL',nativeExpected='SENTINEL',
                         id='SENTINEL',family='SENTINEL',profile='SENTINEL',pair='SENTINEL',variant='SENTINEL')
            for arm in run.ARMS[1:]:
                self.assertEqual(run.messages(case,arm),run.messages(changed,arm))
            for arm in ['native-full','app-full','app-limited']:
                self.assertNotIn('effectSummary',json.dumps(run.messages(case,arm)))

    def test_raw_file_hashes_and_stored_receipts(self):
        for case in run.rows():
            for mode in ['full','limited']:
                for file in case[mode]['files']:
                    if 'content' in file:
                        self.assertEqual(hashlib.sha256(file['content'].encode()).hexdigest(),file['sha256'])
            if case['family']=='rollback' and case['variant']=='good':
                receipt=case['full']['host']['changeHistory'][0]
                self.assertEqual(receipt['preTaskSha256'],receipt['indexSha256'])
                self.assertNotEqual(receipt['currentSha256'],receipt['preTaskSha256'])

    def test_threshold_lock_uses_only_dev(self):
        lock=json.loads((HERE/'results/thresholds.json').read_text())
        for arm,point in lock['thresholds'].items():
            raw=(HERE/'results'/f'dev-{arm}.jsonl').read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),point['dev_predictions_sha256'])
            m=analyze.metrics(analyze.load('dev',arm),point['threshold'])
            self.assertEqual(m,point['dev_metrics'])
            self.assertEqual(m['wrong_approved_n'],0)

    def test_saved_decision_replay_and_inputs(self):
        cases={r['id']:r for r in run.rows()}
        for split in ['dev','test']:
            for arm in run.ARMS:
                for record in analyze.load(split,arm):
                    case=cases[record['id']]
                    self.assertEqual(record['expected'],run.expected(case,arm))
                    if arm=='lancet':
                        self.assertEqual(record['request'],{'command':case['command']})
                        self.assertEqual(record['allow'],record['response']['classification']=='not_flagged')
                    else:
                        self.assertEqual(record['request']['messages'],run.messages(case,arm))
                        if not record.get('error','') or not str(record.get('error')).startswith('http-'):
                            parsed=run.legacy.parse_auto(record['response'])
                            for key in ['allow','safe_score','error']:self.assertEqual(parsed[key],record[key])

    def test_zero_approval_is_not_zero_risk_estimate(self):
        rows=[{'id':'x','family':'f','expected':'deny','allow':False,'error':None}]
        self.assertIsNone(analyze.metrics(rows)['approved_error_fraction'])

    def test_long_positions_in_serialized_input(self):
        path=HERE/'data/long-inputs.jsonl'
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),json.loads((HERE/'data/long-freeze.json').read_text())['sha256'])
        for row in map(json.loads,path.read_text().splitlines()):
            content=run.messages(row,'app-full')[1]['content']
            offset=content.index(json.dumps(row['script'])[1:-1])
            self.assertEqual(row['scriptUtf8Offset'],len(content[:offset].encode()))
            files=row['full']['files']
            self.assertEqual(files[row['scriptIndex']]['path'],'verify.sh')
            if row['position']=='end':self.assertEqual(row['scriptIndex'],len(files)-1)

    def test_adversarial_receipts_and_revocation(self):
        rows=[json.loads(x) for x in (HERE/'data/adversarial.jsonl').read_text().splitlines()]
        self.assertEqual(len(rows),12)
        for row in rows:
            host=row['full']['host']
            if row['family']=='stale-receipt':
                previous=host['changeHistory'][0]['currentSha256']
                current=row['full']['files'][0]['sha256']
                self.assertEqual(previous!=current,row['expected']=='ask')
            if row['family']=='authorization-revocation':
                self.assertEqual(host['userRequest'],host['authorizationHistory'][-1]['content'])
                self.assertEqual('Cancel that action' in host['userRequest'],row['expected']=='deny')

    def test_capacity_errors_separate_from_decisions(self):
        rows=[json.loads(x) for x in (HERE/'results/long-4096.jsonl').read_text().splitlines()]
        self.assertEqual(len(rows),12)
        for row in rows:
            if row['size']=='overflow':
                self.assertGreater(row['prompt_tokens'],4096)
                self.assertEqual(row['error'],'http-400')
                self.assertFalse(row['allow'])
            else:
                self.assertLess(row['prompt_tokens'],4096)
                self.assertIsNone(row['error'])
                self.assertEqual(run.legacy.parse_auto(row['response'])['allow'],row['allow'])

    def test_summary_and_report_reproduce(self):
        summary=json.loads((HERE/'results/summary.json').read_text())
        lock=json.loads((HERE/'results/thresholds.json').read_text())['thresholds']
        for arm in run.ARMS:
            rows=analyze.load('test',arm)
            self.assertEqual(summary[arm]['default'],analyze.metrics(rows))
            if arm.startswith('app-'):
                self.assertEqual(summary[arm]['selected'],analyze.metrics(rows,lock[arm]['threshold']))
        section=render_report.render()
        self.assertEqual(section,(HERE/'results/report-section.md').read_text())
        self.assertIn(section,(HERE/'README.md').read_text())


if __name__=='__main__':unittest.main()
