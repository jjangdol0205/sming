@echo off
chcp 65001 >nul
echo 유튜브 자동 포스팅 스케줄러를 등록합니다...

echo.
echo [1/3] 파이썬 설치 확인 중...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [오류] 파이썬이 설치되어 있지 않거나 경로 설정이 안 되어 있습니다!
    echo Microsoft Store에서 Python을 설치한 뒤 다시 실행해 주세요.
    pause
    exit /b
)

echo.
echo [2/3] 필수 파이썬 라이브러리를 설치합니다...
pip install playwright google-generativeai python-dotenv
playwright install chromium

echo.
echo [3/3] 윈도우 스케줄러에 등록합니다. (매일 오전 8시, 오후 2시)
:: 기존 작업 삭제 (에러 무시)
schtasks /delete /tn "YouTube_Community_Bot_Morning" /f >nul 2>&1
schtasks /delete /tn "YouTube_Community_Bot_Afternoon" /f >nul 2>&1

:: 작업 생성 (d:\sming 폴더에서 실행되도록 지정)
schtasks /create /tn "YouTube_Community_Bot_Morning" /tr "cmd.exe /c cd /d d:\sming && python youtube_community_bot.py" /sc daily /st 08:00 /ru "%USERNAME%"
schtasks /create /tn "YouTube_Community_Bot_Afternoon" /tr "cmd.exe /c cd /d d:\sming && python youtube_community_bot.py" /sc daily /st 14:00 /ru "%USERNAME%"

echo.
echo =================================================================
echo 스케줄러 등록이 완료되었습니다! (매일 오전 8시, 오후 2시 자동 실행)
echo =================================================================
echo.
echo [매우 중요] 지금 바로 아래 명령어를 실행해서 브라우저가 뜨면
echo 유튜브에 로그인 한 번 해주세요! (이후부터는 알아서 로그인 됨)
echo.
echo 실행 명령어: python d:\sming\youtube_community_bot.py
echo.
pause
