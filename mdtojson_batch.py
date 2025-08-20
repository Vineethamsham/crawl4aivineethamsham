import re, json
from pathlib import Path

INPUT_DIR = Path("output_markdown")
OUTPUT_DIR = Path("output_json")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

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

        # Skip empty lines
        if not stripped:
            continue

        # Title
        if stripped.startswith("# ") and not result["title"]:
            result["title"] = stripped[2:].strip()
            continue

        # URL
        if stripped.startswith("URL: "):
            result["url"] = stripped[5:].strip()
            continue

        # Heading
        if re.match(r"^#{2,4} ", stripped):
            if current_section:
                result["sections"].append(current_section)
            current_section = {
                "heading": stripped.lstrip("#").strip(),
                "content": []
            }
            continue

        # Bullet or paragraph or table
        if current_section:
            current_section["content"].append(stripped)
        else:
            # If we get content before any heading
            if not result.get("intro"):
                result["intro"] = []
            result["intro"].append(stripped)

    if current_section:
        result["sections"].append(current_section)

    return result

def process_all_markdowns():
    md_files = list(INPUT_DIR.glob("*.md"))

    for md_path in md_files:
        with md_path.open(encoding="utf-8") as f:
            md_content = f.read()

        parsed_json = parse_markdown_to_json(md_content)

        output_filename = md_path.stem + ".json"
        output_path = OUTPUT_DIR / output_filename

        with output_path.open("w", encoding="utf-8") as f:
            json.dump(parsed_json, f, indent=2, ensure_ascii=False)

        print(f"✅ Converted: {md_path.name} → {output_filename}")

if __name__ == "__main__":
    process_all_markdowns()
