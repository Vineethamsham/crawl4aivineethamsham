import os, json, time, base64, tempfile
from pathlib import Path
import undetected_chromedriver.v2 as uc
from selenium.webdriver.common.by import By

# === ✅ Paths
ROOT = Path(__file__).resolve().parents[1]
LINKS_JSON = ROOT / "discovered_links_all.json"
PDF_DIR = ROOT / "data" / "pdfs"
PDF_DIR.mkdir(parents=True, exist_ok=True)

# === ✅ Setup Chrome
options = uc.ChromeOptions()
options.headless = True
user_data_dir = tempfile.mkdtemp()
options.add_argument(f"--user-data-dir={user_data_dir}")
driver = uc.Chrome(options=options, use_subprocess=True)

# === ✅ Helper
def save_pdf_from_url(url):
    try:
        print(f"🌐 Visiting: {url}")
        driver.get(url)
        time.sleep(3)

        # Expand accordions, summary, buttons
        driver.execute_script("""
            document.querySelectorAll('summary, [role=button], .cmp-accordion__button, .cmp-tabs__tab').forEach(el => {
                try { el.click(); } catch(e) {}
            });
        """)
        time.sleep(2)

        # Scroll to bottom to load lazy content
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        # Get title for filename
        try:
            title = driver.find_element(By.TAG_NAME, "h1").text.strip()
        except:
            title = "Untitled"

        safe_title = "".join(c if c.isalnum() else "-" for c in title)[:80]
        file_path = PDF_DIR / f"{safe_title}.pdf"

        # Use DevTools Protocol to save PDF
        result = driver.execute_cdp_cmd("Page.printToPDF", {
            "printBackground": True,
            "preferCSSPageSize": True
        })
        with open(file_path, "wb") as f:
            f.write(base64.b64decode(result['data']))

        print(f"✅ Saved: {file_path.name}")

    except Exception as e:
        print(f"❌ Error for {url}: {e}")

# === ✅ Main
def main():
    urls = json.loads(LINKS_JSON.read_text(encoding="utf-8"))
    for item in urls:
        url = item.get("url")
        if url:
            save_pdf_from_url(url)

    driver.quit()

if __name__ == "__main__":
    main()
