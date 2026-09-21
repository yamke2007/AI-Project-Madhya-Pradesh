# Intelligent Agriculture Information System: Madhya Pradesh

## Course

**CS F/U 407 – Artificial Intelligence**

## Project

**Intelligent Agriculture Information System: State-Level**

**Selected State:** Madhya Pradesh

**Current Phase:** Phase 1 – Source Discovery and Problem Framework

## Team

| Member | Role |
|---|---|
| Aryan Mishra | Source Lead + Data Engineering Lead |
| Unnati Goyal | Model Lead |
| Yamke Sai Krishna Reddy | Evaluation Lead |

## Project Overview

This project aims to build an intelligent agriculture information system for Madhya Pradesh.

The system will collect and organize agriculture-related information from reliable sources and make it easier to query and connect information across **location, time, source, and agricultural activity**.

The project focuses on government and institutional sources covering areas such as agricultural production, procurement, markets, prices, weather advisories, schemes, insurance, agricultural engineering, and related statistics.

## Problem Statement

Agriculture information for Madhya Pradesh is distributed across multiple government websites, portals, reports, PDFs, spreadsheets, and other sources.

These sources can differ in:

- Format and structure
- Language
- Availability and accessibility
- Time period covered
- Geographic coverage
- Data quality
- Documentation and metadata

The goal is to build a system that can discover these sources, extract useful structured information, store it in a queryable database, and support questions involving agricultural information across **place, time, and source provenance**.

## Phase 1 Objectives

1. Identify reliable agriculture-related sources for Madhya Pradesh.
2. Record source URLs and source metadata.
3. Identify the modalities available in each source.
4. Document limitations and accessibility issues.
5. Determine what useful information can be extracted from each source.
6. Map source information to the planned knowledge-base/database schema.
7. Define the initial agent and tool architecture.
8. Maintain source verification and project documentation.

## Source Categories

The current source discovery covers:

- Agricultural production and statistics
- Agricultural prices and markets
- Procurement and MSP-related information
- Agricultural schemes
- Crop insurance
- Weather and crop advisories
- Agricultural engineering
- Agricultural extension and KVK information
- Economic and agricultural reports
- National agricultural platforms relevant to Madhya Pradesh

The source inventory is maintained separately in the `Source_Inventory` directory.

## Data Modalities

The identified sources may contain:

- HTML/web pages
- PDF documents
- Tables
- Excel/spreadsheet data
- Statistical reports
- Maps or location-based information
- Hindi and English content

Different extraction methods may therefore be required depending on the source.

## Source Limitations

Potential challenges identified during source discovery include:

- Government websites with inconsistent layouts
- PDF documents with different table structures
- Scanned documents requiring OCR
- Hindi/Devanagari text requiring language-aware processing
- Dynamic websites requiring browser-based extraction
- Inconsistent metadata and reporting periods
- Different geographic levels of information
- Changes in website structure over time

## Knowledge Base and Database Plan

The system will organize extracted information using relationships involving:

- Location
- Time
- Agricultural activity
- Crop
- Market
- Price
- Production
- Procurement
- Scheme/advisory
- Source and provenance

The planned schema and data dictionary are maintained in the `Schema` directory.

Source provenance is an important part of the system. Extracted values should retain information about their originating source and relevant metadata so that results can be traced back to the original material.

## Agent and Tool Plan

The planned system uses an agentic architecture in which an LLM coordinates specialized tools for agriculture information retrieval and extraction.

Potential tools include:

- Static web scraping
- Dynamic web-page extraction
- PDF text extraction
- Table extraction
- OCR for scanned documents
- Hindi/Devanagari OCR
- Database insertion and retrieval
- Source/provenance handling

The detailed initial tool plan is documented in `docs/Phase1/Agent_Tool_Plan.md`.

## Repository Structure

```text
AI-Project-Madhya-Pradesh/
├── Schema/
│   ├── database_schema.md
│   └── data_dictionary.md
├── Source_Inventory/
│   ├── MP_Source_Inventory.xlsx
│   └── source_inventory.csv
├── docs/
│   └── Phase1/
│       ├── Agent_Tool_Plan.md
│       ├── Phase1_Report.md
│       ├── Problem_Statement.md
│       ├── Source_Analysis.md
│       └── Team_Info.md
├── logs/
│   └── source_verification_log.md
└── README.md
```

## Phase 1 Documentation

The Phase 1 documentation contains:

- Problem framework
- Source analysis
- Source inventory
- Source verification log
- Initial database/schema design
- Data dictionary
- Agent and tool plan
- Team and role information

## Provenance and Reproducibility

For each source, the project aims to maintain relevant metadata such as:

- Source URL
- Source name
- Collection/verification date
- Language
- Modality
- Geographic coverage
- Time coverage
- License or access information where available
- Relevant limitations

This information will support reproducibility and source-level verification of extracted results.

## Planned Development

The later phases will build on the Phase 1 source and schema work to develop:

1. Data ingestion and assimilation pipelines
2. Agentic extraction tools
3. Database population and querying
4. LLM-based reasoning over the collected information
5. LoRA/QLoRA fine-tuning where appropriate
6. Evaluation with held-out documents
7. Spatial and temporal queries
8. Source/page-level provenance queries
9. Final demonstration and analysis

## Current Status

**Phase 1 – Source Discovery and Problem Framework**

The repository contains the initial source inventory, source analysis, schema design, data dictionary, verification log, and agent/tool planning documents.
