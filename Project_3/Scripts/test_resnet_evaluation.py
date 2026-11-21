"""Verify that the saved ResNet-18 test metrics reproduce from test_predictions.csv alone.

Run AFTER 06_evaluate_resnet.py: python3 Scripts/test_resnet_evaluation.py
No model is loaded and no images are read; these checks only recompute the reports.
"""
import csv
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
RESNET=ROOT/'Output/ResNet'

def read_csv(path):
    with path.open(newline='',encoding='utf-8') as f:
        return list(csv.DictReader(f))

class EvaluationReports(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.predictions=read_csv(RESNET/'test_predictions.csv')
        cls.metrics=json.loads((RESNET/'test_metrics.json').read_text())
        cls.mapping=json.loads((ROOT/'Data/class_mapping.json').read_text())['classes']

    def test_predictions_cover_test_split(self):
        tests={r['photo_id']:r for r in read_csv(ROOT/'Data/bird_images_analysis.csv') if r['split']=='test'}
        self.assertEqual(set(tests),{p['photo_id'] for p in self.predictions})
        self.assertEqual(len(tests),len(self.predictions))
        for p in self.predictions:
            self.assertEqual(p['true_taxon_id'],tests[p['photo_id']]['taxon_id'])
            self.assertEqual(int(p['correct']),int(p['true_taxon_id']==p['predicted_taxon_id']))

    def test_accuracy_and_macro_recall(self):
        correct=sum(p['true_taxon_id']==p['predicted_taxon_id'] for p in self.predictions)
        self.assertEqual(self.metrics['test_images'],len(self.predictions))
        self.assertEqual(self.metrics['correct'],correct)
        self.assertAlmostEqual(self.metrics['accuracy'],correct/len(self.predictions))
        recalls=[]
        for c in self.mapping:
            rows=[p for p in self.predictions if p['true_taxon_id']==c['taxon_id']]
            recalls.append(sum(p['predicted_taxon_id']==c['taxon_id'] for p in rows)/len(rows))
        self.assertAlmostEqual(self.metrics['macro_recall'],sum(recalls)/len(recalls))
        self.assertEqual(self.metrics['meets_80_percent'],correct>=self.metrics['correct_needed_for_80_percent'])

    def test_per_species_csv(self):
        species=read_csv(RESNET/'per_species_metrics.csv')
        self.assertEqual([r['taxon_id'] for r in species],[c['taxon_id'] for c in self.mapping])
        for r in species:
            rows=[p for p in self.predictions if p['true_taxon_id']==r['taxon_id']]
            hits=sum(p['predicted_taxon_id']==r['taxon_id'] for p in rows)
            self.assertEqual(int(r['test_count']),len(rows))
            self.assertEqual(int(r['correct']),hits)
            self.assertAlmostEqual(float(r['recall']),hits/len(rows))

    def test_confusion_matrix_csv(self):
        names={c['taxon_id']:c['common_name'] for c in self.mapping}
        order=[names[c['taxon_id']] for c in self.mapping]
        saved=read_csv(RESNET/'confusion_matrix.csv')
        self.assertEqual([r['true_species'] for r in saved],order)
        self.assertEqual(list(saved[0])[1:],order)
        for r in saved:
            for col in order:
                expected=sum(names[p['true_taxon_id']]==r['true_species'] and names[p['predicted_taxon_id']]==col
                             for p in self.predictions)
                self.assertEqual(int(r[col]),expected)
        self.assertEqual(sum(int(r[col]) for r in saved for col in order),len(self.predictions))

if __name__=='__main__': unittest.main()
