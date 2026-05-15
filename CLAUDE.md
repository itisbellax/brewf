# BREWF — Claude Development Guide

## Project overview

BREWF is a daily tech news digest for CS students. Fetches RSS feeds → stores in SQLite → AI summarizes with student angle → displays in Streamlit. Tagline: "Stay signal, cut the noise."

## Architecture

```
fetcher.py → db.py ← analyzer.py
                ↓
             app.py
          podcast.py (audio digest)
          main.py (daily runner)
```

- `fetcher.py`: pulls RSS (HackerNews, TechCrunch, The Verge), 5 articles per feed
- `db.py`: all SQLite operations — init, save, read, update
- `analyzer.py`: calls Groq API, parses structured output, writes back to DB
- `app.py`: reads from DB, renders Streamlit UI
- `podcast.py`: generates broadcast script via Groq + audio via edge-tts
- `main.py`: daily runner — cleanup old articles → fetch → analyze

## Database schema

```sql
articles (
    id, source, title, summary, link UNIQUE, published,
    ai_summary,    -- bullet points as newline-separated string
    student_angle, -- conditional student take (empty if not applicable)
    category,      -- "Industry News" | "Tech Trends" | "Company Updates"
    tags,          -- CS specialization tags, comma-separated
    fetched_at
)
```

`link` is UNIQUE — duplicate articles are silently ignored on insert.

## AI output format (analyzer.py)

```
CATEGORY: Industry News | Tech Trends | Company Updates
TAGS: Software Engineering | AI & ML | Security | Data Science | Cloud & DevOps | Product & PM
• bullet 1
• bullet 2
• bullet 3
STUDENT TAKE: one sentence (or NONE if not applicable)
```

## UI rules

- Multiselects default to empty = no filter, show all. Selecting = inclusion not exclusion.
- Layout: Industry News full width on top, Tech Trends + Company Updates side by side below
- Light theme only (.streamlit/config.toml)
- Audio player uses st.html() with native <audio> tag (supports seeking)

## Environment

- Python 3.11, conda env named `ai-tech-brief`
- Dependencies: `feedparser`, `groq`, `streamlit`, `python-dotenv`, `edge-tts`
- API keys needed: `GROQ_API_KEY` in `.env`
- Daily cron: launchd plist at `~/Library/LaunchAgents/com.bella.aitechbrief.plist`, runs 9am

## What's not done yet

1. Deployment to Streamlit Cloud (SQLite needs replacing for stateless hosting)
