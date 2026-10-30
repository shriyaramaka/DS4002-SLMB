"""Build the nine-column SARIMAX analysis file for SLMB project 2.

Input : Data/cville_daily_crashes_weather.csv   (built by build_dataset.py)
        Data/cville_weather_daily.csv           (used only to verify lag-7 weather)
Output: Data/cville_sarimax_analysis.csv
        Output/cville_sarimax_analysis.csv      (copy)
        Output/sarimax_validation_report.json

Run from the repo root:  python Scripts/prepare_sarimax_data.py
"""
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

# Paths are resolved from this file's location, so the script works from any directory.
ROOT = Path(__file__).resolve().parents[1]
DAILY = ROOT / "Data" / "cville_daily_crashes_weather.csv"
WEATHER = ROOT / "Data" / "cville_weather_daily.csv"
OUT_DATA = ROOT / "Data" / "cville_sarimax_analysis.csv"
OUT_DIR = ROOT / "Output"

# Final column order: date, outcome, exogenous predictors, then the split label.
COLUMNS = [
    "date_local", "crash_count", "month_sin", "month_cos",
    "temp_mean_c_lag7", "precip_mm_lag7", "snowfall_cm_lag7", "wind_max_kmh_lag7",
    "split",
]
# The no-weather model uses only the calendar terms; the weather model adds the lag-7 weather.
EXOG_CALENDAR = ["month_sin", "month_cos"]
EXOG_WEATHER = ["temp_mean_c_lag7", "precip_mm_lag7", "snowfall_cm_lag7", "wind_max_kmh_lag7"]
# Excluded on purpose: manual crash lags would duplicate the SARIMAX AR/MA terms,
# same-day weather and injury/fatality counts are not known before the target day,
# and the weekly pattern is handled by the seven-day seasonal terms.
FORBIDDEN = [  # must never appear in the analysis file
    "crash_count_lag1", "crash_count_lag7", "crash_count_lag14",
    "crash_count_prior7_mean", "crash_count_prior28_mean",
    "injury_crash_count", "fatal_crash_count", "persons_injured", "persons_killed",
    "observed_temp_max_c", "observed_temp_min_c", "observed_temp_mean_c",
    "observed_precip_mm", "observed_snowfall_cm", "observed_wind_max_kmh",
    "weekday_mon0", "is_weekend",
]


def assign_split(year: int) -> str:
    """Chronological split: fit on 2017-2022, choose orders on 2023, test on 2024-2025."""
    if 2017 <= year <= 2022:
        return "train"
    if year == 2023:
        return "validation"
    if year in (2024, 2025):
        return "test"
    raise ValueError(f"year {year} outside the study period")


def main() -> None:
    # Every check result is stored here and written to the validation report.
    # Any failed assert stops the script before an output file is written.
    checks = {}
    df = pd.read_csv(DAILY, parse_dates=["date_local"]).sort_values("date_local").reset_index(drop=True)

    # 1. Base-table integrity
    # SARIMAX assumes one row per day, so any missing or repeated date would shift the lags.
    gaps = df.date_local.diff().dropna() != pd.Timedelta(days=1)
    checks["dates_unique"] = bool(df.date_local.is_unique)
    checks["dates_continuous"] = not bool(gaps.any())
    checks["study_period"] = [str(df.date_local.min().date()), str(df.date_local.max().date())]
    checks["rows"] = int(len(df))
    checks["total_crashes"] = int(df.crash_count.sum())
    checks["no_partial_2026"] = bool(df.date_local.dt.year.max() <= 2025)
    assert checks["dates_unique"] and checks["dates_continuous"] and checks["no_partial_2026"]
    # Expected totals for the frozen 2017-2025 dataset documented in Data/README.MD.
    assert checks["rows"] == 3287 and checks["total_crashes"] == 5197

    # 2. Month terms follow the documented formula
    # Sine/cosine encoding puts December next to January instead of 11 months away.
    ang = 2 * np.pi * (df.month - 1) / 12
    checks["month_terms_match_formula"] = bool(
        np.allclose(df.month_sin, np.sin(ang)) and np.allclose(df.month_cos, np.cos(ang)))
    assert checks["month_terms_match_formula"]

    # 3. Lag-7 weather equals the standalone weather file seven calendar days earlier
    # Recompute each lag from the raw weather file to confirm build_dataset.py shifted it correctly.
    w = pd.read_csv(WEATHER, parse_dates=["date_local"]).set_index("date_local")
    lag_ok = {}
    for col in EXOG_WEATHER:
        src = col.removesuffix("_lag7")  # e.g. precip_mm_lag7 -> precip_mm
        expected = w[src].reindex(df.date_local - pd.Timedelta(days=7)).to_numpy()
        lag_ok[col] = bool(np.allclose(df[col], expected, equal_nan=True))
        # and it is not the same-day observation
        lag_ok[col] = lag_ok[col] and not np.allclose(df[col], df[f"observed_{src}"])
    checks["weather_lag7_verified"] = lag_ok
    assert all(lag_ok.values())

    # 4. Build the nine-column file (all study dates kept; pre-2017 weather fills early lags)
    out = df[COLUMNS[:-1]].copy()  # every column except split, which is added next
    out["split"] = out.date_local.dt.year.map(assign_split)
    out["date_local"] = out.date_local.dt.strftime("%Y-%m-%d")  # plain dates, no time part

    # The file must have exactly the nine planned columns, no leakage columns, and no blanks.
    checks["columns"] = list(out.columns)
    checks["column_count"] = len(out.columns)
    checks["forbidden_columns_present"] = sorted(set(FORBIDDEN) & set(out.columns))
    checks["missing_values"] = {c: int(v) for c, v in out.isna().sum().items()}
    assert checks["column_count"] == 9 and not checks["forbidden_columns_present"]
    assert sum(checks["missing_values"].values()) == 0

    # 5. Split is chronological and non-overlapping
    # Per-split summaries go into the report. Variance above the mean indicates overdispersed counts.
    split_summary = {}
    for name, g in out.groupby("split", sort=False):
        split_summary[name] = {
            "start": g.date_local.min(), "end": g.date_local.max(), "days": int(len(g)),
            "crashes": int(g.crash_count.sum()),
            "mean_per_day": round(float(g.crash_count.mean()), 4),
            "variance_per_day": round(float(g.crash_count.var()), 4),
            "zero_days": int((g.crash_count == 0).sum()),
        }
    # Splits must appear in time order and each must end before the next begins.
    order = ["train", "validation", "test"]
    assert list(split_summary) == order
    for a, b in zip(order, order[1:]):
        assert split_summary[a]["end"] < split_summary[b]["start"]
    checks["splits"] = split_summary

    # 6. Write outputs
    OUT_DIR.mkdir(exist_ok=True)
    out.to_csv(OUT_DATA, index=False)
    shutil.copy2(OUT_DATA, OUT_DIR / OUT_DATA.name)
    # fit_sarimax_models.py reads this report and refuses to run unless status is "passed"
    # and the predictor lists match its own.
    report = {
        "built_at_utc": datetime.now(timezone.utc).isoformat(),
        "input": str(DAILY.relative_to(ROOT)),
        "output": str(OUT_DATA.relative_to(ROOT)),
        "exog_no_weather": EXOG_CALENDAR,
        "exog_with_weather": EXOG_CALENDAR + EXOG_WEATHER,
        "not_predictors": ["date_local", "split"],
        "notes": [
            "Crash history is modeled by SARIMAX AR/MA and the seven-day seasonal terms; "
            "no manual crash lags are included.",
            "All 3,287 study dates are retained; weather before 2017 supplies the first lag-7 values.",
            "Scaling and imputation are not applied here; fit them on the train split only.",
        ],
        "checks": checks,
        "status": "passed",
    }
    with open(OUT_DIR / "sarimax_validation_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print(f"Wrote {OUT_DATA.relative_to(ROOT)} ({len(out)} rows x {len(out.columns)} cols); all checks passed.")
    for name, s in split_summary.items():
        print(f"  {name:10s} {s['start']} → {s['end']}  {s['days']:4d} days  {s['crashes']:4d} crashes")


if __name__ == "__main__":
    main()
