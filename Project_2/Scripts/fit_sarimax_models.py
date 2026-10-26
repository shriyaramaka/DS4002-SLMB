"""Fit matched SARIMAX models and evaluate rolling next-day forecasts.

Reads the prepared analysis CSV and its validation report. Orders are selected
on 2023 with calendar-only exogenous terms; both model variants share the order.
All scaling is learned from the applicable training period. See Scripts/README.MD.
"""
import itertools
import platform
import sys
from importlib.metadata import version
import json
import warnings
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

try:
    from statsmodels.stats.diagnostic import acorr_ljungbox
    from statsmodels.tsa.statespace.sarimax import SARIMAX
except ImportError as exc:
    raise SystemExit("Missing dependency: install statsmodels (python3 -m pip install statsmodels).") from exc

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "Data" / "cville_sarimax_analysis.csv"
VALIDATION_REPORT = ROOT / "Output" / "sarimax_validation_report.json"
OUT = ROOT / "Output"
OUT.mkdir(exist_ok=True)
CALENDAR = ["month_sin", "month_cos"]
WEATHER = ["temp_mean_c_lag7", "precip_mm_lag7", "snowfall_cm_lag7", "wind_max_kmh_lag7"]
VARIANTS = {"no_weather": CALENDAR, "with_weather": CALENDAR + WEATHER}
ORDERS = list(itertools.product((0, 1), (0, 1), (0, 1)))
SEASONAL_ORDERS = list(itertools.product((0, 1), (0,), (0, 1), (7,)))
BOOTSTRAPS, BLOCK_SIZE, SEED = 2000, 7, 4002


def trend_for_order(order):
    """Use an intercept for undifferenced candidates, no drift when d=1."""
    return "c" if order[1] == 0 else "n"


def constant_forecasts(history, horizon):
    """Estimate constant benchmarks from fitting outcomes only, never evaluation data."""
    return {"constant_mean": np.full(horizon, float(history.mean())),
            "constant_median": np.full(horizon, float(history.median()))}


def fit(y, x, order, seasonal_order, robust=False):
    # Slicing/reindexing can drop DatetimeIndex.freq even when dates remain daily.
    y = y.copy()
    x = x.copy()
    y.index = pd.DatetimeIndex(y.index, freq="D")
    x.index = pd.DatetimeIndex(x.index, freq="D")
    model = SARIMAX(y, exog=x, order=order, seasonal_order=seasonal_order,
                    trend=trend_for_order(order), enforce_stationarity=False,
                    enforce_invertibility=False)
    # A longer final refit can need more optimizer iterations than the shorter
    # order-selection fit. Retry before classifying the fit as nonconverged.
    attempts = ([('lbfgs', 500), ('lbfgs', 1200), ('powell', 800)] if robust
                else [('lbfgs', 200)])
    last_result = None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for method, maxiter in attempts:
            last_result = model.fit(disp=False, method=method, maxiter=maxiter)
            if converged(last_result):
                return last_result
    return last_result


def converged(result):
    return bool(getattr(result, "mle_retvals", {}).get("converged", False))


def roll_forecast(result, y, x):
    """Forecast each row before appending its observed value; no coefficient refit."""
    state, preds = result, []
    for date, actual in y.items():
        xrow = x.loc[[date]].copy()
        xrow.index = pd.DatetimeIndex(xrow.index, freq="D")
        value = state.get_forecast(steps=1, exog=xrow).predicted_mean.iloc[0]
        # Some statsmodels/NumPy versions expose a one-element array here.
        preds.append(float(np.asarray(value).reshape(-1)[0]))
        # extend filters only the new observation; append refilters the full
        # history every day and makes long rolling evaluations unnecessarily slow.
        # A single exogenous row is mechanically constant in every column.
        # The full training design has already been specified; disable only
        # clone-time specification checks for this one-row state update.
        state = state.extend(endog=pd.Series([actual], index=xrow.index),
                             exog=xrow, validate_specification=False)
    return np.asarray(preds)


def score(actual, predicted):
    error = np.asarray(actual, dtype=float) - np.asarray(predicted, dtype=float)
    return {"mae": float(np.mean(np.abs(error))),
            "rmse": float(np.sqrt(np.mean(error ** 2))), "days": int(error.size)}


def moving_block_ci(actual, pred_a, pred_b, rng):
    """Paired CI for MAE(A)-MAE(B), resampling contiguous seven-day blocks."""
    actual = np.asarray(actual, dtype=float)
    loss_diff = np.abs(actual - np.asarray(pred_a)) - np.abs(actual - np.asarray(pred_b))
    n = len(loss_diff)
    blocks_needed = int(np.ceil(n / BLOCK_SIZE))
    starts = np.arange(n)
    estimates = np.empty(BOOTSTRAPS)
    for i in range(BOOTSTRAPS):
        chosen = rng.choice(starts, size=blocks_needed, replace=True)
        idx = np.concatenate([(s + np.arange(BLOCK_SIZE)) % n for s in chosen])[:n]
        estimates[i] = loss_diff[idx].mean()
    return {"mae_difference_a_minus_b": float(loss_diff.mean()),
            "ci_95_percentile": [float(v) for v in np.quantile(estimates, [0.025, 0.975])],
            "resamples": BOOTSTRAPS, "block_size_days": BLOCK_SIZE}


def check_inputs():
    with open(VALIDATION_REPORT) as f:
        report = json.load(f)
    if report.get("status") != "passed" or report.get("output") != "Data/cville_sarimax_analysis.csv":
        raise ValueError("sarimax_validation_report.json must pass and describe the analysis CSV")
    if report.get("exog_no_weather") != CALENDAR or report.get("exog_with_weather") != CALENDAR + WEATHER:
        raise ValueError("Predictor definitions in validation report do not match this script")
    df = pd.read_csv(INPUT, parse_dates=["date_local"]).set_index("date_local").sort_index()
    required = set(CALENDAR + WEATHER + ["crash_count", "split"])
    if not df.index.is_unique or df.index.isna().any() or not required.issubset(df.columns):
        raise ValueError("Analysis CSV has duplicate dates or is missing required columns")
    if df[CALENDAR + WEATHER + ["crash_count"]].isna().any().any():
        raise ValueError("Analysis CSV contains missing model values")
    expected = {"train": ("2017-01-01", "2022-12-31"),
                "validation": ("2023-01-01", "2023-12-31"),
                "test": ("2024-01-01", "2025-12-31")}
    for split, dates in expected.items():
        part = df[df.split == split]
        if part.empty or (part.index.min().strftime("%Y-%m-%d"),
                          part.index.max().strftime("%Y-%m-%d")) != dates:
            raise ValueError(f"Analysis CSV {split} split differs from the documented dates")
    # Compare calendar dates, not raw integer ticks: pandas may use ns or us.
    expected_dates = pd.date_range(df.index.min(), df.index.max(), freq="D")
    if len(df.index) != len(expected_dates) or not (df.index == expected_dates).all():
        raise ValueError("Analysis CSV dates must be daily and continuous")
    # statsmodels uses the DatetimeIndex frequency when constructing forecast dates.
    df = df.asfreq("D")
    return df


def forecast_table(test, predictions, raw_predictions):
    """One scalar per date/model; validate before writing reusable forecasts."""
    rows = []
    for i, (date, actual) in enumerate(test.crash_count.items()):
        for model, pred in predictions.items():
            rows.append({"date_local": date.strftime("%Y-%m-%d"), "year": date.year,
                         "model": model, "actual_crash_count": int(actual),
                         "forecast_crash_count": float(np.asarray(pred).reshape(-1)[i]),
                         "raw_forecast_crash_count": (float(np.asarray(raw_predictions[model][i]).reshape(-1)[0])
                                                      if model in raw_predictions else
                                                      float(np.asarray(pred).reshape(-1)[i])),
                         "clipped": bool(model in raw_predictions and raw_predictions[model][i] < 0)})
    frame = pd.DataFrame(rows)
    if frame.duplicated(["date_local", "model"]).any():
        raise ValueError("Duplicate date/model forecast rows")
    for name, expected in predictions.items():
        exported = frame.loc[frame.model == name, "forecast_crash_count"].to_numpy()
        if not np.allclose(exported, np.asarray(expected).reshape(-1)):
            raise ValueError(f"Exported forecasts differ from predictions: {name}")
    return frame


def main():
    df = check_inputs()
    train, validation = df.loc["2017":"2022"], df.loc["2023"]
    # Training-only standardization; the month terms are retained as specified.
    means = train[CALENDAR + WEATHER].mean()
    scales = train[CALENDAR + WEATHER].std(ddof=0).replace(0, 1.0)
    x_scaled = (df[CALENDAR + WEATHER] - means) / scales

    # Grid: p,q,P,Q in {0,1}, d in {0,1}, D=0, weekly period m=7.
    candidates = [(o, s) for o in ORDERS for s in SEASONAL_ORDERS]
    selection, eligible = [], []
    for candidate_number, (order, seasonal) in enumerate(candidates, start=1):
        item = {"order": list(order), "seasonal_order": list(seasonal),
                "trend": trend_for_order(order)}
        print(f"Order search {candidate_number}/{len(candidates)}: order={order}, seasonal={seasonal}",
              flush=True)
        try:
            result = fit(train.crash_count, x_scaled.loc[train.index, CALENDAR], order, seasonal)
            item["converged"] = converged(result)
            item["aic"] = float(result.aic)
            if not item["converged"]:
                item["status"] = "excluded_nonconverged"
            else:
                pred = roll_forecast(result, validation.crash_count,
                                     x_scaled.loc[validation.index, CALENDAR])
                item["validation_mae"] = float(np.mean(np.abs(validation.crash_count.to_numpy() - pred)))
                item["status"] = "eligible"
                eligible.append((item["validation_mae"], order, seasonal, item["aic"], item))
        except Exception as exc:
            item.update(status="failed", error=str(exc))
        selection.append(item)
    if not eligible:
        raise RuntimeError("No candidate order converged on the 2017-2022 fit.")
    # Deterministic ties: fewer total AR/MA terms, then lower training-fit AIC.
    eligible.sort(key=lambda x: (x[0], x[1][0] + x[1][2] + x[2][0] + x[2][2], x[3]))
    best_mae, best_order, best_seasonal, best_aic, _ = eligible[0]

    # Validation constants are fixed from 2017-2022; neither is selected using test data.
    validation_constants = constant_forecasts(train.crash_count, len(validation))
    baseline_validation_metrics = {
        name: {"forecast_value": float(pred[0]), **score(validation.crash_count, pred)}
        for name, pred in validation_constants.items()
    }
    # Final models are fit to all 2017-2023 data; test is a single untouched pass.
    refit, test = df.loc["2017":"2023"], df.loc["2024":"2025"]
    raw_predictions, clipped_predictions, fit_results = {}, {}, {}
    clip_counts, model_metrics, annual_metrics = {}, {}, {}
    for name, columns in VARIANTS.items():
        print(f"Fitting final {name} model and rolling through test period...", flush=True)
        result = fit(refit.crash_count, x_scaled.loc[refit.index, columns],
                     best_order, best_seasonal, robust=True)
        if not converged(result):
            raise RuntimeError(f"Final {name} model did not converge; not reporting its metrics.")
        raw = roll_forecast(result, test.crash_count, x_scaled.loc[test.index, columns])
        clipped = np.maximum(raw, 0.0)
        raw_predictions[name], clipped_predictions[name], fit_results[name] = raw, clipped, result
        clip_counts[name] = int(np.sum(raw < 0))
        model_metrics[name] = score(test.crash_count, clipped)
        annual_metrics[name] = {}
        for year in (2024, 2025):
            mask = test.index.year == year
            annual_metrics[name][str(year)] = score(test.crash_count.to_numpy()[mask], clipped[mask])

    # Seasonal naive baseline is exactly the observed count seven days earlier.
    naive = df.crash_count.shift(7).loc[test.index].to_numpy(dtype=float)
    # Re-estimate the prespecified constants on 2017-2023, then freeze throughout test.
    test_constants = constant_forecasts(refit.crash_count, len(test))
    predictions = {**clipped_predictions, "seasonal_naive_7day": naive, **test_constants}
    for name in ("seasonal_naive_7day", "constant_mean", "constant_median"):
        pred = predictions[name]
        model_metrics[name] = score(test.crash_count, pred)
        annual_metrics[name] = {}
        for year in (2024, 2025):
            mask = test.index.year == year
            annual_metrics[name][str(year)] = score(test.crash_count.to_numpy()[mask], pred[mask])

    # Paired seven-day moving-block bootstrap; negative differences favor weather.
    rng = np.random.default_rng(SEED)
    intervals = {
        "weather_minus_no_weather": moving_block_ci(test.crash_count, predictions["with_weather"],
                                                    predictions["no_weather"], rng),
        "weather_minus_seasonal_naive": moving_block_ci(test.crash_count, predictions["with_weather"],
                                                        naive, rng),
    }
    intervals_by_year = {}
    for year in (2024, 2025):
        mask = test.index.year == year
        year_rng = np.random.default_rng(SEED + year)
        intervals_by_year[str(year)] = {
            "weather_minus_no_weather": moving_block_ci(
                test.crash_count.to_numpy()[mask], predictions["with_weather"][mask],
                predictions["no_weather"][mask], year_rng),
            "weather_minus_seasonal_naive": moving_block_ci(
                test.crash_count.to_numpy()[mask], predictions["with_weather"][mask],
                naive[mask], year_rng),
        }

    for name in ("constant_mean", "constant_median"):
        intervals[f"weather_minus_{name}"] = moving_block_ci(
            test.crash_count, predictions["with_weather"], predictions[name], rng)
        for year in (2024, 2025):
            mask = test.index.year == year
            baseline_rng = np.random.default_rng(SEED + year + (100 if name == "constant_mean" else 200))
            intervals_by_year[str(year)][f"weather_minus_{name}"] = moving_block_ci(
                test.crash_count.to_numpy()[mask], predictions["with_weather"][mask],
                predictions[name][mask], baseline_rng)

    forecast_table(test, predictions, raw_predictions).to_csv(
        OUT / "sarimax_test_forecasts.csv", index=False)

    # Residual checks on final refits (in-sample one-step innovations).
    residual_checks = {}
    for name, result in fit_results.items():
        resid = pd.Series(np.asarray(result.resid, dtype=float)).replace([np.inf, -np.inf], np.nan).dropna()
        lags = [lag for lag in (7, 14, 28) if lag < len(resid) // 2]
        lb = acorr_ljungbox(resid, lags=lags, return_df=True) if lags else pd.DataFrame()
        residual_checks[name] = {
            "n": int(len(resid)), "mean": float(resid.mean()), "std": float(resid.std(ddof=1)),
            "ljung_box": {str(lag): {"statistic": float(lb.loc[lag, "lb_stat"]),
                                     "p_value": float(lb.loc[lag, "lb_pvalue"])} for lag in lags},
        }

    # Sensitivity: fit only pre-pandemic 2017-2019, then roll through 2020-2021.
    sensitivity_train, sensitivity_period = df.loc["2017":"2019"], df.loc["2020":"2021"]
    s_means = sensitivity_train[CALENDAR + WEATHER].mean()
    s_scales = sensitivity_train[CALENDAR + WEATHER].std(ddof=0).replace(0, 1.0)
    sx = (df[CALENDAR + WEATHER] - s_means) / s_scales
    sensitivity = {}
    for name, columns in VARIANTS.items():
        print(f"Running 2020-2021 sensitivity for {name}...", flush=True)
        sr = fit(sensitivity_train.crash_count, sx.loc[sensitivity_train.index, columns],
                 best_order, best_seasonal, robust=True)
        if not converged(sr):
            sensitivity[name] = {"status": "excluded_nonconverged"}
            continue
        sp = roll_forecast(sr, sensitivity_period.crash_count,
                           sx.loc[sensitivity_period.index, columns])
        sensitivity[name] = {"status": "ok", "fit_period": ["2017-01-01", "2019-12-31"],
                             "evaluation_period": ["2020-01-01", "2021-12-31"],
                             "metrics": score(sensitivity_period.crash_count, np.maximum(sp, 0)),
                             "clipped_forecasts": int(np.sum(sp < 0))}

    report = {
        "environment": {"python": sys.version, "platform": platform.platform(),
                        "packages": {name: version(name) for name in ("numpy", "pandas", "scipy", "statsmodels")}},
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "input": "Data/cville_sarimax_analysis.csv",
        "validation_report": "Output/sarimax_validation_report.json",
        "order_selection": {"fit_period": ["2017-01-01", "2022-12-31"],
                            "validation_period": ["2023-01-01", "2023-12-31"],
                            "criterion": "rolling next-day MAE on no-weather model",
                            "grid": "p,q,P,Q in {0,1}; d in {0,1}; D=0; m=7",
                            "tie_break": "fewest total AR/MA terms, then lower training-fit AIC",
                            "selected_order": list(best_order),
                            "selected_seasonal_order": list(best_seasonal),
                            "selected_validation_mae": best_mae, "selected_training_aic": best_aic,
                            "candidates": selection},
        "scaling": {"fit_period": ["2017-01-01", "2022-12-31"],
                    "means": means.to_dict(), "population_std": scales.to_dict()},
        "final_fit_period": ["2017-01-01", "2023-12-31"],
        "test_period": ["2024-01-01", "2025-12-31"],
        "forecast_method": "one day ahead; append observed count after each forecast, no coefficient refit",
        "metrics": model_metrics, "metrics_by_year": annual_metrics,
        "intercept_policy": {"rule": "trend=c when d=0; trend=n when d=1",
                             "selected_trend": trend_for_order(best_order),
                             "fitted_intercepts": {name: float(result.params.get("intercept", 0.0))
                                                   for name, result in fit_results.items()}},
        "constant_baselines": {
            "validation_fit_period": ["2017-01-01", "2022-12-31"],
            "validation_period": ["2023-01-01", "2023-12-31"],
            "validation_metrics": baseline_validation_metrics,
            "test_fit_period": ["2017-01-01", "2023-12-31"],
            "test_values": {name: float(pred[0]) for name, pred in test_constants.items()},
            "policy": "Separate prespecified mean/median forecasts, fixed throughout evaluation; no test outcomes used to estimate constants",
            "weather_beats_all_benchmarks_on_mae": bool(all(
                model_metrics["with_weather"]["mae"] < model_metrics[name]["mae"]
                for name in ("no_weather", "seasonal_naive_7day", "constant_mean", "constant_median"))),
        },
        "goal_assessment": {
            "target": "with-weather test MAE lower than both no-weather and seasonal-naive models",
            "met": bool(model_metrics["with_weather"]["mae"] < model_metrics["no_weather"]["mae"]
                        and model_metrics["with_weather"]["mae"] < model_metrics["seasonal_naive_7day"]["mae"]),
            "result": ("weather model beats both comparators" if
                       model_metrics["with_weather"]["mae"] < model_metrics["no_weather"]["mae"]
                       and model_metrics["with_weather"]["mae"] < model_metrics["seasonal_naive_7day"]["mae"]
                       else "null result: weather model did not beat both comparators on test MAE"),
        },
        "clipped_negative_forecasts": clip_counts,
        "bootstrap_mae_differences": intervals,
        "bootstrap_mae_differences_by_year": intervals_by_year,
        "bootstrap": {"method": "paired circular moving blocks", "block_size_days": BLOCK_SIZE,
                      "resamples": BOOTSTRAPS, "seed": SEED,
                      "interpretation": "negative weather-minus-comparator favors weather"},
        "residual_checks": residual_checks,
        "sensitivity_2020_2021": sensitivity,
        "forecast_file": "Output/sarimax_test_forecasts.csv",
    }
    with open(OUT / "sarimax_model_report.json", "w") as f:
        json.dump(report, f, indent=2, default=lambda value: float(value))
    print(f"Selected order {best_order} seasonal {best_seasonal}; wrote forecasts and evaluation report.")


if __name__ == "__main__":
    main()
