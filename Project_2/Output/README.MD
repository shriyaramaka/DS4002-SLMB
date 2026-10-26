# Project outputs

This folder contains dataset-build outputs, EDA figures/tables, and fitted model results. The source snapshot was downloaded October 9, 2026.

## Modeling outputs

- `sarimax_test_forecasts.csv`: 3,655 rows covering five models over 731 test dates in 2024–2025. Columns contain date, year, model, observed crash count, scored forecast, raw forecast, and clipping indicator.
- `sarimax_model_report.json`: order search, selected trend/intercepts, overall/yearly MAE and RMSE, validation/test mean and median constants, paired circular seven-day block-bootstrap intervals, residual checks, sensitivity results, and execution environment.
- `sarimax_validation_report.json`: final-input checks and chronological split summaries.
- `cville_sarimax_analysis.csv`: mirror of the final nine-column input in Data/.

The five models are SARIMAX without weather, SARIMAX with lag-seven weather, seven-day seasonal naive, constant mean, and constant median. Mean/median constants use only 2017–2022 for 2023 validation and 2017–2023 for 2024–2025 testing; they stay fixed during each evaluation. The forecast export bug is corrected. Scores and expected results appear in the root README.MD; the JSON is the complete numerical report. No extra summary CSVs or verification scripts are required.

## Existing organized outputs

- `Dataset_Tables/`: five cleaned/intermediate tables. Frozen copies in Data/ are analysis inputs.
- `EDA_Tables/`: six summaries of overall statistics, missingness, annual/weekday patterns, and weather groups.
- `EDA_Figures/`: nine images containing 12 plots. Figure mapping: 01 missingness; 02 monthly trend; 03 annual counts; 04 count distribution; 05 weekdays; 06 hourly patterns/heatmap; 07 severity/collision; 08 locations; 09 weather associations.
- `Reports/`: source quality and provenance reports from the supplied data build.

The builder and notebook write regenerated files directly into Output/, not these organized subfolders. Rerunning replaces same-named generated files but does not refresh subfolder copies automatically. Presentation figures/tables can be saved here as finalized.

## Interpretation

Partial 2026 records are excluded from modeling. Zero-record days do not prove complete reporting or absence of crashes. Weather measures are regional reanalysis. The study evaluates retrospective predictive associations, not causation or individual risk. The implemented sensitivity check trains on 2017–2019 and evaluates 2020–2021; it is not the originally proposed exclusion check. Source terms and attribution are documented in Data/README.MD and the root references.
