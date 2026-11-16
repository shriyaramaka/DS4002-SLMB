# Output

## Completed preparation and loader verification

- preparation_report.json: 482 source / 467 retained / 15 excluded; 265/83/119 splits; 56 observers; 12 classes; integrity, overlap, and class-coverage checks.
- analysis_exclusions.csv: excluded IDs, classes, original splits, and reasons.
- analysis_species_split_counts.csv: final species counts per original partition.
- analysis_species_counts.png and analysis_split_coverage.png: descriptive figures for the reviewed sample.
- near_duplicate_candidates.csv: six DCT-hash candidates and their recorded review outcomes, none confirmed duplicates. This is not exhaustive near-duplicate verification.
- loader_check.json: genuine successful PyTorch batch, mapping, train/validation iteration, determinism and seed checks. No model fitting or test scoring.
- setup_environment.json: exact tested package versions and platform.

## Original establishment EDA retained unchanged

01_species_counts.png, 02_split_coverage.png, 03_observers_and_months.png, 04_image_dimensions.png, and 05_example_images.png concern the original 482 images. So do species_summary.csv, species_split_counts.csv, observer_counts.csv, month_counts.csv, missing_values.csv, image_integrity.csv, pixel_duplicate_candidates.csv, build_summary.json, and eda_summary.json. The old summary's pending human review flag is historical; the new review is explicitly amateur reviewed.


## Completed training-majority baseline

- majority_baseline.json: fixed class chosen from the final training labels, tie rule, training class counts, and data/mapping checksums.
- baseline_test_predictions.csv: photo_id, observation_id, split, true_taxon_id, true_class_index, predicted_taxon_id, predicted_class_index, correct (1/0); one row per eligible held-out test image.
- baseline_metrics.json: 12/119 correct, accuracy 0.1008403361 (10.084%), macro recall 0.0833333333 (8.333%), and the 80% threshold. The predicted class is Northern Cardinal.
- baseline_per_species.csv: class_index, taxon_id, scientific_name, common_name, test_images, correct and recall.
- baseline_confusion_matrix.csv: rows are true taxon IDs and columns predicted taxon IDs; entries are counts.
- baseline_confusion_matrix.png: labeled visualization of the same matrix.

Recreate these with Scripts/04_majority_baseline.py. The majority rule is determined from training only; test labels score the already fixed rule. These are actual executed results, not anticipated scores. Preparation_report and loader_check flags describe those individual stages and do not assert that the separate baseline stage has never run.
