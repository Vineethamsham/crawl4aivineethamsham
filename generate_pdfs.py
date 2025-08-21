from pathlib import Path
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from urllib.parse import quote
import base64

# Paths
ROOT = Path(__file__).parent.parent
LINKS_PATH = ROOT / "data" / "pages_json" / "discovered_links_all.json"
PDF_DIR = ROOT / "data" / "pdf"
PDF_DIR.mkdir(parents=True, exist_ok=True)

# Chrome driver setup
CHROME_DRIVER_PATH = r"C:\Users\YourUser\chromedriver\chromedriver.exe"
BASE_OPTIONS = Options()
BASE_OPTIONS.add_argument("--headless=new")
BASE_OPTIONS.add_argument("--disable-gpu")
BASE_OPTIONS.add_argument("--no-sandbox")
BASE_OPTIONS.add_argument("--window-size=1920,1080")

def save_page_as_pdf(driver, url, output_path):
    driver.get(url)
    time.sleep(2)  # allow JS/content to load
    
    # Expand all accordion and tab elements if needed
    driver.execute_script("""
        document.querySelectorAll('[role=button], summary, .cmp-accordion__button, .cmp-tabs__tab').forEach(el => {
            try { el.click(); } catch(e) {}
        });
    """)
    time.sleep(1)
    
    pdf_data = driver.execute_cdp_cmd("Page.printToPDF", {
        "printBackground": True,
        "paperWidth": 8.5,
        "paperHeight": 11,
        "marginTop": 0,
        "marginBottom": 0,
        "marginLeft": 0,
        "marginRight": 0
    })
    
    with open(output_path, "wb") as f:
        f.write(base64.b64decode(pdf_data['data']))

def main():
    links = json.loads(LINKS_PATH.read_text(encoding="utf-8"))
    driver = webdriver.Chrome(service=ChromeService(CHROME_DRIVER_PATH), options=BASE_OPTIONS)

    for item in links:
        url = item["url"]
        safe_name = quote(url, safe="").replace("%", "_")
        out_path = PDF_DIR / f"{safe_name}.pdf"
        try:
            print(f"Saving PDF for: {url}")
            save_page_as_pdf(driver, url, out_path)
            print(f"✅ Saved: {out_path.name}")
        except Exception as e:
            print(f"❌ Failed for {url}: {e}")

    driver.quit()

if __name__ == "__main__":
    main()
