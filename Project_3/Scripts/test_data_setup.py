"""Small failure-path checks for the handoff (no model/test scoring).

Run: python Scripts/test_data_setup.py
Checks that freeze corruption, wrong split names, and validation augmentation
cannot silently enter an experiment. Complete media/batch checks are separate.
"""
from pathlib import Path
import shutil
import tempfile
import unittest
from bird_dataset import ROOT, BirdDataset, verify_freeze

class SetupGuards(unittest.TestCase):
    def test_freeze_rejects_changed_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'Data').mkdir()
            for path in (ROOT/'Data').glob('*'):
                if path.is_file():
                    shutil.copy2(path, root/'Data'/path.name)
            verify_freeze(root)
            with (root/'Data/bird_images_analysis.csv').open('a') as f:
                f.write('\n')
            with self.assertRaisesRegex(ValueError, 'Frozen data changed'):
                verify_freeze(root)

    def test_validation_cannot_be_augmented(self):
        with self.assertRaisesRegex(ValueError, 'augmentation'):
            BirdDataset('validation', augment=True)

    def test_split_typo_cannot_silently_load_training(self):
        with self.assertRaisesRegex(ValueError, 'split'):
            BirdDataset('validaton')

    def test_original_manifest_cannot_replace_analysis_manifest(self):
        with self.assertRaisesRegex(ValueError, 'frozen analysis manifest'):
            BirdDataset('train', manifest='Data/bird_images.csv')

if __name__ == '__main__':
    unittest.main()
