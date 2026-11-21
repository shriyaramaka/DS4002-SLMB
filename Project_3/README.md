# Identifying Southwest Virginia Bird Species from Photographs

DS 4002, Section 002 · SM: Statistics and Modelling · Maggie Parkhurst and Shriya Ramaka

We identify 12 selected bird species using image pixels, targeting at least 80% accuracy on photographs from held-out observers. **Data preparation, image loading, the training-majority baseline, and ResNet-18 training and evaluation are complete.**

The original collection has 482 photographs. Documented quality screening retains 467: **265 train / 83 validation / 119 test**. All species occur in each split; no observer crosses splits. Source labels were not independently expert-verified. The fixed training-majority baseline predicts Northern Cardinal and scores **12/119 = 10.084% accuracy**, with macro recall **8.333%**.

## Results

An ImageNet-pretrained ResNet-18 [6], [7] with a frozen backbone and a new 12-class output layer, trained with Adam [11] following the fixed-feature-extractor approach in [1], scores **73/119 = 61.345% test accuracy**, with macro recall **60.553%**. That is **51.26 percentage points above the 10.084% baseline**. **The 80% goal was not met:** it requires 96 of 119 correct, and the model was 23 short.

The learning rate and epoch were selected on validation data only: **learning rate 0.001, epoch 12**, with validation accuracy 42/83 = 50.602%. The test set was scored once, after selection, and was not used for tuning. Test accuracy is higher than validation accuracy; with 83 and 119 images, one image changes either score by roughly one percentage point.

Per-species test recall ranges from 100% (Great Blue Heron, Song Sparrow) to 10% (Mourning Dove, 1/10) and 12.5% (Red-winged Blackbird, 1/8). The most frequent confusions are Mourning Dove predicted as Barn Swallow or Eastern Bluebird; Barn Swallow, American Robin, and Eastern Bluebird with one another; and Eastern Phoebe with Carolina Chickadee. See Output/ResNet/per_species_metrics.csv and confusion_matrix.png. On the training data the selected learning rate reached 83–89% accuracy by epochs 12–15 while validation accuracy stayed between 43% and 51% from epoch 7 onward, a substantial generalization gap (Output/ResNet/training_curves.png).

## Software and platform

Use Python 3.10+ with numpy, pandas, Pillow, matplotlib, scipy, torch, torchvision, JupyterLab, and ipykernel. Install Scripts/requirements.txt in a virtual environment. Preparation and the baseline were tested on Linux/CPU (versions in Output/Validation/setup_environment.json). ResNet-18 training and evaluation ran on macOS/CPU with Python 3.13.3, torch 2.15.0, and torchvision 0.29.2 (recorded in Output/ResNet/model_config.json and test_metrics.json). Torch and torchvision must be compatible builds for your platform. A GPU is not required.

Installing packages requires internet. **The ImageNet-pretrained ResNet-18 weights (about 45 MB) download automatically the first time 05_train_resnet.py runs, so that step also requires internet access.** They are cached in the torch hub directory (`~/.cache/torch/hub/checkpoints/resnet18-f37072fd.pth` on macOS/Linux) and reused afterwards. On a python.org macOS install, a `CERTIFICATE_VERIFY_FAILED` error during this download is fixed by running `/Applications/Python 3.x/Install Certificates.command` once. Evaluation (06) does not need the pretrained weights or internet; it loads the saved checkpoint.

## Contents and documentation map

| Location | Files and contents |
|---|---|
| Project root | README.md (orientation), LICENSE.md (code), REFERENCES.md (IEEE)|
| Data/ | README.md, original bird_images.csv, reviewed bird_images_analysis.csv, download_manifest.csv, selected_species.csv, quality_review.csv (original), quality_review_analysis.csv (analysis), near_duplicate_review.csv, review_policy.md, class_mapping.json, dataset_freeze.json. |
| Data/images/ | Original 482 source JPEGs organized by taxon ID and photo ID; excluded photos remain for provenance. |
| Data/raw/ | Cached collection/pilot JSON, plus quality_review_before_setup.csv. Use the manifests to locate the modeling inputs; raw metadata are not features. |
| Scripts/ | README.md, requirements.txt, build_dataset.py, 01_bird_eda.ipynb, 02_prepare_data.py, bird_dataset.py, 03_check_loader.py, test_data_setup.py, 04_majority_baseline.py, test_majority_baseline.py, 05_train_resnet.py, test_resnet_selection.py, 06_evaluate_resnet.py, test_resnet_evaluation.py. |
| Output/ | README.md and one folder per stage: Baseline/ (baseline rule, predictions, metrics, per-species scores, confusion matrix), EDA/ (original EDA figures/tables), Preparation/ (reviewed-sample reports/plots), ResNet/ (training history and curves, model configuration, selected checkpoint, test predictions, metrics, per-species scores, confusion matrix), Validation/ (loader verification, setup software versions). The Output README enumerates them. |

### Repository structure

```text
Project_3/
├── README.md
├── LICENSE.md
├── REFERENCES.md
│
├── Data/
│   ├── README.md
│   ├── bird_images.csv
│   ├── bird_images_analysis.csv
│   ├── selected_species.csv
│   ├── download_manifest.csv
│   ├── quality_review.csv
│   ├── quality_review_analysis.csv
│   ├── near_duplicate_review.csv
│   ├── review_policy.md
│   ├── class_mapping.json
│   ├── dataset_freeze.json
│   ├── 02_split_coverage.png
│   ├── 03_observers_and_months.png
│   ├── images/
│   │   └── <taxon_id>/
│   │       └── <photo_id>.jpg
│   └── raw/
│       ├── observations_<taxon_id>_200.json
│       ├── species_counts.json
│       ├── quality_review_before_setup.csv
│       └── pilot/
│           ├── observations_<taxon_id>.json
│           ├── species_counts.json
│           └── tables/
│               ├── bird_images.csv
│               ├── download_manifest.csv
│               ├── selected_species.csv
│               └── species_availability.csv
│
├── Scripts/
│   ├── README.md
│   ├── requirements.txt
│   ├── build_dataset.py
│   ├── 01_bird_eda.ipynb
│   ├── 02_prepare_data.py
│   ├── bird_dataset.py
│   ├── 03_check_loader.py
│   ├── test_data_setup.py
│   ├── 04_majority_baseline.py
│   ├── test_majority_baseline.py
│   ├── 05_train_resnet.py
│   ├── test_resnet_selection.py
│   ├── 06_evaluate_resnet.py
│   └── test_resnet_evaluation.py
│
└── Output/
    ├── README.md
    ├── Baseline/
    │   ├── majority_baseline.json
    │   ├── baseline_test_predictions.csv
    │   ├── baseline_metrics.json
    │   ├── baseline_per_species.csv
    │   ├── baseline_confusion_matrix.csv
    │   └── baseline_confusion_matrix.png
    ├── EDA/
    │   ├── 01_species_counts.png
    │   ├── 02_split_coverage.png
    │   ├── 03_observers_and_months.png
    │   ├── 04_image_dimensions.png
    │   ├── 05_example_images.png
    │   ├── species_summary.csv
    │   ├── species_split_counts.csv
    │   ├── observer_counts.csv
    │   ├── month_counts.csv
    │   ├── missing_values.csv
    │   ├── image_integrity.csv
    │   ├── pixel_duplicate_candidates.csv
    │   ├── build_summary.json
    │   └── eda_summary.json
    ├── Preparation/
    │   ├── analysis_species_counts.png
    │   ├── analysis_split_coverage.png
    │   ├── analysis_exclusions.csv
    │   ├── analysis_species_split_counts.csv
    │   ├── near_duplicate_candidates.csv
    │   └── preparation_report.json
    ├── ResNet/
    │   ├── training_history.csv
    │   ├── training_curves.png
    │   ├── model_config.json
    │   ├── resnet18_selected.pt
    │   ├── test_predictions.csv
    │   ├── test_metrics.json
    │   ├── per_species_metrics.csv
    │   ├── confusion_matrix.csv
    │   └── confusion_matrix.png
    └── Validation/
        ├── loader_check.json
        └── setup_environment.json
```

`<taxon_id>` and `<photo_id>` represent species folders and individual photograph filenames. The image manifests list each photograph’s exact path. Observation JSON filenames follow the displayed patterns for each selected species.

The two MI2 plots in Data/ are documentation copies of the original figures in Output/EDA/.

## Reproduce the completed results

Setup:

1. Extract Project_3.zip and open a terminal **inside Project_3**, where Data, Scripts, and Output are located.
2. Create an environment with `python -m venv .venv`. Activate it using `source .venv/bin/activate` on macOS/Linux or `.venv\Scripts\activate` on Windows.
3. Install dependencies: `python -m pip install -r Scripts/requirements.txt`.

Then run these commands in order. Scores are fractions from 0 to 1.

| Step | Command | Expected result |
|---|---|---|
| 1 | `python Scripts/02_prepare_data.py` | Applies saved review decisions, verifies image hashes and splits, and recreates the analysis manifest, mapping, freeze, reports, and plots. 467 images, 265/83/119 split sizes, 12 species, 56 observers, `observer_overlap: false`. |
| 2 | `python Scripts/03_check_loader.py` | `passed: true`, batches shaped [32,3,224,224], deterministic validation transforms, repeatable seeded training loading. Does not score a model. |
| 3 | `python Scripts/test_data_setup.py` | 4 tests, OK. |
| 4 | `python Scripts/04_majority_baseline.py` | Predicts Northern Cardinal (taxon 9083) for every image: 12 of 119 correct, accuracy 0.1008403361, macro recall 0.0833333333. |
| 5 | `python Scripts/test_majority_baseline.py` | 4 tests, OK. Run after step 4; it checks the saved baseline files. |
| 6 | `python Scripts/05_train_resnet.py` | Trains 2 learning rates × 15 epochs on train/validation only. Prints `Selected lr=0.001 epoch 12 (validation accuracy 0.5060)` and a 44.8 MB checkpoint. **About 6 minutes on a laptop CPU** (5 min 47 s measured on macOS, 6 CPU threads). Downloads the pretrained weights on first run. |
| 7 | `python Scripts/test_resnet_selection.py` | 4 tests, OK. Checks the learning-rate/epoch selection rule. |
| 8 | `python Scripts/06_evaluate_resnet.py` | Scores the 119 test images once: 73 correct, accuracy 0.6134453782, macro recall 0.6055345118, `meets_80_percent: false`, `beats_baseline: true`. |
| 9 | `python Scripts/test_resnet_evaluation.py` | 4 tests, OK. Recomputes all test metrics from test_predictions.csv and checks they match the saved files. |

05 uses a fixed seed (4002), single-process loading, and PyTorch's deterministic-algorithm setting [12]. Running it twice on the same machine produced a byte-identical training_history.csv. Different hardware or library versions may give slightly different numbers.

### Using the saved checkpoint (skip retraining)

The selected model is committed at **Output/ResNet/resnet18_selected.pt** (44.8 MB, under GitHub's 100 MB file limit). It contains the full state_dict, the selected learning rate and epoch, and the class-mapping and manifest SHA-256 hashes. To reproduce the test results without retraining, run steps 1–3 if you want to verify the data, then only steps 8 and 9:

```bash
python Scripts/06_evaluate_resnet.py
python Scripts/test_resnet_evaluation.py
```

06 refuses to run if the checkpoint's class-mapping or manifest hash differs from the current Data files, or if its learning rate/epoch disagree with Output/ResNet/model_config.json. Rerunning 05 overwrites the checkpoint.

## Deviations from MI2

1. **Learning rates.** MI2 Figure 3 lists 0.003, but the MI2 Methodology text lists 0.0003. We compared 0.001 and 0.0003, following the Methodology text.
2. **Split sizes.** MI2 listed 272/90/120 images before quality review. After review the splits are 265/83/119. The 80% goal therefore requires 96 of 119 correct.
3. **Frozen BatchNorm.** The backbone's BatchNorm layers stay in eval mode during training, so their running statistics remain at the ImageNet values. This clarifies what "frozen backbone" means; only the new output layer (6,156 parameters) is trained.

These are also recorded in the `deviations_from_MI2` list in Output/ResNet/model_config.json.

The original notebook can be opened with `jupyter lab Scripts/01_bird_eda.ipynb` and run in order for establishment EDA. It uses the original 482-image manifest. Numbered original plots and eda_summary.json therefore describe that sample; analysis_* outputs describe the reviewed 467-image sample. They are deliberately retained separately.

Do not rerun build_dataset.py over the frozen project as part of routine modeling. It is the original collection script and may recover failed downloads or change cached inputs. Preserve the included source files for reproducibility. If review decisions change deliberately, rerun preparation, validate, and document a new dataset version before training. The loader refuses silently changed frozen inputs.

## Permissions and references

The existing MIT LICENSE.md applies to project code/documentation; photo and metadata permissions remain source-specific. Both manifests retain original credits and source links. See Data/README.md and Data/review_policy.md.

## References

All IEEE references are listed in [REFERENCES.md](REFERENCES.md). Individual photograph credits are recorded in the image manifests.
