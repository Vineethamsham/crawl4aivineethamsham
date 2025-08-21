import json, re, time
from pathlib import Path
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from urllib.parse import urlparse

# === ✅ Config ===
ROOT = Path(__file__).resolve().parents[1]
LINKS_PATH = ROOT / "data" / "pages_json" / "discovered_links_all.json"
MARKDOWN_DIR = ROOT / "data" / "markdown"
CHROMEDRIVER_PATH = r"C:\\Users\\VAmsham1\\chromedriver\\chromedriver.exe"
MARKDOWN_DIR.mkdir(parents=True, exist_ok=True)

# === ✅ Clean filename ===
def sanitize_filename(url):
    parsed = urlparse(url)
    return re.sub(r'\W+', '_', parsed.path).strip('_') + ".md"

# === ✅ Extract readable text ===
def extract_markdown(soup):
    md = []
    for section in soup.select(".cmp-container, .cmp-layoutcontainer, .aem-Grid"):
        for tag in section.find_all(["h2", "h3", "h4", "p", "li", "table"]):
            text = tag.get_text(strip=True)
            if not text or any(skip in text.lower() for skip in ["bookmarks", "navigation", "toolbox"]):
                continue
            if tag.name.startswith("h"):
                md.append("#" * int(tag.name[1]) + f" {text}")
            elif tag.name == "li":
                md.append(f"- {text}")
            elif tag.name == "table":
                rows = tag.find_all("tr")
                for i, row in enumerate(rows):
                    cols = [c.get_text(strip=True) for c in row.find_all(["th", "td"])]
                    if cols:
                        if i == 0:
                            md.append(" | ".join(cols))
                            md.append(" | ".join(["---"] * len(cols)))
                        else:
                            md.append(" | ".join(cols))
            else:
                md.append(text)
        md.append("")  # spacing
    return "\n".join(md)

# === ✅ Expand and render HTML fully ===
def fetch_and_convert(url):
    print(f"🔍 Visiting: {url}")
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=ChromeService(CHROMEDRIVER_PATH), options=options)
    driver.get(url)
    time.sleep(3)
    driver.execute_script("""
        document.querySelectorAll('[role=button], summary, .cmp-accordion__button, .cmp-tabs__tab').forEach(el => {
            try { el.click(); } catch(e) {}
        });
    """)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    title = soup.title.get_text(strip=True) if soup.title else "Untitled"
    filename = sanitize_filename(url)
    with (MARKDOWN_DIR / filename).open("w", encoding="utf-8") as f:
        f.write(f"# {title}\n")
        f.write(f"URL: {url}\n\n")
        f.write(extract_markdown(soup))
    driver.quit()
    print(f"✅ Saved: {filename}")

# === ✅ Main ===
def main():
    links = json.loads(LINKS_PATH.read_text(encoding="utf-8"))
    for item in links:
        try:
            fetch_and_convert(item["url"])
        except Exception as e:
            print(f"❌ Error: {item['url']} → {e}")

if __name__ == "__main__":
    main()
