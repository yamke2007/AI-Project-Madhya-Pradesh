"""Parsers operate on supplied content, never case IDs or expected answers."""
import csv
import io
import re
from bs4 import BeautifulSoup
from .normalization import text, MISSING, NA

STATS_FIELDS = {"crop", "location", "period", "variable", "value", "unit"}

class ExtractionError(ValueError):
    pass

def soup_of(path):
    return BeautifulSoup(path.read_bytes().decode("utf-8-sig"), "html.parser")

IMAGE = (".png", ".jpg", ".jpeg", ".tif", ".tiff")

def detect(path):
    """Primary specialist for an input: (agent, tool, source group). Fixed rules, no model."""
    suffix = path.suffix.lower()
    if suffix == ".csv":
        head = path.read_bytes()[:4096].decode("utf-8-sig", errors="replace").splitlines()[:1]
        cols = {c.strip() for c in next(csv.reader(head), [])} if head else set()
        if STATS_FIELDS.issubset(cols) or not head:
            return "statistics", "csv.DictReader", "Database"
        return "tables", "csv.reader", "Database"
    if suffix == ".pdf":
        return "statistics", "pypdf", "Document"
    if suffix in (".xlsx", ".xlsm"):
        return "tables", "openpyxl.read", "Database"
    if suffix in IMAGE:
        return "tables", "tesseract.ocr_tables", "Document"
    if suffix in (".html", ".htm"):
        soup = soup_of(path)
        content = soup.get_text(" ", strip=True)
        if "Host Organization" in content and "Year of Sanction" in content:
            return "directory", "beautifulsoup4", "Document"
        if "योजना का नाम" in content and "विभाग" in content:
            return "scheme", "beautifulsoup4", "Document"
        if "{{" in content:
            raise ExtractionError("Unrendered dynamic template: export actual results; placeholders are not observations")
        if soup.find("table") is None:
            raise ExtractionError("Unsupported HTML structure: no table found")
        return "tables", "beautifulsoup4.tables", "Document"
    raise ExtractionError("Unsupported modality: use HTML, CSV, XLSX, PDF or an image; audio is pending")

def directory(path):
    soup = soup_of(path)
    records = []
    for ti, table in enumerate(soup.find_all("table"), 1):
        if "Year of Sanction" not in table.get_text():
            continue
        for ri, row in enumerate(table.find_all("tr"), 1):
            cells = row.find_all(["td", "th"], recursive=False)
            if len(cells) != 4 or not re.fullmatch(r"\d+\.?", cells[0].get_text(strip=True)):
                continue
            address, host, sanction = [text(c.get_text(" ", strip=True)) for c in cells[1:]]
            district = re.search(r"Distt\.\s*([A-Za-z ]+)", address)
            year = re.search(r"\b(?:19|20)\d{2}\b", sanction)
            locator = f"table:{ti}/row:{ri}"
            common = dict(crop=NA, location=district.group(1).strip(" ,.-") if district else MISSING,
                          period=NA, locator=locator, evidence=text(row.get_text(" ", strip=True)),
                          record_id=cells[0].get_text(strip=True).rstrip("."))
            for variable, value, unit, kind in (("address",address,"text","text"),
                    ("host_organization",host,"text","text"),
                    ("sanction_year",year.group() if year else MISSING,"year","integer")):
                records.append(dict(common,variable=variable,value=value,unit=unit,value_kind=kind))
    if not records:
        raise ExtractionError("No KVK records found")
    return records, []

def scheme(path):
    soup = soup_of(path)
    records = []
    # Preserve the official Hindi label rather than guess a translated field.
    for ti, table in enumerate(soup.find_all("table"), 1):
        for ri, row in enumerate(table.find_all("tr"), 1):
            cells = row.find_all(["td", "th"], recursive=False)
            if len(cells) != 2:
                continue
            key, value = [text(c.get_text(" ", strip=True)) for c in cells]
            if not key:
                continue
            records.append(dict(crop=NA,location=MISSING,period=MISSING,variable=key,
                value=value or MISSING,unit="text",value_kind="text",locator=f"table:{ti}/row:{ri}",
                evidence=text(row.get_text(" ",strip=True))))
    if not records:
        raise ExtractionError("No two-cell policy rows found")
    return records, []

def statistics(path, max_pages=300):
    if path.suffix.lower() == ".pdf":
        from pypdf import PdfReader
        pdf = PdfReader(path)
        if len(pdf.pages) > max_pages:
            raise ExtractionError("PDF page limit exceeded")
        records = []
        # Intentionally conservative grammar; other facts remain unextracted.
        pattern = re.compile(r"produced\s+([\d,.]+)\s+(lakh tonnes|tonnes)\s+of\s+(wheat|paddy|rice|maize|soybean|gram|cotton)\s+in\s+(\d{4}-\d{2})", re.I)
        text_pages = 0
        for pi, page in enumerate(pdf.pages, 1):
            content = text(page.extract_text() or "")
            text_pages += bool(content)
            for match in pattern.finditer(content):
                value, unit, crop, year = match.groups()
                records.append(dict(crop=crop, location="Madhya Pradesh" if "Madhya Pradesh" in " ".join((p.extract_text() or "") for p in pdf.pages[:3]) else MISSING,
                    period=year,variable="production",value=value,unit=unit,value_kind="decimal",
                    locator=f"page:{pi}/char:{match.start()}-{match.end()}",evidence=match.group(),qualifier="source wording; estimates may be provisional"))
        if not records:
            raise ExtractionError("No supported production sentences; text pages="+str(text_pages)+"; tables/OCR are left to the tables agent")
        return records, ["Partial PDF grammar: only explicit 'produced X tonnes of CROP in YEAR' sentences; omitted facts are not inferred"]
    reader = csv.DictReader(io.StringIO(path.read_text(encoding="utf-8-sig")))
    if not STATS_FIELDS.issubset(reader.fieldnames or []):
        raise ExtractionError("CSV requires headers: "+", ".join(sorted(STATS_FIELDS)))
    records = []
    for row in reader:
        if None in row:
            raise ExtractionError("Malformed CSV: excess columns")
        record = {k: text(v or MISSING) for k,v in row.items()}
        record.setdefault("value_kind", "decimal")
        record["evidence"] = text(" | ".join(str(v or "") for v in row.values()))
        record["locator"] = f"csv:line:{reader.line_num}"
        records.append(record)
    if not records:
        raise ExtractionError("CSV has no data rows")
    return records, []
