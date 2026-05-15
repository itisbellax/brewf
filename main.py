import sqlite3
import json
from datetime import datetime, timedelta
from fetcher import fetch_articles
from db import init_db, save_articles, DB_PATH, get_all_processed
from analyzer import process_all

KEEP_DAYS = 7

def cleanup_old_articles():
    cutoff = (datetime.now() - timedelta(days=KEEP_DAYS)).isoformat()
    conn = sqlite3.connect(DB_PATH)
    deleted = conn.execute(
        "DELETE FROM articles WHERE fetched_at < ?", (cutoff,)
    ).rowcount
    conn.commit()
    conn.close()
    print(f"Cleaned up {deleted} articles older than {KEEP_DAYS} days")

def export_to_json():
    articles = get_all_processed()
    data = [
        {
            "source": a[0], "title": a[1], "ai_summary": a[2],
            "student_angle": a[3], "link": a[4], "published": a[5],
            "category": a[6], "tags": a[7]
        }
        for a in articles
    ]
    with open("articles.json", "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Exported {len(data)} articles to articles.json")

if __name__ == "__main__":
    print("=== BREWF Daily Refresh ===")
    init_db()
    cleanup_old_articles()
    articles = fetch_articles()
    saved = save_articles(articles)
    print(f"Fetched {len(articles)} articles, {saved} new")
    process_all()
    export_to_json()
    print("Done.")
