from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json
import re

# --- Configuration ---
CHROMEDRIVER_PATH = r"C:\Users\VAmsham1\chromedriver\chromedriver.exe"
JSON_PATH = Path("data/pages_json/discovered_links.json")
OUTPUT_DIR = Path("output_markdown")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# --- Load one URL from JSON ---
with open(JSON_PATH, "r", encoding="utf-8") as f:
    url = json.load(f)[0]["url"]
print(f"🌐 Crawling: {url}")

# --- Setup Chrome WebDriver ---
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

service = Service(executable_path=CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=chrome_options)

# --- Visit Page ---
driver.get(url)
driver.implicitly_wait(5)  # wait for content

# --- Extract Page Content ---
soup = BeautifulSoup(driver.page_source, "html.parser")
driver.quit()

# --- Extract Sections ---
sections = soup.find_all(["h2", "h3", "h4", "p", "ul", "ol"])
content_blocks = []

for tag in sections:
    tag_name = tag.name
    tag_text = tag.get_text(strip=True)
    if tag_name in ["h2", "h3"]:
        content_blocks.append(f"\n## {tag_text}\n")
    elif tag_name == "h4":
        content_blocks.append(f"\n### {tag_text}\n")
    elif tag_name == "p":
        content_blocks.append(f"{tag_text}\n")
    elif tag_name in ["ul", "ol"]:
        for li in tag.find_all("li"):
            content_blocks.append(f"- {li.get_text(strip=True)}\n")

markdown = f"# {soup.title.string.strip() if soup.title else 'Document'}\n"
markdown += f"URL: {url}\n\n"
markdown += "".join(content_blocks)

# --- Save to Markdown File ---
def url_to_filename(url: str) -> str:
    name = url.replace("https://", "").replace("http://", "").replace("/", "_")
    return re.sub(r'\W+', '_', name) + ".md"

output_file = OUTPUT_DIR / url_to_filename(url)
with open(output_file, "w", encoding="utf-8") as f:
    f.write(markdown)

print(f"✅ Saved Markdown to {output_file}")
