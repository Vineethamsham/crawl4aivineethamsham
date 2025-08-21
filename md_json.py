import re
import json
from pathlib import Path

# === 📁 Set paths ===
INPUT_DIR = Path("data/markdown")  # Folder with .md files
OUTPUT_DIR = Path("data/json_output")  # Folder to save .json files
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# === 🧠 Markdown → JSON Parser ===
def parse_markdown_to_json(md_text):
    lines = md_text.splitlines()
    result = {
        "title": "",
        "url": "",
        "sections": []
    }

    current_section = None

    for line in lines:
        stripped = line.strip()

        if not stripped:
            continue

        # Page title
        if stripped.startswith("# ") and not result["title"]:
            result["title"] = stripped[2:].strip()
            continue

        # Page URL
        if stripped.lower().startswith("url:"):
            result["url"] = stripped.split(":", 1)[-1].strip()
            continue

        # New section heading
        if re.match(r"^#{2,4} ", stripped):
            if current_section:
                result["sections"].append(current_section)
            current_section = {
                "heading": stripped.lstrip("#").strip(),
                "content": []
            }
            continue

        # Add content to current section
        if current_section:
            current_section["content"].append(stripped)
        else:
            # Handle content before any section heading (e.g., intro)
            if not result.get("intro"):
                result["intro"] = []
            result["intro"].append(stripped)

    # Save the last section
    if current_section:
        result["sections"].append(current_section)

    return result

# === 🚀 Batch Process All .md Files ===
def process_all_markdowns():
    md_files = list(INPUT_DIR.glob("*.md"))

    for md_file in md_files:
        with md_file.open(encoding="utf-8") as f:
            md_text = f.read()

        parsed = parse_markdown_to_json(md_text)

        output_filename = md_file.stem + ".json"
        output_path = OUTPUT_DIR / output_filename

        with output_path.open("w", encoding="utf-8") as f:
            json.dump(parsed, f, indent=2, ensure_ascii=False)

        print(f"✅ Converted: {md_file.name} → {output_filename}")

if __name__ == "__main__":
    process_all_markdowns()
