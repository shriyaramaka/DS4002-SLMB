# Scripts

## Run order for this frozen setup

1. `02_prepare_data.py`: applies review decisions, validates source media and splits, screens DCT-hash candidates, and rebuilds Data/bird_images_analysis.csv, class_mapping.json, dataset_freeze.json and Output preparation reports/plots. No source file is silently replaced.
2. `03_check_loader.py`: actual PyTorch train/validation loading, class mapping, batch shapes, deterministic validation and reproducible seed checks; writes Output/Validation/loader_check.json. Does not score the test set.
3. `test_data_setup.py`: four meaningful negative-path tests: changed freeze, prohibited validation augmentation, misspelled split, and accidental original-manifest use.

`bird_dataset.py` is imported by the future training code; do not run it as a training script. `requirements.txt` includes the original EDA dependencies plus scipy, torch, and torchvision for analysis setup. 

`build_dataset.py` and `01_bird_eda.ipynb` are the existing source-collection and original-sample EDA scripts. The notebook reads the original 482-image manifest and should be described as establishment EDA. Source rebuilding can recover failed downloads and change the collection; routine preparation uses the saved source manifest instead.


## Baseline analysis

4. `04_majority_baseline.py`: fits the fixed majority class using training labels only, evaluates once on the final test images, and writes the baseline rule, per-photo predictions, accuracy, macro/per-species recall and confusion matrix to Output/Baseline/. It verifies frozen input hashes and never reads image pixels.
5. `test_majority_baseline.py`: checks numeric tie-breaking, input-order independence, rejection of empty training data, and agreement of saved metrics with individual predictions.

$$##ResNet-18 training and evaluation are pending.##$$

## Output locations

Collection and original EDA files go to `Output/EDA/`; reviewed-data reports and plots go to `Output/Preparation/`; loader verification goes to `Output/Validation/`; baseline results go to `Output/Baseline/`. Preparation reads both `Data/quality_review_analysis.csv` and `Data/near_duplicate_review.csv`. 
