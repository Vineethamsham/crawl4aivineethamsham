import re
import json
from pathlib import Path

# === 📁 File paths ===
MD_PATH = Path("output_markdown/https_magentapulse_t_mobile_com_us_en_customer_support_plans_business_phones_business_unlimited_enterprise_subsidy_2_0.md")
JSON_OUT = Path("output_json") / MD_PATH.with_suffix(".json").name
JSON_OUT.parent.mkdir(parents=True, exist_ok=True)

# === 🧠 Markdown to JSON parser ===
def parse_markdown(md_text):
    lines = md_text.splitlines()
    result = {"title": None, "url": None, "sections": []}

    current_section = None

    for line in lines:
        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        # Detect Title
        if result["title"] is None and line.startswith("# "):
            result["title"] = line[2:].strip()

        # Detect URL line
        elif result["url"] is None and line.lower().startswith("url:"):
            result["url"] = line.split(":", 1)[-1].strip()

        # Detect new section
        elif line.startswith("## "):
            if current_section:
                result["sections"].append(current_section)
            current_section = {"heading": line[3:].strip(), "content": []}

        # Add content to section
        elif current_section:
            current_section["content"].append(line)

    # Append final section
    if current_section:
        result["sections"].append(current_section)

    return result

# === 🚀 Run the parser ===
with MD_PATH.open("r", encoding="utf-8") as f:
    markdown_text = f.read()

parsed = parse_markdown(markdown_text)

# === 💾 Save to JSON ===
with JSON_OUT.open("w", encoding="utf-8") as f:
    json.dump(parsed, f, indent=2, ensure_ascii=False)

print(f"✅ JSON saved: {JSON_OUT}")
