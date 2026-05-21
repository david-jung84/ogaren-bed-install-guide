"""PDF의 각 페이지 첫 50자 텍스트 추출 — step 매핑 디버깅용."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import fitz
from pathlib import Path

PDF_DIR = Path(r"C:\Users\USER\Desktop\오가렌_DX\침대_설치가이드\assets\pdf")

for pdf_path in sorted(PDF_DIR.glob("*.pdf")):
    print(f"\n========== {pdf_path.stem} ==========")
    doc = fitz.open(pdf_path)
    for i, page in enumerate(doc, start=1):
        text = page.get_text().strip().replace("\n", " ")[:90]
        print(f"  page-{i:02d}: {text}")
    doc.close()
