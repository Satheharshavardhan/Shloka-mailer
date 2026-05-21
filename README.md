# Shloka Mailer

Daily email reader for **Brihat Parāśara Hora Śāstra** (BPHS). Each run sends 3 shlokas with Sanskrit, transliteration, English, and Hindi.

Data source: [enjoylearningsanskrit.com — Parāśara](https://enjoylearningsanskrit.com/scriptures/parashara/) (3,936 shlokas in `structured_shlokas.json`).

---

## How it works

1. `main.py` reads `progress.json` to find the next shloka index.
2. It builds an HTML email for the next 3 entries.
3. It sends via Gmail SMTP and saves the new index to `progress.json`.
4. **GitHub Actions** runs this every day at **4:00 PM IST** so it works even when your computer is off.

---

## For new contributors — quick start

### 1. Clone and install

```bash
git clone https://github.com/Satheharshavardhan/Shloka-mailer.git
cd Shloka-mailer
pip install -r requirements.txt
```

### 2. Configure email (local testing)

```bash
cp .env.example .env
```

Edit `.env`:

| Variable | Description |
|----------|-------------|
| `EMAIL_ADDRESS` | Gmail address used to send |
| `EMAIL_PASSWORD` | [Gmail App Password](https://myaccount.google.com/apppasswords) (not your normal password) |
| `TO_EMAIL` | Who receives the daily email |
| `SHLOKAS_PER_DAY` | Optional, default `3` |

### 3. Test without sending

```bash
python3 main.py --dry-run
```

Open `deprecated/output/email_preview.html` in a browser.

### 4. Send one email locally

```bash
python3 main.py
```

---

## GitHub Actions setup (production)

Use this so emails send on a schedule without your laptop.

1. Fork or use this repo on GitHub.
2. Go to **Settings → Secrets and variables → Actions** and add:

   | Secret name | Value |
   |-------------|--------|
   | `EMAIL_ADDRESS` | Sender Gmail |
   | `EMAIL_PASSWORD` | Gmail App Password |
   | `TO_EMAIL` | Recipient email |

3. Open **Actions → BPHS Daily Mailer → Run workflow** to test.
4. After a successful run, check that `progress.json` was updated in the repo.

Schedule: **4:00 PM IST** daily (see `.github/workflows/daily_mailer.yml`).

**Tip:** If you also use cron on your PC, remove it to avoid duplicate emails:

```bash
crontab -e
```

---

## Project structure

```
Shloka-mailer/
├── main.py                      # Send daily email
├── structured_shlokas.json      # All shlokas (do not edit by hand unless fixing text)
├── progress.json                # Current reading index (updated after each send)
├── requirements.txt
├── .env.example                 # Copy to .env for local runs
├── assets/
│   ├── header.png               # Email banner (embedded)
│   ├── om.png                   # Om icon per shloka (embedded)
│   └── generate_header.py       # Regenerate header.png
├── .github/workflows/
│   └── daily_mailer.yml         # Scheduled cloud runner
├── v2_scrape_and_translate.py   # Re-fetch data from the website (optional)
└── deprecated/                  # Old PDF tools, logs, backups — not used daily
```

---

## Common tasks

| Task | Command |
|------|---------|
| Preview email | `python3 main.py --dry-run` |
| Send email now | `python3 main.py` |
| Regenerate header image | `python3 assets/generate_header.py` |
| Re-scrape website | `python3 v2_scrape_and_translate.py` |
| Resume translation only | `python3 v2_scrape_and_translate.py --translate-only` |
| Reset reading to start | Set `progress.json` to `{"index": 0}` and commit |

---

## JSON entry format

Each item in `structured_shlokas.json`:

```json
{
  "chapter": "Chapter 1",
  "shloka": "1",
  "sanskrit": "...",
  "transliteration": "...",
  "separated_sandhi": "...",
  "english": "...",
  "hindi": "...",
  "commentary": ""
}
```

---

## Troubleshooting

| Problem | What to check |
|---------|----------------|
| No email received | GitHub Actions run logs; Gmail App Password; secrets names match exactly |
| Two emails per day | Disable local `cron` if Actions is enabled |
| `Missing assets` | Run `python3 assets/generate_header.py` |
| Gmail login error | Use App Password; enable 2FA on Google account |
| Book completed | `progress.json` index ≥ 3936; reset index to `0` to restart |

---

## License and data

- Shloka text: [enjoylearningsanskrit.com](https://enjoylearningsanskrit.com/scriptures/parashara/)
- Header image: Navagraha lintel (Cleveland Museum of Art, via Wikimedia Commons) — see `assets/generate_header.py`
