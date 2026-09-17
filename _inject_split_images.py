#!/usr/bin/env python3
"""가이드 HTML 후처리.

1) step-img가 가리키는 페이지에 분할 이미지(-L/-R)가 있으면 두 장으로 교체
   (재실행 시 기존 pair를 먼저 원복하므로 멱등).
2) 인라인 라이트박스 마크업/스크립트를 공통 assets/lightbox.js로 교체.

사용: python _inject_split_images.py [guides/*.html]
"""
import glob
import os
import re
import sys

PAIR = re.compile(
    r'<div class="step-img-pair"><img class="step-img" src="(\.\./assets/img/steps/[\w-]+/[\w-]+)-L\.jpg" '
    r'alt="([^"]*) ①" loading="lazy">.*?</div>',
    re.S,
)
STEP_IMG = re.compile(
    r'<img class="step-img" src="\.\./assets/img/steps/([\w-]+)/([\w-]+)\.jpg" alt="([^"]*)" loading="lazy">'
)
OLD_LIGHTBOX = re.compile(r'<div class="lightbox" id="lightbox" onclick=.*?</div>', re.S)
OLD_SCRIPT = re.compile(r'<script>\s*document\.querySelectorAll\("\.step-img, \.ref-grid figure img"\).*?</script>', re.S)

NEW_LIGHTBOX = (
    '<div class="lightbox" id="lightbox" role="dialog" aria-label="도면 확대">'
    '<button class="lightbox-close" type="button" aria-label="닫기">×</button>'
    '<div class="lightbox-stage"><img id="lightbox-img" src="" alt="" draggable="false"></div>'
    '<div class="lightbox-hint">두 번 탭 · 핀치로 확대 &nbsp;|&nbsp; 바깥 탭으로 닫기</div>'
    '</div>'
)
NEW_SCRIPT = '<script src="../assets/lightbox.js" defer></script>'


def pair_or_single(m):
    slug, name, alt = m.groups()
    if not os.path.exists(os.path.join("assets", "img", "steps", slug, f"{name}-L.jpg")):
        return m.group(0)
    src = f"../assets/img/steps/{slug}/{name}"
    return (
        '<div class="step-img-pair">'
        f'<img class="step-img" src="{src}-L.jpg" alt="{alt} ①" loading="lazy">'
        f'<img class="step-img" src="{src}-R.jpg" alt="{alt} ②" loading="lazy">'
        '</div>'
    )


def process(path):
    html = open(path, encoding="utf-8").read()
    orig = html
    html = PAIR.sub(lambda m: f'<img class="step-img" src="{m.group(1)}.jpg" alt="{m.group(2)}" loading="lazy">', html)
    html = STEP_IMG.sub(pair_or_single, html)
    html = OLD_LIGHTBOX.sub(NEW_LIGHTBOX, html)
    html = OLD_SCRIPT.sub(NEW_SCRIPT, html)
    if html != orig:
        open(path, "w", encoding="utf-8").write(html)
    pairs = len(PAIR.findall(html))
    print(f"{os.path.basename(path):24s} pairs={pairs:2d} lightbox={'js' if NEW_SCRIPT in html else '-'}")


if __name__ == "__main__":
    files = sys.argv[1:] or sorted(glob.glob("guides/*.html"))
    for f in files:
        process(f)
