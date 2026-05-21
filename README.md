# 침대 설치가이드 v1.0

오가렌 그룹(슬립퍼·누어·토들즈)의 침대·매트리스·교구장 설치 가이드를
**통일된 디자인**으로 재구성한 정적 HTML 사이트.

## 시작하기

```
침대_설치가이드/index.html
```

위 파일을 더블클릭하면 메인 허브가 열립니다. 인터넷 연결 시 Pretendard 폰트가
자동으로 로드됩니다 (오프라인이면 시스템 폰트로 대체).

## 구조

```
침대_설치가이드/
├── index.html                  ← 메인 허브 (4개 카테고리 · 검색 · 카드 그리드)
├── assets/
│   └── style.css               ← 공통 디자인 시스템 (Pretendard · 따뜻한 화이트 톤)
└── guides/                     ← 19종 제품별 가이드
    ├── signature-mattress.html (매트리스)
    ├── lundvik.html            (누어 · 룬드빅 - 가장 복잡)
    ├── lundvik-low.html
    ├── lundvik-sliding.html
    ├── lund.html
    ├── storage-bed.html        (레트/코지/플라/포포 패키징표)
    ├── imported-bed.html       (데이/리케/루체)
    ├── robin.html              (누어·슬립퍼 공용)
    ├── hush.html               (슬립퍼 허쉬)
    ├── hadi.html
    ├── dear.html
    ├── teen.html               (허먼밀러)
    ├── curve.html              (패브릭)
    ├── mori-daybed.html        (토들즈 - 유아 안전)
    ├── mori-family.html
    ├── buddy-daybed.html       (4종 변형)
    ├── buddy-babyjang.html     (벽 고정 필수)
    ├── buddy-gyogu.html        (6종 책장·교구장)
    └── lund-library.html       (6종 형태)
```

## 디자인 컨셉

- **컬러**: 따뜻한 화이트 베이지 톤 (#FAF8F5 / #C9A88B 액센트)
- **타이포**: Pretendard (한글 가독성 최우선) + JetBrains Mono (부품 수량)
- **컴포넌트**:
  - 큰 숫자 단계 카드 (counter-reset 기반)
  - 4단계 콜아웃 (danger / warn / info / tip)
  - 부품 테이블 (수량은 모노스페이스)
  - 부품 칩 (chip)
  - 인수 체크리스트
- **모바일 반응형 + 인쇄 친화 (CSS print rules)**
- **메인 허브 검색** — 제품명/시리즈 즉시 필터

## 원본 PDF 링크

각 가이드 상단에 **📄 원본 PDF** 버튼이 있어 Google Drive의 원본을 새 탭으로 엽니다.
시각적 도면이 필요한 경우 원본을 참조할 수 있습니다.

## 확장 가이드

새 제품 추가 시:

1. `guides/<product-slug>.html`을 만들고 기존 페이지(예: `mori-daybed.html`)를 복사·수정
2. `index.html`의 해당 카테고리 섹션에 `<a class="card">` 추가
3. 카드의 `data-search` 속성에 검색 키워드 입력

## 알려진 한계

- PDF의 시각 도면은 텍스트로 재구성된 부분이 많습니다. 정확한 부품 모양·위치는 원본 PDF의 도면을 참조하세요.
- 영상은 Google Drive 링크로만 연결 (다운로드 불가, 권한 필요).
- 모든 컨텐츠는 원본 PDF의 텍스트를 기반으로 재구성되었습니다.

## 빌드 정보

- 생성일: 2026-05-21
- 작성자: 정지훈 (DX팀)
- 원본 출처: Google Drive `오가렌 OS1/설치가이드/` 폴더
- 라이센스: 사내용 (오가렌 그룹)
