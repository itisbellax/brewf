import feedparser
import re
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

def strip_html(text):
    return re.sub(r"<[^>]+>", "", text).strip()

FEEDS = {
    "HackerNews": "https://news.ycombinator.com/rss",
    "TechCrunch": "https://techcrunch.com/feed/",
    "The Verge": "https://www.theverge.com/rss/index.xml",
}

def parse_published(entry):
    """Return a timezone-aware datetime for an RSS entry, or None."""
    raw = entry.get("published", "") or entry.get("updated", "")
    if not raw:
        return None
    try:
        return parsedate_to_datetime(raw)
    except Exception:
        pass
    # Fallback: try ISO format
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None

def fetch_articles(max_per_feed=10, max_age_days=2):
    """Fetch articles published within the last max_age_days days."""
    articles = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)

    for source, url in FEEDS.items():
        feed = feedparser.parse(url)
        count = 0
        for entry in feed.entries:
            if count >= max_per_feed:
                break
            pub_dt = parse_published(entry)
            # If we can't parse the date, include the article (be lenient)
            if pub_dt is not None and pub_dt < cutoff:
                continue
            title = entry.get("title", "")
            summary = strip_html(entry.get("summary", ""))
            if len(summary) < 20:
                summary = title
            published_str = entry.get("published", datetime.now(timezone.utc).isoformat())
            articles.append({
                "source": source,
                "title": title,
                "summary": summary,
                "link": entry.get("link", ""),
                "published": published_str,
            })
            count += 1
    return articles

if __name__ == "__main__":
    articles = fetch_articles()
    print(f"Total articles fetched: {len(articles)}\n")
    for a in articles[:3]:
        print(f"[{a['source']}] {a['title']}")
        print(f"  {a['summary'][:120]}...")
        print()
