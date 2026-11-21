# Scripts

## Run order for this frozen setup

1. `02_prepare_data.py`: applies review decisions, validates source media and splits, screens DCT-hash candidates, and rebuilds Data/bird_images_analysis.csv, class_mapping.json, dataset_freeze.json and Output preparation reports/plots. No source file is silently replaced.
2. `03_check_loader.py`: actual PyTorch train/validation loading, class mapping, batch shapes, deterministic validation and reproducible seed checks; writes Output/Validation/loader_check.json. Does not score the test set.
3. `test_data_setup.py`: four meaningful negative-path tests: changed freeze, prohibited validation augmentation, misspelled split, and accidental original-manifest use.

`bird_dataset.py` is imported by the loader check and the ResNet-18 training and evaluation scripts; do not run it on its own. `requirements.txt` includes the original EDA dependencies plus scipy, torch, and torchvision for analysis setup. 

`build_dataset.py` and `01_bird_eda.ipynb` are the existing source-collection and original-sample EDA scripts. The notebook reads the original 482-image manifest and should be described as establishment EDA. Source rebuilding can recover failed downloads and change the collection; routine preparation uses the saved source manifest instead.


## Baseline analysis

4. `04_majority_baseline.py`: fits the fixed majority class using training labels only, evaluates once on the final test images, and writes the baseline rule, per-photo predictions, accuracy, macro/per-species recall and confusion matrix to Output/Baseline/. It verifies frozen input hashes and never reads image pixels.
5. `test_majority_baseline.py`: checks numeric tie-breaking, input-order independence, rejection of empty training data, and agreement of saved metrics with individual predictions.

## ResNet-18 training and evaluation

6. `05_train_resnet.py`: trains only a new 12-class output layer on a frozen ImageNet-pretrained ResNet-18, compares learning rates 0.001 and 0.0003 for 15 epochs each, and keeps the (learning rate, epoch) with the highest validation accuracy. Never loads the test images. About 6 minutes on CPU; `--device cuda` or `--device mps` are optional.
   - Inputs: Data/bird_images_analysis.csv, Data/images/, Data/class_mapping.json, Data/dataset_freeze.json (via `bird_dataset.py`); ImageNet ResNet-18 weights (downloaded to the torch hub cache on first run; needs internet).
   - Outputs: Output/ResNet/training_history.csv, training_curves.png, model_config.json, resnet18_selected.pt.
7. `test_resnet_selection.py`: unit tests for the selection rule: highest validation accuracy wins, ties go to the earlier epoch, then to the lower learning rate; empty histories are rejected.
   - Inputs: none (imports `select_best` from 05). Outputs: none.
8. `06_evaluate_resnet.py`: loads the selected checkpoint, checks its class-mapping and manifest hashes, and scores the 119 test images once in eval mode without augmentation. Run only after 05; its results must not feed back into tuning.
   - Inputs: Output/ResNet/resnet18_selected.pt, Output/ResNet/model_config.json, Output/Baseline/baseline_metrics.json, and the test split via `bird_dataset.py`. No internet needed.
   - Outputs: Output/ResNet/test_predictions.csv, test_metrics.json, per_species_metrics.csv, confusion_matrix.csv, confusion_matrix.png.
9. `test_resnet_evaluation.py`: recomputes accuracy, macro recall, per-species recall, and the confusion matrix from test_predictions.csv alone and checks they match the saved files. Run after 06.
   - Inputs: Output/ResNet/test_predictions.csv, test_metrics.json, per_species_metrics.csv, confusion_matrix.csv; Data/bird_images_analysis.csv; Data/class_mapping.json. Outputs: none.

05 and 06 reuse `digest` and `write_csv` from `04_majority_baseline.py`. All imports (torch, torchvision, matplotlib) are already in `requirements.txt`.

## Output locations

Baseline results go to `Output/Baseline/`; collection and original EDA files go to `Output/EDA/`; reviewed-data reports and plots go to `Output/Preparation/`; ResNet-18 training, checkpoint, and test results go to `Output/ResNet/`; loader verification goes to `Output/Validation/`. Preparation reads both `Data/quality_review_analysis.csv` and `Data/near_duplicate_review.csv`. 
