
Non-text baseline model for Jeopardy! winner prediction (DS 4002, SLMB).

What it does
  1. Loads the primary sample (final_contestant_games.csv): 3,882 games x 3 contestants.
  2. Makes ONE fixed 80/20 train/test split by whole game (seeded) and saves the
     test game IDs so the enhanced model uses the exact same split.
  3. Fits a conditional (game-level multinomial) logit: each game gets three
     win probabilities that sum to one, via a softmax over the three contestants.
  4. Chooses between candidate feature sets and L2 strengths using grouped
     5-fold CV on TRAINING games only.
  5. Refits on all training games, predicts the held-out test games once, and
     exports predictions alongside uniform 1/3 probabilities.

Only pre-game, non-text information is used. Never used: is_winner (target only),
scores, winnings, games played, wagers, answers, Daily Double info, names, IDs,
game notes, occupation or clue text.

Run:  python baseline_model.py --data final_contestant_games.csv --out OUTPUT

Outputs (written to --out):
  test_game_ids.csv              held-out game IDs, shared with the enhanced model
  baseline_cv_results.csv        CV log loss for every (feature set, L2) pair
  baseline_coefficients.csv      fitted coefficients of the chosen model
  baseline_test_predictions.csv  per-contestant test probabilities (baseline + uniform)
  baseline_test_summary.csv      test log loss and top-1 accuracy
