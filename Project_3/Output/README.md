# Output

Generated figures, tables, model rules, and verification reports are grouped by stage. The original 482-image EDA and the reviewed 467-image analysis are kept separate. Moving these files does not change their numerical contents. Preparation, loader, and baseline outputs were regenerated after restoring the duplicate-review input and updating the dataset freeze.

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

## ResNet

ResNet-18 with a frozen ImageNet backbone and a trained 12-class output layer. Selected on validation: learning rate 0.001, epoch 12 (42/83 = 50.602%). Scored once on test: **73/119 correct, 61.345% accuracy, macro recall 60.553%**. This beats the 10.084% baseline by 51.26 percentage points but **does not meet the 80% goal** (96 correct needed). Accuracy and recall are fractions from 0 to 1.

Written by 05_train_resnet.py (train/validation only):

| File | Contents |
|---|---|
| [training_history.csv](ResNet/training_history.csv) | One row per learning rate and epoch (30 rows). Columns: `lr`, `epoch` (1–15), `train_loss` and `train_accuracy` (averaged over the epoch's augmented training batches), `val_loss` and `val_accuracy` (full validation pass after the epoch, no augmentation). Loss is mean cross-entropy per image. |
| [training_curves.png](ResNet/training_curves.png) | Loss and accuracy by epoch for train (dashed) and validation (solid) at both learning rates; the selected epoch is marked with a dotted line and a star. |
| [model_config.json](ResNet/model_config.json) | Model and run record. Keys: `architecture`, `pretrained_weights`, `frozen_layers`, `trainable_layers`, `trainable_parameters` (6,156), `batchnorm_mode`, `predictors`, `loss`, `optimizer`, `learning_rates_compared`, `batch_size`, `epochs_per_learning_rate`, `seed`, `selection_rule`, `selected_lr`, `selected_epoch`, `selected_val_accuracy`, `train_metrics`, `val_metrics`, `python`, `torch`, `torchvision`, `device`, `deterministic_algorithms`, `manifest_sha256`, `class_mapping_sha256`, `split_sizes`, `test_set_used_for_selection` (false), `test_set_scored` (false at training time), `checkpoint`, `checkpoint_bytes`, `deviations_from_MI2`. |
| [resnet18_selected.pt](ResNet/resnet18_selected.pt) | Selected model, 44.8 MB. A dictionary saved with `torch.save`: `state_dict` (all ResNet-18 weights, including the 12-class `fc` layer), `lr`, `epoch`, `val_accuracy`, `class_mapping_sha256`, `manifest_sha256`, `architecture`, `num_classes`. Load with `torch.load(path, weights_only=True)`. |

Written by 06_evaluate_resnet.py (test split, scored once after selection):

| File | Contents |
|---|---|
| [test_predictions.csv](ResNet/test_predictions.csv) | One row per test image (119). Columns: `photo_id`, `observation_id`, `true_taxon_id`, `true_common_name`, `predicted_taxon_id`, `predicted_common_name`, `correct` (1 or 0). |
| [test_metrics.json](ResNet/test_metrics.json) | Test summary. Keys: `model`, `test_images`, `correct`, `accuracy`, `macro_recall`, `metric_scale`, `baseline_accuracy` (read from Baseline/baseline_metrics.json), `improvement_over_baseline_points` (percentage points), `beats_baseline`, `target_accuracy` (0.8), `correct_needed_for_80_percent` (96), `meets_80_percent`, `selected_lr`, `selected_epoch`, `selected_val_accuracy`, `manifest_sha256`, `class_mapping_sha256`, `test_scored_once`, `used_for_tuning`, `neural_model_trained`, `python`, `torch`, `torchvision`, `device`. |
| [per_species_metrics.csv](ResNet/per_species_metrics.csv) | One row per species in class-mapping order. Columns: `taxon_id`, `common_name`, `test_count` (test images of that species), `correct`, `recall` (correct / test_count). |
| [confusion_matrix.csv](ResNet/confusion_matrix.csv) | 12 × 12 counts. Rows are true species (`true_species` column), columns are predicted species, both labelled with common names in class-mapping order. The diagonal is correct predictions. |
| [confusion_matrix.png](ResNet/confusion_matrix.png) | Heatmap of the confusion matrix with counts in the cells; axes labelled "True species" and "Predicted species". |

## Validation

Recorded setup environment and rerun loader verification.

| File | Contents |
|---|---|
| [loader_check.json](Validation/loader_check.json) | Saved loader/determinism checks. |
| [setup_environment.json](Validation/setup_environment.json) | Recorded setup software and platform. |

## Recreating outputs

From the project root, build_dataset.py writes the collection summary to Output/EDA, and 01_bird_eda.ipynb writes its original-sample EDA there. Routine preparation uses 02_prepare_data.py and writes Output/Preparation. The loader check writes Output/Validation/loader_check.json. The majority baseline writes Output/Baseline. 05_train_resnet.py writes the training files and checkpoint to Output/ResNet, and 06_evaluate_resnet.py adds the test results there. Do not refresh the live collection over frozen inputs just to regenerate figures.


