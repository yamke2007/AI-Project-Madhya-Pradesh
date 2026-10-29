# Agent card: scheme

Status: implemented and tested within the limited scope below; source coverage partial

Inventory sources: S06 (partial), S14 (pending), S16 (pending), S20 (pending)

## Responsibility and input

Extract descriptive scheme fields without interpreting legal benefits or substituting procurement statistics.

Hindi UTF-8 HTML with scheme/department context and two-cell rows. BeautifulSoup 4.14.3, no LLM.

## Extraction, normalization and provenance

Original Hindi label becomes variable; original value retained with row evidence. Crop not applicable; geographic/effective period unknown explicitly coded. Empty values invalid; no inferred amount/zero.

Output: observation-v1 long-form records with source hash/type/agent/run UUID, locator, crop/location/period/variable/value/unit, validation status/errors and raw evidence. See db/dictionary.md and eval/README.md.

## Failure handling and decisions

Router errors yield failed status, no invented observations. Invalid rows remain for audit; partially supported PDFs and incomplete rows yield partial status. Storage is transactional; logs retain failures. All decisions are fixed code. No model inference, confidence estimate, autonomous reasoning or cooperative agent hand-off is claimed.

## Evidence

Real MSP scheme snapshot produces 23 rows, partial because cells are blank. Ten independently source-checked Hindi fragment cases; missing values and incomplete run tested.

Measured per-agent benchmark results are in eval/results.json and eval/phase2_metrics.csv; the high fragment F1 is not independent unseen-document performance. Reference source verification is by the implementing agent, not a calibrated human panel.

## Known limits

Only S06 operational as partial. PMFBY/PM-KISAN/legal pages lack tested source-specific parsers. No general policy reasoning or crop-level entitlement validation.
