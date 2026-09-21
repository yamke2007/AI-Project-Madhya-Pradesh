# Agent and Tool Plan

## 1. High-level architecture

```text
User Query
   |
   v
Query / Reasoning Agent
   |
   +-------------------+
   |                   |
   v                   v
Source Registry     Database Search
   |
   v
Tool Selection
   |
   +---------+---------+---------+---------+
   |         |         |         |         |
 Web      PDF       OCR      Excel/CSV   API
Retriever Extractor  Tool      Reader    Client
   |         |         |         |         |
   +---------+---------+---------+---------+
                         |
                         v
                   Normalization
                         |
                         v
                  Validation Layer
                         |
                  +------+------+
                  |             |
                  v             v
             Human review   Automatic checks
                  |             |
                  +------+------+
                         |
                         v
                    MongoDB / DB
                         |
                         v
                  Answer Generator
                         |
                         v
             Answer + Provenance
```

## 2. Initial tools

### Web retrieval tool
Purpose: retrieve official HTML pages and structured page content.

### PDF extraction tool
Purpose: extract text and tables from government PDFs.

Candidate libraries:
- PyMuPDF
- pdfplumber

### OCR fallback
Purpose: handle scanned/image PDFs or Hindi documents where text extraction fails.

Candidate:
- Tesseract OCR with appropriate language data.

### Spreadsheet reader
Purpose: read XLSX/CSV datasets.

Candidate:
- pandas
- openpyxl

### Dynamic-page tool
Purpose: interact with portals that require browser actions or form selections.

Candidate:
- Playwright

### Database tool
Purpose:
- insert validated records;
- query by crop/district/date;
- preserve source references.

MongoDB can be considered because the course methodology discusses document-oriented storage, but the final database choice should be justified by the team.

## 3. Validation

Raw tool output should not automatically become trusted knowledge.

Validation checks can include:
- required fields present;
- date format valid;
- district/state consistency;
- numeric fields parse correctly;
- duplicate detection;
- source URL recorded;
- source collection date recorded;
- document/page recorded when available.

Human review can be used for uncertain extraction.

## 4. Provenance object

Every stored fact should aim to retain:

```text
source_id
source_url
source_title
publisher
collection_date
language
document_date
page_or_section
extraction_method
confidence
```

## 5. Fine-tuning

Phase 1 should not assume that fine-tuning is already necessary.

First establish:
- source retrieval;
- extraction;
- schema;
- evaluation examples.

Later phases can compare the base model and LoRA/QLoRA adapter on an evaluation set, as required by the project methodology.
