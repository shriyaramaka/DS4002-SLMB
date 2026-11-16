"""Verify the baseline rule and that saved reports match per-image predictions.

Run AFTER 04_majority_baseline.py: python Scripts/test_majority_baseline.py
No model fitting or choices based on test errors are performed by these checks.
"""
import csv
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('majority', Path(__file__).with_name('04_majority_baseline.py'))
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class BaselineChecks(unittest.TestCase):
    def test_numeric_tie_break(self):
        self.assertEqual(module.majority_class([{'taxon_id':'10'},{'taxon_id':'9'}]),'9')

    def test_order_does_not_change_class(self):
        rows=[{'taxon_id':'10'},{'taxon_id':'9'},{'taxon_id':'10'}]
        self.assertEqual(module.majority_class(rows),module.majority_class(list(reversed(rows))))

    def test_empty_training_rejected(self):
        with self.assertRaises(ValueError): module.majority_class([])

    def test_saved_predictions_match_scores(self):
        with (ROOT/'Output/Baseline/baseline_test_predictions.csv').open(newline='') as f:
            predictions=list(csv.DictReader(f))
        metrics=json.loads((ROOT/'Output/Baseline/baseline_metrics.json').read_text())
        with (ROOT/'Data/bird_images_analysis.csv').open(newline='') as f:
            all_rows=list(csv.DictReader(f))
        tests={r['photo_id']:r for r in all_rows if r['split']=='test'}
        winner=module.majority_class([r for r in all_rows if r['split']=='train'])
        self.assertEqual(set(tests),{r['photo_id'] for r in predictions})
        self.assertEqual(len(tests),len(predictions))
        for r in predictions:
            self.assertEqual(r['true_taxon_id'], tests[r['photo_id']]['taxon_id'])
            self.assertEqual(r['predicted_taxon_id'],winner)
            self.assertEqual(int(r['correct']), int(r['true_taxon_id']==winner))
        correct=sum(int(r['correct']) for r in predictions)
        self.assertEqual(metrics['correct'],correct)
        self.assertAlmostEqual(metrics['accuracy'],correct/len(predictions))
        with (ROOT/'Output/Baseline/baseline_per_species.csv').open(newline='') as f:
            species=list(csv.DictReader(f))
        self.assertEqual(sum(int(r['test_images']) for r in species),len(predictions))
        self.assertAlmostEqual(metrics['macro_recall'],sum(float(r['recall']) for r in species)/len(species))

if __name__=='__main__': unittest.main()
