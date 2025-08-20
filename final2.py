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

# === ✅ Noise filter (UI junk) ===
NOISE_FILTER = [
    "skip to main", "navigation", "my stuff", "notifications", "log out",
    "news & events", "resources", "employee services", "bookmarks"
]

# === ✅ Helpers ===
def sanitize_filename(url):
    return re.sub(r'\W+', '_', url).strip('_')

def extract_visible_content(soup):
    blocks = []
    
    for section in soup.select(".cmp-container, .aem-Grid, .cmp-layoutcontainer"):
        content_block = []

        # --- Headings (h2, h3, h4)
        for heading in section.select("h2, h3, h4"):
            level = "#" * int(heading.name[1])  # h2 → ##, h3 → ### etc.
            text = heading.get_text(strip=True)
            if text and not any(noise in text.lower() for noise in NOISE_FILTER):
                content_block.append(f"{level} {text}")

        # --- Paragraphs
        for p in section.select("p"):
            text = p.get_text(strip=True)
            if text and not any(noise in text.lower() for noise in NOISE_FILTER):
                content_block.append(text)

        # --- Lists
        for li in section.select("li, .cmp-list__item"):
            li_text = li.get_text(strip=True)
            if li_text and not any(noise in li_text.lower() for noise in NOISE_FILTER):
                content_block.append(f"- {li_text}")

        # --- Tables
        for table in section.select("table"):
            rows = table.find_all("tr")
            for i, row in enumerate(rows):
                cols = [col.get_text(strip=True) for col in row.find_all(["td", "th"])]
                if not cols:
                    continue
                line = " | ".join(cols)
                content_block.append(line)
                if i == 0:
                    content_block.append("|" + "|".join(["---"] * len(cols)) + "|")

        # Add block if it has meaningful content
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

        # Expand all tabs/accordions
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
