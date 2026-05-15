import streamlit as st
import json
import os

def load_articles():
    if os.path.exists("articles.json"):
        with open("articles.json") as f:
            data = json.load(f)
        return [(a["source"], a["title"], a["ai_summary"], a["student_angle"],
                 a["link"], a["published"], a["category"], a["tags"]) for a in data]
    from db import get_all_processed
    return get_all_processed()

from podcast import generate_podcast, AUDIO_PATH

st.set_page_config(page_title="Brewf", page_icon="📰", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Serif+Display&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .block-container {
        padding-top: 2.5rem;
        max-width: 1200px;
    }

    h1 {
        font-family: 'DM Serif Display', serif;
        font-size: 2.8rem;
        font-weight: 400;
        color: #423A28;
        letter-spacing: -0.5px;
    }

    .brewf-subtitle {
        font-size: 0.9rem;
        color: #95968D;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }

    .section-label {
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 3px;
        color: #95968D;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 1px solid #C0C1B9;
    }

    .article-block {
        background: rgba(241, 242, 236, 0.55);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(192, 193, 185, 0.5);
        border-radius: 16px;
        padding: 14px 16px;
        margin-bottom: 8px;
        transition: box-shadow 0.2s ease;
    }

    .article-block:hover {
        box-shadow: 0 4px 24px rgba(84, 75, 57, 0.08);
        border-color: rgba(149, 150, 141, 0.6);
    }

    .article-title a {
        font-size: 0.92rem;
        font-weight: 600;
        color: #423A28 !important;
        text-decoration: none;
        line-height: 1.45;
    }

    .article-title a:hover {
        color: #544B39 !important;
        text-decoration: underline;
    }

    .article-source {
        font-size: 0.7rem;
        color: #95968D;
        margin: 4px 0 8px 0;
        letter-spacing: 0.3px;
    }

    .tag-pill {
        display: inline-block;
        background: rgba(84, 75, 57, 0.08);
        color: #544B39;
        border: 1px solid rgba(84, 75, 57, 0.2);
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 0.68rem;
        font-weight: 500;
        margin-right: 4px;
        margin-bottom: 6px;
        letter-spacing: 0.3px;
    }

    .bullet-text {
        font-size: 0.82rem;
        color: #544B39;
        line-height: 1.6;
        margin-bottom: 2px;
    }

    .student-angle {
        background: rgba(192, 193, 185, 0.25);
        border-left: 3px solid #95968D;
        border-radius: 0 8px 8px 0;
        padding: 7px 10px;
        font-size: 0.8rem;
        color: #544B39;
        margin-top: 10px;
        line-height: 1.5;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("# BREWF")
st.markdown('<div class="brewf-subtitle">Stay signal, cut the noise.</div>', unsafe_allow_html=True)

col_title, col_pod = st.columns([4, 1])
with col_pod:
    if st.button("🎙️ Listen to today's brief", use_container_width=True):
        with st.spinner("Generating podcast..."):
            path, script = generate_podcast()

def render_audio_player(path):
    with open(path, "rb") as f:
        audio_bytes = f.read()
    import base64
    b64 = base64.b64encode(audio_bytes).decode()
    st.html(f"""
    <audio controls style="width:100%;margin-top:8px;border-radius:8px;">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """)

if os.path.exists(AUDIO_PATH):
    render_audio_player(AUDIO_PATH)

st.markdown("---")

articles = load_articles()

if not articles:
    st.info("No articles yet. Run `python analyzer.py` first.")
    st.stop()

ALL_TAGS = ["Software Engineering", "AI & ML", "Security", "Data Science", "Cloud & DevOps", "Product & PM"]
ALL_SECTIONS = ["Industry News", "Tech Trends", "Company Updates"]
SECTION_ICONS = {"Industry News": "🌐", "Tech Trends": "📈", "Company Updates": "🏢"}
FALLBACK = "Industry News"

st.sidebar.markdown("###  Your Interests")
selected_tags = st.sidebar.multiselect(
    "Prioritize articles related to:",
    options=ALL_TAGS,
    default=[],
)
st.sidebar.markdown("###  Sections")
selected_sections = st.sidebar.multiselect(
    "Show sections:",
    options=ALL_SECTIONS,
    default=[],
)
st.sidebar.markdown(f"**{len(articles)} articles loaded**")

def article_matches(tags_str):
    if not selected_tags:
        return True
    article_tags = [t.strip() for t in (tags_str or "").split(",")]
    return any(t in selected_tags for t in article_tags)

matched, unmatched = [], []
for row in articles:
    (matched if article_matches(row[7] or "") else unmatched).append(row)

grouped = {s: [] for s in ALL_SECTIONS}
for row in matched:
    bucket = row[6] if row[6] in ALL_SECTIONS else FALLBACK
    grouped[bucket].append(row)

def render_article_card(row):
    source, title, ai_summary, student_angle, link, published, category, tags = row
    tag_pills = "".join(
        f'<span class="tag-pill">{t.strip()}</span>'
        for t in (tags or "").split(",") if t.strip()
    )
    bullets_html = "".join(
        f'<div class="bullet-text">{line}</div>'
        for line in (ai_summary or "").splitlines() if line.strip()
    )
    angle_html = (
        f'<div class="student-angle">🎓 {student_angle}</div>'
        if student_angle else ""
    )
    st.markdown(f"""
    <div class="article-block">
        <div class="article-title"><a href="{link}" target="_blank" style="text-decoration:none;color:#111;">{title}</a></div>
        <div class="article-source">{source}</div>
        {tag_pills}
        {bullets_html}
        {angle_html}
    </div>
    """, unsafe_allow_html=True)

active_sections = [s for s in ALL_SECTIONS if s in selected_sections] if selected_sections else ALL_SECTIONS

def render_section(section):
    st.markdown(f"""
    <div class="section-label">{SECTION_ICONS[section]} {section} &nbsp;·&nbsp; {len(grouped[section])} articles</div>
    """, unsafe_allow_html=True)
    if not grouped[section]:
        st.caption("No articles in this category.")
    for row in grouped[section]:
        render_article_card(row)

# Industry News full width on top
if "Industry News" in active_sections:
    render_section("Industry News")

# Tech Trends + Company Updates side by side below
bottom_sections = [s for s in ["Tech Trends", "Company Updates"] if s in active_sections]
if bottom_sections:
    cols = st.columns(len(bottom_sections))
    for i, section in enumerate(bottom_sections):
        with cols[i]:
            render_section(section)

if unmatched:
    with st.expander(f"🔽 Other articles ({len(unmatched)}) — outside your selected interests"):
        other_cols = st.columns(3)
        for j, row in enumerate(unmatched):
            with other_cols[j % 3]:
                render_article_card(row)
