import argparse
import html as html_lib
import json
import os
import smtplib
import sys
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")

BOOK_FILE = "structured_shlokas.json"
PROGRESS_FILE = "progress.json"
SHLOKAS_PER_DAY = int(os.getenv("SHLOKAS_PER_DAY", "3"))
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
HEADER_IMAGE_PATH = os.path.join(ASSETS_DIR, "header.png")
OM_IMAGE_PATH = os.path.join(ASSETS_DIR, "om.png")

FONT = (
    "'Noto Sans Devanagari', 'Nirmala UI', 'Mangal', 'Segoe UI', "
    "Tahoma, Geneva, Verdana, sans-serif"
)


def esc(text: str) -> str:
    return html_lib.escape(str(text))


def nl2br(text: str) -> str:
    return esc(text).replace("\n", "<br>")


def build_section_block(label: str, content: str, bg: str, label_color: str) -> str:
    if not content:
        return ""
    return f"""
          <tr>
            <td style="padding:0 22px 18px 22px;">
              <table width="100%" cellpadding="0" cellspacing="0" role="presentation"
                     style="background:{bg};border-radius:14px;border:1px solid #e8dcc5;">
                <tr>
                  <td style="padding:16px 20px 6px 20px;">
                    <span style="font-family:{FONT};font-size:15px;font-weight:700;
                                 letter-spacing:1.5px;text-transform:uppercase;color:{label_color};">
                      {label}
                    </span>
                  </td>
                </tr>
                <tr>
                  <td style="padding:0 20px 18px 20px;font-family:{FONT};font-size:21px;
                             line-height:1.75;color:#2c2418;">
                    {content}
                  </td>
                </tr>
              </table>
            </td>
          </tr>
"""


def build_shloka_card(entry: dict, card_num: int, om_src: str) -> str:
    sanskrit = nl2br(entry["sanskrit"])
    sections = ""

    if entry.get("transliteration"):
        sections += build_section_block(
            "Transliteration",
            esc(entry["transliteration"]),
            "#faf6ef",
            "#8c6b4a",
        )

    if entry.get("separated_sandhi"):
        sections += build_section_block(
            "विग्रह (Sandhi split)",
            esc(entry["separated_sandhi"]),
            "#f3f0ea",
            "#6b5a48",
        )

    if entry.get("english"):
        sections += build_section_block(
            "English",
            esc(entry["english"]),
            "#f8f9fc",
            "#3d5a80",
        )

    sections += build_section_block(
        "अर्थ (Hindi)",
        esc(entry["hindi"]),
        "#fff5e6",
        "#9a3412",
    )

    if entry.get("commentary"):
        sections += build_section_block(
            "व्याख्या",
            esc(entry["commentary"]),
            "#f5f5f5",
            "#555555",
        )

    return f"""
    <tr>
      <td style="padding:0 28px 32px 28px;">
        <table width="100%" cellpadding="0" cellspacing="0" role="presentation"
               style="background:#fffdf8;border-radius:20px;border:2px solid #d4b896;
                      box-shadow:0 8px 24px rgba(120,72,24,0.10);">
          <tr>
            <td style="background:linear-gradient(135deg,#8b4513 0%,#c47a2c 100%);
                       border-radius:18px 18px 0 0;padding:18px 24px;">
              <table width="100%" cellpadding="0" cellspacing="0" role="presentation">
                <tr>
                  <td style="font-family:{FONT};font-size:17px;font-weight:700;
                             letter-spacing:2px;text-transform:uppercase;color:#ffe8c8;">
                    {esc(entry['chapter'])} &nbsp;·&nbsp; Shloka {esc(entry['shloka'])}
                  </td>
                  <td align="right" width="56">
                    <span style="display:inline-block;background:rgba(255,255,255,0.22);
                                 color:#fff8ee;font-family:{FONT};font-size:22px;font-weight:700;
                                 width:44px;height:44px;line-height:44px;text-align:center;
                                 border-radius:50%;">{card_num}</span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <tr>
            <td style="padding:28px 26px 8px 26px;text-align:center;">
              <img src="{om_src}" alt="Om" width="48" height="48"
                   style="display:block;margin:0 auto 14px auto;opacity:0.85;" />
              <div style="font-family:{FONT};font-size:30px;line-height:1.65;font-weight:700;
                          color:#7a1f14;letter-spacing:0.3px;">
                {sanskrit}
              </div>
            </td>
          </tr>
          {sections}
          <tr><td style="height:10px;font-size:0;line-height:0;">&nbsp;</td></tr>
        </table>
      </td>
    </tr>
"""


def image_sources(for_email: bool) -> tuple[str, str]:
    if for_email:
        return "cid:header_img", "cid:om_img"
    return "assets/header.png", "assets/om.png"


def build_html(
    entries: list[dict], start_index: int, total: int, *, for_email: bool = True
) -> str:
    today = datetime.now().strftime("%A, %d %B %Y")
    end_num = start_index + len(entries)
    header_src, om_src = image_sources(for_email)
    cards = "".join(
        build_shloka_card(entry, i + 1, om_src) for i, entry in enumerate(entries)
    )

    return f"""<!DOCTYPE html>
<html lang="hi">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;600;700&display=swap" rel="stylesheet" />
  <title>BPHS Daily Reading</title>
</head>
<body style="margin:0;padding:0;background:#ebe3d4;
             font-family:{FONT};color:#2c2418;-webkit-text-size-adjust:100%;">

  <table width="100%" cellpadding="0" cellspacing="0" role="presentation"
         style="background:#ebe3d4;padding:24px 12px;">
    <tr>
      <td align="center">

        <table width="680" cellpadding="0" cellspacing="0" role="presentation"
               style="max-width:680px;width:100%;background:#ffffff;
                      border-radius:24px;overflow:hidden;
                      box-shadow:0 12px 40px rgba(80,48,16,0.14);">

          <!-- Header banner -->
          <tr>
            <td style="padding:0;line-height:0;">
              <img src="{header_src}" alt="BPHS daily reading banner"
                   width="680" style="display:block;width:100%;max-width:680px;
                   height:auto;border:0;object-fit:cover;" />
            </td>
          </tr>
          <tr>
            <td style="background:linear-gradient(180deg,#5c2e0e 0%,#8b4513 100%);
                       padding:32px 28px 28px 28px;text-align:center;">
              <p style="margin:0 0 8px 0;font-size:16px;letter-spacing:3px;
                        text-transform:uppercase;color:#f0d4a8;font-weight:600;">
                Daily Jyotisha Study
              </p>
              <h1 style="margin:0 0 14px 0;font-family:{FONT};font-size:34px;
                         line-height:1.25;font-weight:700;color:#fff8ee;">
                Brihat Parāśara Hora Śāstra
              </h1>
              <p style="margin:0;font-size:22px;color:#f5deb3;line-height:1.4;">
                {esc(today)}
              </p>
            </td>
          </tr>

          <!-- Progress pill -->
          <tr>
            <td style="padding:26px 28px 8px 28px;text-align:center;">
              <span style="display:inline-block;background:#f7f0e4;border:2px solid #d4b896;
                           border-radius:999px;padding:14px 28px;font-size:20px;
                           font-weight:600;color:#6b3f1f;line-height:1.4;">
                📖 &nbsp;Shlokas {start_index + 1}–{end_num} &nbsp;·&nbsp; {len(entries)} of {total} total
              </span>
            </td>
          </tr>

          {cards}

          <!-- Footer -->
          <tr>
            <td style="padding:12px 28px 36px 28px;">
              <table width="100%" cellpadding="0" cellspacing="0" role="presentation"
                     style="background:#f7f0e4;border-radius:16px;border:1px solid #e0d0b8;">
                <tr>
                  <td style="padding:26px 24px;text-align:center;">
                    <p style="margin:0 0 10px 0;font-size:22px;color:#5c3d1e;font-weight:600;">
                      🙏 Continue tomorrow at 4:00 PM
                    </p>
                    <p style="margin:0;font-size:18px;color:#7a6248;line-height:1.6;">
                      The next 3 shlokas will arrive in your inbox automatically.
                    </p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

        </table>

        <p style="margin:20px 0 0 0;font-size:15px;color:#8a7a68;text-align:center;
                  line-height:1.5;max-width:680px;">
          Source: enjoylearningsanskrit.com · Parāśara scriptures
        </p>

      </td>
    </tr>
  </table>
</body>
</html>"""


def attach_inline_image(msg: MIMEMultipart, path: str, content_id: str) -> None:
    with open(path, "rb") as f:
        img = MIMEImage(f.read())
    img.add_header("Content-ID", f"<{content_id}>")
    img.add_header("Content-Disposition", "inline", filename=os.path.basename(path))
    msg.attach(img)


def build_email_message(html_body: str) -> MIMEMultipart:
    msg = MIMEMultipart("related")
    msg.attach(MIMEMultipart("alternative"))
    msg.get_payload()[0].attach(MIMEText(html_body, "html", "utf-8"))
    attach_inline_image(msg, HEADER_IMAGE_PATH, "header_img")
    attach_inline_image(msg, OM_IMAGE_PATH, "om_img")
    return msg


def send_daily_email(*, dry_run: bool = False) -> None:
    with open(BOOK_FILE, "r", encoding="utf-8") as f:
        book = json.load(f)

    if not os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "w") as f:
            json.dump({"index": 0}, f)

    with open(PROGRESS_FILE, "r") as f:
        progress = json.load(f)

    current_index = progress["index"]

    if current_index >= len(book):
        print("Book completed.")
        return

    entries = book[current_index : current_index + SHLOKAS_PER_DAY]
    if not entries:
        print("Book completed.")
        return

    if not EMAIL_ADDRESS or not EMAIL_PASSWORD or not TO_EMAIL:
        print("Error: Set EMAIL_ADDRESS, EMAIL_PASSWORD, and TO_EMAIL in .env or secrets.")
        sys.exit(1)

    if not os.path.isfile(HEADER_IMAGE_PATH) or not os.path.isfile(OM_IMAGE_PATH):
        raise FileNotFoundError(
            f"Missing assets in {ASSETS_DIR}. "
            "Ensure assets/header.png and assets/om.png exist."
        )

    subject = f"BPHS Daily Reading — {datetime.now().strftime('%d %B %Y')}"
    html_body = build_html(entries, current_index, len(book), for_email=True)

    print(
        f"Preparing email: shlokas {current_index + 1}–{current_index + len(entries)} "
        f"({len(entries)} shlokas)"
    )

    if dry_run:
        preview_path = os.path.join(
            os.path.dirname(__file__), "deprecated", "output", "email_preview.html"
        )
        os.makedirs(os.path.dirname(preview_path), exist_ok=True)
        preview_html = build_html(entries, current_index, len(book), for_email=False)
        with open(preview_path, "w", encoding="utf-8") as f:
            f.write(preview_html)
        print(f"Dry run: preview saved to {preview_path}")
        return

    msg = build_email_message(html_body)
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = TO_EMAIL
    msg["Subject"] = subject

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, TO_EMAIL, msg.as_string())
        server.quit()

        print("Email sent successfully.")
        progress["index"] += len(entries)
        with open(PROGRESS_FILE, "w") as f:
            json.dump(progress, f)
    except Exception as e:
        print("Error:", e)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send daily BPHS shloka email")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Build preview HTML without sending email",
    )
    args = parser.parse_args()
    send_daily_email(dry_run=args.dry_run)
