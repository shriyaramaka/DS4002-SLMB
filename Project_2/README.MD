# Forecasting Crashes in Charlottesville Based on Weather Conditions

**Group:** SLMB: Statistics, Learning, Models, and Beyond  
**Leader:** Bhargav Garre Venkata  
**Members:** Lyle Mora, Maggie Parkhurst, and Shriya Ramaka  
**Course:** DS 4002, Section 002 — Professor Loreto Alonzi

We study whether weather from seven days earlier improves next-day forecasts of reported Charlottesville crashes beyond crash history and seasonal patterns. The study combines Virginia Department of Transportation (VDOT) crash records [1] and Open-Meteo ERA5 weather [2]. It covers 5,197 reported crashes across 3,287 consecutive days in 2017–2025.

Our goal is a weather-enhanced SARIMAX model with lower test mean absolute error (MAE) than both a SARIMAX model without weather and a seven-day seasonal-naive forecast. SARIMAX explicitly models time dependence [3]. The original Poisson proposal was replaced to meet the project’s time-series requirement.

**Current status:** Data preparation, EDA, fitted forecasts, and a model report are included. The JSON report records a null result for the weather improvement goal. A review found a forecast CSV export error that must be corrected before submission; see [MI3 review](MI3_REVIEW.md). The report’s SARIMAX scores agree with the CSV’s raw forecast column after clipping at zero, but not with its exported `forecast_crash_count` column. Do not use that column for figures or scoring until repaired.

## Repository contents

`Data/` contains frozen source files, cleaned tables, the final modeling input, and metadata. `Scripts/` contains the complete supplied code. `Output/` contains generated tables, EDA figures, forecasts, and model reports. The folder names below use their actual capitalization; commands and links on Linux are case-sensitive. The rubric’s DATA, SCRIPTS, and OUTPUT refer to these same roles.

### 1. Software and platform

Use **Python 3.9 or newer**. The builder uses the standard library, including `zoneinfo`. Install these add-on packages in one environment:

```bash
python -m pip install numpy pandas matplotlib statsmodels jupyterlab ipykernel tzdata
```

- `numpy` and `pandas`: data validation, preparation, numerical calculations, and metrics.
- `matplotlib`: EDA figures.
- `statsmodels`: SARIMAX fitting and residual diagnostics.
- `jupyterlab` and `ipykernel`: running the EDA notebook; IPython is installed as a dependency.
- `tzdata`: America/New_York timezone support, particularly on Windows.

The scripts use `pathlib` and can be run on Windows, macOS, or Linux. The ZIP does not record the platform or package versions used for the original model run. During this repository review, the builder and preparation script passed on Linux with Python 3.12.14, pandas 2.2.3, and NumPy 2.3.5. The full SARIMAX fit and notebook were not rerun in that review environment. Before submission, record the team’s actual analysis platform and package versions; the installation command above is not a pinned environment.

On macOS/Linux, use `python3` in place of `python` if needed. On Windows, use the Python interpreter associated with the selected environment. Record versions after the final successful run with:

```bash
python --version
python -m pip freeze > Output/environment_packages.txt
python -c "import platform; print(platform.platform())" > Output/platform.txt
```

### 2. Map of the documentation and files

```text
Project_2/
├── README.md                         Project orientation and reproduction instructions
├── LICENSE.md                        MIT license for project software
├── REFERENCES.MD                     Extended project reference list
├── MI3_REVIEW.md                      Rubric findings and remaining corrections
├── Data/
│   ├── README.MD                     Summary, provenance, terms, ethics, dictionary, plots
│   ├── cville_crash_incidents.csv     5,432 incidents, including partial 2026
│   ├── cville_weather_daily.csv       3,530 daily weather observations
│   ├── cville_daily_crashes_weather.csv  3,287-row, 33-column intermediate table
│   ├── cville_sarimax_analysis.csv    Final 3,287-row, nine-column model input
│   ├── annual_crash_counts.csv
│   ├── source_codebook.csv
│   ├── quality_report.json
│   ├── provenance.json
│   ├── mi2_daily_crash_distribution.png
│   ├── mi2_annual_crash_counts.png
│   └── raw/
│       ├── crashes.json
│       ├── crash_metadata.json
│       ├── weather.json
│       └── weather_request.json
├── Scripts/
│   ├── README.MD                     Script purposes, dependencies, execution order
│   ├── build_dataset.py              Step 1: reconstruct tables from frozen JSON
│   ├── prepare_sarimax_data.py        Step 2: prepare and validate final model input
│   ├── fit_sarimax_models.py          Step 3: fit models and evaluate forecasts
│   └── Charlottesville_Crash_EDA.ipynb  Step 4: descriptive exploration and plots
└── Output/
    ├── README.MD                     Output descriptions; some statements need updating
    ├── cville_sarimax_analysis.csv    Mirror of final modeling input
    ├── sarimax_validation_report.json
    ├── sarimax_model_report.json      Order search, scores, intervals, diagnostics
    ├── sarimax_test_forecasts.csv     Daily forecasts; export correction required
    ├── Dataset_Tables/
    │   ├── cville_crash_incidents.csv
    │   ├── cville_weather_daily.csv
    │   ├── cville_daily_crashes_weather.csv
    │   ├── annual_crash_counts.csv
    │   └── source_codebook.csv
    ├── EDA_Tables/
    │   ├── eda_summary.csv
    │   ├── eda_missing_values.csv
    │   ├── eda_annual_counts.csv
    │   ├── eda_weekday_counts.csv
    │   ├── eda_precipitation_summary.csv
    │   └── eda_temperature_summary.csv
    ├── EDA_Figures/
    │   ├── eda_figure_01.png           Missing values
    │   ├── eda_figure_02.png           Monthly counts and trailing average
    │   ├── eda_figure_03.png           Annual counts
    │   ├── eda_figure_04.png           Daily count distribution
    │   ├── eda_figure_05.png           Weekday means
    │   ├── eda_figure_06.png           Hourly totals and weekday-hour heatmap
    │   ├── eda_figure_07.png           Severity and collision types
    │   ├── eda_figure_08.png           Spatial concentration
    │   └── eda_figure_09.png           Weather associations
    └── Reports/
        ├── quality_report.json
        └── provenance.json
```

The existing output subfolders contain organized copies. **The supplied scripts write new files directly into `Output/`, not those subfolders.** Rerunning does not update the organized copies automatically. Newly rebuilt files and future model figures therefore appear alongside the SARIMAX reports at the top of `Output/`.

### 3. Instructions for reproducing the results

1. **Download or clone the repository.** Open a terminal in `Project_2/`, the directory containing this README and `Data/`, `Scripts/`, and `Output/`. Install the packages above in your chosen Python environment. Retain a copy of the supplied reports to compare with regenerated outputs; rerunning replaces same-named generated files.

2. **Rebuild the cleaned data from the frozen source snapshot.** Run:

   ```bash
   python Scripts/build_dataset.py
   ```

   This reads `Data/raw/` and writes five CSVs plus `quality_report.json` and `provenance.json` directly into `Output/`. Expected checks include 5,432 incident rows overall, 5,197 study incidents, 3,287 daily study rows, and zero unmatched weather days. Partial 2026 incidents are retained in the incident file but excluded from the study panel. The builder leaves frozen tables in `Data/` unchanged. Do not use `--refresh` to reproduce the October 9 snapshot: that option downloads current source responses.

3. **Connect the rebuilt data to the modeling pipeline.** After confirming the checks pass, copy the two rebuilt model source tables into `Data/`:

   ```bash
   python -c "from pathlib import Path; import shutil; [shutil.copy2(Path('Output')/n, Path('Data')/n) for n in ['cville_daily_crashes_weather.csv', 'cville_weather_daily.csv']]"
   python Scripts/prepare_sarimax_data.py
   ```

   This replaces the corresponding derived Data tables with the frozen-raw rebuild; it does not change `Data/raw/`. The preparation script writes `Data/cville_sarimax_analysis.csv`, an identical `Output/` copy, and `Output/sarimax_validation_report.json`. Expect 3,287 rows, nine columns, no missing values, and splits of 2,191 training days, 365 validation days, and 731 test days. Alternatively, run the preparation script directly against the included frozen Data tables, which matched the raw-data rebuild in review.

4. **Correct the known forecast export error before relying on model CSV outputs.** In `Scripts/fit_sarimax_models.py`, the row-writing block currently uses the first element of a whole forecast array for every date. [MI3_REVIEW.md](MI3_REVIEW.md) gives the exact correction. The code is retained unchanged in this documentation update, so this repair remains required.

5. **Fit and evaluate the models.** Run:

   ```bash
   python Scripts/fit_sarimax_models.py
   ```

   The script searches 32 SARIMAX orders using only 2017–2022 fits and rolling 2023 validation MAE for the no-weather model. Both variants share the selected order. It refits through 2023 and forecasts each 2024–2025 day before using that day’s observed outcome to update the state, without refitting coefficients. Weather predictors are mean temperature, precipitation, snowfall, and maximum wind from seven days earlier; both models also use month sine/cosine terms. Scaling is learned from 2017–2022. The seasonal-naive comparator uses the observed count seven days earlier.

   Results are `Output/sarimax_test_forecasts.csv` and `Output/sarimax_model_report.json`. The report includes overall and annual MAE/RMSE, paired circular seven-day block bootstrap intervals (2,000 resamples; seed 4002), clipping counts, residual Ljung–Box checks, and a pre-pandemic-trained evaluation on 2020–2021. There is no fixed runtime guarantee; the search makes many model fits. Exact numerical reproduction may depend on package versions and optimization.

6. **Run the EDA notebook.** Launch:

   ```bash
   python -m jupyterlab
   ```

   Open `Scripts/Charlottesville_Crash_EDA.ipynb`, select the same Python environment, restart the kernel, and run all cells in order. Start from the project root or `Scripts/`. It reads the frozen Data tables and writes nine PNG figures and six EDA CSV summaries directly into `Output/`; it also displays the plots. The two EDA images in `Data/` are metadata copies of figures 04 and 03. Same-day weather plots are descriptive, not forecasting inputs. The notebook examines the full study period, so it is not evidence that the test years were unseen during data exploration.

7. **Validate the final exported results and record deviations.** Confirm 731 unique dates per model (2,193 forecast rows), actual counts matching Data, seasonal-naive values equal to count lag 7, and CSV MAE/RMSE agreeing with the JSON report. Record package versions and platform. Document the implemented sensitivity analysis as a change from MI2, or implement the preregistered exclusion check; these answer different questions. Save presentation tables and figures in `Output/` as they are finalized for MI4.

## Results included in this snapshot

These figures come from `Output/sarimax_model_report.json`. The SARIMAX scores were independently checked against the raw forecast column after clipping; the seasonal-naive scores were checked against count lag 7 from Data. The whole model search was not rerun for this documentation review.

| Model | Test MAE | Test RMSE | Days |
| --- | ---: | ---: | ---: |
| SARIMAX without weather | 1.089041 | 1.402993 | 731 |
| SARIMAX with earlier weather | 1.089183 | 1.403236 | 731 |
| Seven-day seasonal naive | 1.476060 | 1.969327 | 731 |

The selected order is `(1, 0, 1)` with seasonal order `(1, 0, 1, 7)`. Adding earlier weather changes MAE by approximately **+0.000142 crashes/day** relative to the no-weather model; the reported 95% block-bootstrap interval is approximately **[−0.01584, 0.01440]**. The weather model beats seasonal naive but does not beat the matched no-weather model. The goal is therefore **not met**; this is a null result for improvement from these weather features, not evidence that weather has no relationship with crashes.

## Data terms and interpretation

The software is covered by [LICENSE.md](LICENSE.md). The MIT license does not override third-party data conditions. Preserve VDOT’s source terms [1] and Open-Meteo/ERA5 attribution [2], [4], [5]. The Data README records the unresolved VDOT redistribution terms; confirm the intended repository visibility and instructor access before submission.

Counts describe reported city crashes, not all emergencies, individual risk, or risk per trip. Historical reporting dates and weather publication timing are not fully established, so this is a retrospective forecasting study. SARIMAX is a Gaussian model applied to small counts; negative point forecasts are clipped at zero consistently, and forecasts are not rounded. Predictive associations do not establish causation.

## References

Reference numbers below apply to this README. See [REFERENCES.MD](REFERENCES.MD) for the extended list; older Data `source_ref` tags use the Data README’s numbering.

[1] Virginia Department of Transportation, “Full_Crash,” Virginia Roads, ArcGIS REST Services Directory. Accessed: Oct. 21, 2026. [Online]. Available: https://services.arcgis.com/p5v98VHDX9Atv3l7/arcgis/rest/services/Full_Crash/FeatureServer

[2] Open-Meteo, “Historical Weather API.” Accessed: Oct. 21, 2026. [Online]. Available: https://open-meteo.com/en/docs/historical-weather-api

[3] statsmodels developers, “statsmodels.tsa.statespace.sarimax.SARIMAX,” statsmodels documentation. Accessed: Oct. 21, 2026. [Online]. Available: https://www.statsmodels.org/stable/generated/statsmodels.tsa.statespace.sarimax.SARIMAX.html

[4] Open-Meteo, “Terms & Privacy.” Accessed: Oct. 21, 2026. [Online]. Available: https://open-meteo.com/en/terms

[5] Creative Commons, “Attribution 4.0 International (CC BY 4.0).” Accessed: Oct. 21, 2026. [Online]. Available: https://creativecommons.org/licenses/by/4.0/
