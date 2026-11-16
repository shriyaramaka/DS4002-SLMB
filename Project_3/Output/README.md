# Output

Generated figures, tables, model rules, and verification reports are grouped by stage. The original 482-image EDA and the reviewed 467-image analysis are kept separate. Moving these files does not change their numerical contents. Preparation, loader, and baseline outputs were regenerated after restoring the duplicate-review input and updating the dataset freeze.

## EDA

Initial collection and EDA for 482 images.

| File | Contents |
|---|---|
| [01_species_counts.png](EDA/01_species_counts.png) | Original sampled species counts. |
| [02_split_coverage.png](EDA/02_split_coverage.png) | Original observer-separated split counts. |
| [03_observers_and_months.png](EDA/03_observers_and_months.png) | Original contributor concentration and monthly coverage. |
| [04_image_dimensions.png](EDA/04_image_dimensions.png) | Original image sizes and aspect ratios. |
| [05_example_images.png](EDA/05_example_images.png) | Original labeled examples; photo credits remain in the manifests. |
| [species_summary.csv](EDA/species_summary.csv) | Original species and observer counts. |
| [species_split_counts.csv](EDA/species_split_counts.csv) | Original counts by species and split. |
| [observer_counts.csv](EDA/observer_counts.csv) | Original counts by contributor. |
| [month_counts.csv](EDA/month_counts.csv) | Original counts by month. |
| [missing_values.csv](EDA/missing_values.csv) | Original metadata completeness. |
| [image_integrity.csv](EDA/image_integrity.csv) | Original decoding/hash audit. |
| [pixel_duplicate_candidates.csv](EDA/pixel_duplicate_candidates.csv) | Original identical-pixel candidates. |
| [build_summary.json](EDA/build_summary.json) | Original collection settings and counts. |
| [eda_summary.json](EDA/eda_summary.json) | Original EDA summary. |

## Preparation

Saved reviewed-sample preparation outputs: 265 train, 83 validation, 119 test images.

| File | Contents |
|---|---|
| [analysis_species_counts.png](Preparation/analysis_species_counts.png) | Reviewed-sample species counts. |
| [analysis_split_coverage.png](Preparation/analysis_split_coverage.png) | Reviewed-sample split coverage. |
| [analysis_exclusions.csv](Preparation/analysis_exclusions.csv) | Excluded images and reasons. |
| [analysis_species_split_counts.csv](Preparation/analysis_species_split_counts.csv) | Reviewed counts by class and split. |
| [near_duplicate_candidates.csv](Preparation/near_duplicate_candidates.csv) | Perceptual-hash candidates and recorded review outcomes. |
| [preparation_report.json](Preparation/preparation_report.json) | Saved preparation checks and final sample counts. |

## Baseline

Completed training-majority baseline: Northern Cardinal; 12/119 correct, 10.084% accuracy.

| File | Contents |
|---|---|
| [majority_baseline.json](Baseline/majority_baseline.json) | Fixed rule selected from training labels. |
| [baseline_test_predictions.csv](Baseline/baseline_test_predictions.csv) | Baseline prediction for each test image. |
| [baseline_metrics.json](Baseline/baseline_metrics.json) | Baseline accuracy and macro recall. |
| [baseline_per_species.csv](Baseline/baseline_per_species.csv) | Per-species support, correct counts, and recall. |
| [baseline_confusion_matrix.csv](Baseline/baseline_confusion_matrix.csv) | Confusion-matrix counts. |
| [baseline_confusion_matrix.png](Baseline/baseline_confusion_matrix.png) | Labeled confusion-matrix figure. |

## Validation

Recorded setup environment and rerun loader verification.

| File | Contents |
|---|---|
| [loader_check.json](Validation/loader_check.json) | Saved loader/determinism checks. |
| [setup_environment.json](Validation/setup_environment.json) | Recorded setup software and platform. |

## Recreating outputs

From the project root, build_dataset.py writes the collection summary to Output/EDA, and 01_bird_eda.ipynb writes its original-sample EDA there. Routine preparation uses 02_prepare_data.py and writes Output/Preparation. The loader check writes Output/Validation/loader_check.json. The majority baseline writes Output/Baseline. Do not refresh the live collection over frozen inputs just to regenerate figures.


