import time, json, re
from pathlib import Path
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options

# === ✅ Configuration ===
CHROMEDRIVER_PATH = r"C:\Users\VAmsham1\chromedriver\chromedriver.exe"
JSON_PATH = Path("data/pages_json/discovered_links.json")
OUTPUT_DIR = Path("output_markdown")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# === ✅ Helpers ===
def sanitize_filename(url):
    return re.sub(r'\W+', '_', url).strip('_')


def process_url(url):
    print(f"🌐 Crawling: {url}")

    options = Options()
    options.add_argument("--headless=new")  # Keep browser hidden
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(service=ChromeService(CHROMEDRIVER_PATH), options=options)
    driver.get(url)
    time.sleep(3)

    # 🔄 Expand collapsible sections (accordion buttons, summary, custom toggles)
    driver.execute_script("""
        document.querySelectorAll('[role=button], summary, .cmp-accordion__button').forEach(el => {
            try { el.click(); } catch(e) {}
        });
    """)
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    filename = sanitize_filename(url) + ".md"
    filepath = OUTPUT_DIR / filename

    with filepath.open("w", encoding="utf-8") as f:
        title = soup.title.string.strip() if soup.title else "No Title Found"
        f.write(f"# {title}\n")
        f.write(f"URL: {url}\n\n")

        headers = soup.find_all(["h2", "h3"])
        for header in headers:
            heading_text = header.get_text(strip=True)
            f.write(f"## {heading_text}\n\n")

            section_content = []

            # Walk sibling blocks until next header
            for sibling in header.find_next_siblings():
                if sibling.name in ["h2", "h3"]:
                    break

                # Extract paragraphs inside cmp-text
                if sibling.select_one(".cmp-text p"):
                    for p in sibling.select(".cmp-text p"):
                        text = p.get_text(strip=True)
                        if text:
                            section_content.append(text)

                # Extract list items
                elif sibling.select_one(".cmp-list__item"):
                    for li in sibling.select(".cmp-list__item"):
                        section_content.append(f"- {li.get_text(strip=True)}")

                # Extract tables
                elif sibling.select_one("table"):
                    rows = sibling.select("table tr")
                    for i, row in enumerate(rows):
                        cols = [col.get_text(strip=True) for col in row.select("td, th")]
                        section_content.append(" | ".join(cols))
                        if i == 0:
                            section_content.append("|".join(["---"] * len(cols)))

                # Fallback div/span blocks
                elif sibling.name in ["div", "span"]:
                    text = sibling.get_text(strip=True)
                    if text:
                        section_content.append(text)

            if section_content:
                f.write("\n".join(section_content))
                f.write("\n\n")

    print(f"✅ Saved: {filepath}")


# === ✅ Main logic for testing one URL ===
if __name__ == "__main__":
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        url = json.load(f)[0]["url"]
    process_url(url)
