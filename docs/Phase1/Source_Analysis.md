# Source Analysis

## Source selection principles

Sources were prioritized using the following criteria:

1. Official government or public-sector ownership.
2. Direct relevance to agriculture in Madhya Pradesh.
3. Useful geographic granularity such as state, district, mandi or KVK.
4. Useful temporal information such as date, season or year.
5. Potential for structured extraction.
6. Clear limitations that can be documented.

## Main source families

### A. MP government agriculture systems
These are useful for state-specific agriculture services, fertilizer distribution, agricultural machinery and related farmer services.

### B. Market and procurement systems
e-Anugya/e-Mandi and e-NAM-related sources are relevant to mandi, trading and market information. Procurement portals are relevant to government procurement and MSP-linked processes.

### C. Statistics
The Directorate of Economics and Statistics agriculture systems provide area, production and yield query interfaces and agriculture-statistics reports.

### D. Weather
The India Meteorological Department agricultural meteorology portal provides crop-specific advisories that can be filtered by state and district.

### E. Insurance and schemes
PMFBY and MP government scheme pages provide scheme and insurance information.

### F. Extension and research
ICAR's Madhya Pradesh KVK directory provides district-level agricultural extension institution information.

## Important limitations

- Many government portals are dynamic and may not expose all information as static HTML.
- Some pages require form selections before results are produced.
- PDFs can have tables, scanned pages or inconsistent layouts.
- Hindi content may require language-aware extraction/OCR.
- Data update frequency differs by source.
- A portal may expose information through an application interface without offering a stable downloadable dataset.
- Historical pages may remain online even after the underlying system changes.

## Recommended handling

Record:
- source URL;
- source title;
- source owner;
- modality;
- language;
- collection date;
- geographic coverage;
- time coverage;
- extraction method;
- limitations;
- license/terms where available.

Do not assume that a dynamic page can be scraped indefinitely. Before automated collection, check the site's terms, robots.txt, rate limits and any available official API/bulk-download mechanism.
