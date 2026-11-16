# Image review policy and audit trail

## Purpose and reviewer

The modeling task is identification of a recognizable bird subject in a source photograph. On November 16, 2026, every image of the 482 source images was visually screened in class contact sheets, enlarged ambiguous examples, and recorded decisions in quality_review_analysis.csv. This is **not expert re-identification**, and species labels remain source community labels. 

## Selection rules

Retain a source-labeled bird photograph when a bird subject is recognizable. Keep challenging lighting, distant subjects, partial occlusion, juveniles/nestlings, flight, and multiple birds when a plausible labeled subject is visible. Do not remove an image merely because the species is difficult for a model, and do not crop subjects or change source pixels. Exclude images consisting only of eggs/nests without a bird, isolated feathers/remains, a text card, an identification-app screenshot, or visibly deceased specimens. No decisions used model predictions or accuracy. Review included the original assigned test photographs only for eligibility, not for performance tuning.

The retained held-bird photographs are not inferred to be healthy or alive solely from pose. The exclusion list records visibly deceased/specimen images and non-bird material; it does not diagnose condition. No taxonomic relabeling was performed. Expert / ornithologist inspection can improve this screening; any later edits create a new dataset version and require rerunning preparation and documenting the change before training.

## Decisions and duplicates

The original review log is retained as raw/quality_review_before_setup.csv. The new log adds reviewer and reviewed_on fields, uses review_status=assistant_visual_review, and contains one retain/exclude decision and rationale per source image. 15 images were excluded and 467 retained.

A 32×32 grayscale DCT fingerprint was computed for every source image. The top-left 8×8 coefficients were thresholded around their non-DC median, with the DC bit ignored. All pairs with Hamming distance at most eight were inspected. The six candidates were visually distinct sky/flight photographs, so none was excluded as a duplicate. Decisions are in near_duplicate_review.csv. This threshold can miss crops, edits, bursts, shared sites, or the same bird photographed by different observers. Original contact-sheet screening also considered obvious repeated frames; similar scenes with distinct poses were retained. No comprehensive site-level independence or perfect deduplication is claimed.

## Reproducibility

02_prepare_data.py applies recorded decisions, rechecks hashes, recomputes candidate pairs, verifies all classes and observer isolation, and writes the analysis manifest. It refuses unresolved reviews or unreviewed new candidate pairs. It never reassigns observers to improve class balance. Changing the inputs deliberately requires a new freeze and checks, not silent reuse of earlier results.
