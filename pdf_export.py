from fpdf import FPDF
from pathlib import Path


def get_font_path() -> str:
    base_dir = Path(__file__).parent

    possible_fonts = [
        base_dir / "DejaVuSans.ttf",
        base_dir / "fonts" / "DejaVuSans.ttf",
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/calibri.ttf"),
        Path("C:/Windows/Fonts/segoeui.ttf"),
    ]

    for font_path in possible_fonts:
        if font_path.exists():
            return str(font_path)

    raise FileNotFoundError(
        "Nie znaleziono żadnej czcionki TTF obsługującej polskie znaki. "
        "Dodaj np. DejaVuSans.ttf do folderu projektu albo do folderu 'fonts'."
    )


def quiz_to_pdf(questions: list) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    font_path = get_font_path()

    pdf.add_font("UnicodeFont", "", font_path)
    pdf.set_font("UnicodeFont", size=14)
    pdf.cell(0, 10, "Quiz", new_x="LMARGIN", new_y="NEXT", align="C")

    pdf.set_font("UnicodeFont", size=11)

    for i, q in enumerate(questions, start=1):
        pytanie = str(q.get("pytanie", "Brak pytania"))
        opcje = q.get("opcje", {})

        pdf.ln(4)
        pdf.multi_cell(
            w=0,
            h=7,
            text=f"{i}. {pytanie}",
            new_x="LMARGIN",
            new_y="NEXT"
        )

        for letter, answer in opcje.items():
            pdf.multi_cell(
                w=0,
                h=6,
                text=f"{letter}. {str(answer)}",
                new_x="LMARGIN",
                new_y="NEXT"
            )

    pdf_bytes = pdf.output(dest="S")
    return bytes(pdf_bytes)