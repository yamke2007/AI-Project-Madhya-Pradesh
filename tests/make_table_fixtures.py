"""SYNTHETIC fixtures for the general table agent (code tests only; never evaluation data).
Values are invented and labelled SYNTHETIC in every file. Run: python tests/make_table_fixtures.py
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
D = Path(__file__).parent / "fixtures_tables"
D.mkdir(exist_ok=True)

def pdf_table():
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    rows = [["District", "Crop", "Year", "Season", "Area (Hectare)", "Production (Tonne)", "Yield (Tonne/Hectare)"],
            ["Sehore", "Wheat", "2022-23", "Rabi", "251340", "1120450", "4.46"],
            ["Vidisha", "Wheat", "2022-23", "Rabi", "312005", "1301180", "4.17"],
            ["Hoshangabad", "Wheat", "2022-23", "Rabi", "268900", "1255300", "4.67"],
            ["Total", "", "", "", "832245", "3676930", ""]]
    t = Table(rows); t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.black)]))
    SimpleDocTemplate(str(D / "synthetic_district_apy.pdf"), pagesize=A4).build(
        [Paragraph("SYNTHETIC district-wise area, production and yield", getSampleStyleSheet()["Title"]), t])

def png(name, lines, font_path, size=34):
    img = Image.new("RGB", (1800, 120 + 110 * len(lines)), "white"); dr = ImageDraw.Draw(img)
    f = ImageFont.truetype(font_path, size)
    for i, cells in enumerate(lines):
        x = 40
        for c, w in zip(cells, [520, 420, 420, 420]):
            dr.text((x, 40 + i * 110), c, fill="black", font=f); x += w
    img.save(D / name)

def xlsx():
    from openpyxl import Workbook
    wb = Workbook(); ws = wb.active; ws.title = "prices"
    ws.append(["SYNTHETIC mandi prices 14/10/2024"])
    ws.append(["State", "District", "Market", "Commodity", "Min Price (Rs/Qtl)", "Max Price (Rs/Qtl)", "Modal Price (Rs/Qtl)"])
    ws.append(["Madhya Pradesh", "Indore", "Indore", "Soyabean", 4100, 4550, 4400])
    ws.append(["Madhya Pradesh", "Ujjain", "Ujjain", "Wheat", 2600, 2850, 2725])
    ws.append(["Rajasthan", "Kota", "Kota", "Wheat", 2500, 2700, 2600])
    wb.save(D / "synthetic_mandi_prices.xlsx")

if __name__ == "__main__":
    import sys
    font = sys.argv[1] if len(sys.argv) > 1 else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    pdf_table(); xlsx()
    png("synthetic_scan_en.png", [["SYNTHETIC Wheat production 2021-22"], ["District", "Area ('000 Ha)", "Production ('000 Tonnes)"],
        ["Sagar", "310.5", "1180.2"], ["Raisen", "290.1", "1150.7"], ["Dhar", "205.3", "880.4"]],
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    png("synthetic_scan_hi.png", [["SYNTHETIC मंडी भाव 15/10/2024"], ["जिला", "फसल", "न्यूनतम (रु/क्विंटल)", "अधिकतम (रु/क्विंटल)"],
        ["इंदौर", "सोयाबीन", "4050", "4500"], ["उज्जैन", "गेहूं", "2600", "2850"], ["सीहोर", "चना", "5900", "6400"]], font)
    (D / "synthetic_prices.html").write_text("""<html><head><title>SYNTHETIC mandi bhav 15/10/2024</title></head><body>
<table><tr><th>District</th><th>Mandi</th><th>Commodity</th><th>Min Price (Rs/Qtl)</th><th>Max Price (Rs/Qtl)</th><th>Modal Price (Rs/Qtl)</th></tr>
<tr><td>Dewas</td><td>Dewas</td><td>Soybean</td><td>4050</td><td>4500</td><td>4380</td></tr>
<tr><td>Mandsaur</td><td>Mandsaur</td><td>Garlic</td><td>8000</td><td>16500</td><td>12000</td></tr></table></body></html>""", encoding="utf-8")
    (D / "synthetic_agmarknet.csv").write_text(
        "State,District,Market,Commodity,Variety,Arrival_Date,Min_x0020_Price,Max_x0020_Price,Modal_x0020_Price\n"
        "Madhya Pradesh,Sehore,Ashta,Bengal Gram(Gram)(Whole),Desi,14/10/2024,5900,6400,6200\n", encoding="utf-8")
    print("synthetic table fixtures written to", D)
