# Identifying Southwest Virginia Bird Species from Photographs

DS 4002, Section 002 · SM: Statistics and Modelling · Maggie Parkhurst and Shriya Ramaka

We will identify 12 selected bird species using image pixels, targeting at least 80% accuracy on photographs from held-out observers. **Data preparation, image loading, and the training-majority baseline are complete. ResNet-18 training and evaluation are still pending.** This is not a completed MI3 model analysis yet.

The original collection has 482 photographs. Documented quality screening retains 467: **265 train / 83 validation / 119 test**. All species occur in each split; no observer crosses splits. Source labels were not independently expert-verified. The fixed training-majority baseline predicts Northern Cardinal and scores **12/119 = 10.084% accuracy**, with macro recall **8.333%**. $$##INSERT NEURAL MODEL ACCURACY HERE.##$$

## Software and platform

Use Python 3.10+ with numpy, pandas, Pillow, matplotlib, scipy, torch, torchvision, JupyterLab, and ipykernel. Install Scripts/requirements.txt in a virtual environment. The setup was tested on Linux/CPU; exact tested versions appear in Output/setup_environment.json. Torch and torchvision must be compatible builds for your platform. A GPU is not required for preparation or the baseline. Installing packages requires internet; the completed data/loader/baseline stages then use included local inputs only.

## Contents and documentation map

| Location | Files and contents |
|---|---|
| Project root | README.md (orientation), LICENSE.md (code), REFERENCES.md (IEEE)|
| Data/ | README.md, original bird_images.csv, reviewed bird_images_analysis.csv, download_manifest.csv, selected_species.csv, quality_review.csv (original), quality_review_analysis.csv (analysis), near_duplicate_review.csv, review_policy.md, class_mapping.json, dataset_freeze.json. |
| Data/images/ | Original 482 source JPEGs organized by taxon ID and photo ID; excluded photos remain for provenance. |
| Data/raw/ | Cached collection/pilot JSON, plus quality_review_before_setup.csv. Use the manifests to locate the modeling inputs; raw metadata are not features. |
| Scripts/ | README.md, requirements.txt, build_dataset.py, 01_bird_eda.ipynb, 02_prepare_data.py, bird_dataset.py, 03_check_loader.py, test_data_setup.py, 04_majority_baseline.py, test_majority_baseline.py. |
| Output/ | README.md, original EDA figures/tables, reviewed-sample preparation reports/plots, loader verification, software versions, baseline rule/predictions/metrics/per-species scores/confusion matrix. The Output README enumerates them. |

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
│   └── test_majority_baseline.py
│
└── Output/
    ├── README.md
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
    ├── Baseline/
    │   ├── majority_baseline.json
    │   ├── baseline_test_predictions.csv
    │   ├── baseline_metrics.json
    │   ├── baseline_per_species.csv
    │   ├── baseline_confusion_matrix.csv
    │   └── baseline_confusion_matrix.png
    └── Validation/
        ├── loader_check.json
        └── setup_environment.json
```

`<taxon_id>` and `<photo_id>` represent species folders and individual photograph filenames. The image manifests list each photograph’s exact path. Observation JSON filenames follow the displayed patterns for each selected species.

The two MI2 plots in Data/ are documentation copies of the original figures in Output/EDA/. $$##ResNet-18 scripts and results will be added to this map when completed.$$##

## Reproduce the completed results

1. Extract Project_3.zip and open a terminal **inside Project_3**, where Data, Scripts, and Output are located.
2. Create an environment with `python -m venv .venv`. Activate it using `source .venv/bin/activate` on macOS/Linux or `.venv\Scripts\activate` on Windows.
3. Install dependencies: `python -m pip install -r Scripts/requirements.txt`.
4. Rebuild the reviewed sample: `python Scripts/02_prepare_data.py`. It applies saved review decisions, verifies image hashes and splits, and recreates the analysis manifest, mapping, freeze, reports, and plots. Expected: 467 images, 265/83/119 split sizes, 12 species, 56 observers, no overlap.
5. Check loading: `python Scripts/03_check_loader.py`. Expected: passed=true, tensors shaped [32,3,224,224], deterministic validation transforms, and repeatable seeded training loading. It does not score a model.
6. Run preparation/loader guard tests: `python Scripts/test_data_setup.py`.
7. Run baseline tests: `python Scripts/test_majority_baseline.py`.
8. Recreate baseline predictions and scores: `python Scripts/04_majority_baseline.py`. Expected: predicted species Northern Cardinal (taxon 9083), 12 correct of 119, accuracy 0.1008403361, macro recall 0.0833333333. Scores are fractions from 0 to 1. Compare Output/baseline_metrics.json with baseline_test_predictions.csv.

The original notebook can be opened with `jupyter lab Scripts/01_bird_eda.ipynb` and run in order for establishment EDA. It uses the original 482-image manifest. Numbered original plots and eda_summary.json therefore describe that sample; analysis_* outputs describe the reviewed 467-image sample. They are deliberately retained separately.

Do not rerun build_dataset.py over the frozen project as part of routine modeling. It is the original collection script and may recover failed downloads or change cached inputs. Preserve the included source files for reproducibility. If review decisions change deliberately, rerun preparation, validate, and document a new dataset version before training. The loader refuses silently changed frozen inputs.

## Permissions and references

The existing MIT LICENSE.md applies to project code/documentation; photo and metadata permissions remain source-specific. Both manifests retain original credits and source links. See Data/README.md and Data/review_policy.md.

## References

All IEEE references are listed in [REFERENCES.md](REFERENCES.md). Individual photograph credits are recorded in the image manifests.
