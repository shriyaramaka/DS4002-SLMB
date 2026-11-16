"""Verify the prepared loader without fitting a model or scoring test images.

Run: python Scripts/03_check_loader.py
Output: Output/Validation/loader_check.json. Exercises complete train/validation loading,
mapping, deterministic validation, train-only augmentation, and repeat seeds.
Test media integrity is checked by 02_prepare_data.py, not used for tuning here.
"""
from pathlib import Path
import json
import platform
import torch
import torchvision
from bird_dataset import BirdDataset, make_loaders, ROOT

def main():
    # Keep this small CPU check fast and avoid platform-specific subprocesses.
    torch.set_num_threads(2)
    loaders, mapping = make_loaders()
    observed = {}
    first = {}
    for split in ['train', 'validation']:
        ids = []
        for x, y, photo_ids in loaders[split]:
            assert x.ndim == 4 and tuple(x.shape[1:]) == (3,224,224)
            assert x.dtype == torch.float32 and torch.isfinite(x).all()
            assert y.dtype == torch.int64 and int(y.min()) >= 0 and int(y.max()) < 12
            assert all(isinstance(pid, str) for pid in photo_ids)
            if split not in first:
                first[split] = (x.clone(), y.clone(), list(photo_ids))
            ids.extend(photo_ids)
        assert len(set(ids)) == len(ids) == len(loaders[split].dataset)
        observed[split] = len(ids)
    v = loaders['validation'].dataset
    assert torch.equal(v[0][0], v[0][0]), 'Validation transform changed'
    try:
        BirdDataset('validation', augment=True)
        raise AssertionError('Validation augmentation was accepted')
    except ValueError:
        pass
    # Verify class-index agreement with manifest keys for every eligible row.
    for split in ['train','validation','test']:
        ds = loaders[split].dataset
        assert {r['taxon_id'] for r in ds.rows} == set(ds.class_to_index)
    # Same seed gives the same first shuffled/augmented training batch.
    again, _ = make_loaders(seed=4002)
    x,y,pids = next(iter(again['train']))
    a,b,c = first['train']
    assert torch.equal(x,a) and torch.equal(y,b) and list(pids)==c
    result = dict(passed=True, batch_shape=list(a.shape), label_dtype=str(b.dtype),
                  classes=len(mapping['classes']), complete_splits_loaded=observed,
                  split_sizes={s:len(l.dataset) for s,l in loaders.items()},
                  validation_deterministic=True, seeded_training_reproducible=True,
                  test_images_scored=False, model_fitted=False,
                  python=platform.python_version(), torch=torch.__version__, torchvision=torchvision.__version__)
    (ROOT/'Output/Validation').mkdir(parents=True, exist_ok=True)
    (ROOT/'Output/Validation/loader_check.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__ == '__main__':
    main()
