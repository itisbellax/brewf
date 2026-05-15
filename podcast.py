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

    prompt = f"""You are the host of BREWF, a daily 5-minute tech podcast for CS students. Your style: direct, smart, a little dry. Like a friend who actually read the news so you don't have to.

Today's stories:
{stories}

Rules:
- Open with a one-liner that hooks the listener, mention BREWF
- Cover each story in 2-4 sentences max: what happened, why it matters. No filler.
- One quick personal take per story — opinionated, not neutral
- Transitions should feel natural, not scripted ("Next up...", "Meanwhile...", "And this one's interesting...")
- Close in one sentence, sign off as BREWF
- NOTHING but spoken words. No brackets, no labels, no stage directions, no music cues.
- Under 500 words. Every sentence must earn its place."""

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

def generate_podcast(max_articles=8):
    articles = load_articles()[:max_articles]
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
