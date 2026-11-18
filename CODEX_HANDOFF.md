# CODEX_HANDOFF.md

> **문서 기준일: 2026-09-10**
> 작성 근거: `ogaren-bed-install-guide` 리포 `main` 브랜치 최신 커밋 `a90d809` (2026-09-07) 실측.
> 대상: 이 프로젝트를 이어받는 개발 에이전트(Codex).

---

## 0. 먼저 읽을 것 — 이 문서의 범위와 한계

| 항목 | 상태 |
|---|---|
| 확인 가능 범위 | `C:\Users\USER\Desktop\오가렌_DX\침대_설치가이드\` 한 프로젝트 (= GitHub `david-jung84/ogaren-bed-install-guide`) |
| **확인 불가 범위** | `C:\Users\USER\Desktop\오가렌_DX\` 아래의 **다른 하위 프로젝트 전부** — 이 문서 작성 환경(Linux 컨테이너)에 클론되지 않음 |
| `AGENTS.md` | **리포 어디에도 존재하지 않음** (`find` 전체 검색 결과 0건) |
| `CLAUDE.md` | **리포 어디에도 존재하지 않음** (동일) |
| `.github/` | **없음** — GitHub Actions·CI·PR 템플릿·이슈 템플릿 모두 없음 |

즉, 이 프로젝트의 "에이전트 운영 규칙"은 `AGENTS.md`/`CLAUDE.md`가 아니라
`C:\Users\USER\Desktop\오가렌_DX\침대_설치가이드\_WEEKLY_CHECK.md` **한 파일에 들어 있습니다.**
Codex는 작업 시작 전 그 파일을 반드시 정독해야 합니다. 사실상 이 리포의 헌법입니다.

> **확인 필요**: `오가렌_DX` 상위 폴더에 MTS 대시보드 등 다른 프로젝트가 있다는 언급이
> `...\침대_설치가이드\DEPLOY.md`에 나오지만, 실물은 확인하지 못했습니다. 추측으로 적지 않았습니다.

---

## 1. 프로젝트 목적

### 해결하는 업무
오가렌 그룹(**슬립퍼 · 누어 · 토들즈**)의 침대 프레임·매트리스·교구장 **설치 가이드**는
원래 Google Drive에 흩어진 PDF/PPTX/XLSX 조립도였습니다.
현장 설치기사와 CS가 PDF를 내려받아 확대해 보는 방식이라 접근성과 통일성이 없었습니다.

이 프로젝트는 그 원본을 **하나의 정적 HTML 사이트**로 재구성해,
누구나 URL 하나로 모바일에서 열어 단계별로 조립할 수 있게 만듭니다.

- 배포 URL: `https://david-jung84.github.io/ogaren-bed-install-guide/`
- 근거: `C:\Users\USER\Desktop\오가렌_DX\침대_설치가이드\DEPLOY.md`

### 운영 중 기능 vs 실험용 기능

| 구분 | 내용 |
|---|---|
| **운영 중** | 정적 사이트 본체 (`index.html` + `guides\*.html` 19종 + `assets\`) |
| **운영 중** | 매주 월요일 09:00 KST Google Drive 원본 변경 감지 루틴 (`_WEEKLY_CHECK.md` 절차) |
| **운영 중** | 변경 감지 결과의 GitHub Issue 자동 생성 (현재 8건 열림) |
| **개발 중 / 미결** | 신규 제품 **블룸(bloom)** 가이드 — 감지만 되고 7주째 미착수 |
| **실험 / 비배포** | PR #9 `guides\_fun-bad-signature.html` (사내 유머 페이지, draft, `index.html` 미링크) |
| **보관 / 일회성** | `_convert_hybrid.py`, `_inspect_pdf_pages.py` (특정 시점 디버깅용 스크립트) |

---

## 2. 상위 폴더 지도

기준 루트: `C:\Users\USER\Desktop\오가렌_DX\침대_설치가이드\`

| 폴더 / 파일 | 역할 | 상태 |
|---|---|---|
| `index.html` | 메인 허브. 4개 카테고리 카드 그리드 + 클라이언트 검색 필터 | **운영 중** |
| `guides\` | 제품별 가이드 HTML 19개. URL 영구성 대상 | **운영 중** |
| `assets\style.css` | 공통 디자인 시스템 892줄. 모든 페이지가 이것만 참조 | **운영 중** |
| `assets\img\` | 제품 대표 썸네일 16장 | **운영 중** |
| `assets\img\steps\` | PDF 페이지를 JPG로 변환한 단계 도면. 16개 슬러그 폴더 · 총 298개 파일 · 26MB | **운영 중 (산출물)** |
| `assets\pdf\` | 원본 PDF 로컬 캐시 | **보관 / Git 제외** (`.gitignore`에 명시, 리포에 없음) |
| `_inventory.json` | Drive file_id ↔ 가이드 슬러그 매핑 원장. **이 프로젝트의 단일 진실 원천** | **운영 중** |
| `_weekly_check.py` | 주간 변경 감지 엔진 | **운영 중** |
| `_WEEKLY_CHECK.md` | 주간 루틴 절차서 + 가드레일. 사실상 AGENTS.md 역할 | **운영 중** |
| `scan_result.json` | Drive 스캔 결과 입력 파일 | **운영 중 (단, 현재 stale — 5장 참조)** |
| `_change_report.md` | 주간 검증 산출 보고서 | **산출물 (현재 stale)** |
| `_verify_mapping.py` | 단계 텍스트 ↔ PDF 페이지 매핑 정합성 검증 | **개발 중 (설정 미동기 — 6장 참조)** |
| `_convert_hybrid.py` | 하이브리드 제품 1회성 변환 스크립트 | **완료 / 보관** |
| `_inspect_pdf_pages.py` | PDF 페이지 텍스트 덤프 디버깅 도구 | **완료 / 보관** |
| `_deploy.bat` | 최초 GitHub Pages 배포 원클릭 스크립트 | **완료 (배포 끝남, 재실행 불필요)** |
| `DEPLOY.md` | 배포 3가지 옵션 설명서 | **보관 (참고용)** |
| `README.md` | 프로젝트 개요 | **보관 — 내용이 낡음, 5장 참조** |
| `.nojekyll` | GitHub Pages Jekyll 처리 비활성화 | **운영 중 (삭제 금지)** |

---

## 3. 핵심 실행 시스템

**빌드 시스템이 없습니다.** npm/webpack/번들러 전부 없음. 순수 정적 HTML입니다.

| 항목 | 내용 |
|---|---|
| 실행 진입 파일 | `C:\Users\USER\Desktop\오가렌_DX\침대_설치가이드\index.html` — 더블클릭하면 바로 열림 |
| 설정 파일 | `_inventory.json` (추적 원장), `.gitignore`, `.nojekyll` |
| 로컬 실행 | 파일 더블클릭. 서버 필요 시 `python -m http.server 8000` |
| 주간 검증 실행 | `python _weekly_check.py --scan scan_result.json` |
| 검증 + 원장 반영 | `python _weekly_check.py --scan scan_result.json --apply` |
| 매핑 정합성 테스트 | `python _verify_mapping.py` (**로컬 `assets\pdf\` 필요 — 리포에는 없음**) |
| 배포 | `git push origin main` → GitHub Pages 자동 재배포 (1~2분) |
| 재시작 개념 | 없음. 서버 프로세스가 존재하지 않음 |

### 외부 의존성

| 의존 대상 | 용도 | 비고 |
|---|---|---|
| **Google Drive** | 원본 조립도 PDF 보관소. 루트 folder_id는 `_inventory.json`의 `_meta.drive_root` | Drive MCP 커넥터로 접근 |
| **GitHub Pages** | 호스팅 | `main` 브랜치 `/` (root) |
| **cdn.jsdelivr.net** | Pretendard 웹폰트 | 오프라인 시 시스템 폰트로 자동 대체 |
| **PyMuPDF (`fitz`)** | PDF → JPG 변환 | 파이썬 스크립트가 import |
| **데이터베이스** | **없음** | |
| **채널톡 / 외부 발송 API** | **없음** — 코드·설정 어디에도 연동 흔적 없음 | 4장 참조 |

---

## 4. 주요 업무 흐름

```
[입력]  Google Drive 설치가이드 폴더 (재귀 스캔)
   │      ↳ 에이전트가 Drive MCP로 스캔 → scan_result.json 작성
   ▼
[감지]  python _weekly_check.py --scan scan_result.json
   │      ↳ _inventory.json의 drive_file_id / last_modified 와 대조
   │      ↳ 4분류: 🔄수정 · 🆕신규 · 🗑️단종 · ✓동일
   ▼
[저장]  _change_report.md 생성 (사람용 보고서)
   │      exit code 0 = 변경 없음 / 1 = 변경 있음
   ▼
[처리]  🔄수정 → 자동: PDF 재다운로드 → 페이지 JPG 재생성 → HTML 재삽입 → --apply
        🆕신규 → 자동 금지: GitHub Issue 생성 후 사람 판단 대기
        🗑️단종 → 자동 금지: 2주 연속 감지 시에만 archive 검토
   ▼
[발송]  git commit + push → GitHub Pages 자동 재배포
        ⚠️ 채널톡·메일·슬랙 등 외부 채널 발송 로직은 존재하지 않음.
           사용자 통지 수단은 (1) GitHub Issue (2) 세션 내 텍스트 보고 두 가지뿐.
```

### 오류 및 재시도 흐름
`_WEEKLY_CHECK.md` "위험 가드레일" 절에 명시된 규칙 그대로입니다.

- **PDF 다운로드 실패 시 `_inventory.json`을 변경하지 말 것** → 다음 주 자동 재시도
- **변경이 없으면 `git push`하지 말 것**
- 단종 의심은 1회 감지로 처리하지 않음 → 2주 연속일 때만 archive

> 자동 재시도 스케줄러나 백오프 로직 같은 **코드 레벨 재시도는 없습니다.**
> 재시도는 "다음 주 루틴이 다시 돈다"는 주 단위 자연 재시도가 전부입니다.

---

## 5. 현재 진행 상태 (2026-09-10 기준)

### 완료된 작업
- 가이드 19종 전량 게시. `index.html` 카드 19개 ↔ `guides\*.html` 19개 **완전 일치, 고아 파일 0**
- `_inventory.json` 추적 항목 19개 = 가이드 수와 일치
- 단계 도면 이미지 16개 슬러그 완비 (예: `odd` 48장, `lund-library` 40장, `buddy-gyogu` 28장)
- 주간 검증 루틴 2026-05-21 이후 매주 무중단 실행 (커밋 로그로 확인)
- GitHub Pages 배포 완료 · 정상 운영

### 미완료 작업

| # | 내용 | 근거 |
|---|---|---|
| 1 | **블룸(bloom) 가이드 미생성** — 2026-07-24 최초 감지 후 7주 방치 | Issue #4·5·6·8·10·11·12 |
| 2 | **동일 사안 Issue 7건 중복 생성** — 루틴이 기존 Issue 존재 여부를 확인하지 않음 | 위와 동일 |
| 3 | 모리 데이베드 구버전 처리 판단 미결 (2026-05-25 감지) | Issue #1 |
| 4 | Draft PR #2 (`weekly-check-2026-06-01`) 3개월 이상 방치 | 열린 PR 목록 |
| 5 | Draft PR #9 (사내 유머 페이지) 머지/폐기 판단 미결 | 열린 PR 목록 |

### 알려진 오류 / 불일치 — **Codex가 가장 먼저 볼 것**

| 증상 | 상세 | 위치 |
|---|---|---|
| **핵심 스크립트 2개가 리포에 없음** | `_convert_pdfs.py`, `_inject_step_images.py` 가 `.gitignore`에 등재되어 커밋되지 않음. 그런데 `_WEEKLY_CHECK.md` 4단계가 이 둘을 호출하도록 지시함. **클린 클론에서는 주간 루틴의 자동 처리 단계를 재현할 수 없음** | `...\침대_설치가이드\.gitignore` 12~13행 |
| `README.md` 내용이 낡음 | 존재하지 않는 `storage-bed.html` `hadi.html` `teen.html`을 목록에 기재. 반대로 실제 존재하는 `deca-mattress` `hybrid-stable` `odd` 3종이 빠짐 | `...\침대_설치가이드\README.md` |
| `scan_result.json` 최신 아님 | 내부 `scanned_at`은 `2026-08-24`인데 `_inventory.json`의 `last_check`는 `2026-09-07`. 최근 2회 스캔 결과가 커밋되지 않음 | 두 파일 대조 |
| `_change_report.md` 낡음 | 2026-08-17자 보고서가 남아 있음 (3주 전) | 파일 헤더 |
| `_verify_mapping.py` 설정 미동기 | `CONFIG` 딕셔너리에 12개 슬러그만 등록. `deca-mattress` `hybrid-stable` `odd` 누락 → 최근 추가된 3종은 매핑 검증 사각지대 | `...\침대_설치가이드\_verify_mapping.py` |
| DX 인증 배지 누락 | 20개 페이지 중 18개에 `v1.3 · 2026-05-21` 배지. `deca-mattress.html`·`hybrid-stable.html` 2개만 없음 | `grep dx-cert-badge` 결과 |
| 배지 버전 고정 | 모든 배지가 `2026-05-21`로 고정. 내용이 갱신돼도 배지는 그대로 → 신뢰도 저하 | 동일 |

### 임시 구현
- `_convert_hybrid.py`는 `C:\Users\USER\.claude\projects\...\tool-results\toolu_xxx.txt` 라는
  **특정 세션의 캐시 파일 경로가 하드코딩**되어 있습니다. 재실행 불가. 참고용으로만 보세요.
- 모든 파이썬 스크립트가 `C:\Users\USER\Desktop\오가렌_DX\침대_설치가이드`를 절대경로로 하드코딩합니다
  (`_weekly_check.py`만 예외로 `Path(__file__).parent` 사용).

### 다음에 해야 할 작업 (우선순위)

| 순위 | 작업 | 이유 |
|---|---|---|
| **P0** | `_convert_pdfs.py` · `_inject_step_images.py` 를 `.gitignore`에서 제외하고 커밋 | 없으면 자동 파이프라인 전체가 재현 불가. 다른 리스크의 뿌리 |
| **P0** | 블룸 Issue 7건을 1건으로 정리 + 루틴에 "동일 file_id Issue 중복 방지" 추가 | 매주 쓰레기 Issue 증식 중 |
| **P1** | 블룸 가이드 생성 여부 결정 (사람 판단 필요) | 7주 미결. Issue #4에 따르면 원본에 공급사 연락처 등 내부 정보 포함 → 고객 공개 전 정제 필요 |
| **P1** | `README.md` 제품 목록을 실제 19종에 맞춰 갱신 | 신규 인수자가 가장 먼저 읽는 문서인데 틀림 |
| **P2** | `_verify_mapping.py` CONFIG에 3종 추가 | 검증 사각지대 해소 |
| **P2** | `deca-mattress` · `hybrid-stable` 에 DX 인증 배지 추가, 배지 버전 자동화 | 일관성 |
| **P2** | Draft PR #2 · #9 정리 | 리포 위생 |
| **P3** | Issue #1 (모리 데이베드 구버전) 종결 | 이미 `alternate_file_ids`로 회피 중이라 실害는 낮음 |

---

## 6. 중요한 설계 결정

### 왜 정적 HTML인가
설치기사가 현장에서 **모바일로 즉시 열어야 하는 문서**입니다.
로그인·빌드·런타임이 끼면 실패 지점이 늘어납니다.
그래서 프레임워크 없이 HTML + 단일 CSS로 갔고, 오프라인에서도 파일만 있으면 열립니다.
`index.html`의 검색도 서버 없이 순수 JS 필터 30여 줄입니다.

### 왜 `_inventory.json`이 중심인가
Drive의 파일명은 사람이 수시로 바꾸지만 **`file_id`는 불변**입니다.
따라서 추적 키를 파일명이 아닌 `drive_file_id`로 잡았습니다.
`alternate_file_ids` 필드는 "같은 제품의 다른 버전"을 한 슬러그에 묶어
루틴이 **신규 제품으로 오탐하지 않게** 하는 장치입니다
(예: `lund-library`의 진도 구버전 32p, `odd`의 부품도 별도 PDF).

### 변경하면 위험한 부분

| 대상 | 위험 |
|---|---|
| `guides\<slug>.html` 파일명 | **절대 변경 금지.** 현장 설치기사에게 URL이 배포되어 있음. 단종 제품도 페이지는 보존하는 게 이 리포의 원칙 |
| `_inventory.json`의 `drive_file_id` | 잘못 건드리면 루틴이 전 제품을 "단종 + 신규"로 오판 |
| `.nojekyll` 삭제 | GitHub Pages가 `_`로 시작하는 파일·폴더를 무시하게 됨 → 배포 깨짐 |
| `assets\style.css` 전역 토큰 | 20개 페이지가 이 한 파일만 참조. 변수 하나 바꾸면 전체 사이트에 즉시 반영 |
| `main` 브랜치 직접 push | Pages가 즉시 재배포됨. 검증 없는 push = 즉시 대외 노출 |

### 과거에 실패했던 접근 / 교훈
- **PDF 도면을 텍스트로만 재구성** → 부품 모양·위치 전달 실패. 이후 페이지 JPG를 단계마다 삽입하는 방식으로 전환했고, 각 페이지 상단에 원본 PDF 링크 버튼(총 34개)을 유지합니다.
- **단계 ↔ PDF 페이지 자동 매핑** → 오매핑 발생. `_verify_mapping.py`(키워드 겹침 점수 기반 의심 탐지)를 별도로 만들어 보정하고 있습니다. 완전 자동화는 포기하고 사람 검토를 남긴 상태입니다.
- **신규 제품 자동 생성** → 내용 없는 빈 가이드가 사이트에 노출될 위험 때문에 **명시적으로 금지**로 굳혔습니다 (`_WEEKLY_CHECK.md` 가드레일).

### 호환성 제약
- 파이썬 스크립트는 Windows 콘솔 인코딩 대응으로 `sys.stdout`을 UTF-8로 강제 래핑합니다. 제거하면 한글 출력이 깨집니다.
- PDF 변환은 PyMuPDF(`fitz`) 전제. 대용량 PDF는 `Matrix(1.5, 1.5)` / JPEG quality 80으로 낮춰 처리한 선례가 있습니다 (`_convert_hybrid.py`).
- 리포 용량이 이미 `.git` 23MB + `assets` 26MB입니다. 이미지 배율을 올리면 Pages 배포가 무거워집니다.

---

## 7. 핵심 파일 목록

모두 실제로 열어서 확인한 파일입니다. 추측한 항목은 별도 표기했습니다.

| 절대경로 | 역할 |
|---|---|
| `C:\Users\USER\Desktop\오가렌_DX\침대_설치가이드\_WEEKLY_CHECK.md` | **최우선 정독.** 주간 루틴 6단계 절차 + 자동화 금지 가드레일 |
| `C:\Users\USER\Desktop\오가렌_DX\침대_설치가이드\_inventory.json` | 슬러그 ↔ Drive file_id ↔ 최종수정일 원장. 19종 추적 |
| `C:\Users\USER\Desktop\오가렌_DX\침대_설치가이드\_weekly_check.py` | 변경 감지 엔진. `--apply`로 원장 갱신, exit code로 변경 유무 반환 |
| `C:\Users\USER\Desktop\오가렌_DX\침대_설치가이드\scan_result.json` | Drive 스캔 입력. 에이전트가 매주 새로 씀 (현재 2026-08-24자) |
| `C:\Users\USER\Desktop\오가렌_DX\침대_설치가이드\_change_report.md` | 검증 산출 보고서 (현재 2026-08-17자) |
| `C:\Users\USER\Desktop\오가렌_DX\침대_설치가이드\_verify_mapping.py` | 단계 텍스트와 PDF 페이지 매핑 정합성 점수화. CONFIG 12종만 등록 |
| `C:\Users\USER\Desktop\오가렌_DX\침대_설치가이드\_convert_hybrid.py` | 하이브리드 1회성 변환. 세션 캐시 경로 하드코딩 → 재실행 불가 |
| `C:\Users\USER\Desktop\오가렌_DX\침대_설치가이드\_inspect_pdf_pages.py` | PDF 페이지별 앞 90자 덤프. 매핑 디버깅용 |
| `C:\Users\USER\Desktop\오가렌_DX\침대_설치가이드\index.html` | 메인 허브. 카드 19개 + 검색 JS. 신규 제품 추가 시 카드 등록 지점 |
| `C:\Users\USER\Desktop\오가렌_DX\침대_설치가이드\assets\style.css` | 892줄 디자인 시스템. 전 페이지 공용 |
| `C:\Users\USER\Desktop\오가렌_DX\침대_설치가이드\guides\odd.html` | 가장 최근 작성된 가이드. **신규 가이드 작성 시 이 파일을 템플릿으로 복사할 것** |
| `C:\Users\USER\Desktop\오가렌_DX\침대_설치가이드\guides\lund-library.html` | 구버전/신버전 도면 병행 표기 사례. 설계변경 대응 참고용 |
| `C:\Users\USER\Desktop\오가렌_DX\침대_설치가이드\.gitignore` | `assets\pdf\`와 변환 스크립트 2개를 제외. **P0 이슈의 원인 파일** |
| `C:\Users\USER\Desktop\오가렌_DX\침대_설치가이드\.nojekyll` | 빈 파일. 삭제 금지 |
| `C:\Users\USER\Desktop\오가렌_DX\침대_설치가이드\DEPLOY.md` | 배포 옵션 3종. 이미 옵션 A로 배포 완료됨 |
| `C:\Users\USER\Desktop\오가렌_DX\침대_설치가이드\_deploy.bat` | 최초 배포용 배치. 재실행할 일 없음 |
| `C:\Users\USER\Desktop\오가렌_DX\침대_설치가이드\README.md` | 개요. **제품 목록이 실제와 불일치 — 갱신 대상** |

**존재하지 않지만 코드가 참조하는 파일 (재현 시 반드시 확보):**

| 절대경로 | 상태 |
|---|---|
| `C:\Users\USER\Desktop\오가렌_DX\침대_설치가이드\_convert_pdfs.py` | Git 제외. 로컬 PC에는 있을 것으로 **추측** — 확인 필요 |
| `C:\Users\USER\Desktop\오가렌_DX\침대_설치가이드\_inject_step_images.py` | 동일. Git 제외. **확인 필요** |
| `C:\Users\USER\Desktop\오가렌_DX\침대_설치가이드\assets\pdf\` | Git 제외. `_verify_mapping.py` 실행 전제 조건 |

---

## 8. 데이터와 보안

### 개인정보
- **리포 안에는 고객 개인정보가 없습니다.** 전 파일 스캔 결과 이름·연락처·주소·주문정보 등 미검출.
- 다만 Issue #4 기록에 따르면 **블룸 원본 PDF에 공급사 연락처와 내부 주의사항이 포함**되어 있습니다.
  → 블룸 가이드를 만들 때 **원본 PDF를 그대로 게시하면 안 됩니다.** 정제 후 게시.

### 비밀키 · 인증정보
- **리포 안에 API 키·토큰·비밀번호가 없습니다.** (`api_key|token|password|secret|Authorization` 전수 검색 결과 코드 오탐 2건 외 0건)
- 실제 인증은 두 군데 **외부**에 있습니다. 문서·코드에 절대 복사하지 마세요.
  1. **Google Drive 접근 권한** — 에이전트 세션의 Drive MCP 커넥터 인증
  2. **GitHub push 권한** — 로컬 Git credential / 세션 토큰

### 읽기 전용으로 다뤄야 하는 것

| 대상 | 이유 |
|---|---|
| **Google Drive 원본 폴더 전체** | 제품기획팀 소유. 이 프로젝트는 **읽기만** 합니다. 삭제·이동·덮어쓰기 금지 |
| `guides\*.html` 파일명 | URL 영구성. 리네임·삭제 금지 |
| 과거 주간 검증 커밋 이력 | 변경 추적의 근거 |

### 승인 없이 실행하면 안 되는 작업

1. **`git push origin main`** — Pages 즉시 재배포 = 대외 즉시 공개
2. **`index.html`에서 카드 제거 / `guides\*.html` 삭제** — `_WEEKLY_CHECK.md` 가드레일이 명시적으로 금지
3. **신규 제품 가이드 자동 생성** — 사람이 슬러그·제목·단계 텍스트를 정한 뒤에만
4. **`_inventory.json`에서 항목 삭제** — 2주 연속 단종 확인 전에는 금지
5. **`.gitignore`를 풀어 `assets\pdf\`를 커밋** — 리포 용량 폭증. P0 작업은 **파이썬 스크립트 2개만** 대상
6. **Drive 원본 파일 수정** — 어떤 경우에도 금지

---

## 9. 검증 상태

### 마지막으로 성공한 것
- **주간 검증 루틴**: 2026-09-07 성공. 결과 "수정 1 / 신규 1 / 단종 0".
  `odd` 조립도 modifiedTime 갱신(2026-07-06 → 2026-09-05) 및 이미지 재변환 완료, 내용 변경 없음 확인.
  블룸 신규 감지 → Issue #12 생성, 자동 처리 안 함 (가드레일 준수). 커밋 `a90d809`.
- **정적 무결성 (2026-09-10 본 문서 작성 중 직접 확인)**:
  `index.html` 링크 19개 ↔ `guides\` 파일 19개 완전 일치, 깨진 링크 0, 고아 파일 0.
- **주간 루틴 연속성**: 2026-05-21 이후 매주 월요일 커밋이 끊김 없이 존재.

### 확인하지 못한 것 (Codex가 검증해야 할 목록)

| 항목 | 사유 |
|---|---|
| `python _weekly_check.py` 실제 실행 | 이 환경에 파이썬 의존성·Drive 접근이 없어 미실행 |
| `python _verify_mapping.py` 실제 실행 | `assets\pdf\` 원본이 리포에 없어 실행 불가 |
| `_convert_pdfs.py` / `_inject_step_images.py` 동작 | 파일 자체가 리포에 없음 |
| 배포 URL 실제 접속 | 브라우저 검증 미수행 |
| 단계 이미지와 실제 조립 순서의 내용 정확성 | 도면 대조는 사람(제품기획/CS) 검토 영역 |
| `오가렌_DX` 상위 폴더의 다른 프로젝트 | 이 환경에 없음 |

### 운영 환경 vs 로컬 환경 차이

| | 로컬 (`C:\Users\USER\Desktop\오가렌_DX\침대_설치가이드\`) | 운영 (GitHub Pages) |
|---|---|---|
| `assets\pdf\` 원본 PDF | 있음 (추측 — 확인 필요) | 없음 (gitignore) |
| 변환 스크립트 2개 | 있음 (추측 — 확인 필요) | 없음 (gitignore) |
| 경로 기준 | Windows 절대경로 하드코딩 | 상대경로만 사용 |
| 폰트 | 오프라인 시 시스템 폰트 대체 | jsdelivr CDN에서 Pretendard 로드 |
| 배포 반영 | 즉시 | push 후 1~2분 |

### 기준 날짜
- 문서 작성일: **2026-09-10**
- 근거 커밋: `a90d809` (2026-09-07)
- 리포 상태: 열린 Issue 8건 / 열린 Draft PR 2건 (#2, #9) / 워킹트리 클린

---

## 10. Codex 시작 체크리스트

```
[ ] 1. _WEEKLY_CHECK.md 정독 — 이 리포의 유일한 에이전트 규칙서
[ ] 2. _inventory.json 구조 파악 — drive_file_id / alternate_file_ids 개념
[ ] 3. 로컬에 _convert_pdfs.py, _inject_step_images.py, assets\pdf\ 가 실재하는지 확인
       → 있으면 P0: gitignore에서 스크립트 2개 제외 후 커밋
       → 없으면 사용자에게 즉시 보고. 자동 파이프라인 복구가 최우선
[ ] 4. 블룸 Issue 7건(#4,5,6,8,10,11,12) 중복 정리 방침을 사용자와 합의
[ ] 5. 가이드 신규 작성 시 guides\odd.html 복사에서 시작
[ ] 6. main 직접 push 금지. 브랜치 → PR 경유
```

---

*이 문서는 리포 실측 기반으로 작성되었으며, 확인하지 못한 사항은 "추측" 또는 "확인 필요"로 표기했습니다.*
