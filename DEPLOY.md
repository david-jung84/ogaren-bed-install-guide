# 공개 링크로 배포하기

침대 설치가이드를 누구나 접근할 수 있는 URL로 호스팅하는 방법.

3가지 옵션이 있습니다 — 가장 위가 추천.

---

## 🥇 옵션 A: GitHub Pages (추천)

**최종 URL**: `https://david-jung84.github.io/ogaren-bed-install-guide/`
**소요 시간**: 약 3분
**비용**: 무료

이미 `david-jung84` 계정으로 MTS 대시보드를 운영 중이니 같은 흐름.

### 단계 1 — 빈 repo 만들기 (사용자 액션 30초)

브라우저에서 [github.com/new](https://github.com/new) 열고:
- **Owner**: `david-jung84`
- **Repository name**: `ogaren-bed-install-guide`
- **Visibility**: `Public`
- 나머지 옵션 (README, gitignore, license)은 **모두 체크 해제**
- `Create repository` 클릭

### 단계 2 — 자동 푸시 (더블클릭)

`_deploy.bat` 더블클릭하면 푸시 + Pages 설정 페이지까지 자동으로 열립니다.

또는 수동으로:
```bash
cd "C:\Users\USER\Desktop\오가렌_DX\침대_설치가이드"
git push -u origin main
```

### 단계 3 — Pages 활성화 (클릭 3번)

`https://github.com/david-jung84/ogaren-bed-install-guide/settings/pages`

- **Source**: `Deploy from a branch`
- **Branch**: `main` / `/ (root)`
- `Save` 클릭

1~2분 후 위 URL이 활성화됩니다.

---

## 🥈 옵션 B: Netlify Drop (가장 빠름, 계정 불필요)

**최종 URL**: `https://<랜덤이름>.netlify.app` (예: `silly-sunshine-1a2b.netlify.app`)
**소요 시간**: 30초
**비용**: 무료 (7일 후 만료 — 계정 가입 시 영구)

1. 브라우저에서 [app.netlify.com/drop](https://app.netlify.com/drop) 열기
2. `C:\Users\USER\Desktop\오가렌_DX\침대_설치가이드.zip` 파일을 드래그 (이미 준비됨)
3. URL 발급 즉시 완료

가입 (무료) 시 URL이 영구 보관되며, 도메인 변경 (예: `ogaren-bed-guide.netlify.app`)도 가능.

---

## 🥉 옵션 C: Cloudflare Pages

MTS와 같은 Cloudflare 인프라를 쓰고 싶을 때.

```bash
cd "C:\Users\USER\Desktop\오가렌_DX\침대_설치가이드"
npx wrangler login                         # 브라우저로 CF 로그인 (한 번만)
npx wrangler pages deploy . --project-name=ogaren-bed-guide
```

**최종 URL**: `https://ogaren-bed-guide.pages.dev`

---

## 추가 — 도메인 연결 (선택)

GitHub Pages / Cloudflare Pages 모두 `guide.ogaren.com` 같은 커스텀 도메인 연결 가능.

도메인이 있다면:
- GitHub: Settings → Pages → Custom domain 입력 + DNS CNAME 설정
- Cloudflare: 자동 (대시보드에서 도메인 연결)

---

## 비공개로 공유하고 싶다면

침대 설치가이드는 사내 자료지만 공개해도 큰 문제는 없습니다 (제품 정보 위주).
민감한 정보를 추가할 계획이라면:

- **GitHub Pages** → repo를 Private로 만들면 Pages도 자동 Private 처리 (단, 유료 Plan 필요)
- **Cloudflare Pages** → Access (무료 50명/월) 로 SSO 보호 가능
- **간단**: HTTP Basic Auth를 Cloudflare Workers로 앞단 보호

지금은 공개로 진행 → 필요 시 변경.
