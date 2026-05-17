from fpdf import FPDF
import datetime

def generate_pdf(result: dict) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(20, 20, 20)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(45, 106, 79)
    pdf.cell(0, 12, "PlantMD - Disease Detection Report", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 7, f"Generated: {datetime.datetime.now().strftime('%d %B %Y, %H:%M')}", ln=True, align="C")
    pdf.ln(6)
    if result["status"] == "healthy":
        pdf.set_fill_color(234, 243, 222)
        pdf.set_text_color(59, 109, 17)
    elif result["status"] == "diseased":
        pdf.set_fill_color(252, 235, 235)
        pdf.set_text_color(163, 45, 45)
    else:
        pdf.set_fill_color(250, 238, 218)
        pdf.set_text_color(133, 79, 11)
    pdf.set_font("Helvetica", "B", 14)
    name = result['disease_name'].encode('latin-1', 'replace').decode('latin-1')
    pdf.cell(0, 12, f"  Diagnosis: {name}", ln=True, fill=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(4)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(60, 8, f"Severity: {result['severity']}")
    pdf.cell(60, 8, f"Confidence: {result['confidence']}%")
    pdf.cell(60, 8, f"Urgency: {result['urgency']}", ln=True)
    if result.get("scientific_name"):
        pdf.set_font("Helvetica", "I", 10)
        pdf.set_text_color(100, 100, 100)
        sname = result['scientific_name'].encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(0, 7, f"Scientific name: {sname}", ln=True)
        pdf.set_text_color(0, 0, 0)
    pdf.ln(4)
    def clean(text):
        return text.encode('latin-1', 'replace').decode('latin-1')
    def section(title, lines):
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(45, 106, 79)
        pdf.cell(0, 9, title, ln=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "", 11)
        for line in lines:
            pdf.multi_cell(0, 7, f"  {clean(str(line))}")
        pdf.ln(3)
    section("Observation", [result.get("description", "")])
    section("Recommended Treatments", [f"* {t}" for t in result.get("treatments", [])])
    section("Possible Causes", [f"* {c}" for c in result.get("causes", [])])
    section("Prevention Tips", [f"* {p}" for p in result.get("prevention", [])])
    pdf.set_y(-20)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 10, "PlantMD | AI Plant Disease Detection | Master Thesis Project", align="C")
    return bytes(pdf.output())
