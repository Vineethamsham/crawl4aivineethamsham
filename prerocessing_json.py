import re, json
from pathlib import Path
from collections import defaultdict

INPUT_DIR = Path("output_json")
OUTPUT_DIR = Path("output_json_cleaned")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NOISE_TERMS = [
    "skip to main", "my stuff", "log out", "navigation", "bookmarks", "resources", "news & events"
]

def is_noisy(text):
    text_lower = text.lower()
    return any(term in text_lower for term in NOISE_TERMS)

def clean_section_content(content):
    cleaned = []
    seen_lines = set()

    for line in content:
        line = line.strip()
        if not line or is_noisy(line):
            continue
        if line in seen_lines:
            continue
        seen_lines.add(line)
        cleaned.append(line)
    
    return cleaned

def merge_duplicate_sections(sections):
    merged = defaultdict(list)

    for section in sections:
        heading = section.get("heading", "").strip()
        content = clean_section_content(section.get("content", []))
        if not content:
            continue
        merged[heading].extend(content)

    return [{"heading": heading, "content": list(dict.fromkeys(contents))} for heading, contents in merged.items()]

def clean_json_file(json_data):
    cleaned = {
        "title": json_data.get("title", "").strip(),
        "url": json_data.get("url", "").strip(),
        "sections": merge_duplicate_sections(json_data.get("sections", []))
    }

    if "intro" in json_data:
        intro = clean_section_content(json_data["intro"])
        if intro:
            cleaned["intro"] = intro

    return cleaned

def process_all_jsons():
    for path in INPUT_DIR.glob("*.json"):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        cleaned = clean_json_file(data)
        out_path = OUTPUT_DIR / path.name

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(cleaned, f, indent=2, ensure_ascii=False)

        print(f"✅ Cleaned: {path.name} → {out_path.name}")

if __name__ == "__main__":
    process_all_jsons()
