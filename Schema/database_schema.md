# Initial Database Schema

## Core entities

### Source
- source_id
- title
- publisher
- url
- modality
- language
- license_or_terms
- collection_date
- notes

### Location
- location_id
- state
- district
- block
- village
- mandi
- latitude
- longitude

### Crop
- crop_id
- crop_name
- crop_group
- season

### Production
- production_id
- crop_id
- location_id
- season
- year
- area
- production
- yield
- source_id

### MarketPrice
- market_price_id
- crop_id
- mandi
- location_id
- date
- min_price
- max_price
- modal_price
- arrival_quantity
- source_id

### Procurement
- procurement_id
- crop_id
- location_id
- season
- year
- quantity
- MSP
- procurement_center
- source_id

### Scheme
- scheme_id
- scheme_name
- department
- eligibility
- benefit
- application_process
- source_id

### FertilizerRecommendation
- recommendation_id
- crop_id
- nutrient
- fertilizer
- recommended_quantity
- unit
- source_id

### WeatherAdvisory
- advisory_id
- location_id
- crop_id
- advisory_date
- advisory_text
- source_id

### InsuranceStatistic
- insurance_id
- crop_id
- location_id
- season
- year
- farmers
- area_insured
- premium
- claims_paid
- farmer_benefit
- source_id

### KVK
- kvk_id
- name
- district
- host_organization
- address
- source_id

## Relationships

```text
Location ----< Production >---- Crop
Location ----< MarketPrice >--- Crop
Location ----< Procurement >--- Crop
Location ----< WeatherAdvisory >--- Crop
Location ----< InsuranceStatistic >--- Crop
Crop --------< FertilizerRecommendation
Source ------< all factual records
```

## Query dimensions

The initial schema intentionally supports:
- spatial queries;
- temporal queries;
- crop-based queries;
- source/provenance queries;
- combinations of the above.
