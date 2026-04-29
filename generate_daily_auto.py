import google.generativeai as genai
import datetime
import os
import json
import subprocess
import time
import datetime
import urllib.request
import coupang_api
from urllib.error import HTTPError

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

BLOG_DIR = "blog"
BLOG_LIST = "blog_list.html"

TEMPLATE = """<!DOCTYPE html>
<html lang="ko">

<head>
    <!-- Google Tag Manager -->
    <script>(function (w, d, s, l, i) {{
            w[l] = w[l] || []; w[l].push({{
                'gtm.start':
                    new Date().getTime(), event: 'gtm.js'
            }}); var f = d.getElementsByTagName(s)[0],
                j = d.createElement(s), dl = l != 'dataLayer' ? '&l=' + l : ''; j.async = true; j.src =
                    'https://www.googletagmanager.com/gtm.js?id=' + i + dl; f.parentNode.insertBefore(j, f);
        }})(window, document, 'script', 'dataLayer', 'GTM-KF4LZQTB');</script>
    <!-- End Google Tag Manager -->

    <script type="text/javascript">
        (function (c, l, a, r, i, t, y) {{
            c[a] = c[a] || function () {{ (c[a].q = c[a].q || []).push(arguments) }};
            t = l.createElement(r); t.async = 1; t.src = "https://www.clarity.ms/tag/" + i;
            y = l.getElementsByTagName(r)[0]; y.parentNode.insertBefore(t, y);
        }})(window, document, "clarity", "script", "vm4cezh8lk");
    </script>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{
            word-break: keep-all;
            font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
        }}
    </style>
    <!-- 수익화: 쿠팡 파트너스 다이나믹 배너 적용됨 -->

    <!-- SEO Meta Tags will be added later -->
</head>

<body class="bg-[#FFFFF0] text-gray-900 leading-[1.8] text-[20px] md:text-[22px]">
    <!-- Google Tag Manager (noscript) -->
    <noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-KF4LZQTB" height="0" width="0"
            style="display:none;visibility:hidden"></iframe></noscript>
    <!-- End Google Tag Manager (noscript) -->

    <main class="max-w-2xl mx-auto p-5 md:p-8 bg-white shadow-xl min-h-screen flex flex-col">

        <h1 class="text-3xl md:text-4xl font-extrabold mb-8 text-[{title_color}] leading-tight mt-4">
            {title}
        </h1>

        <article class="flex-grow">
            {content}
        </article>

        <!-- 쿠팡 파트너스 다이나믹 배너 (강력한 후원 명분 추가) -->
        <section class="mt-12 mb-4 px-2 flex justify-center flex-col items-center">
            <div class="w-full bg-[#FFF3E0] border-2 border-[#FFB300] rounded-2xl p-4 mb-4 text-center shadow-md animate-pulse">
                <p class="text-lg font-extrabold text-[#D84315] mb-1">🎁 파라다이스 응원방 후원하기 (비용 0원)</p>
                <p class="text-sm font-bold text-gray-700 leading-snug">
                    팬님들! 평소 필요하신 <span class="text-[#00563F]">생수나 휴지를 아래 배너를 눌러서 쿠팡에서 구매해 주시면</span> 응원방 운영에 큰 힘이 됩니다! (팬님 추가 비용 없음)
                </p>
            </div>
            <script src="https://ads-partners.coupang.com/g.js"></script>
            <script>
                new PartnersCoupang.G({{"id":983781,"template":"carousel","trackingCode":"AF7865143","width":"680","height":"140","tsource":""}});
            </script>
            <!-- 오늘의 골드박스 특가 버튼 -->
            <a href="https://influencers.coupang.com/s/paradisehero" target="_blank"
                class="mt-5 w-full bg-gradient-to-r from-[#FF0000] to-[#FF5E00] text-white text-xl font-extrabold py-4 rounded-xl shadow-lg active:scale-95 transition-transform block text-center">
                ⏰ 놓치면 후회하는 쿠팡 오늘의 반값 특가
            </a>
            <p class="text-center text-[11px] font-bold text-gray-400 mt-3 break-keep">
                ※ 이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.
            </p>
        </section>

        <a href="../index.html"
            class="block w-full bg-[#00563F] text-white text-center font-extrabold py-5 rounded-2xl shadow-lg active:scale-95 transition-transform mt-8 text-2xl">
            🔙 시니어 꿀팁 포털 메인으로 돌아가기
        </a>

    </main>
</body>

</html>
"""

def get_color(cat):
    if cat == 'health': return '#00A862'
    if cat == 'economy': return '#D9381E'
    if cat == 'wisdom': return '#009DFF'
    return '#00A862'

def get_persona_guidance(blogType):
    if blogType == 'health':
        return """
당신은 대한민국 네이버 블로그 생태계를 완벽하게 이해하고 있으며, 복지/건강 전문가 일명 **'지원금 마스터 (김쌤)'**입니다.
이 블로그의 핵심 콘셉트는 "복잡한 정부 혜택, 내 지갑 속으로 쏙 들어오게!" 입니다.

[블로그 톤앤매너 및 필수 작성 가이드]
1. 독자 지칭 및 기본 문체:
   - 독자를 반드시 "우리 독자님들~", "선배님들", "시니어 여러분" 등으로 친근하게 지칭하세요.
   - 글의 분위기는 딱딱한 부처별 보도자료 말투 대신 매우 친절하고 명확한 설명조입니다.
   - 친절한 존댓말("~지원받을 수 있어요", "~입니다", "~준비하셨나요?")을 주로 사용하며, 약간의 이모티콘을 적절히 포함하세요.
"""
    elif blogType == 'wisdom':
        return """
당신은 사람들의 지친 마음을 위로하고 삶의 통찰을 전해주는 인생 멘토 **'인생 지혜와 인간관계 (김쌤)'**입니다. 
당신은 현학적이지 않고 편안한 어조로 인간관계의 지혜, 명언, 심리학적 통찰을 다룹니다.

[블로그 톤앤매너 및 필수 작성 가이드]
1. 독자 지칭 및 기본 문체:
   - 독자 여러분을 "우리 벗님들", "인생의 선배님들", "소중한 인연" 등으로 친근하고 따뜻하게 칭합니다.
   - 문체는 라디오 DJ나 편안한 찻집 주인이 이야기하듯 다정하고 차분한 조언의 톤("~라는 생각이 듭니다", "~하시길 바랍니다")을 유지하세요.
"""
    elif blogType == 'economy':
        return """
당신은 은퇴 설계 분야의 일타 강사이자, 시니어들의 생활비와 절세를 지켜드리는 일명 **'은퇴 경제 전문가 (김쌤)'**입니다.
이 블로그의 모토는 "은퇴는 끝이 아닌 새로운 시작입니다." 입니다.

[블로그 톤앤매너 및 데이터 활용 원칙]
1. 독자 지칭 및 기본 문체:
   - "은퇴를 앞두신 50대, 60대 여러분", "오늘도 품격 있는 노후를 준비하시는 시니어 선배님들" 등으로 지칭합니다.
   - 전문적인 세무/연금/절약 지식을 예리하게 분석하되, 실생활에 적용할 수 있게 사례를 들어 쉽게 설명합니다.
"""

def build_prompt(keyword, blogType):
    currentYear = datetime.datetime.now().year
    guidance = get_persona_guidance(blogType)
    return f"""{guidance}

[입력 정보]
- 주제/키워드: {keyword}
- 작성 기준 연도: 무조건 {currentYear}년 (절대로 과거 연도를 출력하지 마세요)

[공통 필수 준수 가이드]
1. 분량과 깊이: 모바일 환경에서 지루하지 않게 읽고 바로 아래 배너를 클릭할 수 있도록 공백 제외 400자 ~ 600자 내외로 매우 짧고 임팩트 있게 작성하세요.
2. 후원 유도 멘트 필수: 글의 마지막 문단에는 반드시 "글 하단의 골드박스 특가 링크를 누르시거나 쿠팡 배너를 통해 생수, 휴지를 구입해 주시면 우리 응원방에 큰 힘이 됩니다!"라는 문구를 자연스럽게 포함하세요.
3. 클릭을 유도하는 극도의 후킹형 블로그 제목 작성: 25자 이내로 최대한 짧고 자극적으로 지정하세요.
4. 가독성을 극대화하는 세련된 구조 (100% HTML 태그):
   - 문단은 항상 <p style='margin-bottom: 26px; color: #333; line-height: 1.8; font-weight: bold;'> 로 감싸서 큼직하고 시원하게 보이게 하세요.
   - 대주제 예시: <h2 style='font-size: 24px; font-weight: 900; color: #D84315; margin-top: 40px; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px dashed #D84315;'>...</h2>
   - 마크다운(##, **, 등) 절대 사용 금지! 오직 브라우저에서 바로 렌더링 가능한 순수 HTML 태그만 출력하세요.

[출력 형식 제한]
반드시 아래 특수 구분자를 사용하세요.
[TITLE]
(생성된 블로그 제목 1줄 텍스트)
[/TITLE]
[CONTENT]
(생성된 블로그 본문 순수 HTML 전체 코드. 플레이스홀더는 쓰지 마세요!!)
[/CONTENT]
"""

def generate_keywords():
    prompt = """
당신은 대한민국 시니어(50대~70대)를 위한 블로그 콘텐츠 디렉터입니다.
매일 새로운 글을 쓰기 위해 3가지 카테고리에 맞춰서 오늘 포스팅할 매력적인 롱테일 키워드(제목 후보)를 각각 1개씩(총 3개) 생성해주세요.
시니어들의 고민을 해결해주고 클릭을 유발하는 자극적이고 유익한 키워드가 좋습니다. 어제와 비슷한 뻔한 주제가 아닌 매우 구체적이고 새로운 주제여야 합니다.

카테고리 1. health (건강음식, 장수비결, 질병예방, 운동 등)
카테고리 2. economy (재산지키기, 증여세, 노령연금, 사기/스미싱 예방 등)
카테고리 3. wisdom (인간관계, 노년의 마음가짐, 가족 소통, 명언 등)

반드시 아래 JSON 형식으로만 응답해주세요. 마크다운 백틱 없이 순수 JSON만 출력해야 정상 파싱됩니다!
{
  "health": "생성된 건강 키워드",
  "economy": "생성된 경제 키워드",
  "wisdom": "생성된 지혜 키워드"
}
"""
    print("Generating keywords...")
    response = model.generate_content(prompt, generation_config={"temperature": 0.9})
    text = response.text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.endswith("```"):
        text = text[:-3]
    try:
        keywords = json.loads(text)
        return keywords
    except Exception as e:
        print(f"Failed to parse JSON keywords from Gemini: {text}")
        print(f"Error: {e}")
        # 로드 실패시 기본 키워드 반환
        return {
            "health": "시니어 겨울철 면역력 높이는 물 마시기 습관",
            "economy": "자녀에게 미리 현금 증여할 때 주의할 점",
            "wisdom": "나이 들수록 편안한 사람의 3가지 특징"
        }

def generate_blog(keyword, blogType):
    prompt = build_prompt(keyword, blogType)
    response = model.generate_content(prompt, generation_config={"temperature": 0.7})
    text = response.text
    
    title = "제목 누락"
    content = "<p>내용 누락</p>"
    
    try:
        title = text.split('[TITLE]')[1].split('[/TITLE]')[0].strip()
    except:
        pass
        
    try:
        content = text.split('[CONTENT]')[1].split('[/CONTENT]')[0].strip()
    except:
        if '[CONTENT]' in text:
            content = text.split('[CONTENT]')[1].strip()
            
    return title, content

def insert_link_to_blog_list(category_id, link_html, filepath="blog_list.html"):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    marker = ""
    if category_id == 'health':
        marker = "<!-- 건강/의료/장수 비결 -->"
    elif category_id == 'economy':
        marker = "<!-- 재산/복지/사기 예방 -->"
    elif category_id == 'wisdom':
        marker = "<!-- 생활/가족 소통 -->"
        
    marker_idx = -1
    for i, line in enumerate(lines):
        if marker in line:
            marker_idx = i
            break
            
    if marker_idx == -1:
        print(f"Could not find marker for {category_id}")
        return
        
    div_close_idx = -1
    for i in range(marker_idx, len(lines)):
        if "</div>" in lines[i]:
            div_close_idx = i
            break
            
    if div_close_idx != -1:
        lines.insert(div_close_idx, f"                {link_html}\n")
        
    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)

def main():
    if not GEMINI_API_KEY:
        print("GEMINI_API_KEY is missing!")
        return
        
    if not os.path.exists(BLOG_DIR):
        os.makedirs(BLOG_DIR)
        
    # Get max post number
    files = os.listdir(BLOG_DIR)
    max_num = 0
    for file in files:
        if file.startswith("post") and file.endswith(".html"):
            num_str = file.replace("post", "").replace(".html", "")
            if num_str.isdigit():
                max_num = max(max_num, int(num_str))
                
    curr_num = max_num + 1
    
    daily_keywords = generate_keywords()
    print(f"Today's Keywords: {daily_keywords}")
    
    categories = ['health', 'economy', 'wisdom']
    
    for cat in categories:
        keyword = daily_keywords.get(cat)
        if not keyword:
            continue
            
        print(f"Generating [{cat}] post for: {keyword}")
        title, content = generate_blog(keyword, cat)
        title_clean = title.replace('"', '').replace("'", "")
        
        html = TEMPLATE.format(
            title=title_clean,
            title_color=get_color(cat),
            content=content
        )
        
        filename = f"post{curr_num}.html"
        filepath = os.path.join(BLOG_DIR, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
            
        print(f"Saved {filepath}")
        
        link_html = f'<a href="blog/{filename}" class="block w-full bg-white border-2 border-[{get_color(cat)}] p-4 rounded-xl shadow-sm hover:bg-gray-50 active:scale-95 transition-transform text-xl font-bold text-gray-800">{curr_num}. {title_clean}</a>'
        
        insert_link_to_blog_list(cat, link_html, BLOG_LIST)
        print(f"Injected link to {BLOG_LIST} for {cat}")
        
        time.sleep(2) # To avoid rate limits
        curr_num += 1
        
    # Run post-processing (migrate_posts.py) to add images, related posts, and footer
    print("Running post-processing (migrate_posts.py)...")
    try:
        subprocess.run(["python", "migrate_posts.py"], check=True)
        print("Post-processing completed successfully.")
    except Exception as e:
        print(f"Failed to run migrate_posts.py: {e}")

    # Run SEO and Sitemap scripts
    print("Running SEO and Sitemap generation scripts...")
    try:
        subprocess.run(["node", "add_seo_tags.js"], check=True)
        print("SEO tags added successfully.")
    except Exception as e:
        print(f"Failed to run add_seo_tags.js: {e}")
        
    try:
        subprocess.run(["node", "build_sitemap.js"], check=True)
        print("Sitemap generated successfully.")
    except Exception as e:
        print(f"Failed to run build_sitemap.js: {e}")
        
    print("Fetching Coupang Goldbox Deals...")
    coupang_api.update_index_html()
        
    print("All tasks completed.")

if __name__ == "__main__":
    main()
