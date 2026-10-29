# Agent card: statistics

Status: implemented and tested within the limited scope below; source coverage partial

Inventory sources: S11 (pending), S12 (pending), S13 (pending), S23 (partial)

## Responsibility and input

Import explicitly structured numeric observations and conservatively extract supported production sentences.

CSV required six headers plus optional metadata; text-layer PDF with one explicit English production grammar. Python csv / pypdf 6.12.1; no LLM.

## Extraction, normalization and provenance

Preserve value string, declared unit/qualifier and origin metadata; normalize crop/location/period; physical CSV line or PDF page/character locator and evidence. Lower bounds/targets remain distinct variables.

Output: observation-v1 long-form records with source hash/type/agent/run UUID, locator, crop/location/period/variable/value/unit, validation status/errors and raw evidence. See db/dictionary.md and eval/README.md.

## Failure handling and decisions

Router errors yield failed status, no invented observations. Invalid rows remain for audit; partially supported PDFs and incomplete rows yield partial status. Storage is transactional; logs retain failures. All decisions are fixed code. For PDFs the supervisor runs this agent first and then the tables agent; when the sentence grammar finds nothing, that is recorded as a hand-off to the tables agent rather than a run failure.

## Evidence

Ten PDF-source-checked manual-transcription CSV cases, unit/period/context/1% matching tests, real PDF wheat sentence and dump restore tested. PDF yields one wheat fact; not a general PDF table extractor.

Measured per-agent benchmark results are in eval/results.json and eval/phase2_metrics.csv; the high fragment F1 is not independent unseen-document performance. Reference source verification is by the implementing agent, not a calibrated human panel.

## Known limits

S23 partial. S11/S12 interactive queries and S13 annual tables pending. CSV evaluation measures importer, not automatic transcription. Manual source context carries rice periods; PDF parser does not infer them. No trusted LGD registry.
