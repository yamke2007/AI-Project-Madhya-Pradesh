# Problem Statement

## Title

**Intelligent Agriculture Information System: Madhya Pradesh**

## Background

Agriculture-related information for Madhya Pradesh is distributed across multiple official systems. Examples include market/mandi information, procurement systems, fertilizer distribution, agricultural machinery services, government schemes, crop insurance, weather advisories and agricultural statistics.

The same user question may require information from more than one source and may involve state, district, crop, date or season dimensions.

## Problem

There is a need for a unified information layer that can discover relevant sources, extract structured agriculture information, connect records across location and time, and return answers with source provenance.

## Proposed Solution

Build an agentic agriculture information system for Madhya Pradesh that:

1. maintains a source registry;
2. uses appropriate retrieval tools for webpages, PDFs, dashboards and structured files;
3. extracts structured agriculture entities and relationships;
4. validates extracted information before persistence;
5. stores the information in a queryable database;
6. answers natural-language queries;
7. provides provenance such as source URL, document title, collection date and page/section when available.

## Example Questions

- What was the production of a selected crop in a selected MP district in a selected year?
- What are the recorded mandi prices for a commodity on a given date?
- Which MP districts have KVKs listed by ICAR?
- What fertilizer quantity is recommended for a selected crop in the MP fertilizer calculator?
- What crop insurance statistics are available for Madhya Pradesh for a selected season/year?
- Which source and page support a particular numerical answer?

## Boundaries

The Phase 1 repository is a source-discovery and knowledge-base-design artifact. It is not yet the final working agent or production database.

Personal farmer information, Aadhaar-linked records and other unnecessary personal data are out of scope.
