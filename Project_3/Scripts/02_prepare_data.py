"""Reproduce the reviewed analysis manifest without modifying source photographs.

Run: python Scripts/02_prepare_data.py
Inputs: Data/bird_images.csv, quality_review_analysis.csv, near_duplicate_review.csv, images/.
Outputs: Data/bird_images_analysis.csv, class_mapping.json, dataset_freeze.json;
         Output/Preparation/preparation_report.json, analysis_species_split_counts.csv,
         analysis_exclusions.csv, near_duplicate_candidates.csv.
Review decisions are inputs, not automatic botanical/zoological verification.
Preparation fails on missing decisions, corrupted images, changed source hashes,
overlapping observers, unresolved candidate pairs, or absent classes in a split.
"""
from pathlib import Path
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
import numpy as np
from scipy.fft import dctn
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DATA, OUTPUT = ROOT / 'Data', ROOT / 'Output/Preparation'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read_csv(path):
    with path.open(encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)

def write_csv(path, fields, rows):
    with path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

def phash(path):
    # DCT perceptual fingerprint: screen all pairs, including different splits.
    # A low distance triggers review; it never automatically deletes an image.
    with Image.open(path) as im:
        pixels = np.asarray(im.convert('L').resize((32, 32), Image.Resampling.BICUBIC), dtype=float)
    coefficients = dctn(pixels, type=2, norm='ortho')[:8, :8].ravel()
    bits = coefficients > np.median(coefficients[1:])
    bits[0] = False
    return bits

def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    fields, source = read_csv(DATA / 'bird_images.csv')
    _, decisions = read_csv(DATA / 'quality_review_analysis.csv')
    ids = [r['photo_id'] for r in source]
    assert len(set(ids)) == len(ids), 'Duplicate source photo IDs'
    assert len({r['observation_id'] for r in source}) == len(source)
    assert len({r['photo_id'] for r in decisions}) == len(decisions)
    assert set(ids) == {r['photo_id'] for r in decisions}, 'Incomplete or stale review log'
    review = {r['photo_id']: r for r in decisions}
    for row in decisions:
        assert row['decision'] in {'retain', 'exclude'}, 'Unresolved quality decision'
        assert row['reason'].strip(), 'Every decision needs a reason'

    # Validate all original media, even when visual review excludes a file.
    fingerprints = []
    for row in source:
        path = (ROOT / row['image_path']).resolve()
        assert path.is_relative_to(DATA.resolve()), 'Image path outside Data'
        assert path.is_file(), f'Missing image {row["photo_id"]}'
        assert digest(path) == row['sha256'], f'Changed source bytes: {row["photo_id"]}'
        with Image.open(path) as im:
            im.load()
            assert (im.width, im.height) == (int(row['width']), int(row['height']))
        fingerprints.append(phash(path))

    _, pair_decisions = read_csv(DATA / 'near_duplicate_review.csv')
    pairs_reviewed = {}
    for pair in pair_decisions:
        key = tuple(sorted((pair['photo_id_a'], pair['photo_id_b'])))
        assert key not in pairs_reviewed, 'Duplicate pair decision'
        pairs_reviewed[key] = pair
    candidates = []
    for i, a in enumerate(source):
        for j in range(i):
            b = source[j]
            distance = int(np.count_nonzero(fingerprints[i] != fingerprints[j]))
            if distance > 8:
                continue
            key = tuple(sorted((a['photo_id'], b['photo_id'])))
            pair = pairs_reviewed.get(key)
            assert pair is not None and pair['decision'] in {'distinct_images', 'duplicate'}, f'Review candidate pair {key}'
            assert pair['reason'].strip()
            if pair['decision'] == 'duplicate':
                assert not all(review[k]['decision'] == 'retain' for k in key), 'Both duplicates retained'
            candidates.append(dict(photo_id_a=key[0], photo_id_b=key[1], hamming_distance=distance,
                                   cross_split=a['split'] != b['split'], decision=pair['decision'], reason=pair['reason']))

    retained = sorted((r for r in source if review[r['photo_id']]['decision'] == 'retain'), key=lambda r: int(r['photo_id']))
    assert len({r['sha256'] for r in retained}) == len(retained), 'Exact duplicate retained'
    taxa = sorted({r['taxon_id'] for r in source}, key=int)
    assert len(taxa) == 12
    groups = {}
    for row in retained:
        assert all(row[k].strip() for k in ['taxon_id', 'observer_id', 'photo_id', 'split'])
        assert row['split'] in {'train', 'validation', 'test'}
        groups.setdefault(row['observer_id'], set()).add(row['split'])
    assert all(len(splits) == 1 for splits in groups.values()), 'Observer leakage'
    counts = Counter((r['taxon_id'], r['split']) for r in retained)
    assert all(counts[(t, s)] for t in taxa for s in ['train', 'validation', 'test']), 'Missing class after exclusions'
    mapping = {'schema_version': 1, 'ordering': 'ascending numeric taxon_id', 'classes': [
        dict(class_index=i, taxon_id=t, scientific_name=next(r['scientific_name'] for r in source if r['taxon_id']==t),
             common_name=next(r['common_name'] for r in source if r['taxon_id']==t)) for i, t in enumerate(taxa)]}
    write_csv(DATA / 'bird_images_analysis.csv', fields, retained)
    (DATA / 'class_mapping.json').write_text(json.dumps(mapping, indent=2)+'\n')
    exclusions = [dict(photo_id=r['photo_id'], taxon_id=r['taxon_id'], common_name=r['common_name'], split=r['split'], reason=review[r['photo_id']]['reason'])
                  for r in source if review[r['photo_id']]['decision'] == 'exclude']
    write_csv(OUTPUT / 'analysis_exclusions.csv', ['photo_id','taxon_id','common_name','split','reason'], exclusions)
    write_csv(OUTPUT / 'analysis_species_split_counts.csv', ['taxon_id','common_name','train','validation','test','total'],
              [dict(taxon_id=t, common_name=mapping['classes'][i]['common_name'],
                    **{s: counts[(t,s)] for s in ['train','validation','test']}, total=sum(counts[(t,s)] for s in ['train','validation','test'])) for i,t in enumerate(taxa)])
    write_csv(OUTPUT / 'near_duplicate_candidates.csv', ['photo_id_a','photo_id_b','hamming_distance','cross_split','decision','reason'], candidates)
    frozen = {str(p.relative_to(ROOT)): digest(p) for p in [DATA/'bird_images.csv', DATA/'quality_review_analysis.csv',
              DATA/'near_duplicate_review.csv', DATA/'bird_images_analysis.csv', DATA/'class_mapping.json']}
    (DATA / 'dataset_freeze.json').write_text(json.dumps({'sha256': frozen, 'source_images': 'per-image hashes in both manifests'}, indent=2)+'\n')
    report = dict(source_images=len(source), analysis_images=len(retained), excluded=len(exclusions), species=len(taxa),
                  observers=len(groups), split_counts=dict(Counter(r['split'] for r in retained)),
                  observer_overlap=False, all_classes_in_all_splits=True, all_source_images_decode_and_match_hash=True,
                  near_duplicate_threshold=8, near_duplicate_candidates=len(candidates),
                  review_method='visual screening of all source contact sheets with enlarged ambiguous examples; no expert species re-identification',
                  human_expert_review_complete=False, model_trained=False, test_predictions_generated=False,
                  manifest_sha256=digest(DATA/'bird_images_analysis.csv'), class_mapping_sha256=digest(DATA/'class_mapping.json'))
    (OUTPUT / 'preparation_report.json').write_text(json.dumps(report, indent=2)+'\n')
    # Updated descriptive figures refer to the reviewed sample. The original
    # notebook outputs remain as the historical 482-image establishment EDA.
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    names = [c['common_name'] for c in mapping['classes']]
    values = [sum(counts[(t,s)] for s in ['train','validation','test']) for t in taxa]
    fig, ax = plt.subplots(figsize=(10,6))
    ax.barh(names, values, color='#365f45')
    ax.set(xlabel='Retained source photographs', title='Reviewed analysis sample by species')
    fig.tight_layout()
    fig.savefig(OUTPUT/'analysis_species_counts.png', dpi=150)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(10,6))
    left = np.zeros(len(taxa))
    for split, color in zip(['train','validation','test'], ['#365f45','#c5a64c','#6a8ca8']):
        widths = np.array([counts[(t,split)] for t in taxa])
        ax.barh(names, widths, left=left, label=split, color=color)
        left += widths
    ax.set(xlabel='Retained source photographs', title='Reviewed sample with original observer assignments')
    ax.legend(loc='upper left', bbox_to_anchor=(1.01,1))
    fig.tight_layout()
    fig.savefig(OUTPUT/'analysis_split_coverage.png', dpi=150)
    plt.close(fig)
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
