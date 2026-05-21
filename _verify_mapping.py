"""
각 가이드 step 텍스트 ↔ 매핑된 PDF 페이지 텍스트 대조 검증.

기준:
- step의 h4 제목과 p 본문에서 핵심 키워드 추출
- 매핑된 PDF 페이지 텍스트와 비교 → 키워드 일치 점수
- 점수 낮은 곳 = 매핑 의심 → 출력
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import re
from pathlib import Path
import fitz

ROOT = Path(r"C:\Users\USER\Desktop\오가렌_DX\침대_설치가이드")
PDF_DIR = ROOT / "assets" / "pdf"
GUIDES_DIR = ROOT / "guides"

# _inject_step_images.py 의 CONFIG 와 동기화
CONFIG = {
    "signature-mattress": {"pdf": "signature",       "step_pages": [3, 4, 4, 4, 4]},
    "lundvik":            {"pdf": "lundvik",         "step_pages": [14, 15, 16, 17, 18, 19, 24, 26]},
    "lundvik-low":        {"pdf": "lundvik-low",     "step_pages": [4, 4, 5, 6, 6, 9, 9, 10]},
    "lundvik-sliding":    {"pdf": "lundvik-sliding", "step_pages": [3, 4, 5, 5, 6, 7, 8]},
    "lund":               {"pdf": "lund",            "step_pages": [9, 9, 9, 10, 12, 13]},
    "hush":               {"pdf": "hush",            "step_pages": [3, 3, 4, 4, 7, 8, 9, 5]},
    "mori-daybed":        {"pdf": "mori-daybed",     "step_pages": [4, 4, 4, 4, 4, 4]},
    "mori-family":        {"pdf": "mori-family",     "step_pages": [5, 6, 7, 8, 9, 10, 11, 12]},
    "buddy-daybed":       {"pdf": "buddy-daybed",    "step_pages": [6, 7, 7, 7, 7, 8, 9, 10, 10]},
    "buddy-babyjang":     {"pdf": "buddy-babyjang",  "step_pages": [5, 5, 6, 6, 6, 6, 9, 9]},
    "buddy-gyogu":        {"pdf": "buddy-gyogu",     "step_pages": [4, 4, 4, 5, 5]},
    "lund-library":       {"pdf": "lund-library",    "step_pages": [6, 6, 7, 6, 7]},
}


def extract_keywords(text: str) -> set:
    """한글 명사/숫자 위주 키워드 추출 (2자 이상)."""
    # HTML 태그 제거
    text = re.sub(r"<[^>]+>", " ", text)
    # 한글, 영문, 숫자만
    tokens = re.findall(r"[가-힣]{2,}|[A-Za-z]{2,}|\d+", text)
    # 불용어 제거 + 너무 흔한 것 제거
    stop = {
        "주세요", "합니다", "있습니다", "위해", "위치", "방향", "다음",
        "단계", "도면", "이미지", "참고", "확인", "주의", "또는",
        "set", "ea", "page", "pp",
        "조립", "설치", "결합",  # 모든 설명에 나옴
    }
    return {t for t in tokens if t.lower() not in stop and len(t) >= 2}


def extract_steps(html: str) -> list:
    """HTML에서 step 추출: (step_idx, h4_text, p_text, mapped_page)."""
    step_re = re.compile(
        r'<li class="step"[^>]*>(.*?)</li>',
        re.DOTALL
    )
    steps = []
    for i, m in enumerate(step_re.finditer(html), start=1):
        inner = m.group(1)
        h4_match = re.search(r'<h4>(.*?)</h4>', inner, re.DOTALL)
        p_match = re.search(r'<p>(.*?)</p>', inner, re.DOTALL)
        # mapped page from img src
        img_match = re.search(r'page-(\d+)\.jpg', inner)
        h4 = re.sub(r"<[^>]+>", "", h4_match.group(1)).strip() if h4_match else ""
        p = re.sub(r"<[^>]+>", "", p_match.group(1)).strip() if p_match else ""
        page = int(img_match.group(1)) if img_match else None
        steps.append((i, h4, p, page))
    return steps


def get_pdf_pages_text(pdf_slug: str) -> dict:
    """PDF의 페이지번호 → 텍스트."""
    pdf_path = PDF_DIR / f"{pdf_slug}.pdf"
    if not pdf_path.exists():
        return {}
    doc = fitz.open(pdf_path)
    pages = {}
    for i, page in enumerate(doc, start=1):
        pages[i] = page.get_text()
    doc.close()
    return pages


def main():
    print("=" * 90)
    print(" 단계 ↔ PDF 페이지 매핑 검증 보고서")
    print("=" * 90)

    issues = []

    for slug, cfg in CONFIG.items():
        html_path = GUIDES_DIR / f"{slug}.html"
        if not html_path.exists():
            continue

        html = html_path.read_text(encoding="utf-8")
        steps = extract_steps(html)
        pdf_pages = get_pdf_pages_text(cfg["pdf"])

        if not pdf_pages:
            print(f"\n⚠️ [{slug}] PDF 없음 — skip")
            continue

        print(f"\n━━━ [{slug}] {len(steps)} steps ━━━")

        for step_idx, h4, p, page in steps:
            step_text = f"{h4} {p}"
            step_kw = extract_keywords(step_text)
            page_text = pdf_pages.get(page, "")
            page_kw = extract_keywords(page_text)

            if not step_kw:
                continue

            # 겹치는 키워드
            overlap = step_kw & page_kw
            score = len(overlap) / max(len(step_kw), 1) * 100

            # 인접 페이지 점수 (앞, 뒤)
            adj_scores = {}
            for delta in [-2, -1, 1, 2]:
                p2 = page + delta
                if p2 in pdf_pages:
                    p2_kw = extract_keywords(pdf_pages[p2])
                    p2_score = len(step_kw & p2_kw) / max(len(step_kw), 1) * 100
                    adj_scores[p2] = p2_score

            # 의심: 현재 페이지 점수 < 25% AND 인접 페이지 중 더 높은 게 있음
            best_adj = max(adj_scores.values()) if adj_scores else 0
            best_adj_page = max(adj_scores, key=adj_scores.get) if adj_scores else None
            suspicious = score < 25 and best_adj > score + 10

            flag = "🚨" if suspicious else ("⚠️ " if score < 30 else "✓ ")
            preview = h4[:35]
            print(f"  {flag} step {step_idx:2d} → page-{page:02d}  ({score:4.0f}%)  '{preview}'")
            if suspicious:
                # 인접 점수도 출력
                adj_str = "  ".join(f"p{p}:{s:.0f}%" for p, s in sorted(adj_scores.items()))
                print(f"          📍 인접: {adj_str}")
                print(f"          ➡️ 제안: page-{best_adj_page:02d} ({best_adj:.0f}%)")
                issues.append((slug, step_idx, h4, page, best_adj_page, score, best_adj))

    print("\n" + "=" * 90)
    if issues:
        print(f" 🚨 매핑 의심 {len(issues)}건")
        print("=" * 90)
        for slug, idx, h4, cur, sug, s1, s2 in issues:
            print(f"  {slug}: step {idx} '{h4[:40]}'  page-{cur:02d}({s1:.0f}%) → page-{sug:02d}({s2:.0f}%)")
    else:
        print(" ✓ 모든 매핑이 적절합니다.")
    print("=" * 90)


if __name__ == "__main__":
    main()
