import sqlite3, os, smtplib
from openai import OpenAI
from email.mime.text import MIMEText
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()
DB = os.path.expanduser("~/work/news-digest/articles.db")
MAX_ARTICLES = 15  # fixed ceiling — controls token budget regardless of feed count

def get_recent_articles():
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    conn = sqlite3.connect(DB)
    rows = conn.execute("""
        SELECT title, url, summary, source
        FROM articles
        WHERE fetched_at > ?
        AND summarized = 0
        ORDER BY published_at DESC
        LIMIT ?
    """, (cutoff, MAX_ARTICLES)).fetchall()
    conn.close()
    return rows

def mark_summarized(rows):
    urls = [r[1] for r in rows]
    conn = sqlite3.connect(DB)
    conn.executemany(
        "UPDATE articles SET summarized=1 WHERE url=?",
        [(u,) for u in urls]
    )
    conn.commit()
    conn.close()

def build_prompt(rows):
    lines = []
    for title, url, summary, source in rows:
        lines.append(f"- [{source}] {title} ({url}): {summary}")
    return "\n".join(lines)

def summarize(articles: str) -> str:
    client = OpenAI(base_url="http://localhost:8080/v1", api_key="none")
    resp = client.chat.completions.create(
        model="mistral",
        messages=[{
            "role": "user",
            "content": (
                "You are a technical news curator for an expert in edge AI, "
                "video systems, and SoC platforms. Summarize these articles "
                "into a daily digest. Group by theme. For each include: "
                "title, one sentence summary, and full URL. "
                "Do not omit URLs.\n\n"
                f"{articles}"
            )
        }],
        max_tokens=1200,
    )
    return resp.choices[0].message.content

def send_email(body: str):
    gmail_user = os.environ["GMAIL_USER"]
    gmail_pass = os.environ["GMAIL_APP_PASSWORD"]
    msg = MIMEText(body)
    msg["Subject"] = f"Daily Tech Digest — {datetime.now().strftime('%b %d')}"
    msg["From"] = gmail_user
    msg["To"] = gmail_user
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(gmail_user, gmail_pass)
        s.send_message(msg)

if __name__ == "__main__":
    rows = get_recent_articles()
    if not rows:
        print("No new articles, skipping.")
    else:
        print(f"Summarizing {len(rows)} articles...")
        prompt = build_prompt(rows)
        digest = summarize(prompt)
        mark_summarized(rows)
        send_email(digest)
        print("Done.")
