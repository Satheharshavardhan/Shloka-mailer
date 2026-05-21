# Shloka Mailer — Brihat Parāśara Hora Śāstra

Sends **3 shlokas per day** by email from `structured_shlokas.json` (3,936 verses scraped from [enjoylearningsanskrit.com](https://enjoylearningsanskrit.com/scriptures/parashara/)).

## Recommended: GitHub Actions (works when your laptop is off)

The workflow [`.github/workflows/daily_mailer.yml`](.github/workflows/daily_mailer.yml) runs **every day at 4:00 PM IST** on GitHub’s servers and commits `progress.json` after each send.

### One-time setup

1. **Create a GitHub repo** (e.g. `shloka_mailer`) and push this project (see below).

2. **Add repository secrets** (Settings → Secrets and variables → Actions → New repository secret):

   | Secret | Value |
   |--------|--------|
   | `EMAIL_ADDRESS` | Your Gmail address |
   | `EMAIL_PASSWORD` | Gmail [App Password](https://myaccount.google.com/apppasswords) |
   | `TO_EMAIL` | Recipient address |

3. **Enable Actions**: Actions tab → enable workflows if prompted.

4. **Test manually**: Actions → **BPHS Daily Mailer** → **Run workflow**.

5. **Optional**: Disable local cron so you don’t send twice:
   ```bash
   crontab -e   # remove the shloka_mailer line
   ```

Progress is stored in `progress.json` in the repo and updated automatically after each successful run.

---

## Local setup (optional / testing)

```bash
cd shloka_mailer
pip install -r requirements.txt
cp .env.example .env   # fill in credentials
python3 main.py --dry-run   # preview only
python3 main.py             # send email
```

### `.env` variables

```
EMAIL_ADDRESS=you@gmail.com
EMAIL_PASSWORD=your_app_password
TO_EMAIL=recipient@gmail.com
SHLOKAS_PER_DAY=3
```

---

## Project layout

```
main.py                    # Daily email sender
structured_shlokas.json    # All shlokas (source of truth)
progress.json              # Next index (synced by GitHub Actions)
assets/                    # Header + Om images (embedded in email)
v2_scrape_and_translate.py # Re-scrape / re-translate if needed
deprecated/                # Old PDF pipeline, logs, drafts (not used daily)
```

Regenerate header image:

```bash
python3 assets/generate_header.py
```

---

## Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit: BPHS daily shloka mailer"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/shloka_mailer.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.
