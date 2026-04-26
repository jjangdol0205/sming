import os
import time
import re
from dotenv import load_dotenv
import google.generativeai as genai
from playwright.sync_api import sync_playwright

# ---------------------------------------------------------
# 환경 변수 및 설정
# ---------------------------------------------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ★ 여기에 본인의 유튜브 채널 핸들(예: @goldenvoice94)을 입력하세요! ★
YOUTUBE_HANDLE = "@여기에_유튜브_핸들을_입력하세요" 
SITE_URL = "https://paradise-hero.com"

# ---------------------------------------------------------
# 1. AI 멘트 생성 함수
# ---------------------------------------------------------
def generate_community_post():
    if not GEMINI_API_KEY:
        print("GEMINI_API_KEY가 없습니다. .env 파일을 확인해주세요.")
        return None

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    당신은 가수 황영웅님을 열렬히 응원하는 5070 시니어 팬덤의 리더 '김쌤'입니다.
    오늘 유튜브 커뮤니티 게시판에 올릴 짧고 감동적인 응원 멘트를 작성해주세요.
    
    [조건]
    1. 황영웅님에 대한 응원, 날씨나 계절에 맞는 따뜻한 아침 인사, 건강 당부 등을 포함할 것.
    2. 글 마지막에는 반드시 아래 문구와 링크를 자연스럽게 포함할 것:
       "👇 오늘의 필수 스밍/투표 미션 및 쿠팡 특가 보러가기 👇"
       "{SITE_URL}"
    3. 길이는 3~5문장 정도로 너무 길지 않게 작성.
    4. 친근하고 예의 바른 '해요체/합쇼체' 사용. 이모티콘(🎵, 💚, ☕ 등) 적절히 사용.
    """
    
    print("AI 멘트 생성 중...")
    response = model.generate_content(prompt)
    post_text = response.text.strip()
    return post_text

# ---------------------------------------------------------
# 2. 플레이라이트(Playwright) 자동 포스팅 함수
# ---------------------------------------------------------
def post_to_youtube_community(post_text):
    # 크롬 사용자 데이터(쿠키)를 저장할 로컬 폴더
    user_data_dir = os.path.join(os.getcwd(), "youtube_profile")
    
    print("브라우저를 시작합니다...")
    with sync_playwright() as p:
        # headless=False 로 하면 화면이 보임. (처음 로그인할 때는 보여야 함)
        # 평소 스케줄러로 돌릴 때는 headless=True 로 바꿔도 되지만, 유튜브는 창을 띄우는 것이 안전함.
        browser = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            channel="chrome", # 시스템에 설치된 실제 크롬 사용
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        page = browser.new_page()
        
        # 1. 유튜브 메인 접속 (로그인 확인)
        page.goto("https://www.youtube.com")
        time.sleep(3)
        
        # 로그인 버튼이 있는지 확인
        login_button = page.locator("a[href^='https://accounts.google.com/ServiceLogin']")
        if login_button.count() > 0:
            print("==================================================")
            print("🚨 로그인이 필요합니다!")
            print("브라우저 창에서 직접 유튜브에 로그인해주세요.")
            print("로그인이 완료되면 이 창에서 엔터를 누르세요...")
            print("==================================================")
            input("로그인 완료 후 엔터 누르기: ")
        
        # 2. 내 채널 커뮤니티 탭으로 이동
        community_url = f"https://www.youtube.com/{YOUTUBE_HANDLE}/community"
        print(f"커뮤니티 탭으로 이동 중: {community_url}")
        page.goto(community_url)
        time.sleep(5)
        
        try:
            # 3. 글 작성 입력창 클릭
            # 유튜브 UI 구조에 따라 선택자(Selector)가 다를 수 있음
            input_box = page.locator("#placeholder-area")
            input_box.click()
            time.sleep(1)
            
            # 실제 텍스트가 들어가는 에디터 요소
            editor = page.locator("#contenteditable-root").nth(0)
            editor.fill(post_text)
            print("멘트를 입력했습니다.")
            time.sleep(2)
            
            # 4. 게시 버튼 클릭
            submit_button = page.locator("ytd-button-renderer#submit-button")
            submit_button.click()
            print("✅ 게시글 등록 버튼을 클릭했습니다!")
            time.sleep(5) # 등록될 때까지 대기
            
        except Exception as e:
            print("게시 과정에서 오류가 발생했습니다. 핸들이 정확한지, 커뮤니티 탭이 활성화되어 있는지 확인하세요.")
            print(e)
            # 오류 확인을 위해 30초 대기
            time.sleep(30)
            
        print("브라우저를 종료합니다.")
        browser.close()

if __name__ == "__main__":
    if YOUTUBE_HANDLE == "@여기에_유튜브_핸들을_입력하세요":
        print("🚨 스크립트 상단의 YOUTUBE_HANDLE 값을 본인의 유튜브 핸들로 변경해주세요!")
    else:
        text = generate_community_post()
        if text:
            print("\n--- 오늘 등록할 멘트 ---")
            print(text)
            print("------------------------\n")
            post_to_youtube_community(text)
