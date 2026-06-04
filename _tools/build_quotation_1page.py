"""Generate 1-page Website Development Quotation PDF (standalone, not part of app)."""
from fpdf import FPDF


class QuotationPDF(FPDF):
    def footer(self):
        self.set_y(-12)
        self.set_font("Mangal", size=9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "Thank You  |  AlitWorld", align="C")


def main() -> None:
    pdf = QuotationPDF("P", "mm", "A4")
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()

    font_path = r"C:\Windows\Fonts\mangal.ttf"
    pdf.add_font("Mangal", "", font_path)
    pdf.add_font("Mangal", "B", font_path)

    # Title block
    pdf.set_fill_color(17, 24, 39)
    pdf.rect(10, 10, 190, 28, "F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Mangal", "B", 16)
    pdf.set_xy(10, 14)
    pdf.cell(190, 8, "Website Development Quotation", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Mangal", "", 10)
    pdf.cell(190, 6, "Digital Magazine / Content Portal  |  Python + Angular + MongoDB", align="C")

    y = 42
    pdf.set_text_color(17, 24, 39)

    def section_title(text: str, yy: float) -> float:
        pdf.set_font("Mangal", "B", 11)
        pdf.set_fill_color(254, 243, 199)
        pdf.set_xy(10, yy)
        pdf.cell(190, 7, f"  {text}", fill=True)
        return yy + 8

    def body(text: str, yy: float, size: int = 8) -> float:
        pdf.set_font("Mangal", "", size)
        pdf.set_xy(12, yy)
        pdf.multi_cell(186, 4.2, text)
        return pdf.get_y() + 1

    y = section_title("Project Overview", y)
    y = body(
        "Complete digital magazine website with Hindi/English content, admin panel (posts + PDF upload up to 50MB), "
        "writer submission, Open Mic registration, e-certificate download, and e-magazine archive.",
        y,
    )

    y = section_title("Main Menu & Pages", y)
    cols = [
        "• मुखपृष्ठ, संपादकीय, काव्यांजलि, लेख-आलेख, बाल साहित्य, कहानी कोना",
        "• विशेषांक, हमारे रचनाकार, साक्षात्कार, निहारिका रसोई, सौंदर्य, तारे-सितारे",
        "• पुराने अंक (PDF Archive), रचना भेजें, संपर्क सूत्र",
    ]
    for line in cols:
        y = body(line, y, 7.5)

    y = section_title("Homepage Special + Technical", y)
    y = body(
        "Homepage: आज का सुविचार | महीने के श्रेष्ठ रचनाकार | युवा मंच | Open Mic | E-Certificate  ||  "
        "Stack: Angular (Frontend), Python FastAPI/Django (Backend), MongoDB, Custom Admin CMS  ||  "
        "UI: Responsive, mobile-friendly, SEO-ready, modern magazine layout.",
        y,
        7.5,
    )

    # Cost box (3 columns)
    y += 2
    pdf.set_font("Mangal", "B", 10)
    box_h = 32
    w = 62
    boxes = [
        ("Project Cost", "₹30,000\n(Fixed Price)", (17, 24, 39)),
        ("Timeline", "20 – 30 Days\nDevelopment", (124, 45, 18)),
        ("Deliverables", "Website + Admin\nSource + Deploy + Training", (180, 83, 9)),
    ]
    x = 10
    for title, val, rgb in boxes:
        pdf.set_fill_color(*rgb)
        pdf.rect(x, y, w, box_h, "F")
        pdf.set_text_color(255, 255, 255)
        pdf.set_xy(x + 2, y + 3)
        pdf.cell(w - 4, 5, title, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Mangal", "", 9)
        pdf.set_xy(x + 2, y + 10)
        pdf.multi_cell(w - 4, 4.5, val)
        pdf.set_font("Mangal", "B", 10)
        x += w + 2

    y += box_h + 4
    pdf.set_text_color(17, 24, 39)
    y = section_title("Notes", y)
    y = body(
        "Hosting, domain & subscription charges extra (if required). Advanced modules (mobile app / AI) = additional cost. "
        "Includes full CMS, content publishing, and audience engagement features for writers & readers.",
        y,
        7.5,
    )

    out = r"e:\Meri niharika\Website Development Quotation - 1 Page.pdf"
    pdf.output(out)
    print(out)


if __name__ == "__main__":
    main()
