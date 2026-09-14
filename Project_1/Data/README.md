# Raw Jeopardy Contestant-Clue Dataset

## Data Summary

`jeopardy_raw_contestant_clue_data.csv.gz` is the connected raw dataset for the Jeopardy winner-prediction project. It contains 1,095,594 rows representing 365,198 unique clue records, 18,924 contestant-game records, 11,883 contestants, and all 6,308 Cluebase games from September 27, 1984, through July 26, 2019. The unit of observation is a **contestant-clue pair**: each clue is repeated once for each of the three contestants in its game. Every game contains exactly three contestants and one recorded winner. The compressed file is approximately 28.4 MiB and expands to approximately 449.5 MiB. It can be read directly without manual extraction using `pandas.read_csv("jeopardy_raw_contestant_clue_data.csv.gz", compression="gzip")`; because the expanded data are large, `usecols=` or `chunksize=` should be used on computers with limited memory. The file currently lives in the group's shared project files; before MI2 submission, place it in the group's private course storage and add the private group/instructor access link here: **[Private dataset link - add URL]**.

## Provenance

The file combines the supplied Cluebase CSV archive with J. Wolle's `combined_season1-42.tsv` dataset. Cluebase contributes the game, season, contestant, final-score, winner, and J! Archive-link fields. The Wolle file contributes category text, displayed clue text, expected correct responses, clue values, Daily Double values, comments, notes, and Final Jeopardy records. The sources were connected by `air_date`, which is unique among the Cluebase games in this snapshot. Wolle supplied clue records for 6,293 games, while the Cluebase clue table supplied a fallback for 15 dates absent from Wolle. Thus, all 6,308 games have at least one clue record, although two games contain only a Final Jeopardy clue. The file contains 180,340 Jeopardy-round clues, 178,634 Double Jeopardy clues, and 6,224 Final Jeopardy clues before each clue is repeated for the three contestants. Source values were retained as closely as possible; processing primarily renamed fields, standardized round labels, added source identifiers, and performed the relational joins.

## License and Use Restrictions

No license permitting unrestricted redistribution was supplied with either attached dataset. The Wolle repository states that the Jeopardy data are the property of Jeopardy Productions, Inc. and asks users not to create public-facing websites, applications, or products from the data. Cluebase describes its software as open source, but its documentation states that its data were obtained from J! Archive. J! Archive's current terms prohibit automated collection and republication of data collected or derived from the site. This combined raw file should therefore be treated as restricted educational-research data, not as an openly licensed dataset. Store it privately and share it only with the project group and instructor as needed for DS 4002. Do not publish the raw file, republish the clue text or personal records, monetize it, or use it in a public-facing product without permission from the relevant rights holders. Original code, field definitions, processing instructions, and aggregate findings that do not reproduce the underlying records may be shared. This is a conservative use statement rather than legal advice.

Relevant sources and terms:

- Clue dataset: https://github.com/jwolle1/jeopardy_clue_dataset
- Cluebase documentation: https://cluebase.readthedocs.io/en/latest/
- Cluebase repository: https://github.com/lukelavin/Cluebase
- J! Archive terms: https://www.j-archive.com/help.php

## File Structure

Each game-clue combination appears three times, once for each contestant. Game-level fields therefore repeat across all rows in a game, contestant-level fields repeat across all clues associated with that contestant's game, and clue-level fields repeat across the three contestants. Use `game_id` to identify games, `contestant_id` to identify people, and `clue_source_record_id` to identify clues. The combination of `game_id`, `contestant_id`, and `clue_source_record_id` uniquely describes the intended row. For game-level summaries, remove duplicated `game_id` values. For clue-level summaries, remove duplicated `clue_source_record_id` values. For contestant-game modeling, first aggregate clues within each `game_id` and then retain one row per `game_id` and `contestant_id`.

## Data Dictionary

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

## Predictor Leakage Guidance

The raw file intentionally retains both inputs and outcomes so that the analysis remains reproducible. For the planned semantic winner model, the safe starting text variables are `contestant_intro`, `category`, and `clue_text`, after extracting occupation text from the introduction. Useful structural fields may include `round` and `clue_value`. The target is `is_winner`. At minimum, exclude `score1`, `score2`, `score3`, `winner_id`, `contestant_final_score`, `contestant_games_played`, `contestant_total_winnings`, `daily_double_value`, and all contestant response or wagering information from predictors. Names, IDs, URLs, correct responses, notes, and source indicators should also be excluded from semantic features unless a clearly justified audit or sensitivity analysis requires them. Fit all text transformations only on the training data and keep all rows from the same game together during validation.

## Known Limitations and Uncertainty

Clue coverage varies substantially. Games contain between 1 and 61 unique clue records; two games contain only their Final Jeopardy clue, and many historical games have fewer than a full board. The file contains 6,224 Final Jeopardy clues for 6,308 games, so Final Jeopardy is missing for some games. Two clue records lack a correct response. Cluebase fallback games lack several Wolle-only fields and may have unreliable Daily Double flags. Source text may include transcription errors, messy formatting, or incomplete representations of image, audio, and video clues. Contestant introductions are not standardized occupation labels. The data also do **not** identify which contestant attempted or answered each individual clue, so contestant-level clue accuracy and exact Coryat scores cannot be reconstructed from this file. Those analyses would require a separate response-level or scoring dataset. These limitations should be reported and addressed through completeness thresholds, source indicators, mapping-confidence fields, and sensitivity analyses.

## Ethical Statement

Contestant names, introductions, occupations, scores, and results were publicly displayed, but contestants did not provide them specifically for this research. Keep the row-level file private, minimize unnecessary display of names and hometowns, and present aggregate findings whenever possible. Occupation text is an incomplete proxy for knowledge and may reproduce occupational, educational, geographic, demographic, and linguistic stereotypes. Do not interpret semantic alignment as intelligence, individual ability, or a causal effect of a job or degree. Document ambiguous occupation mappings and their uncertainty rather than forcing a match. If UVA-major profiles are explored, describe the results only as similarity between program text and clue content, not as predicted performance of actual UVA students or graduates.

## Reproducibility Checks

- Compressed file: `jeopardy_raw_contestant_clue_data.csv.gz`
- Rows: 1,095,594
- Unique games: 6,308
- Unique contestant-game records: 18,924
- Unique contestants: 11,883
- Unique clue records: 365,198
- Games using Wolle clues: 6,293
- Games using Cluebase fallback clues: 15
- SHA-256: `0641b261635230da5745f046ac323ff9793fa614c953574d92ddfae8a2bef382`
