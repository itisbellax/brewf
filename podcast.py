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

    prompt = f"""You are the host of BREWF, a daily tech podcast for CS university students. Think NPR meets a sharp tech newsletter — informed, engaging, clear. Not stiff, not silly.

Here are today's stories:
{stories}

Write a 5-minute broadcast script with:
- Open with "Welcome to BREWF" and today's date feel
- Each story delivered with clarity and one brief personal take — no fluff, no forced jokes
- Natural transitions that keep momentum
- Short, punchy sentences easy to follow while commuting
- A grounded sign-off mentioning BREWF

STRICT RULES:
- No stage directions, no music cues, no brackets like [music], [pause], [intro]
- No labels like "Story 1:" or "Host:"
- Just the exact words to be spoken aloud, nothing else
- Under 700 words"""

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
        communicate = edge_tts.Communicate(script, voice="en-US-AriaNeural")
        await communicate.save(AUDIO_PATH)
    asyncio.run(synthesize())

    return AUDIO_PATH, script

if __name__ == "__main__":
    path, script = generate_podcast()
    if path:
        print(f"\nScript:\n{script}\n\nSaved to {path}")
