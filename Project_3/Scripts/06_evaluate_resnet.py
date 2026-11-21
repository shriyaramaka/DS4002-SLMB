"""Score the selected ResNet-18 once on the held-out test images.

Run from Project_3, only AFTER 05_train_resnet.py:  python3 Scripts/06_evaluate_resnet.py
All model choices (learning rate, epoch) were fixed on validation data by 05. These test
results are final reporting only: they must not feed back into training, tuning, or
checkpoint selection.

Inputs:  Output/ResNet/resnet18_selected.pt (selected state_dict, lr, epoch, mapping hash)
         Output/ResNet/model_config.json (selection record from 05)
         Data/bird_images_analysis.csv, Data/images/, Data/class_mapping.json,
         Data/dataset_freeze.json (via bird_dataset.py's test loader)
         Output/Baseline/baseline_metrics.json (baseline accuracy for comparison)
Outputs: Output/ResNet/test_predictions.csv, test_metrics.json, per_species_metrics.csv,
         confusion_matrix.csv, confusion_matrix.png
Accuracy and recall are fractions from 0 to 1, as in the baseline metrics.
"""
import importlib.util
import json
import math
import platform
from pathlib import Path

import torch
import torchvision
from torch import nn
from torchvision.models import resnet18

from bird_dataset import ROOT, make_loaders

# Reuse the baseline's hashing and CSV helpers rather than duplicating them.
spec = importlib.util.spec_from_file_location('majority', Path(__file__).with_name('04_majority_baseline.py'))
baseline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(baseline)

RESNET = ROOT/'Output/ResNet'
TARGET_ACCURACY = 0.8


def load_model(checkpoint, num_classes):
    # Same architecture as 05; pretrained weights are not needed because every
    # parameter, frozen backbone included, comes from the saved state_dict.
    model = resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    model.load_state_dict(checkpoint['state_dict'], strict=True)
    return model.eval()


def main():
    torch.use_deterministic_algorithms(True, warn_only=True)
    manifest_sha = baseline.digest(ROOT/'Data/bird_images_analysis.csv')
    mapping_sha = baseline.digest(ROOT/'Data/class_mapping.json')
    checkpoint = torch.load(RESNET/'resnet18_selected.pt', map_location='cpu', weights_only=True)
    config = json.loads((RESNET/'model_config.json').read_text())
    base = json.loads((ROOT/'Output/Baseline/baseline_metrics.json').read_text())
    if checkpoint['class_mapping_sha256'] != mapping_sha:
        raise ValueError('Checkpoint was trained with a different class mapping')
    if checkpoint['manifest_sha256'] != manifest_sha or base['manifest_sha256'] != manifest_sha:
        raise ValueError('Checkpoint or baseline was produced from a different manifest')
    if (checkpoint['lr'], checkpoint['epoch']) != (config['selected_lr'], config['selected_epoch']):
        raise ValueError('Checkpoint does not match the selection recorded in model_config.json')

    loaders, mapping_file = make_loaders()
    mapping = mapping_file['classes']
    by_index = {c['class_index']: c for c in mapping}
    model = load_model(checkpoint, len(mapping))

    # The existing test loader: unshuffled, no augmentation. Only pixels reach the model.
    test = loaders['test']
    assert test.dataset.split == 'test' and len(test.dataset) == 119
    rows_by_photo = {r['photo_id']: r for r in test.dataset.rows}
    predictions = []
    with torch.no_grad():
        for images, labels, photo_ids in test:
            predicted = model(images).argmax(1)
            for photo_id, true_index, pred_index in zip(photo_ids, labels.tolist(), predicted.tolist()):
                true, pred = by_index[true_index], by_index[pred_index]
                predictions.append(dict(photo_id=photo_id, observation_id=rows_by_photo[photo_id]['observation_id'],
                                        true_taxon_id=true['taxon_id'], true_common_name=true['common_name'],
                                        predicted_taxon_id=pred['taxon_id'], predicted_common_name=pred['common_name'],
                                        correct=int(true_index == pred_index)))
    assert len({p['photo_id'] for p in predictions}) == len(predictions) == len(test.dataset)
    baseline.write_csv(RESNET/'test_predictions.csv', list(predictions[0]), predictions)

    # Explicit support per class, so recall is never computed over zero images.
    per_species = []
    for c in mapping:
        rows = [p for p in predictions if p['true_taxon_id'] == c['taxon_id']]
        assert rows, f"No test images for {c['common_name']}"
        correct = sum(p['correct'] for p in rows)
        per_species.append(dict(taxon_id=c['taxon_id'], common_name=c['common_name'],
                                test_count=len(rows), correct=correct, recall=correct/len(rows)))
    baseline.write_csv(RESNET/'per_species_metrics.csv', list(per_species[0]), per_species)

    correct = sum(p['correct'] for p in predictions)
    accuracy = correct/len(predictions)
    metrics = dict(model='resnet18_frozen_backbone', test_images=len(predictions), correct=correct,
                   accuracy=accuracy, macro_recall=sum(r['recall'] for r in per_species)/len(mapping),
                   metric_scale='accuracy and recall are fractions from 0 to 1; improvement is in percentage points',
                   baseline_accuracy=base['accuracy'],
                   improvement_over_baseline_points=100*(accuracy - base['accuracy']),
                   beats_baseline=accuracy > base['accuracy'],
                   target_accuracy=TARGET_ACCURACY,
                   correct_needed_for_80_percent=math.ceil(TARGET_ACCURACY*len(predictions)),
                   meets_80_percent=accuracy >= TARGET_ACCURACY,
                   selected_lr=checkpoint['lr'], selected_epoch=checkpoint['epoch'],
                   selected_val_accuracy=checkpoint['val_accuracy'],
                   manifest_sha256=manifest_sha, class_mapping_sha256=mapping_sha,
                   test_scored_once=True, used_for_tuning=False, neural_model_trained=True,
                   python=platform.python_version(), torch=torch.__version__, torchvision=torchvision.__version__,
                   device='cpu')
    (RESNET/'test_metrics.json').write_text(json.dumps(metrics, indent=2)+'\n')

    names = [c['common_name'] for c in mapping]
    matrix = [[sum(p['true_taxon_id'] == a['taxon_id'] and p['predicted_taxon_id'] == b['taxon_id'] for p in predictions)
               for b in mapping] for a in mapping]
    baseline.write_csv(RESNET/'confusion_matrix.csv', ['true_species']+names,
                       [dict(true_species=name, **dict(zip(names, row))) for name, row in zip(names, matrix)])

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(matrix, cmap='Blues')
    ax.set(xticks=range(len(names)), yticks=range(len(names)), xticklabels=names, yticklabels=names,
           xlabel='Predicted species', ylabel='True species',
           title=f'ResNet-18 held-out test counts: {correct}/{len(predictions)} correct')
    plt.setp(ax.get_xticklabels(), rotation=65, ha='right')
    peak = max(max(row) for row in matrix)
    for i, row in enumerate(matrix):
        for j, value in enumerate(row):
            if value:
                ax.text(j, i, str(value), ha='center', va='center', color='white' if value > peak/2 else 'black')
    fig.colorbar(im, ax=ax, label='Images')
    fig.tight_layout()
    fig.savefig(RESNET/'confusion_matrix.png', dpi=150)
    plt.close(fig)
    print(json.dumps(metrics, indent=2))


if __name__ == '__main__':
    main()
