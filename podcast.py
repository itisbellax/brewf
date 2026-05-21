from groq import Groq
import edge_tts
import asyncio
import json
from dotenv import load_dotenv
import os

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
AUDIO_PATH = "podcast.mp3"

def generate_script(articles):
    stories = ""
    for i, row in enumerate(articles, 1):
        source, title, ai_summary, student_angle, link, published, category, tags = row
        bullets = " ".join(
            line.lstrip("•").strip()
            for line in (ai_summary or "").splitlines() if line.strip()
        )
        angle = f" {student_angle}" if student_angle else ""
        stories += f"\nStory {i}: {title}. {bullets}.{angle}\n"

    prompt = f"""You are the host of BREWF, a daily tech podcast for CS students. Style: direct, smart, a little dry. Like a friend who actually read the news so you don't have to.

Today's stories:
{stories}

Rules:
- Open with a punchy one-liner, always say the full name "BREWF" (not "BREW")
- Cover each story in 2-3 sentences: what happened, why it matters to CS students. Zero filler.
- Natural transitions only: "Next up", "Meanwhile", "Here's one worth noting" — never "Story 1" or numbered labels
- One quick opinionated take per story
- Close in one sentence, sign off as BREWF
- ONLY spoken words. No brackets, no labels, no stage directions, no music cues, no numbering.
- Under 450 words. Cut anything that doesn't add value."""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()

def load_articles():
    if os.path.exists("articles.json"):
        with open("articles.json") as f:
            data = json.load(f)
        return [(a["source"], a["title"], a["ai_summary"], a["student_angle"],
                 a["link"], a["published"], a["category"], a["tags"]) for a in data]
    from db import get_all_processed
    return get_all_processed()

CS_TAGS = {"Software Engineering", "AI & ML", "Security", "Data Science", "Cloud & DevOps", "Product & PM"}

def generate_podcast(max_articles=8):
    all_articles = load_articles()
    articles = [
        a for a in all_articles
        if a[3] and any(t.strip() in CS_TAGS for t in (a[7] or "").split(","))
    ][:max_articles]
    if not articles:
        articles = [a for a in all_articles if a[3]][:max_articles]
    if not articles:
        return None, "No articles available."

    print("Generating broadcast script...")
    script = generate_script(articles)

    print("Converting to audio...")
    async def synthesize():
        communicate = edge_tts.Communicate(script, voice="en-US-JennyNeural")
        await communicate.save(AUDIO_PATH)
    asyncio.run(synthesize())

    return AUDIO_PATH, script

if __name__ == "__main__":
    path, script = generate_podcast()
    if path:
        print(f"\nScript:\n{script}\n\nSaved to {path}")
