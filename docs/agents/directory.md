# Agent card: directory

Status: implemented and tested within the limited scope below; source coverage partial

Inventory sources: S21 (partial), S22 (pending)

## Responsibility and input

Extract extension institution facts from ICAR-style HTML tables.

Four-column English directory HTML; serial/address/host/sanction-year. BeautifulSoup 4.14.3, no LLM.

## Extraction, normalization and provenance

Header routing; 1-based table/row locators and full row evidence. District is the explicit Distt. token; address/host text retained; sanction year integer. Crop/observation period not applicable.

Output: observation-v1 long-form records with source hash/type/agent/run UUID, locator, crop/location/period/variable/value/unit, validation status/errors and raw evidence. See db/dictionary.md and eval/README.md.

## Failure handling and decisions

Router errors yield failed status, no invented observations. Invalid rows remain for audit; partially supported PDFs and incomplete rows yield partial status. Storage is transactional; logs retain failures. All decisions are fixed code. No model inference, confidence estimate, autonomous reasoning or cooperative agent hand-off is claimed.

## Evidence

Real 54-row snapshot produces 162 observations. Ten source-derived row cases; unit tests cover count, source locators and independent expected district/year pairs.

Measured per-agent benchmark results are in eval/results.json and eval/phase2_metrics.csv; the high fragment F1 is not independent unseen-document performance. Reference source verification is by the implementing agent, not a calibrated human panel.

## Known limits

Historical typo/freshness unverified; no inferred LGD. S22 telephone PDF remains pending; no OCR/contact extraction claimed.
