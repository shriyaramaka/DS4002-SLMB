import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize

# Fixed seed so the train/test split and CV folds are identical on every run.
SEED = 4002
TEST_FRAC = 0.20
# Clue values doubled on 2001-11-26; used only as a coarse era marker.
ERA_CUTOFF = pd.Timestamp("2001-11-26")


# data
def load_data(path):
    # Read only the columns the baseline needs, so nothing else can leak in.
    cols = ["game_id", "contestant_id", "contestant_position", "air_date", "is_winner"]
    df = pd.read_csv(path, usecols=cols)
    df["air_date"] = pd.to_datetime(df["air_date"])
    # Sorting puts each game's three rows next to each other in position order
    # (1, 2, 3); to_arrays() relies on this to reshape rows into games.
    df = df.sort_values(["game_id", "contestant_position"]).reset_index(drop=True)

    # Structural checks: three contestants, positions 1-3, one winner per game.
    g = df.groupby("game_id")
    assert (g.size() == 3).all(), "every game needs exactly 3 contestants"
    assert (g["is_winner"].sum() == 1).all(), "every game needs exactly 1 winner"
    assert (g["contestant_position"].apply(lambda s: sorted(s) == [1, 2, 3])).all()
    return df


def split_games(df, seed=SEED, test_frac=TEST_FRAC):
    # Split by game, not by row, so all three contestants of a game land on the
    # same side. Sorting the IDs first makes the seeded draw reproducible.
    games = np.sort(df["game_id"].unique())
    rng = np.random.default_rng(seed)
    test = set(rng.choice(games, size=int(round(test_frac * len(games))), replace=False))
    is_test = df["game_id"].isin(test)
    train, test_df = df[~is_test].copy(), df[is_test].copy()
    assert not set(train.game_id) & set(test_df.game_id), "game leaked across split"
    return train, test_df


# features
# Game-level variables are identical for all three contestants, so they can only
# matter through interactions with a contestant-level variable (position).
def build_features(df, feature_set):
    # Position 1 is the reference category, so it has no column; pos2/pos3
    # coefficients are log-odds shifts relative to the position 1 contestant.
    pos2 = (df["contestant_position"] == 2).astype(float)
    pos3 = (df["contestant_position"] == 3).astype(float)
    X = {"pos2": pos2, "pos3": pos3}
    if feature_set == "position_x_era":
        # Lets the position effect differ before vs. after the clue-value change.
        late = (df["air_date"] >= ERA_CUTOFF).astype(float)
        X["pos2_x_late"] = pos2 * late
        X["pos3_x_late"] = pos3 * late
    elif feature_set != "position":
        raise ValueError(feature_set)
    return pd.DataFrame(X, index=df.index)


def to_arrays(df, X):
    """Reshape to (n_games, 3, n_features) and (n_games,) winner index."""
    # Assumes df is sorted by game then position (see load_data), so every
    # consecutive block of three rows is one game.
    n = len(df) // 3
    Xa = X.to_numpy().reshape(n, 3, X.shape[1])
    # y[i] is which of the three contestants (0, 1 or 2) won game i.
    y = df["is_winner"].to_numpy().reshape(n, 3).argmax(axis=1)
    return Xa, y


# model
def softmax_probs(Xa, w):
    # Utility for each contestant is a linear score; the softmax across the
    # three contestants in a game turns scores into win probabilities.
    u = Xa @ w
    # Subtracting the row max doesn't change the softmax but avoids overflow.
    u -= u.max(axis=1, keepdims=True)
    e = np.exp(u)
    return e / e.sum(axis=1, keepdims=True)


def fit(Xa, y, l2):
    n = len(y)

    def loss_grad(w):
        # Mean negative log-likelihood of the actual winners, plus an L2 penalty.
        p = softmax_probs(Xa, w)
        nll = -np.log(p[np.arange(n), y] + 1e-15).mean() + l2 * w @ w
        # Gradient of the conditional logit: winner's features minus the
        # probability-weighted average features in that game.
        chosen = Xa[np.arange(n), y]                     # (n, k)
        expected = (p[:, :, None] * Xa).sum(axis=1)      # (n, k)
        grad = -(chosen - expected).mean(axis=0) + 2 * l2 * w
        return nll, grad

    # Start from all-zero weights (= uniform 1/3 probabilities) and minimize.
    res = minimize(loss_grad, np.zeros(Xa.shape[2]), jac=True, method="L-BFGS-B")
    return res.x


def log_loss(p, y):
    # Average -log(probability given to the actual winner); lower is better.
    # Uniform guessing scores log(3) ~= 1.0986.
    return -np.log(np.clip(p[np.arange(len(y)), y], 1e-15, 1)).mean()


def accuracy(p, y):
    # Share of games where the highest-probability contestant actually won.
    return (p.argmax(axis=1) == y).mean()


# tuning
def grouped_cv(train, feature_set, l2, k=5, seed=SEED):
    # Assign each training game (not each row) to one of k folds at random.
    games = np.sort(train["game_id"].unique())
    folds = np.random.default_rng(seed + 1).permutation(len(games)) % k
    fold_of = dict(zip(games, folds))
    f = train["game_id"].map(fold_of).to_numpy()
    losses = []
    for i in range(k):
        # Train on k-1 folds, score log loss on the held-out fold.
        tr, va = train[f != i], train[f == i]
        Xt, yt = to_arrays(tr, build_features(tr, feature_set))
        Xv, yv = to_arrays(va, build_features(va, feature_set))
        losses.append(log_loss(softmax_probs(Xv, fit(Xt, yt, l2)), yv))
    return float(np.mean(losses))


# main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="final_contestant_games.csv")
    ap.add_argument("--out", default="OUTPUT")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    df = load_data(args.data)
    train, test = split_games(df)
    print(f"Games: {df.game_id.nunique()} | train {train.game_id.nunique()} | test {test.game_id.nunique()}")

    # Shared split file: the enhanced model must use exactly these test games.
    pd.DataFrame({"game_id": np.sort(test.game_id.unique())}).to_csv(out / "test_game_ids.csv", index=False)

    # Tune on training games only.
    # Every combination of feature set and L2 strength is scored by grouped CV;
    # the pair with the lowest mean CV log loss wins.
    grid = [(fs, l2) for fs in ["position", "position_x_era"] for l2 in [0.0, 0.001, 0.01, 0.1]]
    cv = pd.DataFrame([{"feature_set": fs, "l2": l2, "cv_log_loss": grouped_cv(train, fs, l2)} for fs, l2 in grid])
    cv = cv.sort_values("cv_log_loss").reset_index(drop=True)
    cv.to_csv(out / "baseline_cv_results.csv", index=False)
    print("\nGrouped 5-fold CV on training games:\n", cv.round(5).to_string(index=False))
    best_fs, best_l2 = cv.loc[0, "feature_set"], cv.loc[0, "l2"]

    # Refit on all training games, evaluate once on test games.
    X_tr = build_features(train, best_fs)
    w = fit(*to_arrays(train, X_tr), best_l2)
    Xte, yte = to_arrays(test, build_features(test, best_fs))
    p_base = softmax_probs(Xte, w)
    # Uniform 1/3 per contestant: the no-information benchmark to beat.
    p_unif = np.full_like(p_base, 1 / 3)

    pd.DataFrame({"feature": X_tr.columns, "coefficient": w}).to_csv(out / "baseline_coefficients.csv", index=False)

    # One row per test contestant. ravel() flattens (games, 3) back to rows in
    # the same game/position order as the sorted test DataFrame.
    preds = test[["game_id", "contestant_id", "contestant_position", "is_winner"]].copy()
    preds["p_baseline"] = p_base.ravel()
    preds["p_uniform"] = p_unif.ravel()
    # Sanity check: the three probabilities in each game must sum to 1.
    assert np.allclose(preds.groupby("game_id").p_baseline.sum(), 1)
    preds.to_csv(out / "baseline_test_predictions.csv", index=False)

    # Accuracy is NaN for uniform because every contestant ties at 1/3.
    summary = pd.DataFrame({
        "model": ["uniform_1/3", f"baseline ({best_fs}, l2={best_l2})"],
        "test_log_loss": [log_loss(p_unif, yte), log_loss(p_base, yte)],
        "test_top1_accuracy": [np.nan, accuracy(p_base, yte)],
    })
    summary.to_csv(out / "baseline_test_summary.csv", index=False)
    print(f"\nChosen: {best_fs}, l2={best_l2}")
    print("Coefficients (relative to position 1):", dict(zip(X_tr.columns, np.round(w, 4))))
    print("\nHeld-out test results:\n", summary.round(4).to_string(index=False))
    print("\nImplied test win probabilities by position:")
    print(preds.groupby("contestant_position").p_baseline.mean().round(4).to_string())


if __name__ == "__main__":
    main()
