import argparse
import json
import os
import re
import sys
import time
import requests
from bs4 import BeautifulSoup
import translators as ts
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "https://enjoylearningsanskrit.com/scriptures/parashara/chapter-"
MAX_CHAPTERS = 97
OUTPUT_FILE = "structured_shlokas.json"
RAW_FILE = os.path.join(
    os.path.dirname(__file__), "deprecated", "data", "structured_shlokas_raw.json"
)
MAX_RETRIES = 3
TRANSLATE_DELAY = 0.5
PROGRESS_FILE = "translate_progress.json"


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\r", " ").replace("\n", " ")
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"^\d+\.\s*", "", text)
    return text


def fetch_chapter_html(chapter_num: int) -> str:
    url = f"{BASE_URL}{chapter_num}"
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                return response.text
            last_error = f"HTTP {response.status_code}"
        except Exception as exc:
            last_error = str(exc)
        if attempt < MAX_RETRIES:
            time.sleep(2 * attempt)
    raise RuntimeError(f"Chapter {chapter_num}: {last_error}")


def scrape_chapter(chapter_num: int) -> tuple[int, list[dict] | None]:
    try:
        html = fetch_chapter_html(chapter_num)
        soup = BeautifulSoup(html, "html.parser")
        verse_wrappers = soup.find_all("div", class_="verse-wrapper")

        if not verse_wrappers:
            raise RuntimeError("no verse-wrapper elements found")

        chapter_shlokas = []
        for shloka_count, wrapper in enumerate(verse_wrappers, start=1):
            devanagari_div = wrapper.find("div", class_="verse-devanagari")
            sanskrit_text = clean_text(devanagari_div.get_text()) if devanagari_div else ""

            eng_div = wrapper.find("div", class_="verse-translation_en")
            english_text = clean_text(eng_div.get_text()) if eng_div else ""

            trans_div = wrapper.find("div", class_="verse-transliteration")
            transliteration_text = clean_text(trans_div.get_text()) if trans_div else ""

            sandhi_div = wrapper.find("div", class_="verse-no-sandhi")
            separated_sandhi_text = clean_text(sandhi_div.get_text()) if sandhi_div else ""

            if not sanskrit_text or not english_text:
                print(
                    f"  Chapter {chapter_num}, shloka {shloka_count}: "
                    "skipped (missing sanskrit or english)"
                )
                continue

            chapter_shlokas.append(
                {
                    "chapter": f"Chapter {chapter_num}",
                    "shloka": str(shloka_count),
                    "sanskrit": sanskrit_text,
                    "transliteration": transliteration_text,
                    "separated_sandhi": separated_sandhi_text,
                    "english": english_text,
                    "commentary": "",
                }
            )

        print(f"Chapter {chapter_num}: scraped {len(chapter_shlokas)} shlokas")
        return chapter_num, chapter_shlokas
    except Exception as exc:
        print(f"Chapter {chapter_num} SCRAPE FAILED: {exc}")
        return chapter_num, None


def scrape_all(max_chapters: int = MAX_CHAPTERS) -> list[dict]:
    all_shlokas_dict: dict[int, list[dict]] = {}
    failed: list[int] = []

    print(f"Phase 1: scraping {max_chapters} chapters...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(scrape_chapter, c): c
            for c in range(1, max_chapters + 1)
        }
        for future in as_completed(futures):
            chapter_num, shlokas = future.result()
            if shlokas is None:
                failed.append(chapter_num)
            else:
                all_shlokas_dict[chapter_num] = shlokas

    if failed:
        raise RuntimeError(f"Scrape failed for chapters: {sorted(failed)}")

    all_shlokas = []
    for chapter_num in range(1, max_chapters + 1):
        all_shlokas.extend(all_shlokas_dict[chapter_num])

    with open(RAW_FILE, "w", encoding="utf-8") as f:
        json.dump(all_shlokas, f, ensure_ascii=False, indent=2)

    print(f"Phase 1 complete: {len(all_shlokas)} shlokas saved to {RAW_FILE}")
    return all_shlokas


def translate_text_with_retry(text: str) -> str:
    for attempt in range(1, 8):
        try:
            result = ts.translate_text(
                text,
                translator="bing",
                from_language="en",
                to_language="hi",
            )
            return clean_text(result)
        except Exception as exc:
            wait = min(90, 5 * attempt)
            print(f"    Retry in {wait}s ({exc})")
            time.sleep(wait)
    raise RuntimeError(f"Translation failed: {text[:60]}...")


def load_translate_progress() -> int:
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, encoding="utf-8") as f:
            return json.load(f).get("completed", 0)
    return 0


def save_translate_progress(completed: int) -> None:
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump({"completed": completed}, f)


def translate_all(shlokas: list[dict]) -> list[dict]:
    start_index = load_translate_progress()
    total = len(shlokas)

    print(f"Phase 2: translating {total} shlokas via Bing (from {start_index + 1})...")

    for i in range(start_index, total):
        if i % 25 == 0:
            print(f"  Progress: {i}/{total} ({100 * i // total}%)")

        shlokas[i]["hindi"] = translate_text_with_retry(shlokas[i]["english"])

        if (i + 1) % 10 == 0:
            save_translate_progress(i + 1)
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(shlokas, f, ensure_ascii=False, indent=2)

        time.sleep(TRANSLATE_DELAY)

    if os.path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)

    return shlokas


def scrape_and_translate(max_chapters: int = MAX_CHAPTERS) -> None:
    shlokas = scrape_all(max_chapters)
    shlokas = translate_all(shlokas)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(shlokas, f, ensure_ascii=False, indent=2)

    print(f"Done. Saved {len(shlokas)} shlokas to {OUTPUT_FILE}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--translate-only",
        action="store_true",
        help="Translate existing raw JSON without re-scraping",
    )
    args = parser.parse_args()

    if args.translate_only:
        if not os.path.exists(RAW_FILE):
            print(f"Missing {RAW_FILE}. Run full scrape first.", file=sys.stderr)
            sys.exit(1)
        start_index = load_translate_progress()
        if start_index > 0 and os.path.exists(OUTPUT_FILE):
            with open(OUTPUT_FILE, encoding="utf-8") as f:
                shlokas = json.load(f)
            print(f"Resuming from checkpoint at shloka {start_index + 1}")
        else:
            with open(RAW_FILE, encoding="utf-8") as f:
                shlokas = json.load(f)
        shlokas = translate_all(shlokas)
        print(f"Done. Saved {len(shlokas)} shlokas to {OUTPUT_FILE}.")
    else:
        scrape_and_translate()
