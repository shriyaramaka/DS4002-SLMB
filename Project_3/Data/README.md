# Bird Identification Data

## Data summary

This folder contains the initial source records and final image dataset for the DS 4002 bird identification project. The dataset contains **482 validated photographs of 12 bird species**, contributed by **60 observers**, within the project's defined Southwest Virginia study area. Images were compiled from iNaturalist; no Kaggle data are used.

The final analysis inputs are **`bird_images.csv` together with the photographs in `images/`**. Each row represents one photograph from one observation. The planned model predicts species from image pixels and is evaluated using held-out accuracy. This package contains EDA, not a fitted classifier or achieved accuracy results.

## Files and folders

| Name | Description |
|---|---|
| `README.md` | Documentation for this data folder. |
| `bird_images.csv` | Final image manifest containing species labels, observation and photo IDs, image paths, dates, observer IDs, image dimensions, hashes, source credits, licenses, and proposed data splits. |
| `download_manifest.csv` | Audit of all 484 selected download attempts, including the two failures. Only successful retained images appear in `bird_images.csv`. |
| `selected_species.csv` | Source availability and sample-selection counts for the 12 requested species. |
| `quality_review.csv` | Human image-review log with review status, decisions, and reasons. Review is incomplete; existing entries are preserved when the notebook is rerun. |
| `images/` | Downloaded photographs, organized as `<taxon_id>/<photo_id>.jpg`. The manifest's `image_path` locates each file relative to the project root. |
| `raw/` | Initial cached iNaturalist API responses used to assemble the dataset. |
| `raw/species_counts.json` | Original API response describing regional species availability. Observation counts reflect source coverage, not standardized bird abundance. |
| `raw/observations_<taxon_id>_200.json` | Twelve source-response files, with up to 200 matching candidate observations per requested species. |
| `raw/pilot/` | Earlier pilot API snapshots, retained as provenance. These are not additional rows in the final dataset. |

The 12 observation-response taxon IDs are **3454, 4956, 8021, 9083, 9100, 9744, 11901, 12727, 12942, 17008, 144814, and 145310**. The pilot folder contains `species_counts.json` and corresponding `observations_<taxon_id>.json` files.

`taxon_id` is the species class key. Read IDs as categorical strings. Dates use `YYYY-MM-DD`; image dimensions are in pixels. Missing metadata are not zero. Source community identifications remain subject to error and human review.

## Where to find the scripts

Code is stored in the sibling **Scripts** folder:

- [build_dataset.py](../Scripts/build_dataset.py): assembles the dataset from cached source responses, downloads missing photographs, validates images, removes exact byte duplicates, and assigns observer-separated splits. Writes the final data manifests and `Output/build_summary.json`.
- [01_bird_eda.ipynb](../Scripts/01_bird_eda.ipynb): commented exploratory notebook with section headers and executed outputs. Audits the manifest, image files, class balance, split coverage, observers, dates, and image sizes; saves tables and plots to `Output/`. Creates the review log if missing and preserves existing review entries.
- [requirements.txt](../Scripts/requirements.txt): packages needed for collection and EDA.

## Recreate the data and EDA

Keep **Data**, **Scripts**, and **Output** together. Run commands from the **project root**, the folder containing those three folders:

```bash
python -m pip install -r Scripts/requirements.txt
```

To reproduce the EDA for the included frozen sample:

```bash
jupyter lab Scripts/01_bird_eda.ipynb
```

Open the notebook, select your Python environment, and run all cells in order. Included photographs and cached data allow EDA without internet access. Expected results: **482 images**, **12 species**, **272 training**, **90 validation**, and **120 test images**. All records from an observer belong to the same split.

To rebuild the source-derived dataset separately:

```bash
python Scripts/build_dataset.py
```

Existing raw responses and images are reused. Missing records or photographs require internet access. A rebuild can recover previously failed downloads and change the sample, so keep the supplied manifest for reproducing the frozen EDA and version any newly rebuilt dataset separately. The observation-date cutoff is November 5, 2026; retain cached source responses because the live source can change.

## Generated outputs

Generated EDA results belong in the sibling **Output** folder. Keep the actual input photographs, final manifest, and review decisions here in **Data**.

| File in `Output/` | Contents |
|---|---|
| `01_species_counts.png` | Image counts by species. |
| `02_split_coverage.png` | Species counts across training, validation, and test sets. |
| `03_observers_and_months.png` | Observer concentration and monthly coverage. |
| `04_image_dimensions.png` | Image dimensions and aspect ratios. |
| `05_example_images.png` | One source-labeled example per species; credits are in `bird_images.csv`. |
| `species_summary.csv` | Species-level image and observer counts. |
| `species_split_counts.csv` | Image counts by species and split. |
| `observer_counts.csv` | Retained image counts per observer. |
| `month_counts.csv` | Image counts by observation month. |
| `missing_values.csv` | Missing manifest values by feature. |
| `image_integrity.csv` | Image validation and decoded-image audit results. |
| `pixel_duplicate_candidates.csv` | Identical decoded-image candidates; not a complete near-duplicate test. |
| `build_summary.json` | Collection settings, counts, download results, and split sizes. |
| `eda_summary.json` | EDA counts and verification results. |
| `README.md` | Output-folder documentation. |

### Exploratory plots

![Bird species counts](../Output/01_species_counts.png)

Species counts range from 23 to 60 photographs, so the sample is not balanced. Counts describe this selected sample, not regional bird abundance.

![Species coverage by split](../Output/02_split_coverage.png)

Every species appears in each partition. Keeping observers separate reduces one source of leakage but does not guarantee independent sites or individual birds.

## Source permissions and limitations

Photo credits, original URLs, and individual CC0, CC BY, or CC BY-SA license links are recorded in `bird_images.csv`. Preserve credits and follow each photograph's linked terms. A project code license does not override image permissions. Raw metadata has its own source license fields.

Human quality and identification review remains incomplete. Complete the review log and check near duplicates before freezing a modeling benchmark. This selected 12-species sample does not represent all Southwest Virginia birds, and observer effort affects its coverage. Avoid using IDs, paths, names, or credit text as image-model predictors.

## References

[1] iNaturalist, “iNaturalist API.” [Online]. Available: https://api.inaturalist.org/v1/docs/. [Accessed: Nov. 5, 2026].

[2] iNaturalist, “API Recommended Practices.” [Online]. Available: https://www.inaturalist.org/pages/api+recommended+practices. [Accessed: Nov. 5, 2026].

[3] iNaturalist, “Can I use the photos and sounds that are posted on iNaturalist?” [Online]. Available: https://help.inaturalist.org/en/support/solutions/articles/151000169918. [Accessed: Nov. 5, 2026].
