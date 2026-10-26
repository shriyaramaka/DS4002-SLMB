# Project References

Charlottesville Crash and Weather Forecasting — DS 4002, SLMB
References [1]–[6] retain the numbering used in the MI2 discussion. Reference [3] documents the original Poisson proposal; [6] supports the revised SARIMAX plan. The current preparation script and EDA notebook do not implement forecasting yet. References for proposed methods do not imply that those methods have already been run.

## References

Charlottesville Crash and Weather Forecasting — DS 4002, SLMB
Reference [3] documents the historical Poisson proposal; [6] supports the implemented SARIMAX models. This file uses its own numbering, which can differ from MI2 and the root README. Forecast fitting, MAE/RMSE, and paired circular block resampling are implemented in fit_sarimax_models.py. Reference [14] is background on block resampling, not a package called by this implementation.

## Where each source applies

| Project component | References | Use |
| --- | --- | --- |
| Crash data | [1], [7] | Public source records, jurisdiction filter, field definitions, and coded-value labels. DMV maintains the underlying records; VDOT publishes the public service. |
| Weather data | [2] | ERA5 historical reanalysis, weather variables, units, grid resolution, and publication delay. |
| Data terms and attribution | [1], [4], [5] | VDOT source conditions and Open-Meteo/CC BY attribution requirements. |
| Initial modeling proposal | [3] | Poisson regression from the original plan; retain for project history or a benchmark if implemented. |
| Revised forecasting approach | [6], [8] | SARIMAX, temporal dependence, seasonal models, dynamic regression, and chronological forecast evaluation. Useful textbook sections include Chapters 5, 9, and 10. |
| EDA software | [9]–[11] | Tables and date handling, numerical operations, validation, and plotted figures in the existing notebook. |
| Forecast metrics | [12], [13] | MAE as the primary metric and RMSE as a secondary metric. |
| Uncertainty assessment | [14] | Consecutive-block resampling for dependent observations. The code uses a NumPy implementation of circular blocks; this is a background reference, not evidence that seven-day blocks are optimal for this dataset. |

## Data attribution and provenance

**Crash records:** Virginia DMV TREDS records, published by the Virginia Department of Transportation through Virginia Roads [1], [7]. City records were selected using `PHYSICAL_JURIS = '104'`. The source's disclaimers and use conditions remain applicable; this reference list does not grant redistribution rights.

**Weather:** Historical weather data provided by Open-Meteo using ERA5 reanalysis [2]. The requested coordinates were 38.03° N, 78.48° W; the returned grid point was 38.00° N, 78.50° W. Under the project's documented use of CC BY 4.0 [4], [5], retain attribution and the license link and identify changes. Project changes include conversion to tables, date joins, aggregation, and derived lag features.

**Snapshot:** The project data were downloaded October 9, 2026. The access dates above identify when these reference pages were checked for this file; they do not indicate a new data download. Consult `provenance.json` and the original request files for retrieval timestamps and source hashes.

## Citation consistency

Use these references for the current project narrative. Standalone documents may renumber references in order of first appearance. Older dataset READMEs and CSV `source_ref` tags use their own numbering; interpret those tags using the corresponding original README rather than assuming that they match this file. Do not edit historical source-reference tags silently.

Software documentation links above describe the tools, not the exact package versions installed by the group. Record the versions actually used when running the final analysis. Cite only the methods and software used in each submitted report, and describe any change from the preregistered plan.

## References

[1] Virginia Department of Transportation, “Full_Crash,” Virginia Roads, ArcGIS REST Services Directory. Accessed: Oct. 21, 2026. [Online]. Available: https://services.arcgis.com/p5v98VHDX9Atv3l7/arcgis/rest/services/Full_Crash/FeatureServer

[2] Open-Meteo, “Historical Weather API.” Accessed: Oct. 21, 2026. [Online]. Available: https://open-meteo.com/en/docs/historical-weather-api

[3] Scikit-learn developers, “PoissonRegressor,” scikit-learn documentation. Accessed: Oct. 21, 2026. [Online]. Available: https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.PoissonRegressor.html

[4] Open-Meteo, “Terms & Privacy.” Accessed: Oct. 21, 2026. [Online]. Available: https://open-meteo.com/en/terms

[5] Creative Commons, “Attribution 4.0 International (CC BY 4.0).” Accessed: Oct. 21, 2026. [Online]. Available: https://creativecommons.org/licenses/by/4.0/

[6] Statsmodels developers, “statsmodels.tsa.statespace.sarimax.SARIMAX,” statsmodels documentation. Accessed: Oct. 21, 2026. [Online]. Available: https://www.statsmodels.org/stable/generated/statsmodels.tsa.statespace.sarimax.SARIMAX.html

[7] Virginia Department of Transportation, “CrashData_Basic (ID: 0),” Full_Crash, ArcGIS REST Services Directory. Accessed: Oct. 21, 2026. [Online]. Available: https://services.arcgis.com/p5v98VHDX9Atv3l7/arcgis/rest/services/Full_Crash/FeatureServer/0

[8] R. J. Hyndman and G. Athanasopoulos, *Forecasting: Principles and Practice*, 3rd ed. Melbourne, Australia: OTexts, 2021. Accessed: Oct. 21, 2026. [Online]. Available: https://otexts.com/fpp3/

[9] The pandas development team, “pandas documentation.” Accessed: Oct. 21, 2026. [Online]. Available: https://pandas.pydata.org/docs/

[10] NumPy developers, “NumPy documentation.” Accessed: Oct. 21, 2026. [Online]. Available: https://numpy.org/doc/stable/

[11] Matplotlib developers, “Matplotlib documentation.” Accessed: Oct. 21, 2026. [Online]. Available: https://matplotlib.org/stable/

[12] Scikit-learn developers, “mean_absolute_error,” scikit-learn documentation. Accessed: Oct. 21, 2026. [Online]. Available: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.mean_absolute_error.html

[13] Scikit-learn developers, “root_mean_squared_error,” scikit-learn documentation. Accessed: Oct. 21, 2026. [Online]. Available: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.root_mean_squared_error.html

[14] K. Sheppard, “arch.bootstrap.MovingBlockBootstrap,” arch documentation. Accessed: Oct. 21, 2026. [Online]. Available: https://bashtage.github.io/arch/bootstrap/generated/arch.bootstrap.MovingBlockBootstrap.html


[1] Virginia Department of Transportation, “Full_Crash,” Virginia Roads, ArcGIS REST Services Directory. Accessed: Oct. 21, 2026. [Online]. Available: https://services.arcgis.com/p5v98VHDX9Atv3l7/arcgis/rest/services/Full_Crash/FeatureServer

[2] Open-Meteo, “Historical Weather API.” Accessed: Oct. 21, 2026. [Online]. Available: https://open-meteo.com/en/docs/historical-weather-api

[3] Scikit-learn developers, “PoissonRegressor,” scikit-learn documentation. Accessed: Oct. 21, 2026. [Online]. Available: https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.PoissonRegressor.html

[4] Open-Meteo, “Terms & Privacy.” Accessed: Oct. 21, 2026. [Online]. Available: https://open-meteo.com/en/terms

[5] Creative Commons, “Attribution 4.0 International (CC BY 4.0).” Accessed: Oct. 21, 2026. [Online]. Available: https://creativecommons.org/licenses/by/4.0/

[6] Statsmodels developers, “statsmodels.tsa.statespace.sarimax.SARIMAX,” statsmodels documentation. Accessed: Oct. 21, 2026. [Online]. Available: https://www.statsmodels.org/stable/generated/statsmodels.tsa.statespace.sarimax.SARIMAX.html

[7] Virginia Department of Transportation, “CrashData_Basic (ID: 0),” Full_Crash, ArcGIS REST Services Directory. Accessed: Oct. 21, 2026. [Online]. Available: https://services.arcgis.com/p5v98VHDX9Atv3l7/arcgis/rest/services/Full_Crash/FeatureServer/0

[8] R. J. Hyndman and G. Athanasopoulos, *Forecasting: Principles and Practice*, 3rd ed. Melbourne, Australia: OTexts, 2021. Accessed: Oct. 21, 2026. [Online]. Available: https://otexts.com/fpp3/

[9] The pandas development team, “pandas documentation.” Accessed: Oct. 21, 2026. [Online]. Available: https://pandas.pydata.org/docs/

[10] NumPy developers, “NumPy documentation.” Accessed: Oct. 21, 2026. [Online]. Available: https://numpy.org/doc/stable/

[11] Matplotlib developers, “Matplotlib documentation.” Accessed: Oct. 21, 2026. [Online]. Available: https://matplotlib.org/stable/

[12] Scikit-learn developers, “mean_absolute_error,” scikit-learn documentation. Accessed: Oct. 21, 2026. [Online]. Available: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.mean_absolute_error.html

[13] Scikit-learn developers, “root_mean_squared_error,” scikit-learn documentation. Accessed: Oct. 21, 2026. [Online]. Available: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.root_mean_squared_error.html

[14] K. Sheppard, “arch.bootstrap.MovingBlockBootstrap,” arch documentation. Accessed: Oct. 21, 2026. [Online]. Available: https://bashtage.github.io/arch/bootstrap/generated/arch.bootstrap.MovingBlockBootstrap.html

## Where each source applies

| Project component | References | Use |
| --- | --- | --- |
| Crash data | [1], [7] | Public source records, jurisdiction filter, field definitions, and coded-value labels. DMV maintains the underlying records; VDOT publishes the public service. |
| Weather data | [2] | ERA5 historical reanalysis, weather variables, units, grid resolution, and publication delay. |
| Data terms and attribution | [1], [4], [5] | VDOT source conditions and Open-Meteo/CC BY attribution requirements. |
| Initial modeling proposal | [3] | Poisson regression from the original plan; retain for project history or a benchmark if implemented. |
| Revised forecasting approach | [6], [8] | SARIMAX, temporal dependence, seasonal models, dynamic regression, and chronological forecast evaluation. Useful textbook sections include Chapters 5, 9, and 10. |
| EDA software | [9]–[11] | Tables and date handling, numerical operations, validation, and plotted figures in the existing notebook. |
| Planned forecast metrics | [12], [13] | MAE as the primary metric and RMSE as a secondary metric. |
| Planned uncertainty assessment | [14] | Consecutive-block resampling for dependent observations. This is an implementation reference, not evidence that seven-day blocks are optimal for this dataset. |

## Data attribution and provenance

**Crash records:** Virginia DMV TREDS records, published by the Virginia Department of Transportation through Virginia Roads [1], [7]. City records were selected using `PHYSICAL_JURIS = '104'`. The source's disclaimers and use conditions remain applicable; this reference list does not grant redistribution rights.

**Weather:** Historical weather data provided by Open-Meteo using ERA5 reanalysis [2]. The requested coordinates were 38.03° N, 78.48° W; the returned grid point was 38.00° N, 78.50° W. Under the project's documented use of CC BY 4.0 [4], [5], retain attribution and the license link and identify changes. Project changes include conversion to tables, date joins, aggregation, and derived lag features.

**Snapshot:** The project data were downloaded October 9, 2026. The access dates above identify when these reference pages were checked for this file; they do not indicate a new data download. Consult `provenance.json` and the original request files for retrieval timestamps and source hashes.

## Citation consistency

Use these references for the current project narrative. Standalone documents may renumber references in order of first appearance. Older dataset READMEs and CSV `source_ref` tags use their own numbering; interpret those tags using the corresponding original README rather than assuming that they match this file. Do not edit historical source-reference tags silently.

Software documentation links above describe the tools, not the exact package versions installed by the group. Record the versions actually used when running the final analysis. Cite only the methods and software used in each submitted report, and describe any change from the preregistered plan.
