# news-digest

A self-hosted daily tech news digest running entirely on a Jetson Orin NX.
Fetches RSS feeds, summarizes with a local Mistral 7B model via llama.cpp,
and delivers results by email. No cloud API costs.

## Stack

| Component | Tool |
|---|---|
| Hardware | NVIDIA Jetson Orin NX 8GB |
| LLM inference | llama.cpp (llama-server) |
| Model | Mistral 7B Instruct Q4_K_M |
| Storage | SQLite |
| Email delivery | Gmail SMTP (App Password) |
| Scheduler | cron |

## Folder Structure

```
news-digest/
├── README.md
├── .env                        # credentials (never commit)
├── .gitignore
├── requirements.txt
│
├── fetch.py                    # pulls RSS feeds → stores in SQLite (runs 4x/day)
├── summarize.py                # reads DB → LLM → sends email (runs 1x/day)
│
├── data/
│   └── articles.db             # SQLite database (auto-created on first run)
│
├── logs/                       # cron output (auto-created)
│   ├── fetch.log
│   └── digest.log
│
└── scripts/
    ├── setup.sh                # one-time environment setup
    └── install-crontab.sh      # installs cron jobs
```

## Setup

### 1. Prerequisites

llama-server must be running before `summarize.py` is called.
See `scripts/setup.sh` for the systemd service setup, or start manually:

```bash
cd ~/work/llama.cpp
./llama-server \
  -m ~/work/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf \
  -ngl 30 \
  -c 4096 \
  -t 6 \
  --host 0.0.0.0 \
  --port 8080 \
  --cache-ram 512
```

### 2. Python environment

```bash
cd ~/work/news-digest
python3 -m venv nd-venv
source nd-venv/bin/activate
pip install -r requirements.txt
```

### 3. Credentials

```bash
cp .env.example .env
nano .env  # fill in your values
chmod 600 .env
```

`.env` contents:
```
GMAIL_USER=you@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
```

To get a Gmail App Password:
1. Enable 2-Step Verification at https://myaccount.google.com/security
2. Generate an App Password at https://myaccount.google.com/apppasswords
3. Use the 16-character password — not your regular Gmail password

### 4. Install cron jobs

```bash
bash scripts/install-crontab.sh
```

Or add manually via `crontab -e`:
```
# Fetch articles 4x per day
0 */6 * * * cd <PATH>/news-digest && <PATH>/news-digest/nd-venv/bin/python fetch.py >> logs/fetch.log 2>&1

# Summarize and email once daily at 8am
0 8 * * * cd <PATH>/news-digest && <PATH>/news-digest/nd-venv/bin/python summarize.py >> logs/digest.log 2>&1
```

## Usage

### Run manually

```bash
source nd-venv/bin/activate

# Fetch latest articles into DB
python fetch.py

# Summarize and send email
python summarize.py
```

### Check what's in the database

```bash
sqlite3 data/articles.db "SELECT source, title, published_at FROM articles ORDER BY published_at DESC LIMIT 20;"
```

### Check articles not yet summarized

```bash
sqlite3 data/articles.db "SELECT count(*) FROM articles WHERE summarized=0;"
```

### Search historical articles

```bash
sqlite3 data/articles.db "SELECT title, url FROM articles WHERE title LIKE '%RISC-V%';"
```

### Check logs

```bash
tail -f logs/fetch.log
tail -f logs/digest.log
```

## Configuration

### Adding RSS feeds

Edit the `FEEDS` list in `fetch.py`. Adding more feeds has no impact on
token usage — the summarizer always picks a fixed number (`MAX_ARTICLES`)
from the database regardless of how many feeds are configured.

Suggested feeds for edge AI / video systems / SoC:

```python
# Edge AI & Embedded
"https://semiengineering.com/feed/"
"https://www.edge-ai-vision.com/feed/"
"https://www.eetimes.com/feed/"

# Chip industry
"https://semiwiki.com/feed/"

# NVIDIA / Jetson
"https://developer.nvidia.com/blog/feed/"

# Security & systems
"https://www.theregister.com/headlines.atom"

# Hacker News filtered
"https://hnrss.org/frontpage?points=100&q=AI+edge+GPU+SoC"
```

To find feeds: go to any site and try appending `/feed`, `/rss`, or `/atom`
to the URL. Most CMS platforms expose one of these.

### Tuning article count

In `summarize.py`:
```python
MAX_ARTICLES = 15  # increase if you have more context budget
```

At 4096 context with Mistral Q4_K_M, 15 articles is a safe ceiling.
Increase `MAX_ARTICLES` if you raise `-c` on the llama-server.

### Changing email frequency

- For weekly digest: change the summarize cron to `0 8 * * 1` (Mondays only)
- Fetch frequency can stay at 4x/day regardless — it just builds up the DB

## How it works

```
fetch.py (every 6h)
  └── parse RSS feeds
  └── deduplicate by URL hash
  └── store new articles in SQLite (summarized=0)

summarize.py (daily 8am)
  └── query DB: last 24h, summarized=0, limit MAX_ARTICLES
  └── build prompt
  └── POST to llama-server (localhost:8080)
  └── mark articles as summarized=1
  └── send email via Gmail SMTP
```

Articles are never deleted from the DB — they accumulate as a searchable
personal archive.

## Troubleshooting

**No articles fetched:**
- Check feed URLs are still valid: `curl -s https://semiengineering.com/feed/ | head -50`
- Relax the date cutoff in `summarize.py` temporarily to `timedelta(hours=48)`

**503 from llama-server:**
- Model is still loading — check `journalctl -u llama-server -f`
- Wait for "server is listening" in the logs

**Token exceeded error:**
- Reduce `MAX_ARTICLES` or shorten the summary field in `fetch.py`
- Or increase `-c` context in llama-server (up to ~6144 is safe on 8GB Orin)

**Email not sending:**
- Verify App Password is correct (no spaces): `echo $GMAIL_APP_PASSWORD`
- Test SMTP directly: `python -c "import smtplib; s=smtplib.SMTP_SSL('smtp.gmail.com',465); s.login('you@gmail.com','yourapppass'); print('ok')"`
