"""Train the MI2 frozen-backbone ResNet-18 and select a learning rate/epoch on validation.

Purpose: fit only a new 12-class output layer on an ImageNet-pretrained ResNet-18,
compare two learning rates, and keep the (learning rate, epoch) with the highest
validation accuracy. The test split is never loaded, iterated, or scored here.

Inputs:  Data/bird_images_analysis.csv (frozen analysis manifest, via bird_dataset.py)
         Data/images/<taxon_id>/<photo_id>.jpg (pixels only)
         Data/class_mapping.json, Data/dataset_freeze.json
         torchvision ResNet18_Weights.IMAGENET1K_V1 (torch hub cache; downloaded if absent)
Outputs: Output/ResNet/training_history.csv, training_curves.png, model_config.json,
         resnet18_selected.pt (selected state_dict with its lr, epoch, mapping hash)

Run from Project_3:  python3 Scripts/05_train_resnet.py [--device cpu|cuda|mps]
CPU is the default. Approximate CPU runtime: 5-15 minutes for 2 learning rates x 15
epochs on a recent laptop (estimate; every epoch runs the full backbone forward pass).

Deviations from MI2 (also written to model_config.json):
1. Learning rates 0.001 and 0.0003. MI2 Figure 3 says 0.003 but the Methodology text
   says 0.0003; the Methodology value is used.
2. Final split sizes are 265/83/119 after quality review (MI2 listed 272/90/120).
   The 80% goal now requires 96 of 119 test images correct.
3. Backbone BatchNorm layers stay in eval mode during training, clarifying what a
   frozen backbone means (running statistics stay at their ImageNet values).
"""
import argparse
import copy
import csv
import importlib.util
import json
import os
import platform
from pathlib import Path

import torch
import torchvision
from torch import nn
from torchvision.models import resnet18, ResNet18_Weights

from bird_dataset import ROOT, make_loaders, seed_everything

# Reuse the baseline's hashing and CSV helpers rather than duplicating them.
spec = importlib.util.spec_from_file_location('majority', Path(__file__).with_name('04_majority_baseline.py'))
baseline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(baseline)

SEED = 4002
BATCH_SIZE = 32
EPOCHS = 15
LEARNING_RATES = (0.001, 0.0003)
NUM_CLASSES = 12
OUTPUT = ROOT/'Output/ResNet'
HISTORY_FIELDS = ['lr', 'epoch', 'train_loss', 'train_accuracy', 'val_loss', 'val_accuracy']
SELECTION_RULE = ('highest validation accuracy; ties go to the earlier epoch, '
                  'then to the lower learning rate')
DEVIATIONS = [
    'Learning rates 0.001 and 0.0003 compared. MI2 Figure 3 lists 0.003 but the MI2 '
    'Methodology text lists 0.0003; the Methodology value is used.',
    'Final split sizes are 265 train / 83 validation / 119 test after quality review '
    '(MI2 listed 272/90/120 before review). The 80% goal requires 96 of 119 correct.',
    'Backbone BatchNorm layers are kept in eval mode during training so their running '
    'statistics stay at the ImageNet values; this clarifies "frozen backbone".',
]


def select_best(records):
    """Return the record chosen by the MI2 rule.

    Highest val_accuracy wins; ties go to the earlier epoch, then the lower lr.
    Accuracies share one validation denominator, so equal counts give equal floats.
    """
    if not records:
        raise ValueError('Cannot select from an empty training history')
    return min(records, key=lambda r: (-r['val_accuracy'], r['epoch'], r['lr']))


def build_model():
    model = resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)
    # Freeze every pretrained parameter, then replace fc. The new layer's parameters
    # are created with requires_grad=True, so fc is the only trainable part.
    for p in model.parameters():
        p.requires_grad = False
    model.fc = nn.Linear(model.fc.in_features, NUM_CLASSES)
    trainable = [name for name, p in model.named_parameters() if p.requires_grad]
    assert trainable == ['fc.weight', 'fc.bias'], trainable
    return model


def set_training_mode(model):
    # requires_grad=False stops weight updates, but BatchNorm in train mode would still
    # overwrite its running mean/variance with bird-batch statistics on every forward
    # pass. Keeping the whole network in eval mode and switching only fc to train mode
    # leaves the backbone exactly as pretrained on ImageNet.
    model.eval()
    model.fc.train()


def check_split(loader):
    # This script tunes on train/validation only; the test split must never reach it.
    split = loader.dataset.split
    assert split in {'train', 'validation'}, f'{split} split must not be used for training or selection'


def train_one_epoch(model, loader, criterion, optimizer, device):
    check_split(loader)
    set_training_mode(model)
    total_loss, correct, seen = 0.0, 0, 0
    # photo_ids are discarded: only pixels and labels reach the model.
    for images, labels, _photo_ids in loader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        logits = model(images)
        loss = criterion(logits, labels)
        loss.backward()
        optimizer.step()
        # Weight by batch size so the last, smaller batch counts correctly.
        total_loss += loss.item()*labels.size(0)
        correct += (logits.argmax(1) == labels).sum().item()
        seen += labels.size(0)
    return total_loss/seen, correct/seen


@torch.no_grad()
def evaluate(model, loader, criterion, device):
    check_split(loader)
    model.eval()
    total_loss, correct, seen = 0.0, 0, 0
    for images, labels, _photo_ids in loader:
        images, labels = images.to(device), labels.to(device)
        logits = model(images)
        total_loss += criterion(logits, labels).item()*labels.size(0)
        correct += (logits.argmax(1) == labels).sum().item()
        seen += labels.size(0)
    return total_loss/seen, correct/seen


def resolve_device(name):
    if name == 'cuda' and not torch.cuda.is_available():
        raise SystemExit('--device cuda requested but CUDA is not available')
    if name == 'mps' and not torch.backends.mps.is_available():
        raise SystemExit('--device mps requested but MPS is not available')
    return torch.device(name)


def plot_curves(history, selected, path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    colors = dict(zip(LEARNING_RATES, ['tab:blue', 'tab:orange']))
    for lr in LEARNING_RATES:
        rows = [r for r in history if r['lr'] == lr]
        epochs = [r['epoch'] for r in rows]
        for ax, metric in zip(axes, ['loss', 'accuracy']):
            ax.plot(epochs, [r[f'train_{metric}'] for r in rows], '--', color=colors[lr], label=f'train, lr={lr}')
            ax.plot(epochs, [r[f'val_{metric}'] for r in rows], '-', color=colors[lr], label=f'validation, lr={lr}')
    for ax in axes:
        ax.axvline(selected['epoch'], color='gray', linestyle=':', label=f"selected: lr={selected['lr']}, epoch {selected['epoch']}")
        ax.set_xlabel('Epoch')
        ax.set_xticks(range(1, EPOCHS+1))
        ax.legend(fontsize=8)
    axes[1].plot(selected['epoch'], selected['val_accuracy'], 'k*', markersize=12)
    axes[0].set(ylabel='Cross-entropy loss (mean per image)', title='Loss by epoch')
    axes[1].set(ylabel='Accuracy (fraction correct)', title='Accuracy by epoch', ylim=(0, 1))
    fig.suptitle('ResNet-18, frozen backbone: training and validation curves')
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--device', choices=['cpu', 'cuda', 'mps'], default='cpu')
    device = resolve_device(parser.parse_args().device)

    # Needed for deterministic cuBLAS on CUDA; harmless elsewhere.
    os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
    torch.use_deterministic_algorithms(True, warn_only=True)
    torch.backends.cudnn.benchmark = False
    OUTPUT.mkdir(parents=True, exist_ok=True)

    history, best_state, split_sizes = [], None, None
    criterion = nn.CrossEntropyLoss()
    for lr in LEARNING_RATES:
        # Identical starting conditions for each learning rate: same seed, fresh
        # loaders (same shuffles/flips), and the same initial fc weights.
        seed_everything(SEED)
        loaders, mapping = make_loaders(batch_size=BATCH_SIZE, seed=SEED, num_workers=0)
        # make_loaders also builds a test Dataset (manifest rows only, no pixels). Its
        # size is recorded; its loader is discarded unused before any training.
        split_sizes = {split: len(loader.dataset) for split, loader in loaders.items()}
        del loaders['test']
        model = build_model().to(device)
        optimizer = torch.optim.Adam(model.fc.parameters(), lr=lr)
        for epoch in range(1, EPOCHS+1):
            train_loss, train_acc = train_one_epoch(model, loaders['train'], criterion, optimizer, device)
            val_loss, val_acc = evaluate(model, loaders['validation'], criterion, device)
            record = dict(lr=lr, epoch=epoch, train_loss=train_loss, train_accuracy=train_acc,
                          val_loss=val_loss, val_accuracy=val_acc)
            history.append(record)
            print(f'lr={lr} epoch {epoch:2d}: train loss {train_loss:.4f} acc {train_acc:.4f} | '
                  f'val loss {val_loss:.4f} acc {val_acc:.4f}', flush=True)
            # If this epoch is now the rule's choice over everything seen so far, keep a
            # CPU copy of its weights; only that copy is saved at the end.
            if select_best(history) is record:
                best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
                best_fc = copy.deepcopy(model.fc).cpu()

    selected = select_best(history)
    assert torch.equal(best_fc.weight, best_state['fc.weight'])

    baseline.write_csv(OUTPUT/'training_history.csv', HISTORY_FIELDS, history)
    plot_curves(history, selected, OUTPUT/'training_curves.png')

    manifest_sha = baseline.digest(ROOT/'Data/bird_images_analysis.csv')
    mapping_sha = baseline.digest(ROOT/'Data/class_mapping.json')
    checkpoint = OUTPUT/'resnet18_selected.pt'
    torch.save(dict(state_dict=best_state, lr=selected['lr'], epoch=selected['epoch'],
                    val_accuracy=selected['val_accuracy'], class_mapping_sha256=mapping_sha,
                    manifest_sha256=manifest_sha, architecture='resnet18', num_classes=NUM_CLASSES),
               checkpoint)
    checkpoint_bytes = checkpoint.stat().st_size

    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    config = dict(
        architecture='torchvision resnet18', pretrained_weights='ResNet18_Weights.IMAGENET1K_V1',
        frozen_layers=['conv1', 'bn1', 'layer1', 'layer2', 'layer3', 'layer4'],
        trainable_layers=['fc: Linear(512, 12)'], trainable_parameters=trainable_params,
        batchnorm_mode='eval during training (running statistics frozen at ImageNet values)',
        predictors='image pixels only (224x224 resize, ImageNet normalization, train-only horizontal flip)',
        loss='CrossEntropyLoss', optimizer='Adam on fc parameters only (default betas, no weight decay)',
        learning_rates_compared=list(LEARNING_RATES), batch_size=BATCH_SIZE, epochs_per_learning_rate=EPOCHS,
        seed=SEED, selection_rule=SELECTION_RULE,
        selected_lr=selected['lr'], selected_epoch=selected['epoch'],
        selected_val_accuracy=selected['val_accuracy'],
        train_metrics='averaged over each epoch on augmented batches while training',
        val_metrics='full validation pass after each epoch, eval mode, no augmentation',
        python=platform.python_version(), torch=torch.__version__, torchvision=torchvision.__version__,
        device=str(device), deterministic_algorithms='torch.use_deterministic_algorithms(True, warn_only=True)',
        manifest_sha256=manifest_sha, class_mapping_sha256=mapping_sha, split_sizes=split_sizes,
        test_set_used_for_selection=False, test_set_scored=False,
        checkpoint='Output/ResNet/resnet18_selected.pt', checkpoint_bytes=checkpoint_bytes,
        deviations_from_MI2=DEVIATIONS)
    (OUTPUT/'model_config.json').write_text(json.dumps(config, indent=2)+'\n')
    print(f"Selected lr={selected['lr']} epoch {selected['epoch']} "
          f"(validation accuracy {selected['val_accuracy']:.4f}).")
    print(f'Checkpoint {checkpoint.relative_to(ROOT)}: {checkpoint_bytes/1e6:.1f} MB (GitHub limit 100 MB).')


if __name__ == '__main__':
    main()
