"""Reusable image-only dataset and reproducible loaders for the frozen bird sample.

Import from another script in Scripts: from bird_dataset import make_loaders
Each batch is (images [B,3,224,224], labels [B], photo_ids).
Does not download weights, train a model, or compute test accuracy.
"""
from pathlib import Path
import csv
import hashlib
import json
import random
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from torchvision.transforms import InterpolationMode
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)

def seed_everything(seed=4002):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    # Same environment/seed is reproducible; devices/versions may still differ.
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True

def verify_freeze(root=ROOT):
    root = Path(root).resolve()
    freeze = json.loads((root / 'Data/dataset_freeze.json').read_text())
    for name, expected in freeze['sha256'].items():
        actual = hashlib.sha256((root / name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f'Frozen data changed: {name}. Review and rerun preparation before training.')

def image_transform(training=False):
    # MI2 specifies a direct 224x224 resize. Do not silently substitute the
    # weights' default 256px resize/center crop: that would change preprocessing.
    steps = [transforms.Resize((224,224), interpolation=InterpolationMode.BILINEAR, antialias=True)]
    if training:
        steps.append(transforms.RandomHorizontalFlip(p=0.5))
    steps += [transforms.ToTensor(), transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD)]
    return transforms.Compose(steps)

class BirdDataset(Dataset):
    def __init__(self, split, root=ROOT, manifest='Data/bird_images_analysis.csv', augment=None):
        if split not in {'train','validation','test'}:
            raise ValueError('split must be train, validation, or test')
        self.root = Path(root).resolve()
        verify_freeze(self.root)
        canonical = (self.root / 'Data/bird_images_analysis.csv').resolve()
        requested = (self.root / manifest).resolve()
        if requested != canonical:
            raise ValueError('Use the frozen analysis manifest; do not silently switch datasets.')
        self.mapping = json.loads((self.root / 'Data/class_mapping.json').read_text())
        classes = self.mapping['classes']
        self.class_to_index = {c['taxon_id']: c['class_index'] for c in classes}
        if sorted(self.class_to_index.values()) != list(range(12)):
            raise ValueError('Expected exactly 12 class indices, 0 through 11')
        with requested.open(encoding='utf-8', newline='') as f:
            self.rows = [r for r in csv.DictReader(f) if r['split'] == split]
        if not self.rows:
            raise ValueError(f'Empty split: {split}')
        self.split = split
        augment = split == 'train' if augment is None else augment
        if augment and split != 'train':
            raise ValueError('Validation/test augmentation is prohibited')
        self.transform = image_transform(training=augment)

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, index):
        row = self.rows[index]
        path = (self.root / row['image_path']).resolve()
        if not path.is_relative_to(self.root / 'Data'):
            raise ValueError('Image path outside Data')
        # Recheck bytes at read time so a changed image cannot silently train.
        if hashlib.sha256(path.read_bytes()).hexdigest() != row['sha256']:
            raise ValueError(f'Image changed: {row["photo_id"]}')
        with Image.open(path) as im:
            image = self.transform(im.convert('RGB'))
        return image, self.class_to_index[row['taxon_id']], row['photo_id']

def _seed_worker(worker_id):
    worker_seed = torch.initial_seed() % (2**32)
    random.seed(worker_seed)
    np.random.seed(worker_seed)

def make_loaders(root=ROOT, batch_size=32, seed=4002, num_workers=0):
    """Call afresh with the same seed for EACH learning-rate candidate.

    num_workers=0 is portable on Windows/macOS and notebooks; use a main guard
    in scripts before increasing it. Only the training split is shuffled.
    """
    seed_everything(seed)
    datasets = {s: BirdDataset(s, root=root) for s in ['train','validation','test']}
    loaders = {}
    for split, dataset in datasets.items():
        generator = torch.Generator().manual_seed(seed)
        loaders[split] = DataLoader(dataset, batch_size=batch_size, shuffle=split=='train',
                                    num_workers=num_workers, drop_last=False,
                                    generator=generator, worker_init_fn=_seed_worker)
    return loaders, datasets['train'].mapping
