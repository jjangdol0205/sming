import requests
import json
import os
import re

POSTS = [
    {
        "keyword": "환절기 노인 면역력 높이는 시니어 밥상 보약 슈퍼푸드 3가지",
        "blogType": "health",
        "category_id": "health" # health category in blog_list.html is '#00A862' text color
    },
    {
        "keyword": "비싼 세금 물지 않고 합법적으로 자녀에게 미리 현금 증여하는 방법 5천만원",
        "blogType": "economy",
        "category_id": "economy" # economy category is '#D9381E' in blog_list.html
    },
    {
        "keyword": "나이 들수록 친구가 멀어지는 이유와 노년기 편안한 인간관계를 위한 마음가짐",
        "blogType": "wisdom",
        "category_id": "wisdom" # wisdom category is '#009DFF' in blog_list.html
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

BLOG_DIR = "blog"
BLOG_LIST = "blog_list.html"

def get_color(cat):
    if cat == 'health': return '#00A862'
    if cat == 'economy': return '#D9381E'
    if cat == 'wisdom': return '#009DFF'
    return '#00A862'

def main():
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
    new_links = { 'health': [], 'economy': [], 'wisdom': [] }
    
    API_URL = "http://localhost:3000/api/generate"
    
    for item in POSTS:
        print(f"Generating post for: {item['keyword']}")
        resp = requests.post(API_URL, json={
            "keyword": item["keyword"],
            "blogType": item["blogType"]
        }, timeout=120)
        
        if resp.status_code != 200:
            print(f"Failed to generate: {resp.text}")
            continue
            
        data = resp.json()
        title = data["title"]
        content = data["content"]
        
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
        
        # Prepare link for blog_list.html
        cat_id = item["category_id"]
        link_html = f'<a href="blog/{filename}" class="block w-full bg-white border-2 border-[{get_color(cat_id)}] p-4 rounded-xl shadow-sm hover:bg-gray-50 active:scale-95 transition-transform text-xl font-bold text-gray-800">{curr_num}. {title}</a>'
        new_links[cat_id].append(link_html)
        
        curr_num += 1
        
    # Update blog_list.html
    # We will let another script or code inject this. 
    # For now, let's just write down the links so we can inject them manually.
    with open("new_links.json", "w", encoding="utf-8") as f:
        json.dump(new_links, f, ensure_ascii=False)
        
    print("Done generating 3 posts.")

if __name__ == "__main__":
    main()
