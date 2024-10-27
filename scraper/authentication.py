from playwright.sync_api import sync_playwright
import time

def authenticate(url: str) -> dict:
    with sync_playwright() as pw:
        args = []
        args.append("--disable-blink-features=AutomationControlled")
        browser = pw.chromium.launch(headless=False, args=args)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})        
        page = context.new_page()
        page.goto(url=url)
        
        save = input("save? :")
        if (save == "y"):
            storage = context.storage_state(path="./scraper/playwright/.auth/state.json")
        time.sleep(1)
   

if __name__ == "__main__":
    authenticate("https://www.youtube.com")