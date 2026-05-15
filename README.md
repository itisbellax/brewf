# AI Tech Brief

A daily tech news digest built for CS students, with AI-generated summaries and internship-relevant insights.

## What it does

- Pulls tech news from HackerNews, TechCrunch, and The Verge via RSS
- Uses Groq (LLaMA 3.1) to summarize each article and add a "what this means for CS students" angle
- Displays articles in a categorized, newsletter-style web app built with Streamlit

## Project structure

```
ai-tech-brief/
├── fetcher.py        # RSS feed fetching and HTML stripping
├── db.py             # SQLite read/write operations
├── analyzer.py       # Groq AI summarization and categorization
├── app.py            # Streamlit web interface
├── requirements.txt  # Python dependencies
├── .env              # API keys (never commit this)
└── articles.db       # SQLite database (auto-generated, never commit)
```

## Setup

1. Clone the repo and create a conda environment:
   ```bash
   conda create -n ai-tech-brief python=3.11
   conda activate ai-tech-brief
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the project root:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```
   Get a free API key at [console.groq.com](https://console.groq.com)

3. Initialize the database and fetch articles:
   ```bash
   python -c "from db import init_db; init_db()"
   python fetcher.py
   ```

4. Run AI summarization:
   ```bash
   python analyzer.py
   ```

5. Launch the web app:
   ```bash
   streamlit run app.py
   ```

## Development workflow

To refresh with new articles:
```bash
python fetcher.py    # fetch new articles into DB
python analyzer.py   # summarize any unprocessed articles
streamlit run app.py # view results
```

## Tech stack

| Layer | Tool |
|---|---|
| News source | RSS feeds via `feedparser` |
| Storage | SQLite (`sqlite3`) |
| AI model | LLaMA 3.1 8B via Groq API |
| Frontend | Streamlit |

## Roadmap

- [ ] Relevance scoring per article (high/medium/low for students)
- [ ] Scheduled daily refresh
- [ ] Deploy to Streamlit Cloud
