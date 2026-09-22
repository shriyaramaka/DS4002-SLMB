# Jeopardy! winner prediction: Project 1 data

## Data summary and access

The files below are the ones currently shown in `Project_1/Data`. The connected raw file contains 6,308 games, 18,924 contestant-game records, and 365,198 distinct clues (1,095,594 contestant-clue rows). The processed contestant file contains the **3,882 primary games** that have at least 50 recorded clues and a stated occupation for all three contestants. It has 11,646 contestant-game rows. The raw file is needed to obtain the 225,388 distinct clues in those games; there is currently **no separate final clue file in this folder**.

For the winner model, compare each contestant's `occupation_text_for_model` with the category and clue text from the raw file, joined by `game_id`. SOC and CIP are optional exploratory annotations, not required to predict the winner.

## Files in `Project_1/Data`

| File | Contents |
| --- | --- |
| `jeopardy_raw_contestant_clue_data.csv.gz` | Connected raw contestant-clue data, including recorded clues, answer keys, scores, and winners. One clue appears once for each contestant in its game. |
| `final_contestant_games.csv` | One row per contestant-game in the primary sample; cleaned occupation phrase, winner label, uncertainty, and optional SOC/CIP fields. |
| `soc_cip_links.csv` | Official SOC-to-CIP pairs for occupations appearing in the processed data, including CIP program names. Optional for the main model. |
| `Cluebase_Data_Download.ipynb` | Earlier data-acquisition notebook. It documents the acquisition attempt and is not needed to read the files above. |
| `Initial_EDA.ipynb` | Earlier exploration of the raw connected data. |
| `Final_EDA.ipynb` | Later exploration of the raw connected data and the pre-processed data. |
| `README.md` | This description of the data, fields, processing, and limitations. |

The raw `.csv.gz` file can be opened directly with `pd.read_csv('jeopardy_raw_contestant_clue_data.csv.gz', compression='gzip')`. Read it in chunks or request specific columns if memory is limited. The two notebooks could eventually move to a `SCRIPTS` folder, but they are listed here because that is where they currently appear and are relevant to data.

## Provenance and construction

Cluebase supplies games, contestants, introductions, scores, and winners [1]. J. Wolle's Jeopardy! clue data supplies categories, clue prompts, answers, values, and rounds for 6,293 games; Cluebase supplies clues for 15 other games [2]. The sources were joined by air date for the raw file. The occupation phrase comes from the contestant introduction after removing locations and certain surrounding text. A proposed O*NET-SOC occupation and uncertainty tier were assigned using exact titles, selected synonyms, broad-role rules, or approximate title matching [3]. The **2020 Classification of Instructional Programs (CIP)–2018 Standard Occupational Classification (SOC) crosswalk** was joined on the seven-character SOC code [4]. Its `99.9999 / NO MATCH` marker was treated as no CIP link. CIP is a possible program connected with a job, **not evidence of the contestant's education or UVA major**. The crosswalk is many-to-many: the file retains all program links rather than selecting a degree for each person.

The MI2 preprocessing rule removes 94 games with fewer than 50 distinct clues, leaving 6,214. Of those, 2,332 games have at least one introduction without an identifiable occupation and are excluded **as entire games** to preserve three contestants and one winner per game. This leaves 3,882 primary games. Students without a stated occupation, age-only introductions, and homemaker descriptions were not assigned a job. The final contestant file omits answer text, scores, current-game wagers, postgame notes, and snapshot total winnings, while keeping `is_winner` as the supervised target. When preparing clues from the raw file for analysis, deduplicate each clue across the three contestants and clean HTML tags/entities and extra spaces from category and clue text. The raw file stores original clue values, including the source's zero marker for Final Jeopardy, which has no fixed face value. If a later script constructs relative clue values, treat Final Jeopardy separately. Text embeddings and model parameters must be fitted using training games only.

## Source terms and ethics

Neither the Cluebase-derived records nor Wolle's clue data came with permission to republish the connected row-level dataset publicly; Wolle identifies Jeopardy! rights held by Jeopardy Productions [1], [2]. Keep the raw and final contestant/clue files within the group's approved restricted access. The NCES crosswalk is distributed on the official CIP resource site [4]. O*NET 31.0 occupation data are distributed under Creative Commons Attribution 4.0; the attribution and license are at [3], [5]. The team added parsing and uncertain links; O*NET has not checked or endorsed those links. Public documentation and aggregate plots should avoid reproducing substantial clue text or unnecessary contestant identities.

The occupations and winner records were publicly broadcast but contestants did not give them for this analysis. Occupation text is a rough proxy for subject knowledge, and mappings may vary with job wording and historical period. Do not interpret a similarity score or CIP link as intelligence, actual education, causal career effects, or expected success of UVA students. Summarize findings at the group level.

## Data dictionary: raw connected file

The following fields belong to the **raw** contestant-clue file. Game fields repeat for each clue and contestant; contestant fields repeat for the clues in that game; each clue repeats for three contestants.

### Game-Level Fields

| Feature | Type | Description and uncertainty |
|---|---|---|
| `game_id` | Integer | Cluebase's internal game identifier. Use for grouping and joins, not as a numeric predictor. IDs may not remain stable across different source snapshots. |
| `episode_num` | Integer | Broadcast episode number reported by Cluebase. It is an identifier and should not ordinarily be modeled as a continuous quantity. |
| `season_id` | Integer | Cluebase's internal season identifier. It is not the broadcast season number; use `season_name` for interpretation. |
| `season_name` | String | Human-readable season label. The data include Season 1 through Season 35 and Super Jeopardy!, with incomplete coverage in several early seasons. |
| `season_start_date` | Date | Start date stored in the Cluebase season table. It describes the source's season boundaries and may not account for every special broadcast. |
| `season_end_date` | Date | End date stored in the Cluebase season table. It describes the source's season boundaries and may not account for every special broadcast. |
| `season_total_games` | Integer | Total-game value stored in the Cluebase season table. This describes the archived source snapshot and should not be assumed to measure complete historical coverage. |
| `air_date` | Date (`YYYY-MM-DD`) | Broadcast date reported by Cluebase and used to connect the two sources. It is unique among Cluebase games in this snapshot, but a source transcription error could cause an incorrect match. |
| `game_notes` | String or blank | Cluebase notes about tournaments, returning contestants, missing material, or unusual formats. This is an audit field and may contain postgame information or contestant identities, so it should not be used directly as a predictor. |
| `j_archive_game_url` | String | Source URL stored by Cluebase for manual provenance checks. It should not be used as a predictor or automatically scraped. |
| `contestant1_id` | Integer | Cluebase ID of the contestant listed in game position 1. |
| `contestant2_id` | Integer | Cluebase ID of the contestant listed in game position 2. |
| `contestant3_id` | Integer | Cluebase ID of the contestant listed in game position 3. |
| `score1` | Integer, dollars | Final score of the contestant in position 1. This is a postgame outcome and would cause target leakage if used to predict the winner. |
| `score2` | Integer, dollars | Final score of the contestant in position 2. This is a postgame outcome and would cause target leakage if used to predict the winner. |
| `score3` | Integer, dollars | Final score of the contestant in position 3. This is a postgame outcome and would cause target leakage if used to predict the winner. |
| `winner_id` | Integer | Cluebase ID of the recorded winner. This is an outcome field and must not be used as a predictor. |

### Contestant-Level Fields

| Feature | Type | Description and uncertainty |
|---|---|---|
| `contestant_position` | Integer (`1`, `2`, or `3`) | Contestant slot in the Cluebase game record. The ordering may follow archival conventions and should not be treated as meaningful without investigation. |
| `contestant_id` | Integer | Cluebase's internal contestant identifier. Use to recognize repeated contestants and manage train-test leakage; do not use the numeric value as a predictor. |
| `contestant_name` | String | Publicly displayed contestant name. Retained for auditing and occupation mapping, but not appropriate as a model predictor. Spellings may contain source errors. |
| `contestant_intro` | String | Introduction text, usually including an occupation and hometown. Occupation phrases have not yet been separated from location or other descriptors. Wording is inconsistent, and ambiguous roles require mapping uncertainty. |
| `contestant_games_played` | Integer | Number of games attributed to the contestant in the Cluebase snapshot. This may include games occurring after the row's game and therefore poses serious temporal and outcome leakage. Do not use it without reconstructing a pregame value. |
| `contestant_total_winnings` | Integer, dollars | Total winnings attributed to the contestant in the Cluebase snapshot. This is a cumulative postgame field and must not be used as a predictor in its current form. |
| `contestant_final_score` | Integer, dollars | This contestant's final score in the current game. It is an outcome and must not be used to predict the winner. |
| `is_winner` | Binary integer (`0` or `1`) | Target indicating whether the contestant won the game. Exactly one contestant per game has value `1`. It is the supervised outcome, never a predictor. |

### Clue-Level Fields

| Feature | Type | Description and uncertainty |
|---|---|---|
| `clue_available` | Binary integer | Equals `1` when a clue record is present. All current rows have a clue because the two sources together supply at least one clue for every game; the field permits future explicit missing-clue rows. |
| `clue_source` | Category | `wolle_season1_42` for games matched to the Wolle TSV or `cluebase_fallback` for games absent from that source. Source differences should be checked in sensitivity analysis. |
| `clue_source_record_id` | String | Constructed unique clue identifier using the source and source-row ID, such as `wolle:123` or `cluebase:456`. It identifies a clue across its three contestant copies. |
| `clue_number_in_game` | Integer | Sequential order of the clue record within the selected source for a game. It preserves source order but is not guaranteed to equal the clue's actual selection order during gameplay. |
| `round` | Category | Standardized round label: `J!`, `DJ!`, or `FJ!`. Cluebase fallback games do not contain Final Jeopardy records. |
| `source_round` | String or integer-like string | Original round value from the selected source before standardization. Wolle uses `1`, `2`, and `3`; Cluebase uses text labels. |
| `clue_value` | Integer, dollars, or blank | Face value shown on the board before wagering. Final Jeopardy normally has no fixed clue value. Values differ across historical eras and special formats. |
| `daily_double_flag` | Binary integer | Indicates whether the Wolle source reports a positive Daily Double wager or the Cluebase source marks the clue as a Daily Double. Cluebase documentation warns that its Daily Double flag was not reliably scraped, so fallback values are uncertain. Daily Double location is revealed during play and should not be treated as pregame information. |
| `daily_double_value` | Integer, dollars, or blank | Wager amount for a Daily Double when supplied by Wolle. This is gameplay information and would cause leakage in a pregame or board-only prediction. It is blank for Cluebase fallback clues. |
| `category` | String | Category heading associated with the clue. Category wording may include punctuation, wordplay, or source transcription errors. |
| `category_comments` | String or blank | Host or source comments associated with a category in the Wolle data. It is blank for Cluebase fallback clues and may contain information not visible on the board. Audit before any model use. |
| `clue_text` | String | Displayed clue prompt. No clue-text values are missing in the connected file. Multimedia-dependent clues may still be incomplete or difficult to interpret from text alone. |
| `correct_response` | String or blank | Expected correct response. Two unique clue records have missing responses. Because contestants do not see the answer key when selecting a clue, this field should be excluded from a board-only winner-prediction model even though it can support descriptive content analysis. |
| `clue_notes` | String or blank | Miscellaneous clue notes from Wolle, including special-format information. Blank for Cluebase fallback clues. Notes may contain information unavailable before or during ordinary play and require auditing before use. |

## Data dictionary: final contestant and SOC–CIP files

`final_contestant_games.csv` has one row per (`game_id`, `contestant_id`). `is_winner` is the target; never use it as a predictor. Join this file to distinct raw clues on `game_id` when constructing board similarity. Names, identifiers, dates, and mappings are for tracing or separate checks, not the main occupation-text feature set.

| Final contestant field | Meaning and uncertainty |
| --- | --- |
| `game_id`, `contestant_id` | Keys for the game and person; a contestant may appear in multiple games. Do not use numeric IDs as model features. |
| `contestant_name`, `contestant_intro` | Public source text retained for tracing occupation extraction; introductions can contain hometowns and non-job material. |
| `occupation_phrase`, `occupation_text_for_model` | Extracted job phrase and cleaned primary text feature. The extraction can be incomplete or contain a misleading title. |
| `is_winner` | Target label, 1 for the single recorded winner per game. **Never include as an input.** |
| `contestant_position` | Source lineup slot, 1 to 3; possible structural baseline input, subject to archival-order effects. |
| `air_date`, `season_name`, `episode_num` | Broadcast date and audit labels; use for checks or group/time splitting, not as outcome proxies. |
| `clue_count`, `category_count` | Recorded clue and distinct category counts for each game; coverage can still be incomplete. |
| `j_clue_count`, `dj_clue_count`, `fj_clue_count` | Recorded clue counts for Jeopardy!, Double Jeopardy!, and Final Jeopardy. Some games lack FJ records. |
| `proposed_onet_soc_code`, `proposed_soc_code` | Optional proposed O*NET code and seven-character 2018 SOC portion; uncertain for broad or approximate matches. |
| `proposed_soc_title`, `proposed_soc_url` | Proposed occupation name and O*NET page, not a validated job classification. |
| `soc_uncertainty_level`, `soc_mapping_method` | Tier and method used to select the proposed occupation; details below. |
| `optional_soc_profile_text` | Job phrase plus proposed SOC description; **not** the default model input because weak SOC guesses can add wrong information. |
| `cip_candidate_count`, `candidate_cip_codes` | Number and `|`-separated list of official 2020 CIP program codes for the proposed SOC; an empty list indicates no crosswalk match. |
| `cip_mapping_status` | `one_crosswalk_program`, `multiple_possible_programs`, or `no_crosswalk_program`. A unique crosswalk edge still does not establish an actual degree. |
| `clue_source_set` | Wolle or Cluebase source(s) represented in the board, for sensitivity checks only. |

The raw file's clue-level fields are defined above. For the winner analysis, use each unique (`game_id`, `clue_source_record_id`) once, taking its `category`, `clue_text`, `round`, and `clue_value` from the raw file. Do not use its `correct_response`, scores, or wagers as predictors.

`soc_cip_links.csv` has `soc_code`, `official_soc_title`, `cip_code`, and `cip_title`, as printed in the official crosswalk. Joining it directly to contestants would multiply rows; aggregate CIP results by SOC or contestant and keep the original one-row-per-contestant unit for winner modeling.

### Mapping uncertainty

| Tier | Interpretation |
| --- | --- |
| `high_exact_title` | Unique match to the O*NET title or a singular form. |
| `medium_curated_match` | Selected equivalent job name or clear occupational rule. |
| `low_contextual_role` | Job named in a longer introduction; specialty or seniority may differ. |
| `low_broad_role` | Only a general family such as “teacher” is stated. |
| `low_multiple_roles` | Introduction describes more than one possible role; one representative code is recorded. |
| `very_low_approximate` | Closest title by letter pattern; may refer to another occupation. |
| `very_low_weak_guess` | Especially weak title suggestion; unsuitable as a confirmed SOC assignment. |
| `very_low_multiple_roles` | More than one role plus only a weak title suggestion. |

There are 3,786 high or medium contestant-game mappings among the 11,646 primary rows; **7,860** are lower confidence. Only 140 games have three high/medium SOC matches. For the preregistered primary analysis, compare the original occupation phrase with the board for all 3,882 games; a SOC-description or CIP analysis must be labeled exploratory or evaluated separately.

## Exploratory analysis and reproducing MI3 inputs

`Initial_EDA.ipynb` explores the raw connected file. Its plots and summary tables should be saved to the repository's `OUTPUT` folder when run. There are no figure files in the `Data` folder shown above; the MI3 rubric calls for at least two explanatory plots in the data metadata.

To prepare model inputs using the files currently in this folder:

1. Load `final_contestant_games.csv` and `jeopardy_raw_contestant_clue_data.csv.gz` in Python. Filter the raw rows to `game_id` values in the final contestant file, then keep one copy per (`game_id`, `clue_source_record_id`). This produces **225,388 distinct clues** for the primary sample.
2. Use `occupation_text_for_model` as the contestant text and the raw `category` and `clue_text` as the board text. Clean HTML and whitespace before comparisons. Treat Final Jeopardy and any within-round clue-value weighting separately from ordinary clue values.
3. Make one fixed **80% train / 20% test split by whole game**, as planned in MI2. Use exactly the same games for the baseline and enhanced models. Fit text transformations and tune models using training games only. Do not use `is_winner`, scores, answer keys, wagers, names, or postgame fields as predictors.
4. Compute one win probability per contestant that sums to one per game. Compare held-out game-level log loss with the recorded winner, the matched non-text baseline, and uniform one-in-three probabilities. Save the final scripts, figures, predictions, and summary tables in the MI3 repository.

For CIP names, join `final_contestant_games.csv` on `proposed_soc_code` = `soc_cip_links.csv`'s `soc_code`. Because one occupation can link to many programs, this join will repeat contestants; do **not** use that expanded table directly as one-row-per-player model data. The `candidate_cip_codes` field already lists the available codes without expanding the rows. Uncertain SOC/CIP links are not evidence of a person's actual major.

## References

[1] L. Lavin, “Cluebase documentation.” [Online]. Available: https://cluebase.readthedocs.io/en/latest/

[2] J. Wolle, “Jeopardy clue dataset,” GitHub repository. [Online]. Available: https://github.com/jwolle1/jeopardy_clue_dataset

[3] National Center for O*NET Development, “O*NET 31.0 occupation data.” [Online]. Available: https://www.onetcenter.org/dl_files/database/db_31_0_json/occupation_data.json

[4] National Center for Education Statistics, “2020 CIP/SOC crosswalk.” [Online]. Available: https://nces.ed.gov/ipeds/cipcode/Files/CIP2020_SOC2018_Crosswalk.xlsx

[5] National Center for O*NET Development, “O*NET database license.” [Online]. Available: https://www.onetcenter.org/license_db.html
