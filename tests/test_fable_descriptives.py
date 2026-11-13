"""Statistical regression checks for the post hoc supplement only."""
import unittest
import numpy as np

from supplement import fable_descriptives as d


class WordBootstrapTests(unittest.TestCase):
    def test_fixed_source_composition_has_no_between_source_bootstrap_noise(self):
        # Pooling these two sources would create spurious uncertainty.
        result = d.Boot().diff([np.zeros(8), np.ones(8)], [np.zeros(8)])
        self.assertEqual(result, {"estimate": 0.5, "ci95": [0.5, 0.5]})

    def test_h4_equal_intent_weights_despite_unequal_bank_sizes(self):
        # +1 in animal-intent and -1 in no-intent must cancel, even though
        # the fresh bank contains twice as many no-intent words.
        result = d.Boot().contrast([
            (0.5, [np.ones(4)]), (-0.5, [np.zeros(8)]),
            (0.5, [np.zeros(4)]), (-0.5, [np.ones(8), np.ones(8)])])
        self.assertEqual(result, {"estimate": 0.0, "ci95": [0.0, 0.0]})

    def test_response_median_resamples_whole_words(self):
        # Independent response resampling would put both percentile limits
        # at zero. Resampling the two words must allow an all-one draw.
        result = d.Boot().median([[np.zeros(100), np.ones(10)]])
        self.assertEqual(result["estimate"], 0.0)
        self.assertEqual(result["ci95"], [0.0, 1.0])
        self.assertEqual(result["undefined_draws"], 0)

    def test_conditional_median_keeps_words_without_cues(self):
        result = d.Boot().median([[np.array([]), np.array([0.25, 0.25])]])
        self.assertEqual(result["estimate"], 0.25)
        self.assertEqual(result["ci95"], [0.25, 0.25])
        self.assertGreater(result["undefined_draws"], 2000)
        self.assertLess(result["undefined_draws"], 3000)

    def test_even_median_uses_both_middle_observations(self):
        result = d.Boot().median([[np.array([1, 2, 8, 9])]])
        self.assertEqual(result["estimate"], 5.0)
        self.assertEqual(result["ci95"], [5.0, 5.0])

    def test_conditional_ratio_pairs_numerator_and_denominator(self):
        result = d.Boot().ratio([np.array([[1, 2], [10, 20]])])
        self.assertEqual(result["estimate"], 0.5)
        self.assertEqual(result["ci95"], [0.5, 0.5])
        self.assertEqual(result["undefined_draws"], 0)

    def test_empty_condition_is_not_reported_as_zero(self):
        for result in [d.Boot().median([[np.array([]), np.array([])]]),
                       d.Boot().ratio([np.zeros((2, 2))])]:
            self.assertIsNone(result["estimate"])
            self.assertIsNone(result["ci95"])
            self.assertEqual(result["undefined_draws"], d.DRAWS)
            self.assertEqual(d.fmt(result), "not estimable")


if __name__ == "__main__":
    unittest.main()
