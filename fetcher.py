import feedparser
import re
from datetime import datetime

def strip_html(text):
    return re.sub(r"<[^>]+>", "", text).strip()

FEEDS = {
    "HackerNews": "https://news.ycombinator.com/rss",
    "TechCrunch": "https://techcrunch.com/feed/",
    "The Verge": "https://www.theverge.com/rss/index.xml",
}

def fetch_articles(max_per_feed=7):
    articles = []
    for source, url in FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:max_per_feed]:
            title = entry.get("title", "")
            summary = strip_html(entry.get("summary", ""))
            if len(summary) < 20:
                summary = title
            articles.append({
                "source": source,
                "title": title,
                "summary": summary,
                "link": entry.get("link", ""),
                "published": entry.get("published", datetime.now().isoformat()),
            })
    return articles

if __name__ == "__main__":
    articles = fetch_articles()
    print(f"Total articles fetched: {len(articles)}\n")
    for a in articles[:3]:
        print(f"[{a['source']}] {a['title']}")
        print(f"  {a['summary'][:120]}...")
        print()
