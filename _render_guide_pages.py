#!/usr/bin/env python3
"""가이드 PDF → 단계 이미지 렌더러.

전체 페이지(page-NN.jpg, 여백 크롭)를 만들고, 좌/우 2단 레이아웃 페이지는
반쪽(page-NN-L.jpg / page-NN-R.jpg)을 추가로 생성한다. 벡터 원본에서 직접
렌더하므로 크롭·확대에 화질 손실이 없다.

사용:
  python _render_guide_pages.py <pdf> <slug> [--prefix assembly-] [--no-split]
  → assets/img/steps/<slug>/<prefix>page-NN(.jpg|-L.jpg|-R.jpg)
"""
import argparse
import glob
import os

import pymupdf
from PIL import Image

ZOOM_DETECT = 1.8   # 레이아웃 분석용 (기존 이미지와 동일 스케일 → 임계값 재사용)
ZOOM_FULL = 2.4     # 전체 페이지 출력
ZOOM_HALF = 3.0     # 반쪽 출력
QUALITY = 82
GAMMA = 1.35        # 연회색 선·라벨을 어둡게 (흰 배경은 유지)
PAD_PT = 10
INK = 200

_LUT = [round(255 * (v / 255) ** GAMMA) for v in range(256)] * 3


def content_bbox(gray, box, ink=235):
    region = gray.crop(box).point(lambda v: 255 if v < ink else 0)
    bb = region.getbbox()
    if not bb:
        return None
    return (bb[0] + box[0], bb[1] + box[1], bb[2] + box[0], bb[3] + box[1])


def find_split(gray):
    """본문 밴드에서 중앙에 가장 가까운 '내용 없는 열 구간'(구분선 포함 가능)을 찾아
    (왼쪽 영역 끝 x, 오른쪽 영역 시작 x)를 돌려준다. 2단이 아니면 None."""
    W, H = gray.size
    y0, y1 = int(H * 0.17), int(H * 0.93)
    px = gray.load()
    rows = range(y0, y1, 3)
    n_rows = len(rows)

    def kind(x):
        ink = sum(1 for y in rows if px[x, y] < INK)
        if ink <= 2:
            return "E"          # empty
        if ink > 0.3 * n_rows:
            return "L"          # 세로 구분선
        return "C"              # content

    xs = range(int(W * 0.30), int(W * 0.70))
    kinds = {x: kind(x) for x in xs}
    runs, start = [], None
    for x in xs:
        if kinds[x] != "C":
            start = x if start is None else start
        elif start is not None:
            runs.append((start, x - 1))
            start = None
    if start is not None:
        runs.append((start, xs[-1]))
    # 실제 단 사이 여백은 충분히 넓다 (점선 사이 1~5px 틈은 제외)
    runs = [r for r in runs if r[1] - r[0] + 1 >= 12 and any(kinds[x] == "E" for x in range(r[0], r[1] + 1))]
    if not runs:
        return None
    lx, rx = min(runs, key=lambda r: abs((r[0] + r[1]) / 2 - W / 2))

    def density(xa, xb):
        return sum(1 for y in range(y0, y1, 6) for x in range(xa, xb, 6) if px[x, y] < INK)

    if density(int(W * 0.08), lx) <= 150 or density(rx + 1, int(W * 0.92)) <= 150:
        return None

    # 틈을 가로지르는 선 검사: 점선(리더)이 지나가면 목차형 페이지 → 분할 금지.
    # 박스 테두리 같은 실선은 잘려도 무방하므로 허용.
    for y in range(y0, y1, 2):
        left = any(px[x, y] < INK for x in range(max(0, lx - 40), lx))
        right = any(px[x, y] < INK for x in range(rx + 1, min(W, rx + 41)))
        if not (left and right):
            continue
        cols = [px[x, y] < INK for x in range(lx, rx + 1)]
        coverage = sum(cols) / len(cols)
        # <15%는 글자 안티앨리어싱 흘러넘침, ≥80%는 실선 → 둘 다 무시
        if 0.15 <= coverage < 0.8:
            return None
    return lx, rx + 1


def trim_footer(gray, box):
    """영역 하단에 고립된 작은 덩어리(페이지 번호 등)가 있으면 잘라낸다."""
    W, H = gray.size
    x0, y0, x1, y1 = box
    px = gray.load()
    inked = [any(px[x, y] < INK for x in range(x0, x1, 2)) for y in range(y0, y1)]
    y = len(inked) - 1
    while y >= 0 and not inked[y]:
        y -= 1
    end = y
    while y >= 0 and inked[y]:
        y -= 1
    blob_top = y + 1
    g = y
    while g >= 0 and not inked[g]:
        g -= 1
    if g < 0:
        return box
    gap, blob_h = y - g, end - blob_top + 1
    if blob_h < 0.05 * H and gap > 0.03 * H:
        bb = content_bbox(gray, (x0, y0 + blob_top, x1, y0 + end + 1))
        if bb and (bb[2] - bb[0]) < 0.12 * W:
            return (x0, y0, x1, y0 + g + 1)
    return box


def to_rect(box, zoom, page, pad=PAD_PT):
    r = pymupdf.Rect(box[0] / zoom - pad, box[1] / zoom - pad, box[2] / zoom + pad, box[3] / zoom + pad)
    return r & page.rect


def render(page, rect, zoom, path):
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), clip=rect, colorspace=pymupdf.csRGB)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples).point(_LUT)
    img.save(path, quality=QUALITY, optimize=True, progressive=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("slug")
    ap.add_argument("--prefix", default="")
    ap.add_argument("--no-split", action="store_true")
    a = ap.parse_args()

    out = os.path.join("assets", "img", "steps", a.slug)
    os.makedirs(out, exist_ok=True)
    for f in glob.glob(os.path.join(out, f"{a.prefix}page-*.jpg")):
        os.remove(f)

    doc = pymupdf.open(a.pdf)
    split_pages = []
    for i, page in enumerate(doc, 1):
        g = page.get_pixmap(matrix=pymupdf.Matrix(ZOOM_DETECT, ZOOM_DETECT), colorspace=pymupdf.csGRAY)
        gray = Image.frombytes("L", (g.width, g.height), g.samples)
        W, H = gray.size
        base = os.path.join(out, f"{a.prefix}page-{i:02d}")

        full = content_bbox(gray, (0, 0, W, H)) or (0, 0, W, H)
        render(page, to_rect(full, ZOOM_DETECT, page), ZOOM_FULL, base + ".jpg")

        split = None if a.no_split else find_split(gray)
        if split:
            lx, rx = split
            y0, y1 = int(H * 0.15), int(H * 0.95)
            halves = []
            for box in ((0, y0, lx, y1), (rx, y0, W, y1)):
                bb = content_bbox(gray, box)
                if bb:
                    bb = content_bbox(gray, trim_footer(gray, bb))
                halves.append(bb)
            L, R = halves
            if L and R and (L[2] - L[0]) > W * 0.2 and (R[2] - R[0]) > W * 0.2:
                render(page, to_rect(L, ZOOM_DETECT, page), ZOOM_HALF, base + "-L.jpg")
                render(page, to_rect(R, ZOOM_DETECT, page), ZOOM_HALF, base + "-R.jpg")
                split_pages.append(i)
    print(f"{a.slug}{' ' + a.prefix if a.prefix else ''}: {len(doc)}pp, split {len(split_pages)} → {split_pages}")


if __name__ == "__main__":
    main()
