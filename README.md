# Intelligent Agriculture Information System: Madhya Pradesh

**Course:** CS F/U 407 – Artificial Intelligence  
**Project:** Intelligent Agriculture Information System: State-Level  
**State:** Madhya Pradesh (MP)  
**Current Phase:** Phase 1 – Source Discovery and Knowledge Base Design

## Team

Replace the placeholders below with the three team members' details.

| Member | Role |
|---|---|
| Member 1 | Source Lead + Data Engineering Lead |
| Member 2 | Model Lead |
| Member 3 | Evaluation Lead |

## 1. Project Overview

This project aims to build an agriculture information system for Madhya Pradesh by collecting, organizing, extracting and querying information from heterogeneous agriculture-related sources.

The Phase 1 focus is source discovery and knowledge-base design. The system is intended to support information related to crops, production, prices and mandi activity, procurement, fertilizer and agricultural inputs, schemes, crop insurance, weather advisories, agricultural machinery and district-level agricultural information.

## 2. Phase 1 Objectives

- Define the purpose and scope of the Madhya Pradesh agriculture knowledge base.
- Identify reliable agriculture-related sources.
- Record source URLs and modalities such as webpages, PDFs and dashboards.
- Record language and geographic/time coverage.
- Identify useful information that can be extracted from each source.
- Record limitations such as dynamic pages, PDFs, OCR requirements and access restrictions.
- Draft an initial knowledge-base schema.
- Propose an initial agent/tool architecture.
- Maintain a source verification log for reproducibility.

## 3. Repository Structure

```text
AI-Project-Madhya-Pradesh/
├── README.md
├── Source_Inventory/
│   ├── MP_Source_Inventory.xlsx
│   └── source_inventory.csv
├── Schema/
│   ├── database_schema.md
│   └── data_dictionary.md
├── docs/
│   └── Phase1/
│       ├── Phase1_Report.md
│       ├── Problem_Statement.md
│       ├── Source_Analysis.md
│       └── Agent_Tool_Plan.md
└── logs/
    └── source_verification_log.md
```

## 4. Main Source Categories

1. State agriculture department and farmer portals
2. Procurement and MSP information
3. Mandi/market and price information
4. Fertilizer and agricultural input information
5. Agricultural machinery and irrigation equipment
6. Government schemes
7. Crop insurance
8. Weather/agrometeorological advisories
9. Agricultural statistics
10. KVK/agricultural extension information

## 5. Initial Status

The source inventory contains official/government sources identified during Phase 1 research. Each entry should be re-checked by the team before final submission, especially dynamic dashboards and pages whose structure may change.

## 6. Important Principle

The system should preserve provenance. Every extracted fact should eventually be associated with source URL, source title, collection date, language, and where possible document/page information.

## 7. Next Steps

- Replace team placeholders.
- Re-open and verify every source in the inventory.
- Add any additional MP-specific district/KVK sources discovered by the team.
- Finalize the schema after source review.
- Add GitHub commit history showing individual contributions.
- Do not add personal farmer/Aadhaar data.
