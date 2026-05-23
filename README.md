# BREWF

**A daily AI-powered tech news digest for CS students.**  
Live at → [itisbellax.github.io/brewf](https://itisbellax.github.io/brewf/)

---

## What it does

Every morning at 9:00 AM, a scheduled job:

1. Pulls the latest articles from HackerNews, TechCrunch, and The Verge via RSS
2. Uses Groq (LLaMA 3.1) to summarize each article and add a *"what this means for CS students"* angle
3. Categorizes articles by topic (AI/ML, Security, Cloud, PM, etc.)
4. Generates a spoken podcast (`podcast.mp3`) from today's top stories using `edge-tts`
5. Exports everything to `articles.json` and pushes both files to GitHub Pages

The frontend is a self-contained static `index.html` served by GitHub Pages — no server required.

---

## Architecture

```
┌─────────────────────────────────────────────┐
│  macOS launchd  (daily @ 09:00)             │
│                                             │
│  fetcher.py → db.py → analyzer.py          │
│       ↓           ↓          ↓             │
│  RSS feeds    SQLite     Groq API           │
│                   ↓                        │
│             main.py                        │
│           ↙        ↘                       │
│  articles.json   podcast.mp3               │
│        ↓               ↓                  │
│     git push → GitHub Pages                │
└─────────────────────────────────────────────┘

GitHub Pages serves:
  index.html                 ← React 18 (CDN) frontend
  articles.json              ← fetched by browser on load
  podcast.mp3                ← streamed by audio player
  CabinetGrotesk-Black.ttf  ← display font
```

---

## File structure

```
ai-tech-brief/
├── main.py                    # Daily pipeline: fetch → analyze → export → push
├── fetcher.py                 # RSS feed fetching (HN, TechCrunch, The Verge)
├── db.py                      # SQLite read/write, 7-day retention, LIMIT 20 export
├── analyzer.py                # Groq AI: summarize + student angle + categorize
├── podcast.py                 # edge-tts text-to-speech podcast generation
│
├── index.html                 # Static frontend (React 18 via CDN, self-contained)
├── articles.json              # Generated daily — consumed by index.html
├── podcast.mp3                # Generated daily — served by GitHub Pages
├── CabinetGrotesk-Black.ttf  # Display font (Cabinet Grotesk Black)
│
├── requirements.txt           # Python dependencies (pipeline only)
├── .env                       # API keys — never committed
└── articles.db                # SQLite database — never committed
```

---

## Setup

### 1. Clone & create environment

```bash
git clone https://github.com/itisbellax/brewf.git
cd brewf
conda create -n ai-tech-brief python=3.11
conda activate ai-tech-brief
pip install -r requirements.txt
```

### 2. Configure API keys

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
```

Get a free key at [console.groq.com](https://console.groq.com).

### 3. Run the pipeline manually

```bash
python main.py
```

This fetches articles, summarizes them, generates the podcast, and pushes `articles.json` + `podcast.mp3` to GitHub.

---

## Automation (macOS launchd)

A `launchd` plist runs `main.py` daily at 9:00 AM using the conda environment's Python:

```
~/Library/LaunchAgents/com.bella.aitechbrief.plist
```

Logs are written to `cron.log` in the project directory (gitignored).

To reload the job after any changes:

```bash
launchctl unload ~/Library/LaunchAgents/com.bella.aitechbrief.plist
launchctl load ~/Library/LaunchAgents/com.bella.aitechbrief.plist
```

---

## Frontend

`index.html` is a fully self-contained static page with no build step:

- **React 18** loaded from CDN (with SRI integrity hashes)
- **Babel standalone** for in-browser JSX transform
- **Cabinet Grotesk Black** served from `./CabinetGrotesk-Black.ttf`
- **Geist** (body + mono) from Google Fonts
- Animated canvas background with warm-brown blobs
- Category filter pills, article cards with AI summaries and student angles
- Podcast player with waveform visualizer and real audio duration
- Mobile responsive (optimized for <640px screens)

---

## Tech stack

| Layer | Tool |
|---|---|
| News sources | RSS via `feedparser` |
| Storage | SQLite (`sqlite3`), 7-day rolling window |
| AI summarization | LLaMA 3.1 8B via Groq API |
| Podcast | `edge-tts` (Microsoft Neural TTS) |
| Frontend | React 18 (CDN), Babel standalone, static HTML |
| Hosting | GitHub Pages |
| Automation | macOS launchd |
