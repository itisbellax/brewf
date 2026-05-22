import sqlite3

DB_PATH = "articles.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            title TEXT,
            summary TEXT,
            link TEXT UNIQUE,
            published TEXT,
            ai_summary TEXT,
            student_angle TEXT,
            category TEXT,
            tags TEXT,
            fetched_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()

def save_articles(articles):
    conn = sqlite3.connect(DB_PATH)
    saved = 0
    for a in articles:
        try:
            conn.execute(
                "INSERT OR IGNORE INTO articles (source, title, summary, link, published) VALUES (?,?,?,?,?)",
                (a["source"], a["title"], a["summary"], a["link"], a["published"])
            )
            saved += conn.total_changes
        except Exception as e:
            print(f"Error saving article: {e}")
    conn.commit()
    conn.close()
    return saved

def get_unprocessed():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id, title, summary FROM articles WHERE ai_summary IS NULL"
    ).fetchall()
    conn.close()
    return rows

def update_ai_fields(article_id, ai_summary, student_angle, category="", tags=""):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "UPDATE articles SET ai_summary=?, student_angle=?, category=?, tags=? WHERE id=?",
        (ai_summary, student_angle, category, tags, article_id)
    )
    conn.commit()
    conn.close()

def get_all_processed(limit=20):
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT source, title, ai_summary, student_angle, link, published, category, tags "
        "FROM articles WHERE ai_summary IS NOT NULL "
        "ORDER BY fetched_at DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return rows
