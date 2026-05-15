from groq import Groq
from dotenv import load_dotenv
import os
import time
from db import get_unprocessed, update_ai_fields

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_article(title, summary):
    prompt = f"""You are an editor writing a tech newsletter for CS university students seeking internships.

Article title: {title}
Article summary: {summary}

Reply entirely in English. Use this EXACT format, no extra text:

CATEGORY: (pick one: Industry News | Tech Trends | Company Updates)

TAGS: (pick 1-2 that apply, comma-separated: Software Engineering | AI & ML | Security | Data Science | Cloud & DevOps | Product & PM)

BULLETS:
• (key point 1, max 20 words)
• (key point 2, max 20 words)
• (key point 3, max 20 words)

STUDENT TAKE: (Follow these rules strictly:
- If the article is about company hiring or funding → say whether this company is worth applying to
- If the article is about a new technology or framework → say whether to learn it and why
- If the article is about layoffs or industry contraction → say the actual impact on entry-level jobs
- If the article is about a product launch → say whether internship opportunities in this area are growing
- If none of the above apply → write NONE
Keep it under 20 words. Do not start with "As a CS student".)"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.choices[0].message.content.strip()

    category = ""
    tags = ""
    bullets = []
    student_angle = ""

    for line in text.splitlines():
        line = line.strip()
        if line.startswith("CATEGORY:"):
            category = line.replace("CATEGORY:", "").strip()
        elif line.startswith("TAGS:"):
            tags = line.replace("TAGS:", "").strip()
        elif line.startswith("•"):
            bullets.append(line)
        elif line.startswith("STUDENT TAKE:"):
            val = line.replace("STUDENT TAKE:", "").strip()
            student_angle = "" if val == "NONE" else val

    bullets_text = "\n".join(bullets)
    return category, tags, bullets_text, student_angle

def process_all():
    articles = get_unprocessed()
    print(f"Processing {len(articles)} articles...")
    for i, (article_id, title, summary) in enumerate(articles):
        try:
            category, tags, bullets_text, student_angle = analyze_article(title, summary)
            update_ai_fields(article_id, bullets_text, student_angle, category, tags)
            print(f"[{i+1}/{len(articles)}] {title[:60]}")
            time.sleep(1)
        except Exception as e:
            print(f"Error on article {article_id}: {e}")

if __name__ == "__main__":
    process_all()
