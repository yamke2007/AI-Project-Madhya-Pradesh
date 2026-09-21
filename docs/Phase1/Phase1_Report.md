# Phase 1 Report – Madhya Pradesh

## 1. Purpose

The proposed Madhya Pradesh agriculture information system will organize heterogeneous agriculture information into a queryable knowledge base. The system should allow an agent to retrieve information while retaining source and temporal provenance.

## 2. Problem Framework

Agriculture information for a state is distributed across government portals, market systems, PDFs, dashboards, statistical reports and agricultural extension sources. These sources differ in format, language, update frequency and geographic granularity.

The project therefore focuses on building a pipeline that can:

1. discover relevant sources;
2. retrieve or read source material;
3. extract structured information;
4. validate extracted information;
5. store structured records;
6. answer user queries with provenance.

## 3. Proposed Information Scope

### Crop and production
- crop
- season
- district
- cultivated area
- production
- yield

### Market and prices
- crop/commodity
- mandi/APMC
- date
- arrivals
- minimum price
- maximum price
- modal/representative price where available

### Procurement
- crop
- procurement season
- procurement quantity
- MSP-related information
- procurement centre information where available

### Inputs
- fertilizer
- recommended quantity
- crop
- nutrient
- fertilizer distribution information
- seed/pesticide/fertilizer testing or licensing information

### Schemes
- scheme name
- department
- eligibility
- application process
- benefit/assistance
- official source

### Insurance
- crop
- season
- state/district
- insured area/farmers where available
- premium/claims/benefit statistics where available

### Weather and advisories
- date
- district
- crop/livestock
- weather/agrometeorological advisory

### Agricultural extension
- KVK
- district
- host organization
- agricultural extension/advisory information

## 4. Initial Source Strategy

Priority should be given to official government sources, official statistical systems, official agricultural research/extension institutions and official scheme portals.

Third-party sources should not be treated as authoritative unless there is a clear reason and their provenance is documented.

## 5. Initial Architecture

```text
Official Sources
      |
      v
Source Discovery / Registry
      |
      v
Retrieval Tools
(Web / PDF / Excel / OCR)
      |
      v
Extraction Agent
      |
      v
Validation / Human Review
      |
      v
Structured Knowledge Base
      |
      v
Query Agent
      |
      v
Answer + Provenance
```

## 6. Phase 1 Acceptance Checklist

- [x] State selected: Madhya Pradesh
- [x] Initial source inventory prepared
- [x] Source modalities recorded
- [x] Source limitations recorded
- [x] Extractable information recorded
- [x] Initial schema drafted
- [x] Initial agent/tool plan drafted
- [ ] Team members and roles filled in
- [ ] Every source manually re-checked immediately before submission
- [ ] GitHub contribution history established
