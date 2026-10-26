# Forecasting Crashes in Charlottesville Based on Weather Conditions

**Group:** SLMB: Statistics, Learning, Models, and Beyond  
**Leader:** Bhargav Garre Venkata  
**Members:** Lyle Mora, Maggie Parkhurst, and Shriya Ramaka  
**Course:** DS 4002, Section 002 — Professor Loreto Alonzi

We test whether earlier weather improves next-day forecasts of reported Charlottesville crashes beyond crash history and seasonality. The study combines VDOT crash records [1] and Open-Meteo ERA5 weather [2]: 5,197 reported crashes across 3,287 days in 2017–2025. Our original goal is lower test MAE for weather-enhanced SARIMAX than both SARIMAX without weather and a seven-day seasonal-naive forecast. Constant mean and median benchmarks were added following later MI2 feedback.

## Repository contents

`Data/` holds frozen source data, intermediate/final tables, metadata, and two explanatory plots. `Scripts/` holds source code and the EDA notebook. `Output/` holds generated tables, figures, model forecasts, and reports. Folder/file capitalization below matches the original repository. Supporting documentation is in [Data/README.MD](Data/README.MD), [Scripts/README.MD](Scripts/README.MD), and [Output/README.MD](Output/README.MD).

### 1. Software and platform

The corrected data/model pipeline was run on Linux, Python 3.12.14, with NumPy 2.3.5, pandas 2.2.3, SciPy 1.17.0, statsmodels 0.14.6, patsy 1.0.3, Matplotlib 3.10.8, and tzdata 2026.5. The model report records the actual model execution environment. Install the analysis dependencies using:

```bash
python -m pip install numpy==2.3.5 pandas==2.2.3 scipy==1.17.0 statsmodels==0.14.6 patsy==1.0.3 matplotlib==3.10.8 tzdata==2026.5
```

For the notebook, also install `jupyterlab` and `ipykernel`. These provide IPython and a notebook interface. Use `python3` instead of `python` if required by your environment. macOS/Windows were not tested in the correction run; paths are portable, and tzdata supplies America/New_York timezone data. The original EDA notebook/plots were retained, not rerun during this correction. No additional review or test files are required to execute the project.

### 2. Documentation map

```text
Project_2/
├── Data/
│   ├── README.MD
│   ├── annual_crash_counts.csv
│   ├── cville_crash_incidents.csv
│   ├── cville_daily_crashes_weather.csv
│   ├── cville_sarimax_analysis.csv
│   ├── cville_weather_daily.csv
│   ├── mi2_annual_crash_counts.png
│   ├── mi2_daily_crash_distribution.png
│   ├── provenance.json
│   ├── quality_report.json
│   ├── raw/
│   │   ├── crash_metadata.json
│   │   ├── crashes.json
│   │   ├── weather.json
│   │   └── weather_request.json
│   └── source_codebook.csv
├── LICENSE
├── Output/
│   ├── Dataset_Tables/
│   │   ├── annual_crash_counts.csv
│   │   ├── cville_crash_incidents.csv
│   │   ├── cville_daily_crashes_weather.csv
│   │   ├── cville_weather_daily.csv
│   │   └── source_codebook.csv
│   ├── EDA_Figures/
│   │   ├── eda_figure_01.png
│   │   ├── eda_figure_02.png
│   │   ├── eda_figure_03.png
│   │   ├── eda_figure_04.png
│   │   ├── eda_figure_05.png
│   │   ├── eda_figure_06.png
│   │   ├── eda_figure_07.png
│   │   ├── eda_figure_08.png
│   │   └── eda_figure_09.png
│   ├── EDA_Tables/
│   │   ├── eda_annual_counts.csv
│   │   ├── eda_missing_values.csv
│   │   ├── eda_precipitation_summary.csv
│   │   ├── eda_summary.csv
│   │   ├── eda_temperature_summary.csv
│   │   └── eda_weekday_counts.csv
│   ├── README.MD
│   ├── Reports/
│   │   ├── provenance.json
│   │   └── quality_report.json
│   ├── cville_sarimax_analysis.csv
│   ├── sarimax_model_report.json
│   ├── sarimax_test_forecasts.csv
│   └── sarimax_validation_report.json
├── README.MD
├── REFERENCES.MD
└── Scripts/
    ├── Charlottesville_Crash_EDA.ipynb
    ├── README.MD
    ├── build_dataset.py
    ├── fit_sarimax_models.py
    └── prepare_sarimax_data.py
```

The builder and notebook write new files directly into `Output/`. Its existing subfolders hold organized copies; rerunning does not automatically replace those copies. Frozen inputs remain in `Data/` unless explicitly copied as described below.

### 3. Reproduce the results

1. **Open a terminal in the repository root**, containing this README and the three project folders. Install the dependencies above. Reruns replace generated files with the same names.

2. **Rebuild the frozen data.** Run:

   ```bash
   python Scripts/build_dataset.py
   ```

   This reads `Data/raw/` and writes five CSVs plus quality/provenance JSONs directly into `Output/`. Expect **5,432 incidents overall, 5,197 study incidents, 3,287 study days, and zero unmatched weather days**. Do not use `--refresh` to reproduce the frozen October 9 snapshot; it downloads current responses.

3. **Prepare the final model input.** Pass the rebuilt daily and weather tables to preparation:

   ```bash
   python -c "from pathlib import Path; import shutil; [shutil.copy2(Path('Output')/n, Path('Data')/n) for n in ['cville_daily_crashes_weather.csv', 'cville_weather_daily.csv']]"
   python Scripts/prepare_sarimax_data.py
   ```

   Expect `Data/cville_sarimax_analysis.csv`, its `Output/` mirror, and `Output/sarimax_validation_report.json`: **3,287 rows, nine columns, no missing values**, and train/validation/test sizes of **2,191/365/731 days**. Raw JSON files are unchanged.

4. **Fit and evaluate the models.** Run:

   ```bash
   python Scripts/fit_sarimax_models.py
   ```

   The search fits 32 candidates on 2017–2022 and selects the no-weather order using rolling next-day validation MAE on 2023. Both SARIMAX variants share the order and refit through 2023. Test forecasts cover 2024–2025, updating states after each observed day without refitting coefficients. Month sine/cosine terms appear in both models; the weather model adds mean temperature, precipitation, snowfall, and wind from seven days earlier. Scaling is learned from 2017–2022.

   Mean/median baselines use 2017–2022 for validation and 2017–2023 for testing, then remain fixed throughout each evaluation. Seasonal naive uses the observed count seven days earlier. Candidate intercepts use `trend='c'` when d=0 and `trend='n'` when d=1 [3].

   Expected outputs are the existing `Output/sarimax_test_forecasts.csv` and `Output/sarimax_model_report.json`. The CSV contains **3,655 rows: five models × 731 days**, with observed counts, scored/raw forecasts, and clipping flags. The exporter checks its values before writing. The report includes overall/yearly MAE/RMSE, baseline values, fitted intercepts, order search, seven-day circular block-bootstrap intervals (2,000 resamples; seed 4002), residual diagnostics, sensitivity results, and environment. Compare with the expected results below; optimizer/package differences may affect final digits. No manual code changes are required.

5. **Run EDA.** Launch `python -m jupyterlab`, open `Scripts/Charlottesville_Crash_EDA.ipynb`, select the installed environment, restart the kernel, and run all cells. Start from the project root or Scripts/. Expect **nine numbered PNG figures and six CSV summaries directly in Output/**, with plots displayed in the notebook. Same-day weather associations are descriptive, not forecasting inputs.

## Expected modeling results

| Model | Test MAE | Test RMSE |
| --- | ---: | ---: |
| SARIMAX without weather | 1.086120 | 1.395554 |
| SARIMAX with earlier weather | 1.090465 | 1.400223 |
| Constant median (predict 1) | 1.114911 | 1.592991 |
| Constant mean | 1.118596 | 1.429067 |
| Seven-day seasonal naive | 1.476060 | 1.969327 |

The selected order is **(1,0,1)** with seasonal order **(1,0,1,7)** and an intercept. The final test constants are **mean = 1.538732394** and **median = 1**. Validation constants are mean = 1.523505249 and median = 1, calculated before 2023.

Both SARIMAX models beat both constant benchmarks and seasonal naive on test MAE. However, the weather model does not beat the no-weather model, so the original goal is **not met**. The weather-minus-no-weather MAE difference is approximately **+0.004344402** crashes/day, with a reported 95% block-bootstrap interval of **[−0.000654253, 0.009597203]**. This does not demonstrate improvement from the lagged weather features.

## Decisions and limitations

The source records count reported city crashes, not all emergencies or risk per trip. Reporting/publication timing is imperfectly known, so this is retrospective forecasting. SARIMAX is a Gaussian model applied to small counts; negative test point forecasts are clipped at zero for both models, and positive forecasts are not rounded. Validation MAE currently uses raw forecasts. Stationarity/invertibility are not enforced; convergence alone does not guarantee stability. Residual Ljung–Box results are descriptive and are not adjusted for fitted AR/MA degrees of freedom.

The implemented sensitivity check trains on 2017–2019 and forecasts 2020–2021. This is a documented deviation from MI2's planned exclusion of 2020–2021 when fitting through 2023; the two analyses are not equivalent. Full-period EDA is not evidence that the test years were unseen during exploration. Predictive associations do not establish causation.

## License and attribution

The existing [LICENSE](LICENSE) provides MIT terms for project software. Third-party data retain their own source conditions: preserve VDOT terms [1] and Open-Meteo/ERA5 attribution and applicable CC BY 4.0 requirements [2], [4], [5]. Data/README.MD documents unresolved VDOT redistribution conditions. GitHub access and repository visibility are managed by the group.

## References

Numbers apply to this README; Data source_ref tags follow the Data README's numbering. The extended bibliography is in [REFERENCES.MD](REFERENCES.MD).

[1] Virginia Department of Transportation, “Full_Crash,” Virginia Roads, ArcGIS REST Services Directory. Accessed: Oct. 21, 2026. [Online]. Available: https://services.arcgis.com/p5v98VHDX9Atv3l7/arcgis/rest/services/Full_Crash/FeatureServer

[2] Open-Meteo, “Historical Weather API.” Accessed: Oct. 21, 2026. [Online]. Available: https://open-meteo.com/en/docs/historical-weather-api

[3] statsmodels developers, “statsmodels.tsa.statespace.sarimax.SARIMAX,” statsmodels documentation. Accessed: Oct. 21, 2026. [Online]. Available: https://www.statsmodels.org/stable/generated/statsmodels.tsa.statespace.sarimax.SARIMAX.html

[4] Open-Meteo, “Terms & Privacy.” Accessed: Oct. 21, 2026. [Online]. Available: https://open-meteo.com/en/terms

[5] Creative Commons, “Attribution 4.0 International (CC BY 4.0).” Accessed: Oct. 21, 2026. [Online]. Available: https://creativecommons.org/licenses/by/4.0/
