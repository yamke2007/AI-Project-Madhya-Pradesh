# Crop and Crop-Stage Scope — Phase 1

## 1. Proposed crop scope

For Phase 1, the project proposes to cover **6 major crop groups/crops commonly represented in Madhya Pradesh agriculture information systems**:

1. Soybean
2. Wheat
3. Gram (Chickpea)
4. Maize
5. Rice (Paddy)
6. Cotton

> **Scope note:** This is a proposed project scope for the Phase 1 design. The exact final crop list should be confirmed against the team's selected official Madhya Pradesh agricultural/statistical sources before implementation.

## 2. Crop-stage / agricultural-information coverage

The project is designed to cover the following stages and information areas:

| Stage / activity | Information to capture | Example source types |
|---|---|---|
| Seed-related information | seed availability, seed-related advisories, testing/licensing information where available | Agriculture department, seed-related official pages/PDFs |
| Farm planning | crop selection, season, fertilizer recommendations, scheme information | Agriculture portals, advisories, official schemes |
| Field monitoring | weather advisories, crop advisories, pest/disease-related information where available | IMD/agromet and official agriculture advisories |
| Production | area, production, yield, season and year | DES/statistical reports |
| Procurement | procurement quantity, procurement centres and MSP-related information | e-Uparjan, official procurement sources |
| Aggregation, storage and logistics | mandi/APMC, arrivals, market information and procurement-centre information where available | e-Mandi/e-NAM and official market systems |
| Market and supply chain | mandi, commodity, date, min/max/modal price and arrivals where available | e-Mandi/e-NAM and market portals |

## 3. Phase 1 design principle

Not every source will contain information for every crop or stage. The source registry should record the actual coverage of each source rather than assuming that a source supports all six crops and all stages.

## 4. Planned query dimensions

The system should support combinations of:

- crop
- agricultural stage/activity
- district/location
- season
- year/date
- market/mandi
- source

These dimensions connect the crop-stage requirement to the database and agent design.
