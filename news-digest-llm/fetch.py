import sqlite3, feedparser, re, os
from datetime import datetime, timezone
from hashlib import md5

DB = os.path.expanduser("~/work/news-digest/articles.db")

FEEDS = [
    "https://semiengineering.com/feed/",
    "https://www.edge-ai-vision.com/feed/",
    "https://hnrss.org/frontpage?points=100&q=AI+edge+GPU+SoC",
    "https://www.theregister.com/headlines.atom",
    "https://developer.nvidia.com/blog/feed/",
    "https://semiwiki.com/feed/",
    # add as many as you want - no token impact
]

def strip_html(text):
    return re.sub(r'<[^>]+>', '', text).strip()

def init_db(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id TEXT PRIMARY KEY,
            title TEXT,
            url TEXT,
            summary TEXT,
            source TEXT,
            published_at TEXT,
            fetched_at TEXT,
            summarized INTEGER DEFAULT 0
        )
    """)
    conn.commit()

def fetch_all():
    conn = sqlite3.connect(DB)
    init_db(conn)
    total = 0
    for feed_url in FEEDS:
        feed = feedparser.parse(feed_url)
        source = feed.feed.get('title', feed_url)
        for entry in feed.entries[:10]:
            article_id = md5(entry.link.encode()).hexdigest()
            pub = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                pub = datetime(*entry.published_parsed[:6],
                               tzinfo=timezone.utc).isoformat()
            summary = strip_html(getattr(entry, 'summary', ''))[:200]
            try:
                conn.execute("""
                    INSERT OR IGNORE INTO articles
                    (id, title, url, summary, source, published_at, fetched_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    article_id, entry.title, entry.link,
                    summary, source, pub,
                    datetime.now(timezone.utc).isoformat()
                ))
                total += 1
            except Exception as e:
                print(f"  skip: {e}")
    conn.commit()
    conn.close()
    print(f"Fetched, {total} new articles stored.")

if __name__ == "__main__":
    fetch_all()
