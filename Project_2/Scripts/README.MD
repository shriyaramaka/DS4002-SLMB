# Scripts

## Files

| File | Purpose |
| --- | --- |
| `build_dataset.py` | Rebuilds the cleaned crash, weather, joined daily, annual-count, and codebook tables from the source JSON files. Checks identifiers, geography, counts, and joins, and generates quality and provenance reports. |
| `prepare_sarimax_data.py` | Builds the nine-column SARIMAX analysis file from the joined daily table. Verifies the study period, month terms, and lag-7 weather, excludes leakage columns, assigns the train/validation/test split, and writes a validation report. |
| `Charlottesville_Crash_EDA.ipynb` | Explores data quality, trends, weekday/hour patterns, severity, collision types, locations, and weather associations. Saves nine figure files containing 12 plots and six summary tables. |

## Requirements

- Python 3.9 or newer, with America/New_York timezone data.
- The builder uses only Python's standard library.
- `prepare_sarimax_data.py` requires `pandas` and `numpy`.
- The notebook requires `pandas`, `numpy`, `matplotlib`, and a notebook environment such as Jupyter or VS Code with a Python kernel.

## Run the dataset builder

From the project root:

```bash
python3 Scripts/build_dataset.py
```

This reads `Data/raw/` and writes rebuilt CSVs, `quality_report.json`, and `provenance.json` directly into `Output/`. It leaves the frozen inputs in `Data/` unchanged.

To download current source records and rebuild:

```bash
python3 Scripts/build_dataset.py --refresh
```

New API responses are saved in `Output/raw/` and used by that invocation. A later run without `--refresh` returns to the frozen `Data/raw/` inputs. Date ranges remain fixed unless changed explicitly in the script.

## Build the SARIMAX analysis file

From the project root:

```bash
python3 Scripts/prepare_sarimax_data.py
```

This reads `Data/cville_daily_crashes_weather.csv` and `Data/cville_weather_daily.csv`, then writes `Data/cville_sarimax_analysis.csv`, a copy at `Output/cville_sarimax_analysis.csv`, and `Output/sarimax_validation_report.json`. The script stops with an error if any check fails, for example if the row count is not 3,287, a lag-7 weather value does not match the weather file, or a leakage column appears in the output.

## Run the EDA notebook

Open `Scripts/Charlottesville_Crash_EDA.ipynb` with the working directory set to the project root or `Scripts/`, then run all cells in order. The notebook reads the frozen CSVs in `Data/` and writes figures and summary tables directly into `Output/`. Plots are also displayed inside the notebook.

Figure names run from `eda_figure_01.png` through `eda_figure_09.png`. Summary files are `eda_summary.csv`, `eda_missing_values.csv`, `eda_annual_counts.csv`, `eda_weekday_counts.csv`, `eda_precipitation_summary.csv`, and `eda_temperature_summary.csv`.

The separate outputs-only download organizes copies into subfolders for convenience; the current scripts themselves write directly into `Output/`. Rerunning them replaces their same-named generated files.

