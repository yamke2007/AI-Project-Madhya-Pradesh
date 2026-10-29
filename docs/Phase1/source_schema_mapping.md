# Phase 1: Source-to-Schema Mapping

## Purpose

This document maps the Phase 1 source inventory to the initial knowledge-base schema. The mapping identifies which existing entities can represent information from each source, why the source is relevant, and where the current schema does not directly represent the source's information.

The mapping is based on the current source inventory and initial database schema. It is intended to guide Phase 2 data assimilation while keeping the Phase 1 schema minimal and source-grounded.

## Core Schema Entities

The current schema contains the following main entities:

- Source
- Location
- Crop
- Production
- MarketPrice
- Procurement
- Scheme
- FertilizerRecommendation
- WeatherAdvisory
- InsuranceStatistic
- KVK

## Source-to-Schema Mapping

| Source | Primary schema entity/entities | Information represented | Mapping rationale / limitation |
|---|---|---|---|
| MP e-Vikas fertilizer distribution system | Source; Location; Crop; FertilizerRecommendation (partial) | Fertilizer distribution, farmer token workflow, fertilizer calculation/tracking | Fertilizer-related recommendations/calculations can fit FertilizerRecommendation. Distribution/token workflow is not fully represented by the current schema and should not be forced into an unrelated entity. |
| MP e-Vikas fertilizer calculator | Crop; FertilizerRecommendation; Source | Crop, area, NPK and recommended fertilizer quantities | Directly supports crop-specific fertilizer recommendation fields. Area and nutrient inputs may be stored with the recommendation only if required by the final extraction design. |
| MP e-Anugya / e-Mandi | MarketPrice; Location; Source | Mandi/APMC and agricultural marketing information | Relevant to mandi-level market information. Exact price fields should only be populated when the source exposes the corresponding values. |
| MP e-Mandi user manual | Source | e-Mandi workflow and system context | This is primarily documentation about the system rather than a factual agricultural observation. It can support source interpretation and extraction design but should not automatically become a MarketPrice record. |
| MP e-Uparjan / procurement | Procurement; Location; Crop; Source | Procurement registration and procurement-related information | Directly relevant to procurement. The existing Procurement entity can represent crop, location, season/year, quantity, MSP and procurement-centre information where available. |
| MP CM Helpline scheme: MSP procurement | Scheme; Procurement (partial); Source | Purpose, application process and MSP procurement scheme information | Scheme-level information maps directly to Scheme. Descriptive scheme information should not be treated as operational procurement statistics. |
| MP e-Services agriculture services | Source; Scheme (partial) | Crop arrival/rates, soil testing, seed testing, input quality control and machinery subsidy services | The directory points to separate systems and is not itself a complete dataset. There is no dedicated Service entity in the current schema, so service-directory information should remain source/context metadata unless the schema is expanded later. |
| MP Directorate of Agricultural Engineering | Scheme; Source; Location (where applicable) | Agricultural machinery schemes, custom hiring and equipment information | Scheme-related information can map to Scheme. Machinery/service information does not have a dedicated entity in the current schema. |
| MP farmer agricultural machinery portal | Scheme (partial); Source; Location | Agricultural machinery and irrigation equipment services | The current schema does not have a machinery/service entity. Scheme information may fit Scheme where explicitly provided; interactive application records should not be ingested without a clear project need and authorization. |
| India Meteorological Department crop advisories | WeatherAdvisory; Location; Crop; Source | Crop-specific agrometeorological advisories by state/district/crop | Direct match to WeatherAdvisory, including location, crop, advisory date, text and provenance. |
| DES Area Production Yield query | Production; Location; Crop; Source | Area, production and yield by state, district, crop, season and year | Direct match to Production and its related Location/Crop dimensions. |
| DES APY major district reports | Production; Location; Crop; Source | Major contributing districts for selected crops and years | Supports production/district/crop analysis. Exact fields available should be checked during extraction before populating the schema. |
| DES Agricultural Statistics at a Glance | Production; Procurement (partial); Source; Location; Crop | State/national agricultural statistics including production and procurement-related tables | Relevant tables can populate Production and, where fields match, Procurement. Because this is a broad report, each extracted table must be mapped individually rather than treating the entire PDF as one entity. |
| PMFBY guidelines | Scheme; Source | Crop insurance guidelines and scheme documentation | Primarily supports Scheme-level documentation. The guidelines themselves should not be treated as InsuranceStatistic observations. |
| PMFBY administrative dashboard | InsuranceStatistic; Location; Crop; Source | Insurance coverage, farmers, area insured, premium, claims and farmer benefit statistics | Direct match to InsuranceStatistic, with geographic/crop/time dimensions where the dashboard exposes them. |
| PM-KISAN | Scheme; Source; Location (where applicable) | Farmer scheme information, status, beneficiary services and documentation | Scheme information maps to Scheme. Beneficiary-level information is explicitly outside the project's intended scope and must not be ingested as personal data. |
| PM-KISAN beneficiary list | Source; Location (aggregated only) | Public beneficiary-list query by administrative geography | No beneficiary-level records should be stored. Only aggregated information, if demonstrably needed and permitted, could potentially use Location; the current schema has no beneficiary-statistics entity. |
| e-NAM mandi status | Location; Source; MarketPrice (partial) | e-NAM mandi coverage and trading-related information | Strong fit for mandi/location information. MarketPrice should only be populated when actual price observations and the required fields are exposed. |
| e-NAM mandi online | Location; Source; MarketPrice (partial) | APMC/mandi online-trading information | Relevant to mandi-level market/trading information. Exact market-price fields must be verified before mapping records to MarketPrice. |
| e-NAM state unified license / MP | Scheme (partial); Source; Location | State unified-license acts including Madhya Pradesh | This is legal/documentary information, not a direct match to the current factual entities. It can be retained as a source/document reference; Scheme is only a partial conceptual mapping and should not be used unless the extracted content concerns a scheme/service relevant to the project. |
| ICAR Madhya Pradesh KVK directory | KVK; Location; Source | KVK names, districts and host organizations in MP | Direct match to KVK plus district/location and provenance. |
| ICAR KVK telephone directory | KVK; Location; Source | KVK contact/address information for MP | Directly supports KVK contact/address fields where current schema permits. Because this is a 2020 directory, dates/version should be retained in provenance and current details should be verified before presenting them as current. |
| MP Economic Survey agriculture highlights | Production; InsuranceStatistic (partial); Location; Crop; Source | Agriculture production, cropped area, insurance and irrigation highlights | Relevant tables can support Production and selected insurance statistics. Irrigation information has no dedicated entity in the current schema and should remain unmodeled unless the schema is expanded. |

## Schema Coverage Summary

### Strongly supported entities

- **Source:** All collected information can retain source provenance.
- **Location:** Most sources have state, district, mandi or institutional geographic context.
- **Crop:** Production, market, fertilizer, weather and insurance sources can provide crop dimensions where explicitly available.
- **Production:** Strongly supported by DES APY sources and agricultural statistics reports.
- **MarketPrice:** Supported by e-Mandi/e-NAM sources when actual price observations are exposed.
- **Procurement:** Supported by e-Uparjan and relevant agricultural statistics/procurement material.
- **Scheme:** Supported by government scheme and scheme-documentation sources.
- **FertilizerRecommendation:** Supported by the e-Vikas fertilizer calculator.
- **WeatherAdvisory:** Directly supported by IMD crop advisories.
- **InsuranceStatistic:** Directly supported by the PMFBY administrative dashboard and partially by relevant statistical reports.
- **KVK:** Directly supported by the ICAR KVK directories.

