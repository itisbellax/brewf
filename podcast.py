from groq import Groq
import edge_tts
import asyncio
from dotenv import load_dotenv
from db import get_all_processed
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

    prompt = f"""You are the host of a daily tech podcast for CS university students — think NPR meets a sharp tech newsletter. Informed, engaging, and clear. Not stiff, not silly.

Here are today's stories:
{stories}

Write a 5-minute broadcast script with:
- A confident, warm opener that sets the tone
- Each story delivered with clarity and one brief personal take or insight — no fluff, no forced jokes
- Natural transitions that keep momentum without sounding scripted
- Short, punchy sentences that are easy to follow
- A grounded, forward-looking sign-off

Tone: like a smart friend who keeps you informed. Occasional dry wit is fine, but keep it mostly straight. Under 700 words. No bullet points, no labels, no stage directions — just the words spoken aloud."""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()

def generate_podcast(max_articles=8):
    articles = get_all_processed()[:max_articles]
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
