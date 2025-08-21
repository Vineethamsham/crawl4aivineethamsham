import json, re, time
from pathlib import Path
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options

# === Config ===
ROOT = Path(__file__).resolve().parents[2]
LINKS_PATH = ROOT / "data" / "pages_json" / "discovered_links_all.json"
OUTPUT_DIR = ROOT / "data" / "markdown"
CHROMEDRIVER_PATH = r"C:\Users\VAmsham1\chromedriver\chromedriver.exe"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# === Noise filter ===
NOISE_FILTER = ["skip to main", "navigation", "my stuff", "log out", "resources", "employee services", "bookmarks"]

def sanitize_filename(url):
    return re.sub(r'\W+', '_', url).strip('_')

def extract_clean_markdown(soup):
    markdown_lines = []

    # Focus only on main content
    for container in soup.select(".cmp-container, .cmp-layoutcontainer, .aem-Grid"):
        if any(n in container.get_text().lower() for n in NOISE_FILTER):
            continue

        current_heading = None
        buffer = []

        for tag in container.descendants:
            if tag.name in ["h2", "h3", "h4"]:
                # flush previous section
                if current_heading:
                    markdown_lines.append(current_heading)
                    markdown_lines.extend(buffer)
                    markdown_lines.append("")  # blank line between sections
                buffer = []
                level = "#" * int(tag.name[1])
                heading_text = tag.get_text(strip=True)
                if heading_text:
                    current_heading = f"{level} {heading_text}"

            elif tag.name == "p":
                text = tag.get_text(strip=True)
                if text and not any(n in text.lower() for n in NOISE_FILTER):
                    buffer.append(text)

            elif tag.name == "li":
                text = tag.get_text(strip=True)
                if text and not any(n in text.lower() for n in NOISE_FILTER):
                    buffer.append(f"- {text}")

            elif tag.name == "table":
                rows = tag.find_all("tr")
                for i, row in enumerate(rows):
                    cols = [col.get_text(strip=True) for col in row.find_all(["td", "th"])]
                    if not cols:
                        continue
                    buffer.append(" | ".join(cols))
                    if i == 0:
                        buffer.append("|" + "|".join(["---"] * len(cols)) + "|")

        # flush final section
        if current_heading:
            markdown_lines.append(current_heading)
            markdown_lines.extend(buffer)
            markdown_lines.append("")

    return "\n".join(markdown_lines)

def process_url(url):
    print(f"🌐 Crawling: {url}")
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=ChromeService(CHROMEDRIVER_PATH), options=options)

    try:
        driver.get(url)
        time.sleep(3)

        # Expand all accordions and tabs
        driver.execute_script("""
            document.querySelectorAll('[role=button], summary, .cmp-accordion__button, .cmp-tabs__tab').forEach(el => {
                try { el.click(); } catch(e) {}
            });
        """)
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        title = soup.title.string.strip() if soup.title else "Untitled"
        filename = sanitize_filename(url) + ".md"
        filepath = OUTPUT_DIR / filename
        content = extract_clean_markdown(soup)

        with filepath.open("w", encoding="utf-8") as f:
            f.write(f"# {title}\n")
            f.write(f"URL: {url}\n\n")
            f.write(content or "_No content extracted._")

        print(f"✅ Saved: {filepath.name}")

    finally:
        driver.quit()

def main():
    links = json.loads(LINKS_PATH.read_text(encoding="utf-8"))
    for item in links:
        url = item["url"]
        try:
            process_url(url)
        except Exception as e:
            print(f"❌ Failed for {url} → {e}")

if __name__ == "__main__":
    main()
