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
