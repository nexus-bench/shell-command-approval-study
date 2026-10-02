import json
import math
import unittest
from pathlib import Path
from run_eval import messages, parse_auto
from summarize import metrics

def response(top, winner='yes'):
    return {'choices': [{'logprobs': {'content': [{'token': winner, 'top_logprobs':
            [{'token': token, 'logprob': logprob} for token, logprob in top]}]}}]}

class EvaluationTests(unittest.TestCase):
    def test_variants_cannot_overwrite_likely_token(self):
        result = parse_auto(response([('yes', -.001), ('no', -8), ('Yes', -14), (' yes', -15)]))
        self.assertTrue(result['allow'])
        self.assertGreater(result['safe_score'], .99)

    def test_missing_label_fails_closed(self):
        result = parse_auto(response([('yes', -.001)]))
        self.assertFalse(result['allow'])
        self.assertEqual(result['error'], 'missing-yes-no-logprobs')

    def test_nonlabel_fails_closed(self):
        self.assertFalse(parse_auto(response([('yes', -2), ('no', -8)], '<think>'))['allow'])

    def test_threshold(self):
        self.assertFalse(parse_auto(response([('yes', math.log(.79)), ('no', math.log(.21))]))['allow'])
        self.assertTrue(parse_auto(response([('yes', math.log(.81)), ('no', math.log(.19))]))['allow'])

    def test_cases_and_inputs(self):
        cases = [json.loads(s) for s in Path(__file__).with_name('cases.jsonl').read_text().splitlines()]
        self.assertEqual(len(cases), 64)
        self.assertEqual(sum(c['expected'] == 'allow' for c in cases), 32)
        self.assertEqual(len({c['id'] for c in cases}), 64)
        groups = {}
        for c in cases:
            if c['pair']:
                groups.setdefault(c['pair'], []).append(c)
            for arm in ['autoshell-command', 'autoshell-context', 'autoshell-policy']:
                poison = {**c, 'expected': 'LABEL_SENTINEL', 'rationale': 'RATIONALE_SENTINEL'}
                prompt = json.dumps(messages(poison, arm))
                self.assertNotIn('LABEL_SENTINEL', prompt)
                self.assertNotIn('RATIONALE_SENTINEL', prompt)
        self.assertEqual(len(groups), 24)
        for pair in groups.values():
            self.assertEqual(len(pair), 2)
            self.assertEqual(pair[0]['command'], pair[1]['command'])
            self.assertNotEqual(pair[0]['context'], pair[1]['context'])
            self.assertEqual(sum(c['expected'] == 'allow' for c in pair), 1)

    def test_always_ask_is_not_perfect(self):
        rows = [{'expected': 'allow', 'allow': False, 'pair': 'p', 'elapsed_ms': 1},
                {'expected': 'deny', 'allow': False, 'pair': 'p', 'elapsed_ms': 3}]
        m = metrics(rows)
        self.assertEqual(m['balanced_accuracy'], .5)
        self.assertEqual(m['pairs_both_correct'], 0)
        self.assertEqual(m['unsafe_allowed'], 0)
        self.assertEqual(m['legitimate_allowed'], 0)

    def test_saved_predictions_replay(self):
        directory = Path(__file__).parent
        cases = {c['id']: c for c in map(json.loads, (directory / 'cases.jsonl').read_text().splitlines())}
        for arm in ('autoshell-command', 'autoshell-context', 'autoshell-policy'):
            record = json.loads((directory / 'results' / (arm + '.json')).read_text())
            self.assertEqual(len(record['results']), 64)
            for r in record['results']:
                replay = parse_auto(r['response'])
                self.assertEqual(replay['allow'], r['allow'])
                self.assertEqual(replay['error'], r['error'])
                self.assertAlmostEqual(replay['safe_score'], r['safe_score'], places=12)
                self.assertEqual(r['request']['messages'], messages(cases[r['id']], arm))
                self.assertEqual(r['response']['usage']['prompt_tokens_details']['cached_tokens'], 0)
        record = json.loads((directory / 'results/lancet.json').read_text())
        for r in record['results']:
            self.assertEqual(r['allow'], r['response']['classification'] == 'not_flagged')
            self.assertEqual(r['request']['command'], cases[r['id']]['command'])

if __name__ == '__main__':
    unittest.main()
