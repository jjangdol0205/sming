import os
import time
from playwright.sync_api import sync_playwright

def run():
    user_data_dir = os.path.join(os.getcwd(), "youtube_profile")
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=True,
            channel="chrome",
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        page = browser.new_page()
        
        community_url = "https://www.youtube.com/@김쌤의영웅라디오/community"
        print(f"Going to {community_url}")
        page.goto(community_url)
        time.sleep(5)
        
        page.screenshot(path="yt_debug1.png")
        print("Screenshot saved to yt_debug1.png")
        
        # Check login status
        login_button = page.locator("a[href^='https://accounts.google.com/ServiceLogin']")
        if login_button.count() > 0:
            print("NOT LOGGED IN")
        else:
            print("LOGGED IN")
            
        try:
            print("Looking for #placeholder-area")
            box = page.locator("#placeholder-area")
            if box.count() > 0:
                print("Found #placeholder-area")
            else:
                print("Could not find #placeholder-area")
        except Exception as e:
            print("Error:", e)
            
        browser.close()

if __name__ == "__main__":
    run()
