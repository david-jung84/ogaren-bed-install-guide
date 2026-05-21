@echo off
chcp 65001 > nul
echo.
echo ========================================
echo  오가렌 설치가이드 - GitHub Pages 배포
echo ========================================
echo.
echo 사전 준비: github.com/new 에서 빈 repo 생성
echo   - Owner       : david-jung84
echo   - Repo name   : ogaren-bed-install-guide
echo   - Visibility  : Public
echo   - 다른 옵션은 모두 비활성 (README/gitignore/license 체크 안함)
echo.
echo Enter 키를 누르면 GitHub로 push를 시작합니다...
pause > nul
echo.
echo [1/3] GitHub로 push 중...
git push -u origin main
if errorlevel 1 (
    echo.
    echo 푸시 실패. github.com에서 repo가 생성되었는지 확인하세요.
    pause
    exit /b 1
)
echo.
echo [2/3] GitHub Pages 활성화 안내
echo   브라우저에서 아래 URL 열기:
echo   https://github.com/david-jung84/ogaren-bed-install-guide/settings/pages
echo   - Source: Deploy from a branch
echo   - Branch: main / (root)
echo   - Save 클릭
echo.
echo Enter 키를 누르면 Settings 페이지를 열어드립니다...
pause > nul
start "" "https://github.com/david-jung84/ogaren-bed-install-guide/settings/pages"
echo.
echo [3/3] 약 1~2분 후 아래 URL이 활성화됩니다:
echo.
echo   https://david-jung84.github.io/ogaren-bed-install-guide/
echo.
echo 완료! 이 URL을 누구에게나 공유하시면 됩니다.
echo.
pause
