"""
Build the email header from a museum Navagraha relief (all nine grahas, one row).

Primary source (CC0 / public domain, Cleveland Museum of Art, Wikimedia):
  Lintel with the Nine Planets (Navagrahas), 7th–8th century CE
  https://commons.wikimedia.org/wiki/File:India,_central_India,_7th_-_8th_century_-_Lintel_with_the_Nine_Planets-_Navagrahas_-_1971.61_-_Cleveland_Museum_of_Art.jpg
"""

import os
import urllib.request

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

W, H = 680, 240
ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(ASSETS_DIR, "header.png")
SOURCE_PATH = os.path.join(ASSETS_DIR, "navagraha_source.jpg")

LINTEL_URL = (
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/"
    "India%2C_central_India%2C_7th_-_8th_century_-_Lintel_with_the_Nine_Planets-"
    "Navagrahas_-_1971.61_-_Cleveland_Museum_of_Art.jpg/"
    "1280px-India%2C_central_India%2C_7th_-_8th_century_-_Lintel_with_the_Nine_Planets-"
    "Navagrahas_-_1971.61_-_Cleveland_Museum_of_Art.jpg"
)


def download_source() -> None:
    if os.path.isfile(SOURCE_PATH):
        return
    print("Downloading Navagraha lintel (nine grahas relief)...")
    req = urllib.request.Request(LINTEL_URL, headers={"User-Agent": "shloka-mailer/1.0"})
    with urllib.request.urlopen(req, timeout=90) as resp:
        data = resp.read()
    with open(SOURCE_PATH, "wb") as f:
        f.write(data)


def build_header() -> Image.Image:
    download_source()
    src = Image.open(SOURCE_PATH).convert("RGB")
    sw, sh = src.size

    # Crop the carved deity row (all nine grahas left → right)
    margin_x = int(sw * 0.02)
    top = int(sh * 0.08)
    bottom = int(sh * 0.92)
    cropped = src.crop((margin_x, top, sw - margin_x, bottom))

    banner = cropped.resize((W, H), Image.Resampling.LANCZOS)

    # Warm manuscript / temple stone tone
    banner = ImageEnhance.Color(banner).enhance(1.18)
    banner = ImageEnhance.Contrast(banner).enhance(1.12)
    banner = ImageEnhance.Brightness(banner).enhance(1.05)
    banner = banner.filter(ImageFilter.UnsharpMask(radius=1.2, percent=130, threshold=3))

    rgba = banner.convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Parchment-style side vignette
    for x in range(40):
        a = int(45 * (1 - x / 40))
        draw.line([(x, 0), (x, H)], fill=(48, 28, 12, a))
        draw.line([(W - 1 - x, 0), (W - 1 - x, H)], fill=(48, 28, 12, a))

    # Soft bottom blend into email body
    for y in range(int(H * 0.7), H):
        t = (y - int(H * 0.7)) / (H - int(H * 0.7))
        draw.line([(0, y), (W, y)], fill=(30, 18, 8, int(160 * t)))

    rgba = Image.alpha_composite(rgba, overlay)
    draw = ImageDraw.Draw(rgba)

    # Ornamental frame (book / manuscript border)
    draw.rectangle([0, 0, W, 4], fill="#C89840")
    draw.rectangle([0, H - 4, W, H], fill="#8B5A20")
    draw.rectangle([0, 0, 5, H], fill="#A07030")
    draw.rectangle([W - 5, 0, W, H], fill="#A07030")

    return rgba.convert("RGB")


def main() -> None:
    banner = build_header()
    banner.save(OUT_PATH, "PNG", optimize=True)
    print(f"Saved {OUT_PATH} ({W}x{H})")


if __name__ == "__main__":
    main()
