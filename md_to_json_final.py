import re, json
from pathlib import Path

# === 📁 Directories ===
INPUT_DIR = Path("data/markdown")
OUTPUT_DIR = Path("data/json_test")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# === 🧠 Parser Logic ===
def parse_markdown(md_text):
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

        # Title
        if stripped.startswith("# ") and not result["title"]:
            result["title"] = stripped[2:].strip()
            continue

        # URL
        if stripped.lower().startswith("url:") and not result["url"]:
            result["url"] = stripped.split(":", 1)[1].strip()
            continue

        # Heading (##, ###, ####)
        if re.match(r"^#{2,4} ", stripped):
            if current_section:
                result["sections"].append(current_section)
            current_section = {
                "heading": stripped.lstrip("#").strip(),
                "content": []
            }
            continue

        # Content inside section
        if current_section:
            current_section["content"].append(stripped)
        else:
            # Content before any section (optional)
            if not result.get("intro"):
                result["intro"] = []
            result["intro"].append(stripped)

    if current_section:
        result["sections"].append(current_section)

    return result

# === 🔁 Batch Processor ===
def convert_all_markdowns():
    md_files = list(INPUT_DIR.glob("*.md"))

    for md_path in md_files:
        with md_path.open(encoding="utf-8") as f:
            md_text = f.read()

        parsed = parse_markdown(md_text)
        output_path = OUTPUT_DIR / (md_path.stem + ".json")

        with output_path.open("w", encoding="utf-8") as f:
            json.dump(parsed, f, indent=2, ensure_ascii=False)

        print(f"✅ Converted: {md_path.name} → {output_path.name}")

# === 🚀 Entry Point ===
if __name__ == "__main__":
    convert_all_markdowns()
