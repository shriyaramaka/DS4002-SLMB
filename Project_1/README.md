# Predicting Jeopardy! Winners from Contestant-Board Semantics

This repository contains the data, code, and outputs for Group SLMB's first DS 4002 project. The project tests whether the semantic match between a contestant's occupational profile and the clues on a Jeopardy! board can help predict the game's winner.

**Group:** SLMB: Statistics, Learning, Models, and Beyond  
**Leader:** Shriya Ramaka  
**Members:** Lyle Mora, Maggie Parkhurst, and Bhargav Garre Venkata  
**Course:** DS 4002, Section 002

## Repository Contents

The repository contains the raw and processed data, exploratory analysis, a non-text baseline model, a Sentence-BERT semantic model, and the output files created by those models. The `Data` folder contains a separate README with the data dictionary, provenance, license information, uncertainty notes, and ethical considerations. The `Scripts` folder contains the data-acquisition, exploratory-analysis, and modeling code. All tables, plots, predictions, and model results are stored in `Output`.

## Section 1: Software and Platform

The project was completed in Python on macOS. Team members used Jupyter Notebook, Google Colab, or other local Python applications on their Macs. Git, GitHub, and GitHub Desktop were used to store and share the project.

The data preparation and analysis used the following software and package versions:

- Python `3.13.15`
- pandas `2.2.3`
- NumPy `2.1.3`
- SciPy `1.16.3`
- scikit-learn `1.6.1`
- sentence-transformers `5.7.0`
- Matplotlib `3.10.0`
- Seaborn `0.13.2`
- Requests `2.32.4`

The installed versions can be checked from a terminal using:

```bash
python3 --version
python3 -m pip freeze | grep -Ei '^(pandas|numpy|scipy|scikit-learn|sentence-transformers|matplotlib|seaborn|requests)=='
```

Install the recorded package versions from a terminal using:

```bash
python3 -m pip install pandas==2.2.3 numpy==2.1.3 scipy==1.16.3 scikit-learn==1.6.1 sentence-transformers==5.7.0 matplotlib==3.10.0 seaborn==0.13.2 requests==2.32.4
```

The first run of the semantic model downloads the pretrained Sentence-BERT model `all-MiniLM-L6-v2`, so an internet connection is required for that step. The Cluebase acquisition notebook also requires PostgreSQL if the source database is reconstructed.

## Section 2: Map of the Repository

```text
Project_1/
├── README.md
├── LICENSE
├── REFERENCES.MD
├── Data/
│   ├── README.md
│   ├── jeopardy_raw_contestant_clue_data.csv.gz
│   ├── final_contestant_games.csv
│   └── soc_cip_links.csv
├── Scripts/
│   ├── README.md
│   ├── Cluebase_Data_Download.ipynb
│   ├── Initial_EDA.ipynb
│   ├── Final_EDA.ipynb
│   ├── baseline_model.py
│   └── enhanced_model.ipynb
└── Output/
    ├── eda_final_outputs/
    │   ├── README.md
    │   ├── games_by_clue_count.png
    │   ├── top_categories.png
    │   └── supporting summary CSV files
    ├── baseline_coefficients.csv
    ├── baseline_cv_results.csv
    ├── baseline_test_predictions.csv
    ├── baseline_test_summary.csv
    ├── test_game_ids.csv
    ├── enhanced_model_features.csv
    ├── enhanced_model_feature_summary.csv
    ├── enhanced_model_game_splits.csv
    ├── enhanced_model_metrics.csv
    └── enhanced_model_test_predictions.csv
```

### Main Files

- `README.md` explains the repository and how to reproduce the current results.
- `LICENSE` contains the MIT License and a notice about third-party data.
- `REFERENCES.MD` lists the original data and documentation sources.
- `Data/README.md` explains the datasets and provides the data dictionary.
- `Data/jeopardy_raw_contestant_clue_data.csv.gz` contains the connected raw contestant and clue records.
- `Data/final_contestant_games.csv` contains the final contestant-game sample and occupation-profile fields.
- `Data/soc_cip_links.csv` contains optional links between Standard Occupational Classification occupations and Classification of Instructional Programs fields.
- `Scripts/Cluebase_Data_Download.ipynb` documents the original Cluebase data acquisition.
- `Scripts/Initial_EDA.ipynb` contains the initial exploration of the raw data.
- `Scripts/Final_EDA.ipynb` describes the final analysis sample and creates summary tables and plots.
- `Scripts/baseline_model.py` builds the non-text winner baseline.
- `Scripts/enhanced_model.ipynb` creates semantic similarity features and fits the Sentence-BERT winner model.
- `Output/eda_final_outputs/` contains the exploratory plots and summary tables.
- `Output/` contains the current model features, predictions, metrics, coefficients, and split records.

## Section 3: Instructions for Reproducing the Results

### 1. Download the project folder

Open the GitHub link for the `Project_1` folder. Clone the full repository with GitHub Desktop or Git, or download it as a ZIP file and extract it. Keep the folder names and structure unchanged because the notebooks use relative paths.

Using Git from a terminal:

```bash
git clone <repository-url>
cd <repository-name>/Project_1
```

Replace `<repository-url>` and `<repository-name>` with the correct GitHub information.

### 2. Install the software

Open Terminal on macOS, move into the `Project_1` folder, and install the package versions recorded in Section 1.

The repository already contains the data needed for the current analysis. Do not rerun `Scripts/Cluebase_Data_Download.ipynb` unless you specifically want to reconstruct the source data.

### 3. Reproduce the exploratory analysis and plots

Start Jupyter from the main `Project_1` folder:

```bash
jupyter notebook
```

Open `Scripts/Final_EDA.ipynb` and run every cell from top to bottom. The notebook uses:

```text
Data/final_contestant_games.csv
Data/jeopardy_raw_contestant_clue_data.csv.gz
```

The notebook checks the sample structure, clue coverage, missing text, common categories, occupation wording, and optional SOC/CIP mapping uncertainty. Its plots and summary tables should be saved in:

```text
Output/eda_final_outputs/
```

The two main exploratory plots are:

- `Output/eda_final_outputs/games_by_clue_count.png`
- `Output/eda_final_outputs/top_categories.png`

Descriptions and previews of these plots are provided in `Output/eda_final_outputs/README.md`.

The final sample should contain 3,882 games, 11,646 contestant-game records, three contestants per game, one recorded winner per game, and at least 50 recorded clues per game.

`Scripts/Initial_EDA.ipynb` records the earlier exploration of the raw data and is not required to reproduce the current model results.

### 4. Run the non-text baseline model

From the main `Project_1` folder, run:

```bash
python3 Scripts/baseline_model.py --data Data/final_contestant_games.csv --out Output
```

The script uses a fixed random seed, makes an 80/20 split by game, performs grouped five-fold cross-validation on the training games, selects the baseline specification, and predicts the held-out winners. It rewrites these files in `Output`:

- `test_game_ids.csv`
- `baseline_cv_results.csv`
- `baseline_coefficients.csv`
- `baseline_test_predictions.csv`
- `baseline_test_summary.csv`

The reproduced baseline summary should report a held-out log loss of approximately `1.09649` and top-one accuracy of approximately `0.35180`. Uniform one-in-three probabilities have a log loss of approximately `1.09861`.

### 5. Run the semantic model

Start Jupyter from the main `Project_1` folder:

```bash
jupyter notebook
```

Open `Scripts/enhanced_model.ipynb` and run every cell from top to bottom. On its first run, the notebook may take time to download `all-MiniLM-L6-v2` and create embeddings for the occupation, clue, and category text. The notebook then:

1. Loads the final contestant and raw clue files.
2. Cleans the text.
3. Creates Sentence-BERT embeddings.
4. Calculates contestant-to-board similarity features.
5. Fits and tunes a regularized multinomial logistic-regression model.
6. Evaluates the model on held-out games.
7. Saves the model files in `Output`.

The notebook rewrites:

- `enhanced_model_features.csv`
- `enhanced_model_feature_summary.csv`
- `enhanced_model_game_splits.csv`
- `enhanced_model_metrics.csv`
- `enhanced_model_test_predictions.csv`

The reproduced semantic-model metrics should report 776 held-out games, a log loss of approximately `1.093`, and top-one accuracy of approximately `0.3557`.

### 6. Check the output files

After both models finish, open the CSV files in `Output` and confirm that:

- Each held-out contestant has a predicted probability.
- The three contestant probabilities within each game sum to one.
- Each game has exactly one recorded winner.
- The summary metrics are close to the values listed above.

Small numerical differences can occur across package or operating-system versions. The fixed random seeds should otherwise make the results reproducible.

## Section 4: Analysis of Results

| Model | Log Loss | Accuracy |
|---|---:|---:|
| Baseline | 1.09649 | 0.35180 |
| Uniform | 1.09861 | 0.33333 |
| Enhanced | 1.093 | 0.3557 |

The semantic model produced a small observed improvement over the non-text baseline and uniform probabilities. Its held-out log loss was lower, and its top-one accuracy was slightly higher. However, the size of the difference was modest, and additional uncertainty analysis would be needed to determine whether the improvement is reliable. Factors not represented by the text, including buzzer speed, clue selection, Daily Double placement, and wagering, may have a larger role in determining the winner.

Additional exploratory analysis can link UVA majors to SOC occupations using `Data/soc_cip_links.csv`. These comparisons describe text similarity and should not be interpreted as evidence that a major causes Jeopardy! success.
