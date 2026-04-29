import os
import hmac
import hashlib
import time
import requests
import json

ACCESS_KEY = "3793eab4-a000-4bc3-a659-0e9ee25478bc"
SECRET_KEY = "3f798e0e532b06c42748ed13de8e264f3d597b55"

def generate_hmac(method, uri, secret_key, access_key):
    datetime_str = time.strftime('%y%m%d', time.gmtime()) + 'T' + time.strftime('%H%M%S', time.gmtime()) + 'Z'
    message = datetime_str + method + uri
    signature = hmac.new(bytes(secret_key, "utf-8"),
                         message.encode("utf-8"),
                         hashlib.sha256).hexdigest()

    return f"CEA algorithm=HmacSHA256, access-key={access_key}, signed-date={datetime_str}, signature={signature}"

def get_goldbox_deals():
    method = "GET"
    uri = "/v2/providers/affiliate_open_api/apis/openapi/v1/products/goldbox"
    domain = "https://api-gateway.coupang.com"
    url = domain + uri

    authorization = generate_hmac(method, uri, SECRET_KEY, ACCESS_KEY)
    headers = {"Authorization": authorization, "Content-Type": "application/json"}
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        if data.get("rCode") == "0" and "data" in data:
            products = data["data"]
            return products[:3]
        else:
            print("Coupang API Error:", data)
            return []
    except Exception as e:
        print("Exception:", e)
        return []

def generate_html_snippet(products):
    if not products:
        return ""
    
    html = '<div class="flex flex-col gap-3 w-full my-4">\n'
    for p in products:
        name = p.get('productName', '')
        price = p.get('productPrice', 0)
        image = p.get('productImage', '')
        link = p.get('productUrl', '')
        html += f'''
        <a href="{link}" target="_blank" class="flex items-center gap-3 bg-white p-3 rounded-xl border border-red-200 shadow-sm active:scale-95 transition-transform hover:border-red-400">
            <img src="{image}" alt="상품" class="w-16 h-16 object-cover rounded-lg border border-gray-100">
            <div class="flex flex-col justify-center flex-grow text-left">
                <span class="text-[11px] text-white bg-red-500 rounded-sm px-1.5 py-0.5 w-max font-bold mb-1">오늘의 반값 특가</span>
                <span class="text-xs font-bold text-gray-800 line-clamp-2 leading-snug">{name}</span>
                <span class="text-base font-extrabold text-[#D84315] mt-1">{price:,}원</span>
            </div>
        </a>
        '''
    html += '</div>\n'
    return html

def update_index_html():
    deals = get_goldbox_deals()
    html_snippet = generate_html_snippet(deals)
    
    if not html_snippet:
        print("No deals found, skipping update.")
        return
        
    filepath = "index.html"
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        start_marker = "<!-- COUPANG_GOLDBOX_START -->"
        end_marker = "<!-- COUPANG_GOLDBOX_END -->"
        
        start_idx = content.find(start_marker)
        end_idx = content.find(end_marker)
        
        if start_idx != -1 and end_idx != -1:
            new_content = content[:start_idx + len(start_marker)] + "\n" + html_snippet + content[end_idx:]
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print("Successfully updated index.html with fresh Coupang deals.")
        else:
            print("Markers not found in index.html")
    except Exception as e:
        print("Failed to update index.html:", e)

if __name__ == "__main__":
    update_index_html()
