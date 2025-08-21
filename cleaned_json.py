import json
from pathlib import Path

INPUT_DIR = Path("data/json_test")
OUTPUT_DIR = Path("data/json_cleaned")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NOISE_PATTERNS = [
    "skip to main", "log out", "navigation", "my stuff",
    "notifications", "bookmarks", "employee services"
]

def is_noise(text):
    text_lower = text.lower()
    return any(noise in text_lower for noise in NOISE_PATTERNS)

def dedupe_lines(lines):
    seen = set()
    cleaned = []
    for line in lines:
        line = line.strip()
        if not line or is_noise(line):
            continue
        if line not in seen:
            cleaned.append(line)
            seen.add(line)
    return cleaned

def clean_json_file(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    cleaned_sections = []
    section_signatures = set()

    for section in data.get("sections", []):
        heading = section.get("heading", "").strip()
        content = dedupe_lines(section.get("content", []))

        # Create a unique hashable signature
        signature = (heading, tuple(content))
        if signature not in section_signatures and content:
            section_signatures.add(signature)
            cleaned_sections.append({
                "heading": heading,
                "content": content
            })

    data["sections"] = cleaned_sections

    if "intro" in data:
        data["intro"] = dedupe_lines(data["intro"])

    return data

def process_all_files():
    for json_path in INPUT_DIR.glob("*.json"):
        cleaned_data = clean_json_file(json_path)

        output_path = OUTPUT_DIR / json_path.name
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(cleaned_data, f, indent=2, ensure_ascii=False)

        print(f"✅ Cleaned: {json_path.name} → {output_path.name}")

if __name__ == "__main__":
    process_all_files()
