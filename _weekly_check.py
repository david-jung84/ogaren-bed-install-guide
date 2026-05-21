"""
주간 자동 검증 헬퍼.

이 스크립트는 직접 Google Drive에 접근하지 않습니다 — Claude가 매주 schedule된
시점에 Drive MCP로 폴더를 스캔한 후, scan_result.json을 만들어서 이 스크립트로
넘기는 흐름입니다.

사용법:
    python _weekly_check.py --scan scan_result.json

scan_result.json 포맷:
    {
      "scanned_at": "2026-05-28T09:00:00+09:00",
      "files": [
        {"id": "...", "title": "...", "modifiedTime": "...", "mimeType": "...",
         "parentTitle": "..."},
        ...
      ]
    }

출력:
    - _change_report.md (사람이 검토할 변경 보고서)
    - _inventory.json (자동 업데이트)
    - terminal에 요약 출력
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INV_PATH = ROOT / "_inventory.json"
REPORT_PATH = ROOT / "_change_report.md"


def load_inventory():
    return json.loads(INV_PATH.read_text(encoding="utf-8"))


def save_inventory(inv):
    INV_PATH.write_text(json.dumps(inv, ensure_ascii=False, indent=2), encoding="utf-8")


def slugify(title: str) -> str:
    """제품명에서 슬러그 추론. 한글 제품명은 영문 변환이 어려우니 보수적으로."""
    s = title.lower()
    s = re.sub(r"[^\w가-힣\-]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s[:60]


def is_installation_file(file):
    """설치/조립/부품도 관련 파일인지 휴리스틱 판단."""
    t = file.get("title", "").lower()
    keywords = ["조립도", "조립", "부품도", "설치", "주의사항", "조립영상", "설치영상"]
    return any(k in t for k in keywords)


def is_pdf(file):
    return file.get("mimeType") == "application/pdf"


def find_match(file, tracked):
    """기존 inventory에서 같은 file_id를 가진 항목 찾기."""
    fid = file.get("id")
    for slug, entry in tracked.items():
        if entry.get("drive_file_id") == fid:
            return slug, entry
    return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", required=True, help="scan_result.json from Drive MCP scan")
    ap.add_argument("--apply", action="store_true",
                    help="변경 사항을 inventory.json에 즉시 반영")
    args = ap.parse_args()

    scan = json.loads(Path(args.scan).read_text(encoding="utf-8"))
    inv = load_inventory()
    tracked = inv["tracked"]
    scanned_at = scan.get("scanned_at", datetime.now().isoformat(timespec="seconds"))

    # 분류
    pdfs_in_drive = {f["id"]: f for f in scan["files"] if is_pdf(f)}
    all_files_by_id = {f["id"]: f for f in scan["files"]}

    added = []        # Drive에 새로 추가된 PDF (inventory에 없음)
    modified = []     # 같은 file_id지만 modifiedTime 변경 → 재변환 필요
    removed = []      # inventory에 있지만 Drive에 없음 (단종)
    unchanged = []    # 동일 — 그대로 두기

    # 1) 새/변경 감지
    seen_inv_ids = set()
    for fid, file in pdfs_in_drive.items():
        slug, entry = find_match(file, tracked)
        if slug is None:
            # inventory에 없음 → 새 파일 후보
            if is_installation_file(file):
                added.append(file)
        else:
            seen_inv_ids.add(fid)
            entry_mt = entry.get("last_modified")
            drive_mt = file.get("modifiedTime")
            if entry_mt != drive_mt:
                modified.append({
                    "slug": slug, "file": file,
                    "old_modified": entry_mt, "new_modified": drive_mt
                })
            else:
                unchanged.append(slug)

    # 2) 단종 감지 — inventory에 있는데 Drive에 없음
    for slug, entry in tracked.items():
        fid = entry.get("drive_file_id")
        if not fid:
            continue
        if fid not in all_files_by_id and fid not in seen_inv_ids:
            removed.append({"slug": slug, "entry": entry})

    # 3) 보고서 작성
    lines = [
        f"# 침대 설치가이드 — 주간 변경 보고서",
        f"",
        f"- **검증 일시**: {scanned_at}",
        f"- **이전 검증**: {inv['_meta'].get('last_check', '없음')}",
        f"- **추적 중**: {len(tracked)}개 가이드",
        f"",
        f"## 요약",
        f"",
        f"| 구분 | 갯수 |",
        f"|---|---|",
        f"| 🆕 새로 추가된 PDF | **{len(added)}** |",
        f"| 🔄 수정됨 (재변환 필요) | **{len(modified)}** |",
        f"| 🗑️ 단종 (Drive에서 사라짐) | **{len(removed)}** |",
        f"| ✓ 변경 없음 | {len(unchanged)} |",
        f"",
    ]

    if added:
        lines += ["## 🆕 새로 추가된 PDF", ""]
        for f in added:
            lines += [
                f"- **{f['title']}**",
                f"  - file_id: `{f['id']}`",
                f"  - modified: {f.get('modifiedTime', 'n/a')}",
                f"  - parent: {f.get('parentTitle', 'unknown')}",
                f"  - **액션**: 가이드 페이지 신규 생성 필요",
                f"  - 제안 슬러그: `{slugify(f['title'])}`",
                "",
            ]

    if modified:
        lines += ["## 🔄 수정됨 — 이미지 재변환 필요", ""]
        for m in modified:
            lines += [
                f"- **{m['slug']}** ({m['file']['title']})",
                f"  - 이전: {m['old_modified']}",
                f"  - 현재: {m['new_modified']}",
                f"  - **액션**: PDF 재다운로드 + 페이지 이미지 재생성",
                "",
            ]

    if removed:
        lines += ["## 🗑️ Drive에서 사라진 파일 (단종 가능성)", ""]
        for r in removed:
            lines += [
                f"- **{r['slug']}** ({r['entry'].get('drive_title')})",
                f"  - file_id: `{r['entry'].get('drive_file_id')}`",
                f"  - **액션**: 가이드 페이지 archive/제거 검토 — 다른 폴더로 이동했을 수도 있음",
                "",
            ]

    if not (added or modified or removed):
        lines += ["## ✓ 변경 없음", "", "Drive 폴더가 이전 검증 이후 변경되지 않았습니다."]

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n📄 보고서: {REPORT_PATH.relative_to(ROOT)}")

    # 4) 자동 적용 (--apply)
    if args.apply and modified:
        for m in modified:
            tracked[m["slug"]]["last_modified"] = m["new_modified"]
        inv["_meta"]["last_check"] = scanned_at[:10]
        save_inventory(inv)
        print(f"✓ inventory.json 업데이트 — last_modified {len(modified)}건")

    # 5) 터미널 요약
    print(f"\n=== 주간 검증 결과 ===")
    print(f"🆕 추가:    {len(added)}")
    print(f"🔄 수정:    {len(modified)}")
    print(f"🗑️ 단종:    {len(removed)}")
    print(f"✓ 동일:    {len(unchanged)}")
    print(f"📋 총 추적: {len(tracked)}")

    if added or modified or removed:
        print(f"\n⚠️ 처리 필요 변경 {len(added) + len(modified) + len(removed)}건")
        print(f"   보고서를 검토하세요 → {REPORT_PATH.name}")
        return 1  # exit code 1 = 변경 있음
    return 0


if __name__ == "__main__":
    sys.exit(main())
