"""하이브리드/스테이블 매트리스 PDF 단일 처리 (신규 추가)."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import base64, json
from pathlib import Path
import fitz

ROOT = Path(r"C:\Users\USER\Desktop\오가렌_DX\침대_설치가이드")
SLUG = "hybrid-stable"
SRC = Path(r"C:\Users\USER\.claude\projects\C--Users-USER-Desktop-----DX\5622ee35-2a46-4a9b-91fb-08a17165dbf0\tool-results\toolu_01QQWN2iZjqpwMFbAcWfE27o.txt")

PDF_DIR = ROOT / "assets" / "pdf"
IMG_DIR = ROOT / "assets" / "img" / "steps" / SLUG
PDF_DIR.mkdir(parents=True, exist_ok=True)
IMG_DIR.mkdir(parents=True, exist_ok=True)

print(f"reading {SRC.stat().st_size/1024/1024:.1f} MB")
raw = SRC.read_text(encoding="utf-8")
data = json.loads(raw)
pdf_bytes = base64.b64decode(data["content"])

pdf_path = PDF_DIR / f"{SLUG}.pdf"
pdf_path.write_bytes(pdf_bytes)
print(f"PDF saved: {len(pdf_bytes)/1024/1024:.1f} MB")

# JPG 변환 (1.5x DPI, 큰 PDF라 약간 줄임)
doc = fitz.open(pdf_path)
mat = fitz.Matrix(1.5, 1.5)
for old in IMG_DIR.glob("*.jpg"):
    old.unlink()

for i, page in enumerate(doc, start=1):
    pix = page.get_pixmap(matrix=mat, alpha=False)
    pix.pil_save(IMG_DIR / f"page-{i:02d}.jpg", format="JPEG", quality=80, optimize=True)

n = doc.page_count
total = sum(f.stat().st_size for f in IMG_DIR.glob("*.jpg"))
print(f"\nconverted: {n} pages -> {total/1024/1024:.1f} MB")

# 페이지별 텍스트 미리보기
print("\n=== page text preview ===")
doc2 = fitz.open(pdf_path)
for i, page in enumerate(doc2, start=1):
    text = page.get_text().strip().replace("\n", " ")[:100]
    print(f"  page-{i:02d}: {text}")
doc2.close()
doc.close()
