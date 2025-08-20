import json
import time
import re
from pathlib import Path
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# === CONFIG ===
CHROMEDRIVER_PATH = r"C:\Users\VAmsham1\chromedriver\chromedriver.exe"
JSON_PATH = Path("data/pages_json/discovered_links.json")
OUTPUT_DIR = Path("output_markdown")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# === Load First URL ===
with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)
url = data[0]["url"]  # Only 1st URL for now
print(f"🌐 Crawling: {url}")

# === Clean filename ===
def sanitize_filename(url: str) -> str:
    parsed = urlparse(url)
    return re.sub(r"[^\w]+", "_", parsed.netloc + parsed.path).strip("_")

# === Setup Chrome (Headless) ===
options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

try:
    driver.get(url)
    time.sleep(3)

    # Try to expand interactive sections
    driver.execute_script("""
        document.querySelectorAll('[role=button], summary, .accordion').forEach(el => {
            try { el.click(); } catch(e) {}
        });
    """)
    time.sleep(2)

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # === Markdown output ===
    filename = sanitize_filename(url) + ".md"
    filepath = OUTPUT_DIR / filename

    with filepath.open("w", encoding="utf-8") as f:
        # Page Title and URL
        title = soup.title.string.strip() if soup.title else "No Title"
        f.write(f"# {title}\n")
        f.write(f"URL: {url}\n\n")

        for header in soup.find_all(["h2", "h3"]):
            heading = header.get_text(strip=True)
            f.write(f"## {heading}\n\n")

            section_content = []

            for sibling in header.find_next_siblings():
                if sibling.name in ["h2", "h3"]:
                    break

                if sibling.name == "p":
                    text = sibling.get_text(strip=True)
                    if text:
                        section_content.append(text)

                elif sibling.name in ["ul", "ol"]:
                    for li in sibling.find_all("li"):
                        section_content.append(f"- {li.get_text(strip=True)}")

                elif sibling.name == "table":
                    rows = sibling.find_all("tr")
                    for i, row in enumerate(rows):
                        cols = [col.get_text(strip=True) for col in row.find_all(["td", "th"])]
                        line = " | ".join(cols)
                        section_content.append(line)
                        if i == 0:
                            section_content.append("|".join(["---"] * len(cols)))

                elif sibling.name in ["div", "span"]:
                    text = sibling.get_text(strip=True)
                    if text:
                        section_content.append(text)

            if section_content:
                f.write("\n".join(section_content))
                f.write("\n\n")

    print(f"✅ Saved Markdown to {filepath}")

finally:
    driver.quit()
