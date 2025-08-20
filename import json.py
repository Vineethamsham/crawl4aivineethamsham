import json
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urlparse

# ✅ CONFIGURATION
CHROMEDRIVER_PATH = r"C:\Users\VAmsham1\chromedriver\chromedriver.exe"  # adjust if needed
JSON_PATH = Path("data/pages_json/discovered_links.json")
OUTPUT_DIR = Path("output_markdown")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ✅ Load one URL from JSON
with open(JSON_PATH, "r", encoding="utf-8") as f:
    url = json.load(f)[0]["url"]
print(f"🌐 Crawling: {url}")

# ✅ Setup Selenium
options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=options)
driver.get(url)
time.sleep(3)

# ✅ Try expanding all collapsible elements
driver.execute_script("""
    document.querySelectorAll('summary, button, .accordion').forEach(el => {
        try { el.click(); } catch (e) {}
    });
""")
time.sleep(1.5)

# ✅ Parse with BeautifulSoup
soup = BeautifulSoup(driver.page_source, "html.parser")
driver.quit()

# ✅ Markdown setup
def sanitize_filename(url):
    return re.sub(r'\W+', '_', url).strip('_')

title = soup.title.get_text(strip=True) if soup.title else "No Title"
title_slug = sanitize_filename(url)
md_lines = [f"# {title}", f"URL: {url}", ""]

# ✅ Loop through headings and capture rich content
for header in soup.find_all(["h2", "h3"]):
    heading_text = header.get_text(strip=True)
    md_lines.append(f"## {heading_text}")
    section_content = []

    for sibling in header.find_next_siblings():
        if sibling.name in ["h2", "h3"]:
            break

        # Extract paragraphs
        if sibling.name == "p":
            section_content.append(sibling.get_text(strip=True))

        # Extract lists
        elif sibling.name in ["ul", "ol"]:
            for li in sibling.find_all("li"):
                section_content.append(f"- {li.get_text(strip=True)}")

        # Extract tables
        elif sibling.name == "table":
            rows = sibling.find_all("tr")
            for i, row in enumerate(rows):
                cols = [col.get_text(strip=True) for col in row.find_all(["td", "th"])]
                section_content.append(" | ".join(cols))
                if i == 0:
                    section_content.append("|".join(["---"] * len(cols)))

        # Divs/spans with text
        elif sibling.name in ["div", "span"]:
            section_content.append(sibling.get_text(strip=True))

        # Custom blocks (e.g., cmp-text, cmp-list, cmp-table)
        elif sibling.get("class") and any(cls in sibling.get("class") for cls in ["cmp-text", "cmp-list", "cmp-table"]):
            section_content.append(sibling.get_text(strip=True))

    if section_content:
        md_lines.extend(section_content)
        md_lines.append("")

# ✅ Save Markdown
output_file = OUTPUT_DIR / f"{title_slug}.md"
output_file.write_text("\n".join(md_lines), encoding="utf-8")
print(f"✅ Saved Markdown to {output_file}")
