# Project Scripts

This folder contains every notebook and Python script used for data acquisition, exploratory analysis, and winner modeling. Data inputs are stored in `../Data`, and generated tables, figures, predictions, and metrics are stored in `../Output`.

## Files

| File | Purpose | Main output location |
| --- | --- | --- |
| `Cluebase_Data_Download.ipynb` | Downloads the archived Cluebase PostgreSQL dump and extracts its tables. The completed repository already contains the needed data, so rerunning this notebook is optional. | `../Output/cluebase_project/` |
| `Initial_EDA.ipynb` | Explores the original connected contestant-clue dataset. | `../Output/initial_eda_outputs/` |
| `Final_EDA.ipynb` | Describes the final 3,882-game sample, clue coverage, text fields, common topics, and SOC/CIP uncertainty. | `../Output/eda_final_outputs/` |
| `baseline_model.py` | Fits the non-text winner baseline, performs grouped cross-validation, and saves the shared held-out game IDs. | `../Output/` |
| `enhanced_model.ipynb` | Creates Sentence-BERT contestant-board similarity features and fits the enhanced winner model using the baseline model's held-out games. | `../Output/` |

## Recommended Run Order

From the main `Project_1` folder:

1. Run the final exploratory analysis:

   ```bash
   cd Scripts
   jupyter notebook Final_EDA.ipynb
   ```

2. Return to the project folder and run the baseline model:

   ```bash
   cd ..
   python3 Scripts/baseline_model.py --data Data/final_contestant_games.csv --out Output
   ```

3. Start the enhanced-model notebook from `Scripts` and run every cell:

   ```bash
   cd Scripts
   jupyter notebook enhanced_model.ipynb
   ```

Run `Cluebase_Data_Download.ipynb` only if the raw source tables must be reconstructed. Run `Initial_EDA.ipynb` only to reproduce the earlier raw-data exploration.

## Baseline Outputs

- `test_game_ids.csv`: shared held-out game IDs used by both models.
- `baseline_cv_results.csv`: cross-validation log loss for each baseline specification.
- `baseline_coefficients.csv`: coefficients from the selected baseline.
- `baseline_test_predictions.csv`: baseline and uniform probabilities for held-out contestants.
- `baseline_test_summary.csv`: baseline and uniform log loss and accuracy.

## Enhanced-Model Outputs

- `enhanced_model_features.csv`: contestant-level semantic features.
- `enhanced_model_feature_summary.csv`: descriptive statistics for those features.
- `enhanced_model_game_splits.csv`: train/test assignment for every game.
- `enhanced_model_test_predictions.csv`: semantic-model probabilities for held-out games.
- `enhanced_model_metrics.csv`: semantic-model log loss and accuracy.

Scores, wagers, responses, winner IDs, names, historical winnings, and other postgame information are excluded from the predictor variables. `is_winner` is used only as the target.
