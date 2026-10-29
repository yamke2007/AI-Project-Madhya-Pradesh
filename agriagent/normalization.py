import re
import unicodedata
from decimal import Decimal, InvalidOperation
from datetime import datetime

MISSING = "MISSING:not_in_source"
NA = "MISSING:not_applicable"

def text(value):
    return " ".join(unicodedata.normalize("NFKC", str(value)).split())

CROP_SYNONYMS = {"गेहूं": "wheat", "गेहूँ": "wheat", "धान": "rice", "paddy": "rice",
            "चना": "chickpea", "gram": "chickpea", "सोयाबीन": "soybean",
            "मक्का": "maize", "कपास": "cotton",
            # Added for the general table agent (Agmarknet/DES spellings, more Hindi names)
            "soyabean": "soybean", "soya bean": "soybean", "bengal gram": "chickpea",
            "bengal gram(gram)(whole)": "chickpea", "chana": "chickpea", "paddy(dhan)(common)": "rice",
            "paddy(dhan)": "rice", "dhan": "rice", "चावल": "rice", "सरसों": "mustard",
            "rapeseed & mustard": "mustard", "rapeseed and mustard": "mustard", "मसूर": "lentil",
            "masur": "lentil", "masoor": "lentil", "अरहर": "tur", "तुअर": "tur", "arhar": "tur",
            "arhar/tur": "tur", "उड़द": "urad", "उड़द": "urad", "black gram": "urad", "मूंग": "moong",
            "green gram": "moong", "लहसुन": "garlic", "प्याज": "onion", "आलू": "potato", "टमाटर": "tomato",
            "ज्वार": "jowar", "sorghum": "jowar", "बाजरा": "bajra", "गन्ना": "sugarcane",
            "मूंगफली": "groundnut", "धनिया": "coriander", "makka": "maize", "kapas": "cotton"}


def crop(value):
    if str(value).startswith("MISSING:"):
        return str(value)
    value = text(value).casefold()
    return CROP_SYNONYMS.get(value, value)

# Hindi names and renamed districts -> current English name (lower case). Unknown
# spellings are still kept exactly as written (no speculative correction).
DISTRICT_ALIASES = {"मध्य प्रदेश": "madhya pradesh", "mp": "madhya pradesh", "m.p.": "madhya pradesh",
    "hoshangabad": "narmadapuram", "होशंगाबाद": "narmadapuram", "नर्मदापुरम": "narmadapuram",
    "east nimar": "khandwa", "west nimar": "khargone", "narsimhapur": "narsinghpur", "badwani": "barwani",
    "इंदौर": "indore", "भोपाल": "bhopal", "उज्जैन": "ujjain", "जबलपुर": "jabalpur", "ग्वालियर": "gwalior",
    "सागर": "sagar", "रीवा": "rewa", "सतना": "satna", "सीहोर": "sehore", "विदिशा": "vidisha",
    "देवास": "dewas", "धार": "dhar", "मंदसौर": "mandsaur", "नीमच": "neemuch", "रतलाम": "ratlam",
    "शाजापुर": "shajapur", "राजगढ़": "rajgarh", "रायसेन": "raisen", "हरदा": "harda", "बैतूल": "betul",
    "छिंदवाड़ा": "chhindwara", "सिवनी": "seoni", "बालाघाट": "balaghat", "मंडला": "mandla",
    "कटनी": "katni", "दमोह": "damoh", "पन्ना": "panna", "छतरपुर": "chhatarpur", "टीकमगढ़": "tikamgarh",
    "गुना": "guna", "शिवपुरी": "shivpuri", "मुरैना": "morena", "भिंड": "bhind", "दतिया": "datia",
    "श्योपुर": "sheopur", "खंडवा": "khandwa", "खरगोन": "khargone", "बुरहानपुर": "burhanpur",
    "झाबुआ": "jhabua", "अलीराजपुर": "alirajpur", "बड़वानी": "barwani", "नरसिंहपुर": "narsinghpur",
    "शहडोल": "shahdol", "उमरिया": "umaria", "अनूपपुर": "anuppur", "डिंडोरी": "dindori",
    "सीधी": "sidhi", "सिंगरौली": "singrauli", "अशोकनगर": "ashoknagar", "आगर मालवा": "agar malwa",
    "निवाड़ी": "niwari", "मऊगंज": "mauganj", "मैहर": "maihar", "पांढुर्णा": "pandhurna"}


def location(value):
    if str(value).startswith("MISSING:"):
        return str(value)
    value = text(value).casefold()
    return DISTRICT_ALIASES.get(value, value)

def period(value):
    value = text(value)
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            pass
    return value

UNITS = {"tonne": ("tonne", Decimal(1)), "tonnes": ("tonne", Decimal(1)),
         "lakh tonnes": ("tonne", Decimal(100000)), "kg": ("tonne", Decimal("0.001")),
         "quintal": ("tonne", Decimal("0.1")), "hectare": ("hectare", Decimal(1)),
         "lakh hectare": ("hectare", Decimal(100000)), "percent": ("percent", Decimal(1)),
         "%": ("percent", Decimal(1)), "year": ("year", Decimal(1)),
         "text": ("text", Decimal(1)), "count": ("count", Decimal(1)),
         "lakh farmers": ("count", Decimal(100000)), "INR/quintal": ("INR/quintal", Decimal(1)),
         # Added for the general table agent
         "'000 tonnes": ("tonne", Decimal(1000)), "thousand tonnes": ("tonne", Decimal(1000)),
         "ha": ("hectare", Decimal(1)), "hectares": ("hectare", Decimal(1)),
         "'000 hectare": ("hectare", Decimal(1000)), "thousand hectare": ("hectare", Decimal(1000)),
         "kg/hectare": ("kg/hectare", Decimal(1)), "tonne/hectare": ("kg/hectare", Decimal(1000)),
         "quintal/hectare": ("kg/hectare", Decimal(100)), "bales": ("bales", Decimal(1))}

def number(value):
    return Decimal(text(value).replace(",", ""))

def validate(record, lgd=None):
    errors = []
    for field in ("source", "source_type", "agent", "run_id", "locator", "crop", "location", "period", "unit", "variable"):
        if not isinstance(record.get(field), str) or not record[field].strip():
            errors.append("missing:" + field)
    if record.get("value") in (None, "", MISSING):
        errors.append("missing:value")
    if record.get("unit") not in UNITS:
        errors.append("unknown:unit")
    if record.get("value_kind") not in ("integer", "decimal", "text", "code"):
        errors.append("invalid:value_kind")
    if not re.fullmatch(r"(?:\d{4}|\d{4}-\d{2}|\d{4}-\d{2}-\d{2}|MISSING:[\w_]+)", record.get("period", "")):
        errors.append("invalid:period")
    elif re.fullmatch(r"\d{4}-\d{2}-\d{2}", record["period"]):
        try:
            datetime.strptime(record["period"], "%Y-%m-%d")
        except ValueError:
            errors.append("invalid:period")
    elif re.fullmatch(r"\d{4}-\d{2}", record.get("period", "")):
        start, end = record["period"].split("-")
        if (int(start)+1)%100 != int(end):
            errors.append("invalid:financial_year")
    if record.get("value_kind") in ("integer", "decimal"):
        try:
            n = number(record["value"])
            growth_percent = record.get("unit") in ("percent", "%") and record.get("variable", "").endswith("_growth")
            if not n.is_finite() or n < (-100 if growth_percent else 0) or n > Decimal("1e14"):
                errors.append("implausible:value")
            if record["value_kind"] == "integer" and n != n.to_integral_value():
                errors.append("invalid:integer")
            if record.get("unit") in ("percent", "%") and not growth_percent and n > 100:
                errors.append("implausible:percent")
        except (InvalidOperation, ValueError):
            errors.append("invalid:number")
    code = record.get("lgd_code")
    if code and (not lgd or str(code) not in lgd or location(lgd[str(code)]) != record["location"]):
        errors.append("unverified:lgd_code")
    return errors
