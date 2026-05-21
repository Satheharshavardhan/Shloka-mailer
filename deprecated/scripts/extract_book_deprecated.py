import pdfplumber
import json
import re

PDF_PATH = "parasharaharashasatara-brihat-parashar-hora-shastra.pdf"

chunks = []

with pdfplumber.open(PDF_PATH) as pdf:

    for page_num, page in enumerate(pdf.pages, start=1):

        text = page.extract_text()

        if text:

            text = re.sub(r"\s+", " ", text).strip()

            chunks.append({"page": page_num, "content": text})

with open("book_chunks.json", "w", encoding="utf-8") as f:
    json.dump(chunks, f, ensure_ascii=False, indent=2)

print(f"Saved {len(chunks)} chunks.")
