import json
from playwright.sync_api import sync_playwright, Page
import time

def scroll_to_end_page(page: Page, max_scrolls: int) -> None:
    _prev_height = -1
    _scroll_count = 0
    while _scroll_count < max_scrolls:
        #page.evaluate("window.scrollTo(0, document.scrollingElement.scrollHeight)")
        page.mouse.wheel(0, 15000)
        time.sleep(1)
        new_height = page.evaluate("document.scrollingElement.scrollHeight")
        if new_height == _prev_height:
            break
        _prev_height = new_height
        _scroll_count += 1

def scrape_post_urls(page_url: str) -> None:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1920, "height": 1080}, storage_state="./scraper/playwright/.auth/state.json")
        page = context.new_page()
        
        page.goto(url=page_url)
        page.wait_for_selector("ytd-backstage-post-thread-renderer")
        time.sleep(1)
        
        scroll_to_end_page(page=page, max_scrolls=50)
        
        time.sleep(2)
        posts = page.query_selector_all("ytd-backstage-post-thread-renderer.style-scope")
        urls = []
        for post in posts:
            link = post.query_selector("div:nth-child(1) > ytd-backstage-post-renderer:nth-child(1) > div:nth-child(1) > div:nth-child(2) > ytd-comment-action-buttons-renderer:nth-child(7) > div:nth-child(1) > div:nth-child(8) > ytd-button-renderer:nth-child(1) > yt-button-shape:nth-child(1) > a:nth-child(1)")
            urls.append(link.get_attribute("href"))
        
        with open("./scraper/playwright/post_urls.txt", "w") as file:
            for url in urls:
                file.write("www.youtube.com" + url + "\n")
             
             
def scrape_post_and_comments(url_file: str) -> None:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1920, "height": 1080}, storage_state="./scraper/playwright/.auth/state.json")
        page = context.new_page()
        
        page.goto(url=url_file)
        page.wait_for_selector("ytd-backstage-post-renderer")
        time.sleep(1)
        
        scroll_to_end_page(page=page, max_scrolls=50)
        
        reply_buttons = page.query_selector_all("ytd-button-renderer#more-replies")
        for button in reply_buttons:
            time.sleep(1)
            button.click()
        
        while True:
            more_comments_button = page.query_selector_all("ytd-continuation-item-renderer ytd-button-renderer.ytd-continuation-item-renderer")
            
            if (len(more_comments_button) == 0): 
                break
            
            for button in more_comments_button:
                time.sleep(1)
                button.click()
        
        post_text = page.query_selector("yt-formatted-string#content-text").inner_text()
        post_author = page.query_selector("ytd-backstage-post-thread-renderer div#post a#author-text span").inner_text()
        post_date = page.query_selector("ytd-backstage-post-thread-renderer div#post yt-formatted-string a").inner_text()
        comments = page.query_selector_all("ytd-comment-thread-renderer")
        
        comments_data = []
        for comment in comments:
            comment_text = comment.query_selector("ytd-comment-view-model#comment yt-attributed-string#content-text span").inner_text()
            author_text = comment.query_selector("ytd-comment-view-model#comment a#author-text span").inner_text()
            comment_date = comment.query_selector("ytd-comment-view-model#comment span#published-time-text a").inner_text()
           
            comment_info = {
                "comment_author": author_text,
                "comment_date": comment_date,
                "comment_content": comment_text,
                "replies": []
            }
            
            replies = comment.query_selector_all("ytd-comment-view-model.ytd-comment-replies-renderer")
            for reply in replies:
                author_text = reply.query_selector("a#author-text span").inner_text()
                reply_date = reply.query_selector("span#published-time-text a").inner_text()
                replied_to = reply.query_selector("yt-attributed-string#content-text span span a").inner_text()
                reply_text = reply.query_selector("yt-attributed-string#content-text span").inner_text()

                reply_info = {
                    "reply_author": author_text,
                    "reply_date": reply_date,
                    "reply_to": replied_to,
                    "reply_content": reply_text
                }
                comment_info["replies"].append(reply_info)
            
            comments_data.append(comment_info)
            
        post_data = {
            "author": post_author,
            "date": post_date,
            "content": post_text,
            "comments": comments_data
        }
        data = json.dumps(post_data, indent=4, ensure_ascii=False)
        print(data)
        with open("./scraper/playwright/posts_data.json", "w", encoding='utf8') as file:
            file.write(data)
        
        input("test")
        

if __name__ == "__main__":
    #scrape_post_urls("https://www.youtube.com/@FilmlerveFilimler/community")
    scrape_post_and_comments("https://www.youtube.com/post/UgkxHNTti5hnRLVjVDi9hDiSoVYBUbiSrZKL")