"""Fit/evaluate the registered training-majority baseline on frozen inputs.

Run from any directory: python /path/to/Project_3/Scripts/04_majority_baseline.py
Inputs: Data/bird_images_analysis.csv, class_mapping.json, dataset_freeze.json.
Outputs: Output/Baseline/majority_baseline.json, baseline_test_predictions.csv,
         baseline_metrics.json, baseline_per_species.csv,
         baseline_confusion_matrix.csv, baseline_confusion_matrix.png.
The class is selected ONLY from training labels; test labels only score the
fixed rule. No image tensors, validation tuning, or neural model are involved.
"""
from pathlib import Path
from collections import Counter
import csv
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parents[1]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def majority_class(training_rows):
    """Ties favor the lowest numeric taxon ID, independent of input row order."""
    counts = Counter(r['taxon_id'] for r in training_rows)
    if not counts:
        raise ValueError('Cannot fit a baseline without training rows')
    return min(counts, key=lambda taxon: (-counts[taxon], int(taxon)))

def write_csv(path, fields, rows):
    with path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

def main():
    data, output = ROOT/'Data', ROOT/'Output/Baseline'
    output.mkdir(parents=True, exist_ok=True)
    freeze = json.loads((data/'dataset_freeze.json').read_text())
    for name, expected in freeze['sha256'].items():
        if digest(ROOT/name) != expected:
            raise ValueError(f'Frozen input changed: {name}')
    with (data/'bird_images_analysis.csv').open(encoding='utf-8',newline='') as f:
        rows = list(csv.DictReader(f))
    mapping = json.loads((data/'class_mapping.json').read_text())['classes']
    by_taxon = {c['taxon_id']:c for c in mapping}
    train = [r for r in rows if r['split']=='train']
    test = [r for r in rows if r['split']=='test']
    assert train and test and len({r['photo_id'] for r in test}) == len(test)
    assert not ({r['observer_id'] for r in train} & {r['observer_id'] for r in test})
    winner = majority_class(train)
    trained_rule = dict(model='training_majority', predicted_taxon_id=winner,
                        predicted_class_index=by_taxon[winner]['class_index'],
                        predicted_common_name=by_taxon[winner]['common_name'],
                        training_images=len(train), training_counts=dict(Counter(r['taxon_id'] for r in train)),
                        tie_rule='lowest numeric taxon_id', selected_from='training labels only',
                        manifest_sha256=digest(data/'bird_images_analysis.csv'),
                        class_mapping_sha256=digest(data/'class_mapping.json'))
    (output/'majority_baseline.json').write_text(json.dumps(trained_rule,indent=2)+'\n')
    predictions = [dict(photo_id=r['photo_id'], observation_id=r['observation_id'], split='test',
                        true_taxon_id=r['taxon_id'], true_class_index=by_taxon[r['taxon_id']]['class_index'],
                        predicted_taxon_id=winner, predicted_class_index=by_taxon[winner]['class_index'],
                        correct=int(r['taxon_id']==winner)) for r in test]
    write_csv(output/'baseline_test_predictions.csv',list(predictions[0]),predictions)
    # Explicit per-class support prevents zero-support classes being silently
    # interpreted as zero recall. Preparation requires every class in test.
    per_species = []
    for c in mapping:
        support = sum(r['taxon_id']==c['taxon_id'] for r in test)
        correct = support if c['taxon_id']==winner else 0
        assert support > 0
        per_species.append(dict(**c, test_images=support, correct=correct, recall=correct/support))
    write_csv(output/'baseline_per_species.csv',list(per_species[0]),per_species)
    correct = sum(r['correct'] for r in predictions)
    metrics = dict(model='training_majority', test_images=len(test), correct=correct,
                   accuracy=correct/len(test), macro_recall=sum(r['recall'] for r in per_species)/len(mapping),
                   metric_scale='accuracy and recall are fractions from 0 to 1',
                   predicted_taxon_id=winner, predicted_common_name=by_taxon[winner]['common_name'],
                   target_accuracy=0.8, correct_needed_for_80_percent=math.ceil(.8*len(test)),
                   meets_80_percent=correct/len(test)>=.8,
                   manifest_sha256=trained_rule['manifest_sha256'],
                   class_mapping_sha256=trained_rule['class_mapping_sha256'],
                   neural_model_trained=False)
    (output/'baseline_metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
    matrix = [[sum(p['true_taxon_id']==a['taxon_id'] and p['predicted_taxon_id']==b['taxon_id'] for p in predictions)
               for b in mapping] for a in mapping]
    write_csv(output/'baseline_confusion_matrix.csv', ['true_taxon_id']+[c['taxon_id'] for c in mapping],
              [dict(true_taxon_id=c['taxon_id'], **{k['taxon_id']:v for k,v in zip(mapping,row)}) for c,row in zip(mapping,matrix)])
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(10,8))
    im=ax.imshow(matrix,cmap='Blues')
    ax.set(xticks=range(12),yticks=range(12),
           xticklabels=[c['common_name'] for c in mapping],yticklabels=[c['common_name'] for c in mapping],
           xlabel='Predicted species',ylabel='True species',title='Training-majority baseline: held-out test counts')
    plt.setp(ax.get_xticklabels(),rotation=65,ha='right')
    for i,row in enumerate(matrix):
        for j,value in enumerate(row):
            if value:ax.text(j,i,str(value),ha='center',va='center',color='white' if value>8 else 'black')
    fig.colorbar(im,ax=ax,label='Images')
    fig.tight_layout()
    fig.savefig(output/'baseline_confusion_matrix.png',dpi=150)
    plt.close(fig)
    print(json.dumps(metrics,indent=2))

if __name__=='__main__':
    main()
