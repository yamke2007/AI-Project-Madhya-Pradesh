# Implemented SQLite dictionary and rules

`schema.sql` is authoritative; `agriagent.sqlite` is the runnable populated database, `dump/agriagent.sql` the portable SQL dump and `dump/observations.json` the portable observations. Run `python scripts/db_cli.py --dump` to refresh; `python scripts/db_cli.py --id 1` traces a row to its source URL/hash/path and local locator. Within a packaged project, paths in newer runs are repository-relative; older history can retain original acquisition-machine paths. Resolve a file by its SHA-256 in `data/manifest.csv` if a historical path differs.

| Table / key | Fields and meaning |
|---|---|
| sources / source | Content-addressed `sha256:<digest>` source primary key; URL (unknown if absent), SHA-256, original input path. Distinct snapshots receive distinct source IDs. Inventory IDs S01–S23 are metadata, not hashes. |
| runs / run_id | UUID, source FK, UTC started_at, complete/partial/failed, specialist name and JSON error list. |
| observations / id | Source FK, source_type (Document/Database), agent, run FK, locator, crop, location, period, variable, value string, unit, validation_status, complete JSON payload with evidence, qualifiers and validation_errors. |
| attempts / run_id | Run FK, attempted observation count, inserted count, duplicate rejections. Retains repeated-ingestion evidence even when rows are rejected. |

One row is one observation (long form), so a KVK institution creates address, host_organization and sanction_year rows. Its locator resolves a 1-based HTML table/row; CSV locators use the physical ending line of the parsed CSV record; PDF locators use 1-based physical PDF page and character span in whitespace-normalized pypdf text. PDF printed page labels can differ (survey PDF page 7 is printed page 3). Directory sanction year is a value, not the observation period; no current-directory timestamp is invented. Scheme rows do not assume a crop, geographic applicability, or effective date from nearby prose.

Mandatory provenance fields use `MISSING:not_in_source` and `MISSING:not_applicable` when unknown or inapplicable. Empty observation values get a missing code and invalid validation status. No substitution with zero. Value strings preserve source precision; Decimal controls evaluation, not binary floating-point.

Natural key: `(source, locator, crop, location, period, variable)`, enforced UNIQUE. Foreign keys are enabled on every connection. Invalid rows remain available with validation errors for audit. Repeated ingestion rechecks validation under current rules, updates validation status/errors and records validation_rechecked_run_id while preserving the original insertion run and value; historical run outcomes remain in runs/logs. A run is partial if any row invalid or a parser explicitly reports incomplete coverage. SQL transactions roll back on storage errors and the automation log records failed status. Extraction failure runs with a known source hash are stored with no observations; missing-file attempts remain in CSV logs.

Declared validation: nonempty mandatory fields, allowed units, parsable ISO dates/year/financial-year strings, finite ordinary numbers from 0 to 1e14, integer integrality, percentage shares at most 100, supplied LGD code checked against a supplied code/name registry. Percentage variables ending `_growth` permit values above 100 and decreases down to -100; the survey's 585% growth is not a share. No official registry was available: no inferred or invented codes are stored. General crop-specific plausibility bounds and authoritative district-name validation are partial. Historical source misspellings are retained.

Recompute M14 with count of nonempty mandatory fields / observations, M15 with validation_status='valid' / observations, M16 with sum of COUNT(*) of groups HAVING COUNT(*)>1 / observations. Duplicate attempts are a separate operational rate, not M16. Example SQL:

```sql
SELECT count(*) FROM observations;
SELECT validation_status,count(*) FROM observations GROUP BY validation_status;
SELECT source,locator,crop,location,period,variable,count(*) FROM observations
GROUP BY source,locator,crop,location,period,variable HAVING count(*)>1;
SELECT sum(attempted),sum(inserted),sum(duplicates) FROM attempts;
```

The Database source group is the manually transcribed CSV import, not a verified direct DES portal export. It and the Document group populate the database, but the two-group bonus and live M17 cannot be claimed before instructor verification.
