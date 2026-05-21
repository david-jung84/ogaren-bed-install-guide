# 주간 자동 검증 — Claude 실행 절차서

이 문서는 **Claude의 scheduled task가 매주 실행될 때 따라야 할 절차**입니다.

## 트리거

- **주기**: 매주 월요일 09:00 KST
- **타겟 폴더**: `https://drive.google.com/drive/u/1/folders/1YSGhzk1HySn2T-f8LfWMp4lwayj0ajZa`
  (folder_id: `1YSGhzk1HySn2T-f8LfWMp4lwayj0ajZa`)
- **작업 위치**: `C:\Users\USER\Desktop\오가렌_DX\침대_설치가이드\`

## 절차

### 1. Drive 폴더 스캔

Google Drive MCP로 다음 폴더와 모든 하위 폴더를 재귀 스캔:

```
parentId = '1YSGhzk1HySn2T-f8LfWMp4lwayj0ajZa'
```

하위 폴더 (재귀 필요):
- 프레임 / 매트리스
- 그 아래 누어_1인 가구 / 슬립퍼_패브릭 / 슬립퍼_기성품 / 토들즈_유아동 / 책장&교구장
- 그 아래 룬드, 룬드빅, 디어, 하디, 모리 등 개별 제품 폴더

각 파일에서 추출:
- `id` (Google Drive file ID)
- `title`
- `mimeType`
- `modifiedTime`
- 부모 폴더 이름

### 2. scan_result.json 작성

```json
{
  "scanned_at": "2026-MM-DDTHH:MM:SS+09:00",
  "files": [
    {"id": "...", "title": "...", "mimeType": "...",
     "modifiedTime": "...", "parentTitle": "..."},
    ...
  ]
}
```

저장 위치: `C:\Users\USER\Desktop\오가렌_DX\침대_설치가이드\scan_result.json`

### 3. 변경 감지

```bash
cd "C:\Users\USER\Desktop\오가렌_DX\침대_설치가이드"
python _weekly_check.py --scan scan_result.json
```

결과:
- `_change_report.md` 생성 — 사람이 읽을 변경 보고서
- exit code 0 = 변경 없음 / 1 = 변경 있음

### 4. 변경 사항 처리

`_change_report.md`를 읽고 카테고리별로 처리:

#### 🔄 수정됨 (modified) — 자동 처리

기존 file_id 그대로지만 `modifiedTime`이 바뀐 경우:

1. 해당 PDF를 Drive MCP로 다시 다운로드
2. `_convert_pdfs.py` 로직으로 페이지별 JPG 재생성 → `assets/img/steps/<slug>/`
3. `_inject_step_images.py`로 HTML 재삽입
4. `python _weekly_check.py --scan scan_result.json --apply` 로 inventory 갱신

#### 🆕 새로 추가됨 (added) — 사람 검토 필요

inventory에 없는 새 PDF가 발견된 경우:

1. **자동으로 하지 말 것** — 사람이 다음을 결정해야 함:
   - 새 제품인지 vs 기존 제품의 새 버전인지
   - 가이드 슬러그 / 제목 / 시리즈 카테고리
   - 어떤 단계 텍스트를 쓸지

2. 대신 GitHub Issue를 만들거나 보고서에 명확히 적어 사용자에게 알림:
   ```
   📨 사용자 알림:
   "새 제품 PDF가 감지되었습니다 — 검토 후 가이드 추가 여부 결정 필요"
   - 제목: ...
   - 폴더: ...
   ```

#### 🗑️ 단종됨 (removed) — 사람 검토 필요

inventory에 있던 file_id가 Drive에 없는 경우:

1. **즉시 삭제하지 말 것** — 다른 폴더로 이동했을 수도, 일시 오류일 수도 있음
2. 첫 감지 시: 보고서에 기록만 하고 **2주 연속 감지될 때 archive 처리**
3. archive 처리 시:
   - `index.html`에서 카드 제거 (또는 "단종" 배지 추가)
   - `guides/<slug>.html`은 보존 (URL 영구성 유지)
   - inventory의 해당 항목에 `"archived": true` 추가

### 5. Git commit + push

```bash
git add -A
git commit -m "chore: 주간 검증 [YYYY-MM-DD] — 수정 N건 / 신규 N건 / 단종 N건

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
git push
```

GitHub Pages가 자동으로 재배포 → 사용자에게 별도 알림 불필요.

### 6. 사용자에게 보고

변경이 있었던 경우, 다음 형식으로 사용자에게 메시지:

```
주간 검증 [YYYY-MM-DD] 완료.

🔄 자동 처리: N건 (이미지 재변환 + push 완료)
🆕 새 제품 검토 필요: N건
🗑️ 단종 검토 필요: N건

상세 보고서: _change_report.md
```

변경 없는 경우:

```
주간 검증 [YYYY-MM-DD] 완료. 변경 없음.
```

## 위험 가드레일

- **자동으로 카드/페이지를 삭제하지 말 것** — 항상 사람 검토 후
- **새 제품을 빈 가이드로 자동 추가하지 말 것** — 내용 없는 가이드가 사이트에 노출되면 안 됨
- **git push는 변경이 있을 때만**
- **PDF 다운로드 실패 시 inventory를 변경하지 말 것** — 다음 주 재시도

## 수동 실행 (테스트)

스케줄 없이 수동으로 검증을 돌리려면:

1. Google Drive를 직접 보면서 scan_result.json을 수동 작성, 또는
2. Claude에게 `@_WEEKLY_CHECK.md 절차로 지금 한번 검증해 줘` 라고 요청
