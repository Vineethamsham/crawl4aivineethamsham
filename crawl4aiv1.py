import asyncio
import json
from pathlib import Path
from urllib.parse import urlparse

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

def get_filename_from_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    filename = path.replace("/", "_") or "index"
    return f"{filename}.md"

async def crawl_single_url():
    # Load your discovered links JSON
    input_path = Path("data/pages_json/discovered_links.json")
    output_dir = Path("output_markdown")
    output_dir.mkdir(exist_ok=True)

    with input_path.open(encoding="utf-8") as f:
        url_data = json.load(f)

    # Pick the first URL
    url = url_data[0]["url"]
    print(f"Crawling first URL: {url}")

    # Set up Crawl4AI
    browser_config = BrowserConfig(
        headless=True,
        extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"]
    )
    crawl_config = CrawlerRunConfig(
        markdown_generator=DefaultMarkdownGenerator()
    )

    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.start()

    try:
        session_id = "session1"
        result = await crawler.arun(
            url=url,
            config=crawl_config,
            session_id=session_id
        )
        if result.success:
            filename = get_filename_from_url(url)
            output_path = output_dir / filename
            output_path.write_text(result.markdown.raw_markdown, encoding="utf-8")
            print(f"✅ Saved markdown to {output_path}")
        else:
            print(f"❌ Failed: {url} - Error: {result.error_message}")
    finally:
        await crawler.close()

if __name__ == "__main__":
    asyncio.run(crawl_single_url())

#


import asyncio
import json
from pathlib import Path
from urllib.parse import urlparse
import sys

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

# ✅ Fix Windows event loop issue
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ✅ Optional: Adjust this to your actual Chrome path
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

def get_filename_from_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    filename = path.replace("/", "_") or "index"
    return f"{filename}.md"

async def crawl_single_url():
    input_path = Path("data/pages_json/discovered_links.json")
    output_dir = Path("output_markdown")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load your discovered links
    with input_path.open(encoding="utf-8") as f:
        url_data = json.load(f)

    if not url_data:
        print("❌ No URLs found in the JSON file.")
        return

    url = url_data[0]["url"]
    print(f"🌐 Crawling first URL: {url}")

    # ✅ Use local Chrome to avoid download issues
    browser_config = BrowserConfig(
        headless=True,
        executable_path=CHROME_PATH,
        extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"]
    )
    crawl_config = CrawlerRunConfig(
        markdown_generator=DefaultMarkdownGenerator()
    )

    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.start()

    try:
        session_id = "session1"
        result = await crawler.arun(
            url=url,
            config=crawl_config,
            session_id=session_id
        )
        if result.success:
            filename = get_filename_from_url(url)
            output_path = output_dir / filename
            output_path.write_text(result.markdown.raw_markdown, encoding="utf-8")
            print(f"✅ Markdown saved to: {output_path}")
        else:
            print(f"❌ Crawl failed: {url}")
            print(f"   Reason: {result.error_message}")
    finally:
        await crawler.close()

if __name__ == "__main__":
    asyncio.run(crawl_single_url())

