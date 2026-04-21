import os
import re
import random

BLOG_DIR = "blog"
INDEX_FILE = "index.html"

# Extract links and titles from index.html
def get_all_posts():
    posts = []
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        content = f.read()
        
    # <a href="blog/post1.html" class="...">1. 제목</a>
    matches = re.findall(r'<a href="blog/(post\d+\.html)"[^>]*>([\d]+\.\s*[^<]+)</a>', content)
    for match in matches:
        posts.append({
            "filename": match[0],
            "title": match[1].strip()
        })
    return posts

def migrate():
    posts = get_all_posts()
    print(f"Found {len(posts)} posts in index.html.")
    
    if not os.path.exists(BLOG_DIR):
        print("Blog directory not found!")
        return

    for filename in os.listdir(BLOG_DIR):
        if filename.startswith("post") and filename.endswith(".html"):
            filepath = os.path.join(BLOG_DIR, filename)
            
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Skip if already migrated (check for the new footer or image)
            if 'loremflickr.com' in content and '저자 소개' in content and '관련 꿀팁' in content:
                print(f"Skipping {filename}, already migrated.")
                continue

            # 1. Determine category keyword for the image based on title or random
            post_num = filename.replace('post', '').replace('.html', '')
            post_title_info = next((p for p in posts if p["filename"] == filename), None)
            
            category_keyword = "senior"
            # Try to guess category based on color or content
            if '#00A862' in content:  # health
                category_keyword = "health,senior"
            elif '#D9381E' in content:  # economy
                category_keyword = "money,senior"
            elif '#009DFF' in content:  # wisdom
                category_keyword = "family,senior"

            # 2. Insert Image at the start of <article>
            if '<article class="flex-grow">' in content:
                image_html = f'\n            <img src="https://loremflickr.com/800/400/{category_keyword}?lock={post_num}" alt="관련 이미지" class="w-full h-auto rounded-2xl mb-6 shadow-md border border-gray-200">\n'
                if 'loremflickr.com' not in content:
                    content = content.replace('<article class="flex-grow">', '<article class="flex-grow">' + image_html)
            elif '<article>' in content:
                 image_html = f'\n            <img src="https://loremflickr.com/800/400/{category_keyword}?lock={post_num}" alt="관련 이미지" class="w-full h-auto rounded-2xl mb-6 shadow-md border border-gray-200">\n'
                 if 'loremflickr.com' not in content:
                     content = content.replace('<article>', '<article>' + image_html)

            # 3. Insert E-E-A-T block if missing
            eeat_block = """
        <!-- 저자 소개 및 편집자 선언 (E-E-A-T 확보) -->
        <div class="mt-12 bg-gray-50 border border-gray-200 rounded-2xl p-5 shadow-sm text-sm text-gray-700 leading-relaxed">
            <h4 class="font-extrabold text-gray-900 mb-2 flex items-center gap-2">
                <span class="text-xl">✍️</span> 저자 소개 : 김쌤
            </h4>
            <p class="mb-3">
                대한민국 5070 시니어들의 건강한 삶과 경제적 자립을 위해 꼭 필요한 꿀팁만을 엄선하여 전달하는 시니어 라이프스타일 큐레이터입니다.
            </p>
            <div class="border-t border-gray-300 pt-3 text-xs text-gray-500">
                <strong>[콘텐츠 편집 및 면책 조항]</strong><br>
                본 포스팅은 김쌤의 기획 및 철저한 사실 확인을 바탕으로 작성되었으며, 독자들의 이해를 돕기 위해 AI 기술의 보조를 받아 초안이 작성 및 윤문되었습니다. 본 글에 포함된 의학, 건강, 경제 관련 정보는 일반적인 정보 제공을 목적으로 하며, 전문적인 의학적 진단이나 재무 상담을 대신할 수 없습니다. 개별적인 증상이나 상황에 대해서는 반드시 관련 전문가(의사, 세무사 등)와 상담하시기 바랍니다.
            </div>
        </div>
"""
            if '저자 소개 및 편집자 선언' not in content:
                content = content.replace('</article>', '</article>' + eeat_block)

            # 4. Insert Related Posts
            if '🔥 김쌤이 추천하는 관련 꿀팁 글' not in content:
                # Pick 3 random posts
                related = random.sample([p for p in posts if p["filename"] != filename], min(3, len(posts)))
                related_html = '\n        <!-- 추천 글 -->\n        <div class="mt-8 mb-6">\n            <h3 class="text-xl font-extrabold text-gray-900 mb-4 border-b-2 border-[#FFD700] inline-block pb-1">🔥 김쌤이 추천하는 관련 꿀팁 글</h3>\n            <div class="flex flex-col gap-3">\n'
                for r in related:
                    related_html += f'                <a href="{r["filename"]}" class="block w-full bg-white border border-gray-200 p-4 rounded-xl shadow-sm hover:bg-gray-50 active:scale-95 transition-transform text-lg font-bold text-gray-800 line-clamp-2">{r["title"]}</a>\n'
                related_html += '            </div>\n        </div>\n'
                
                # Insert before the back button
                back_button_pattern = r'<a href="\.\./index\.html"[^>]*>.*?</a>'
                match = re.search(back_button_pattern, content, re.DOTALL)
                if match:
                    content = content[:match.start()] + related_html + content[match.start():]

            # 5. Add footer
            footer_html = """
        <!-- 푸터 -->
        <footer class="text-center border-t border-gray-200 pt-6 mt-10">
            <div class="flex justify-center flex-wrap gap-4 text-sm font-bold text-gray-500 mb-4">
                <a href="../index.html" class="hover:text-gray-800">홈</a>
                <span>|</span>
                <a href="../about.html" class="hover:text-gray-800">운영자 소개</a>
                <span>|</span>
                <a href="../privacy-policy.html" class="hover:text-gray-800">개인정보처리방침</a>
                <span>|</span>
                <a href="../terms-of-service.html" class="hover:text-gray-800">이용약관</a>
            </div>
            <p class="text-xs text-gray-400">© 2024 김쌤과 함께하는 파라다이스. All rights reserved.</p>
        </footer>
"""
            if '<!-- 푸터 -->' not in content:
                # Insert right before </main>
                content = content.replace('</main>', footer_html + '\n    </main>')

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            
            print(f"Migrated {filename}")

if __name__ == "__main__":
    migrate()
    print("Migration complete!")
