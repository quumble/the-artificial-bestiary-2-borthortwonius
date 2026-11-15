import unittest
from run_corpus import rates,pair_counts,MEASURES

def row(source,word,value):return dict(source=source,word=word,values={m:value for m in MEASURES})

class Aggregation(unittest.TestCase):
    def test_all_agree(self):
        p=pair_counts([1]*5);self.assertEqual(p['pair_agreement'],1);self.assertEqual(p['resolved_pairs'],10)
    def test_one_disagrees(self):
        p=pair_counts([1,1,1,1,0]);self.assertEqual(p['pair_agreement'],.6)
    def test_unknown_not_no(self):
        p=pair_counts([1,1,0,None,None]);self.assertEqual(p['resolved_pairs'],3);self.assertEqual(p['pair_coverage'],.3);self.assertAlmostEqual(p['pair_agreement'],1/3)
    def test_all_unknown(self):
        p=pair_counts([None]*5);self.assertIsNone(p['pair_agreement']);self.assertEqual(p['pair_coverage'],0)
    def test_source_balance(self):
        rs=[row('A','x',1)]*9+[row('B','y',0)]
        r=rates(rs)[MEASURES[0]];self.assertEqual(r['weighted_detected'],.5)
    def test_word_balance(self):
        rs=[row('A','x',1)]*9+[row('A','y',0)]
        self.assertEqual(rates(rs)[MEASURES[0]]['weighted_detected'],.5)
    def test_missing_bounds(self):
        rs=[row('A','x',1),row('A','x',None),row('A','x',0),row('A','x',None)]
        r=rates(rs)[MEASURES[0]];self.assertEqual(r['available_case_rate'],.5);self.assertEqual(r['unresolved_assignment_interval'],[.25,.75])
    def test_all_unknown_rates(self):
        r=rates([row('A','x',None)])[MEASURES[0]];self.assertIsNone(r['available_case_rate']);self.assertEqual(r['unresolved_assignment_interval'],[0,1])

if __name__=='__main__':unittest.main()
