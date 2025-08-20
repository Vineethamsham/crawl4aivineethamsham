import re, json
from pathlib import Path

# === 📁 Folder paths ===
INPUT_DIR = Path("output_markdown")
OUTPUT_DIR = Path("output_json")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# === 🔁 Markdown to JSON parser ===
def parse_markdown_to_json(md_text):
    lines = md_text.splitlines()
    result = {
        "title": "",
        "url": "",
        "intro": [],
        "sections": []
    }

    current_section = None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Title
        if stripped.startswith("# ") and not result["title"]:
            result["title"] = stripped[2:].strip()
            continue

        # URL
        if stripped.lower().startswith("url:") and not result["url"]:
            result["url"] = stripped.split(":", 1)[1].strip()
            continue

        # Section Headings (##, ###, ####)
        if re.match(r"^#{2,4} ", stripped):
            if current_section:
                result["sections"].append(current_section)
            current_section = {
                "heading": stripped.lstrip("#").strip(),
                "content": []
            }
            continue

        # Content (bullets, paragraphs, table rows)
        if current_section:
            current_section["content"].append(stripped)
        else:
            result["intro"].append(stripped)

    if current_section:
        result["sections"].append(current_section)

    return result

# === 🗂️ Process all markdown files ===
def process_all_markdowns():
    md_files = sorted(INPUT_DIR.glob("*.md"))

    for md_path in md_files:
        with md_path.open(encoding="utf-8") as f:
            md_content = f.read()

        parsed_json = parse_markdown_to_json(md_content)
        output_filename = md_path.stem + ".json"
        output_path = OUTPUT_DIR / output_filename

        with output_path.open("w", encoding="utf-8") as f:
            json.dump(parsed_json, f, indent=2, ensure_ascii=False)

        print(f"✅ Converted: {md_path.name} → {output_filename}")

# === 🚀 Entry Point ===
if __name__ == "__main__":
    process_all_markdowns()
