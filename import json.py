import json
import time
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# ✅ Path to your ChromeDriver
CHROMEDRIVER_PATH = r"C:\Users\VAmsham1\chromedriver\chromedriver.exe"

# ✅ Load URL from JSON
json_path = Path("data/pages_json/discovered_links.json")
output_dir = Path("output_markdown")
output_dir.mkdir(parents=True, exist_ok=True)

with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

url = data[0]["url"]  # Use the first URL
print(f"🌐 Crawling: {url}")

# ✅ Set up Selenium with ChromeDriver
options = Options()
options.add_argument("--headless")  # You can remove this line if you want to see the browser
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

try:
    driver.get(url)
    time.sleep(3)  # Wait for page to fully load

    # ✅ Try expanding any buttons or tabs
    driver.execute_script("""
        document.querySelectorAll('[role=button], .accordion, summary').forEach(el => {
            try { el.click(); } catch(e) {}
        });
    """)
    time.sleep(1.5)

    html = driver.page_source
    soup = BeautifulSoup(html, "lxml")

    # ✅ Extract Title and Sections
    title = soup.title.get_text(strip=True) if soup.title else "no_title"
    title_slug = urlparse(url).path.strip("/").replace("/", "_") or "index"
    md_lines = [f"# {title}", f"URL: {url}", ""]

    # Extract all h2/h3 sections and paragraphs
    for section in soup.select("h2, h3"):
        heading = section.get_text(strip=True)
        md_lines.append(f"## {heading}")
        content = []
        for sibling in section.find_next_siblings():
            if sibling.name in ["h2", "h3"]:
                break
            text = sibling.get_text(strip=True)
            if text:
                content.append(text)
        md_lines.extend(content)
        md_lines.append("")

    # ✅ Save as Markdown
    md_output = "\n".join(md_lines)
    output_file = output_dir / f"{title_slug}.md"
    output_file.write_text(md_output, encoding="utf-8")

    print(f"✅ Saved Markdown to {output_file}")

finally:
    driver.quit()



import os
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from pathlib import Path

# Setup
URL = "https://magentapulse.t-mobile.com/us/en/customer-support/plans/business/phones/business-unlimited-enterprise-subsidy-2-0"
OUTPUT_DIR = Path("output_markdown")
OUTPUT_DIR.mkdir(exist_ok=True)

# File-safe name
def sanitize_filename(url):
    return re.sub(r'\W+', '_', url).strip('_')

# Setup ChromeDriver (headless optional)
options = Options()
options.add_argument("--headless=new")
driver = webdriver.Chrome(service=ChromeService(), options=options)

# Load page
print(f"🌐 Crawling: {URL}")
driver.get(URL)
time.sleep(3)
soup = BeautifulSoup(driver.page_source, "html.parser")
driver.quit()

# Start writing markdown
filename = sanitize_filename(URL) + ".md"
filepath = OUTPUT_DIR / filename

with filepath.open("w", encoding="utf-8") as f:
    f.write(f"# {soup.title.string.strip()}\n")
    f.write(f"URL: {URL}\n\n")

    headers = soup.find_all(["h2", "h3"])
    for header in headers:
        heading_text = header.get_text(strip=True)
        f.write(f"## {heading_text}\n\n")

        section_content = []

        for sibling in header.find_next_siblings():
            if sibling.name in ["h2", "h3"]:
                break

            # Paragraphs
            if sibling.name == "p":
                text = sibling.get_text(strip=True)
                if text:
                    section_content.append(text)

            # Lists
            elif sibling.name in ["ul", "ol"]:
                for li in sibling.find_all("li"):
                    section_content.append(f"- {li.get_text(strip=True)}")

            # Tables
            elif sibling.name == "table":
                rows = sibling.find_all("tr")
                for i, row in enumerate(rows):
                    cols = [col.get_text(strip=True) for col in row.find_all(["td", "th"])]
                    line = " | ".join(cols)
                    section_content.append(line)
                    if i == 0:
                        section_content.append("|".join(["---"] * len(cols)))  # Markdown table divider

            # Generic divs or spans
            elif sibling.name in ["div", "span"]:
                text = sibling.get_text(strip=True)
                if text:
                    section_content.append(text)

        if section_content:
            f.write("\n".join(section_content))
            f.write("\n\n")

print(f"✅ Saved to {filepath}")




import json
import time
import re
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# ✅ Path to your manually downloaded ChromeDriver
CHROMEDRIVER_PATH = r"C:\Users\VAmsham1\chromedriver\chromedriver.exe"

# ✅ Paths for input/output
INPUT_JSON = Path("data/pages_json/discovered_links.json")
OUTPUT_DIR = Path("output_markdown")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ✅ Utility: create a safe filename from URL
def sanitize_filename(url):
    return re.sub(r'\W+', '_', url).strip('_')

# ✅ Load first URL from your JSON
with INPUT_JSON.open(encoding="utf-8") as f:
    data = json.load(f)

url = data[0]["url"]
anchor_text = data[0].get("anchor_text", "Untitled Plan")
print(f"🌐 Crawling: {url}")

# ✅ Set up Selenium (headless Chrome)
options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

try:
    # Open the URL
    driver.get(url)
    time.sleep(3)  # Wait for full load

    # ✅ Try expanding all interactive/tab/accordion elements
    driver.execute_script("""
        document.querySelectorAll('[role=button], .accordion, summary').forEach(el => {
            try { el.click(); } catch(e) {}
        });
    """)
    time.sleep(1.5)

    # ✅ Parse the full DOM
    soup = BeautifulSoup(driver.page_source, "lxml")

    # ✅ File naming
    title_slug = sanitize_filename(url)
    md_file = OUTPUT_DIR / f"{title_slug}.md"

    # ✅ Markdown building
    md_lines = [f"# {anchor_text}", f"URL: {url}", ""]

    # Loop through each h2/h3 section
    headers = soup.find_all(["h2", "h3"])
    for header in headers:
        heading_text = header.get_text(strip=True)
        md_lines.append(f"## {heading_text}\n")

        section_content = []

        for sibling in header.find_next_siblings():
            if sibling.name in ["h2", "h3"]:
                break

            # Paragraphs
            if sibling.name == "p":
                text = sibling.get_text(strip=True)
                if text:
                    section_content.append(text)

            # Lists
            elif sibling.name in ["ul", "ol"]:
                for li in sibling.find_all("li"):
                    section_content.append(f"- {li.get_text(strip=True)}")

            # Tables
            elif sibling.name == "table":
                rows = sibling.find_all("tr")
                for i, row in enumerate(rows):
                    cols = [col.get_text(strip=True) for col in row.find_all(["td", "th"])]
                    if not cols:
                        continue
                    section_content.append(" | ".join(cols))
                    if i == 0:
                        section_content.append("|".join(["---"] * len(cols)))

            # Generic div/span
            elif sibling.name in ["div", "span"]:
                text = sibling.get_text(strip=True)
                if text:
                    section_content.append(text)

        # Write section content
        if section_content:
            md_lines.extend(section_content)
            md_lines.append("")

    # ✅ Write to .md file
    md_text = "\n".join(md_lines)
    md_file.write_text(md_text, encoding="utf-8")

    print(f"✅ Saved Markdown to: {md_file}")

finally:
    driver.quit()
