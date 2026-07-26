import os
import sys

def convert_txt_to_pdf_via_fpdf(txt_path, pdf_path):
    # Usaremos una biblioteca de Python sencilla para crear PDFs.
    # fpdf2 o reportlab. Si no están en el host de ejecución de inmediato, las instalamos.
    # Alternativamente, podemos escribir un script que genere un PDF usando reportlab o fpdf.
    # Probemos con fpdf.
    try:
        from fpdf import FPDF
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "fpdf2"])
        from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)

    with open(txt_path, "r", encoding="utf-8") as f:
        for line in f:
            # Asegurar compatibilidad de caracteres latin1 con fpdf básico
            clean_line = line.encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 8, clean_line)

    pdf.output(pdf_path)
    print(f"Convertido {txt_path} -> {pdf_path}")

if __name__ == "__main__":
    os.makedirs("rag-service/data/pdfs/publico", exist_ok=True)
    os.makedirs("rag-service/data/pdfs/miembro", exist_ok=True)

    convert_txt_to_pdf_via_fpdf(
        "rag-service/data/pdfs/publico/comunicado_publico.txt",
        "rag-service/data/pdfs/publico/comunicado_publico.pdf"
    )
    convert_txt_to_pdf_via_fpdf(
        "rag-service/data/pdfs/miembro/reglamento_interno.txt",
        "rag-service/data/pdfs/miembro/reglamento_interno.pdf"
    )
