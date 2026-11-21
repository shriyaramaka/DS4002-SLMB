"""Check the MI2 (learning rate, epoch) selection rule used by 05_train_resnet.py.

Run: python3 Scripts/test_resnet_selection.py
Pure-function checks only; no model is trained and no images are loaded.
"""
import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('resnet', Path(__file__).with_name('05_train_resnet.py'))
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

def rec(lr, epoch, val_accuracy):
    return {'lr':lr, 'epoch':epoch, 'val_accuracy':val_accuracy}

class SelectionRule(unittest.TestCase):
    def test_highest_validation_accuracy_wins(self):
        rows=[rec(0.001,1,0.50),rec(0.001,9,0.70),rec(0.0003,4,0.60)]
        self.assertEqual(module.select_best(rows),rec(0.001,9,0.70))

    def test_accuracy_tie_picks_earlier_epoch(self):
        rows=[rec(0.0003,12,70/83),rec(0.001,5,70/83),rec(0.001,8,70/83)]
        self.assertEqual(module.select_best(rows),rec(0.001,5,70/83))

    def test_accuracy_and_epoch_tie_picks_lower_lr(self):
        rows=[rec(0.001,6,70/83),rec(0.0003,6,70/83)]
        self.assertEqual(module.select_best(rows),rec(0.0003,6,70/83))
        self.assertEqual(module.select_best(list(reversed(rows))),rec(0.0003,6,70/83))

    def test_empty_history_rejected(self):
        with self.assertRaises(ValueError): module.select_best([])

if __name__=='__main__': unittest.main()
