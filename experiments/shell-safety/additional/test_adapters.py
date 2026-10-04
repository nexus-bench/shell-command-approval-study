import gzip, json, unittest
from run import CACHE, Kestrel, normalize, secguard_parse

class AdapterTests(unittest.TestCase):
    def require_artifacts(self, *paths):
        missing = [path for path in paths if not (CACHE/path).exists()]
        if missing:
            self.skipTest('Run additional/fetch.py to download pinned artifacts: ' + ', '.join(missing))

    def test_kestrel_export_equivalence(self):
        self.require_artifacts('source/svm.json.gz', 'kestrel/classifier.json')
        # HF weights have already been multiplied by IDF. This independently
        # checks all 50,000 features against the upstream runtime export.
        upstream = json.loads(gzip.decompress((CACHE/'source/svm.json.gz').read_bytes()))
        hf = Kestrel().model
        self.assertEqual(len(hf['ngrams']),len(upstream['ngrams']))
        for i,g in enumerate(upstream['ngrams']):
            self.assertEqual(hf['ngrams'][g],[upstream['coef'][i]*upstream['idf'][i],upstream['idf'][i]])

    def test_kestrel_reference_parity(self):
        self.require_artifacts('source/golden.jsonl', 'kestrel/classifier.json')
        model = Kestrel()
        for line in (CACHE/'source/golden.jsonl').read_text().splitlines():
            row = json.loads(line)
            self.assertEqual(normalize(row['command']),row['normalized'])
            self.assertAlmostEqual(model.score(row['command'])['score'],row['score'],places=8)

    def test_secguard_early_label_and_thinking(self):
        raw = {'completion_probabilities':[{'token':t,'logprob':-.01} for t in ['<think>','\n</think>\n','safe',' extra']]}
        result = secguard_parse(raw)
        self.assertTrue(result['allow'])
        self.assertEqual(result['output'],'<think>\n</think>\nsafe')

    def test_secguard_low_confidence_is_separate(self):
        result = secguard_parse({'completion_probabilities':[{'token':'destructive','logprob':-1}]})
        self.assertTrue(result['allow'])
        self.assertFalse(result['label_allow'])

    def test_secguard_malformed_intervenes(self):
        self.assertFalse(secguard_parse({'content':'maybe'})['allow'])

if __name__ == '__main__':
    unittest.main()
