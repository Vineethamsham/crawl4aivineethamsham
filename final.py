
import time, json, re
from pathlib import Path
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options

# === ✅ Configurations ===
CHROMEDRIVER_PATH = r"C:\Users\VAmsham1\chromedriver\chromedriver.exe"
JSON_PATH = Path("data/pages_json/discovered_links.json")
OUTPUT_DIR = Path("output_markdown")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# === ✅ Helpers ===
def sanitize_filename(url):
    return re.sub(r'\W+', '_', url).strip('_')

def extract_visible_content(soup):
    blocks = []

    # Capture top-level sections based on layout structure
    for section in soup.select(".cmp-container, .aem-Grid, .cmp-layoutcontainer"):
        content_block = []
        heading = section.select_one("h2, h3, h4")
        if heading:
            content_block.append(f"## {heading.get_text(strip=True)}\n")

        # Paragraphs
        for p in section.select("p"):
            text = p.get_text(strip=True)
            if text:
                content_block.append(text)

        # Lists
        for li in section.select(".cmp-list__item"):
            li_text = li.get_text(strip=True)
            if li_text:
                content_block.append(f"- {li_text}")

        # Tables
        for table in section.select("table"):
            rows = table.find_all("tr")
            for i, row in enumerate(rows):
                cols = [col.get_text(strip=True) for col in row.find_all(["td", "th"])]
                line = " | ".join(cols)
                content_block.append(line)
                if i == 0:
                    content_block.append("|" + "|".join(["---"] * len(cols)) + "|")

        # Divs/spans fallback
        for div in section.select("div, span"):
            text = div.get_text(strip=True)
            if text and len(text) > 30:  # avoid tiny repeated spans
                content_block.append(text)

        if content_block:
            blocks.append("\n".join(content_block))

    return "\n\n".join(blocks)

def process_url(url):
    print(f"🌐 Crawling: {url}")

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=ChromeService(CHROMEDRIVER_PATH), options=options)

    try:
        driver.get(url)
        time.sleep(3)

        # Expand tabs/accordions
        driver.execute_script("""
            document.querySelectorAll('[role=button], summary, .cmp-accordion__button, .cmp-tabs__tab').forEach(el => {
                try { el.click(); } catch(e) {}
            });
        """)
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        title = soup.title.string.strip() if soup.title else "No Title Found"
        filename = sanitize_filename(url) + ".md"
        filepath = OUTPUT_DIR / filename

        content = extract_visible_content(soup)

        with filepath.open("w", encoding="utf-8") as f:
            f.write(f"# {title}\n")
            f.write(f"URL: {url}\n\n")
            f.write(content if content else "_No content extracted._")

        print(f"✅ Saved: {filepath}")

    finally:
        driver.quit()

# === ✅ Main logic ===
if __name__ == "__main__":
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        url = json.load(f)[0]["url"]
    process_url(url)
