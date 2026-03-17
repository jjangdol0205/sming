import google.generativeai as genai
import datetime
import os
import json

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

POSTS = [
    {
        "keyword": "환절기 노인 면역력 높이는 시니어 밥상 보약 슈퍼푸드 3가지",
        "blogType": "health",
        "category_id": "health"
    },
    {
        "keyword": "비싼 세금 물지 않고 합법적으로 자녀에게 미리 현금 증여하는 방법 5천만원",
        "blogType": "economy",
        "category_id": "economy"
    },
    {
        "keyword": "나이 들수록 친구가 멀어지는 이유와 노년기 편안한 인간관계를 위한 마음가짐",
        "blogType": "wisdom",
        "category_id": "wisdom"
    }
]

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
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-4633321310054654"
        crossorigin="anonymous"></script>

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

        <a href="../index.html"
            class="block w-full bg-[#00563F] text-white text-center font-extrabold py-5 rounded-2xl shadow-lg active:scale-95 transition-transform mt-auto text-2xl">
            🔙 김쌤의 스밍 포털 메인으로 돌아가기
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
   - 친절한 존댓말("~지원받을 수 있어요", "~입니다", "~준비하셨나요?")을 주로 사용하며, 약간의 이모티콘(💰, 📝, 🎁, 😊)을 포함하세요.
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
   - 전문적인 세무/건보료 지식을 예리하게 분석하되, 실생활에 적용할 수 있게 사례를 들어 쉽게 설명합니다.
"""

def build_prompt(keyword, blogType):
    currentYear = datetime.datetime.now().year
    guidance = get_persona_guidance(blogType)
    return f"""{guidance}

[입력 정보]
- 주제/키워드: {keyword}
- 작성 기준 연도: 무조건 {currentYear}년 (절대로 2024년 등 과거 연도를 출력하지 마세요)

[공통 필수 준수 가이드]
1. 분량과 깊이: 공백 제외 800자 ~ 1,000자 내외로 모바일 환경에서 빠르고 쉽게 읽을 수 있도록 핵심만 간략하고 명쾌하게 작성하세요.
2. 클릭을 유도하는 극도의 후킹형 블로그 제목 작성: 25자 이내로 최대한 짧게 작성하세요. 기호나 숫자로 눈길을 끄세요.
3. 가독성을 극대화하는 세련된 구조 (100% HTML 태그):
   - 문단은 항상 <p style='margin-bottom: 26px; color: #333;'> 로 감싸기.
   - 대주제 예시: <h2 style='font-size: 24px; font-weight: 800; color: #111; margin-top: 70px; margin-bottom: 25px; padding-bottom: 10px; border-bottom: 2px solid #111;'>...</h2>
   - 마크다운(##, **, 등) 절대 사용 금지! 오직 HTML 코드만 출력하세요.

[출력 형식 제한]
반드시 아래 특수 구분자를 사용하세요.
[TITLE]
(생성된 블로그 제목 1줄 텍스트)
[/TITLE]
[CONTENT]
(생성된 블로그 본문 순수 HTML 전체 코드. [THUMBNAIL] 이나 [IMAGE_1] 등의 플레이스홀더는 쓰지 마세요!!)
[/CONTENT]
"""

def generate_blog(item):
    prompt = build_prompt(item['keyword'], item['blogType'])
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

def main():
    BLOG_DIR = "blog"
    if not os.path.exists(BLOG_DIR):
        os.makedirs(BLOG_DIR)
        
    files = os.listdir(BLOG_DIR)
    max_num = 0
    for file in files:
        if file.startswith("post") and file.endswith(".html"):
            num_str = file.replace("post", "").replace(".html", "")
            if num_str.isdigit():
                max_num = max(max_num, int(num_str))
                
    curr_num = max_num + 1
    new_links = { 'health': [], 'economy': [], 'wisdom': [] }
    
    for item in POSTS:
        print(f"Generating post for: {item['keyword']}")
        title, content = generate_blog(item)
        
        html = TEMPLATE.format(
            title=title,
            title_color=get_color(item["category_id"]),
            content=content
        )
        
        filename = f"post{curr_num}.html"
        filepath = os.path.join(BLOG_DIR, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
            
        print(f"Saved {filepath}")
        
        cat_id = item["category_id"]
        link_html = f'<a href="blog/{filename}" class="block w-full bg-white border-2 border-[{get_color(cat_id)}] p-4 rounded-xl shadow-sm hover:bg-gray-50 active:scale-95 transition-transform text-xl font-bold text-gray-800">{curr_num}. {title}</a>'
        new_links[cat_id].append(link_html)
        
        curr_num += 1
        
    with open("new_links_output.json", "w", encoding="utf-8") as f:
        json.dump(new_links, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
