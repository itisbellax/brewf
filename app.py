import streamlit as st
import json
import os
import base64
from datetime import datetime

# ─── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BREWF",
    page_icon="⬛",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Podcast import (graceful fallback) ───────────────────────────────────────
try:
    from podcast import generate_podcast, AUDIO_PATH
    HAS_PODCAST_MODULE = True
except Exception:
    HAS_PODCAST_MODULE = False
    AUDIO_PATH = "podcast.mp3"
    generate_podcast = None

# ─── Data ─────────────────────────────────────────────────────────────────────
def load_articles():
    if os.path.exists("articles.json"):
        with open("articles.json") as f:
            return json.load(f)
    try:
        from db import get_all_processed
        rows = get_all_processed()
        return [{"source": r[0], "title": r[1], "ai_summary": r[2],
                 "student_angle": r[3], "link": r[4], "published": r[5],
                 "category": r[6], "tags": r[7]} for r in rows]
    except Exception:
        return []

@st.cache_data
def load_audio_bytes(path):
    with open(path, "rb") as f:
        return f.read()

# ─── Font: Cabinet Grotesk Black (base64-embedded) ────────────────────────────
def _get_font_face():
    for p in ["CabinetGrotesk-Black.ttf", "fonts/CabinetGrotesk-Black.ttf",
              "static/CabinetGrotesk-Black.ttf"]:
        if os.path.exists(p):
            with open(p, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            return (
                "@font-face{"
                "font-family:'Cabinet Grotesk';"
                f"src:url('data:font/truetype;base64,{b64}') format('truetype');"
                "font-weight:900;font-style:normal;font-display:swap;}"
            )
    return ""

FONT_FACE = _get_font_face()

# ─── Constants ────────────────────────────────────────────────────────────────
TAG_CLASS = {
    "Software Engineering": "brewf-tag-se",
    "AI & ML":              "brewf-tag-ai",
    "Security":             "brewf-tag-sec",
    "Data Science":         "brewf-tag-data",
    "Cloud & DevOps":       "brewf-tag-cloud",
    "Product & PM":         "brewf-tag-pm",
}
ALL_INTERESTS = ["Software Engineering", "AI & ML", "Security",
                 "Data Science", "Cloud & DevOps", "Product & PM"]
ALL_SECTIONS  = ["Industry News", "Tech Trends", "Company Updates"]

# ─── SVG icons ────────────────────────────────────────────────────────────────
def _svg(d, w=16):
    return (f'<svg width="{w}" height="{w}" viewBox="0 0 24 24" fill="none" '
            f'stroke="currentColor" stroke-width="1.5" '
            f'stroke-linecap="round" stroke-linejoin="round">{d}</svg>')

SVG_GLOBE = _svg('<circle cx="12" cy="12" r="9"/>'
                 '<path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>')
SVG_TREND = _svg('<path d="m3 17 6-6 4 4 8-8"/><path d="M14 7h7v7"/>')
SVG_BUILD = _svg('<path d="M3 21V7l6-4 6 4v14"/><path d="M15 11h6v10"/>'
                 '<path d="M7 9v.01M7 13v.01M7 17v.01M11 9v.01M11 13v.01M11 17v.01"/>')
SVG_CAP   = _svg('<path d="m2 10 10-5 10 5-10 5z"/>'
                 '<path d="M6 12v5c0 1.5 3 3 6 3s6-1.5 6-3v-5"/>', w=12)
SVG_PLAY  = _svg('<path d="M7 5v14l12-7z" fill="currentColor" stroke="none"/>', w=14)

SECTION_ICONS = {
    "Industry News":   SVG_GLOBE,
    "Tech Trends":     SVG_TREND,
    "Company Updates": SVG_BUILD,
}

# ─── Render helpers ───────────────────────────────────────────────────────────
def _tag(name):
    cls = TAG_CLASS.get(name.strip(), "brewf-tag-se")
    return f'<span class="brewf-tag {cls}">{name.strip()}</span>'

def _waveform():
    import math
    bars = []
    for i in range(32):
        s = math.sin(i * 1.7) * math.cos(i * 0.6)
        h = int(30 + (1 + s) * 32)
        bars.append(f'<span class="brewf-bar" style="height:{h}%"></span>')
    return "".join(bars)

def render_article(a):
    source        = (a.get("source") or "").upper()
    title         = a.get("title") or ""
    ai_summary    = a.get("ai_summary") or ""
    student_angle = a.get("student_angle") or ""
    link          = a.get("link") or "#"
    tags_str      = a.get("tags") or ""

    bullets      = [l.lstrip("•–—").strip() for l in ai_summary.splitlines() if l.strip()]
    bullets_html = "".join(f"<li>{b}</li>" for b in bullets[:3])
    tags         = [t.strip() for t in tags_str.split(",") if t.strip()]
    tags_html    = "".join(_tag(t) for t in tags)

    take_html = ""
    if student_angle:
        take_html = (
            f'<div class="brewf-take">'
            f'<span class="brewf-take-label">{SVG_CAP} Student Take</span>'
            f'<span class="brewf-take-body">{student_angle}</span>'
            f'</div>'
        )

    return (
        f'<div class="brewf-article">'
        f'  <div class="brewf-article-meta">'
        f'    <span class="brewf-fresh-dot"></span>'
        f'    <span>{source}</span>'
        f'    <span class="brewf-sep">·</span>'
        f'    <span>TODAY</span>'
        f'  </div>'
        f'  <h4 class="brewf-article-title">'
        f'    <a href="{link}" target="_blank" rel="noopener">{title}</a>'
        f'  </h4>'
        f'  <ul class="brewf-bullets">{bullets_html}</ul>'
        f'  <div class="brewf-tags">{tags_html}</div>'
        f'  {take_html}'
        f'</div>'
    )

def render_section(section_name, articles_list):
    icon  = SECTION_ICONS.get(section_name, "")
    count = len(articles_list)
    cards = "".join(render_article(a) for a in articles_list)
    if not cards:
        cards = '<p class="brewf-empty">No stories match your interests in this section.</p>'
    return (
        f'<div class="brewf-feed-section">'
        f'  <div class="brewf-section-head">'
        f'    <span class="brewf-section-icon">{icon}</span>'
        f'    <span class="brewf-section-title">{section_name.upper()}</span>'
        f'    <span class="brewf-section-sep"></span>'
        f'    <span class="brewf-section-count">{count:02d} STORIES</span>'
        f'  </div>'
        f'  {cards}'
        f'</div>'
    )

# ─── Time ─────────────────────────────────────────────────────────────────────
now      = datetime.now()
day_str  = now.strftime("%a").upper()
date_str = now.strftime("%b %d").upper()
time_str = now.strftime("%H:%M")

# ─── Load data ────────────────────────────────────────────────────────────────
articles      = load_articles()
article_count = len(articles)

# ══════════════════════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""<style>
{FONT_FACE}
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700&family=Geist+Mono:wght@400;500&display=swap');

:root{{
  --bg:#0A0A0A;--bg-1:#111;--bg-2:#161616;--bg-3:#1C1C1C;
  --line:#232323;--line-2:#2E2E2E;
  --fg:#FAFAF7;--fg-2:#B8B8B3;--fg-3:#7A7A75;--fg-4:#4A4A47;
  --cream:#E8DFC9;--cream-dim:#A89F8B;
  --signal:#C9A961;
  --font-display:'Cabinet Grotesk','Geist',system-ui,sans-serif;
  --font-sans:'Geist',system-ui,'Helvetica Neue',sans-serif;
  --font-mono:'Geist Mono',ui-monospace,'SF Mono',monospace;
  --ease-out:cubic-bezier(.2,.7,.2,1);
  --dur:200ms;
  --max-w:1280px;
  --gutter:clamp(24px,4vw,64px);
}}

html,body,[class*="css"]{{
  font-family:var(--font-sans)!important;
  background-color:var(--bg)!important;
  color:var(--fg)!important;
  -webkit-font-smoothing:antialiased;
}}

/* ── Hide Streamlit chrome ── */
#MainMenu,header,footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"]{{
  visibility:hidden!important;height:0!important;overflow:hidden!important;
}}
[data-testid="stAppViewContainer"]{{background:transparent!important;}}
.main .block-container{{padding:0!important;max-width:100%!important;}}
section[data-testid="stSidebar"]{{display:none!important;}}
[data-testid="stVerticalBlock"]>div{{gap:0!important;}}
.stApp{{background:transparent!important;position:relative;z-index:1;}}

/* ── Canvas ── */
#brewf-canvas{{
  position:fixed;inset:0;width:100%;height:100%;
  z-index:0;pointer-events:none;
}}

/* ── Nav ── */
.brewf-nav{{
  position:sticky;top:0;z-index:50;
  border-bottom:1px solid var(--line);
  background:rgba(18,17,14,.72);
  -webkit-backdrop-filter:blur(14px);backdrop-filter:blur(14px);
}}
.brewf-nav-inner{{
  height:64px;max-width:var(--max-w);margin:0 auto;
  padding:0 var(--gutter);
  display:flex;align-items:center;justify-content:space-between;
}}
.brewf-nav-left{{display:flex;align-items:center;gap:0;}}
.brewf-wordmark{{font:900 18px/1 var(--font-display);letter-spacing:-.03em;color:var(--fg);}}
.brewf-nav-date{{
  font-family:var(--font-mono);font-size:11px;
  letter-spacing:.16em;text-transform:uppercase;color:var(--fg-3);
  padding-left:16px;border-left:1px solid var(--line);
  white-space:nowrap;margin-left:20px;
}}
.brewf-nav-right{{display:flex;gap:24px;}}
.brewf-navlink{{color:var(--fg-3);font:400 13px/1 var(--font-sans);}}
.brewf-navlink.active{{color:var(--fg);}}

/* ── Hero ── */
.brewf-hero{{
  padding:120px var(--gutter) 48px;
  text-align:center;max-width:var(--max-w);margin:0 auto;
}}
.brewf-eyebrow-pill{{
  display:inline-flex;align-items:center;gap:10px;
  font-family:var(--font-mono);font-size:11px;
  letter-spacing:.18em;text-transform:uppercase;color:var(--fg-3);
  margin-bottom:36px;padding:6px 14px;
  border:1px solid var(--line-2);border-radius:999px;
  background:rgba(31,28,14,.55);
}}
.brewf-signal-dot{{
  width:6px;height:6px;border-radius:50%;
  background:var(--signal);display:inline-block;flex:none;
  animation:brewf-pulse 2s ease-in-out infinite;
}}
@keyframes brewf-pulse{{
  0%,100%{{box-shadow:0 0 0 0 rgba(201,169,97,.5);}}
  50%{{box-shadow:0 0 0 6px rgba(201,169,97,0);}}
}}
.brewf-brand{{
  margin:0 0 20px;
  font:900 clamp(80px,14vw,180px)/.92 var(--font-display);
  letter-spacing:-.05em;color:var(--fg);
}}
.brewf-tagline{{
  font-size:clamp(15px,1.6vw,20px);line-height:1.4;
  color:var(--fg-2);margin:0 auto;max-width:36ch;font-weight:400;
}}

/* ── Podcast player card ── */
.brewf-podcast-wrap{{
  max-width:var(--max-w);margin:28px auto 0;
  padding:0 var(--gutter);
}}
.brewf-player{{
  background:rgba(31,28,14,.78);border:1px solid var(--line);
  border-radius:8px;padding:16px 20px;
  display:flex;align-items:center;gap:18px;
  transition:border-color var(--dur) var(--ease-out);
}}
.brewf-player:hover{{border-color:var(--line-2);}}
.brewf-play-circle{{
  width:44px;height:44px;flex:none;border-radius:50%;
  background:var(--cream);color:var(--bg);
  display:flex;align-items:center;justify-content:center;
}}
.brewf-player-meta{{flex:1;min-width:0;display:flex;flex-direction:column;gap:8px;}}
.brewf-player-label{{font-family:var(--font-mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;}}
.brewf-player-strong{{color:var(--fg);font-weight:500;}}
.brewf-player-dim{{color:var(--fg-3);}}
.brewf-waveform{{display:flex;align-items:flex-end;gap:2px;height:22px;}}
.brewf-bar{{width:3px;background:var(--fg-4);border-radius:1px;display:inline-block;}}

/* ── Interests bar ── */
.brewf-interests-wrap{{
  max-width:var(--max-w);margin:0 auto;
  padding:18px var(--gutter) 36px;
  border-bottom:1px solid var(--line);margin-bottom:44px;
  display:flex;align-items:flex-start;gap:16px;flex-wrap:wrap;
}}
.brewf-interests-label{{
  font-family:var(--font-mono);font-size:11px;
  letter-spacing:.18em;text-transform:uppercase;color:var(--fg-3);
  margin-top:7px;white-space:nowrap;flex:none;
}}

/* st.pills overrides */
div[data-testid="stPills"]{{padding:0!important;margin:0!important;}}
div[data-testid="stPills"] label{{display:none!important;}}
div[data-testid="stPills"]>div>div{{display:flex!important;gap:8px!important;flex-wrap:wrap!important;}}
div[data-testid="stPills"] button{{
  background:transparent!important;color:var(--fg-2)!important;
  border:1px solid var(--line-2)!important;border-radius:999px!important;
  padding:6px 14px!important;font:400 13px/1.2 var(--font-sans)!important;
  min-height:auto!important;height:auto!important;
  transition:all var(--dur)!important;box-shadow:none!important;
}}
div[data-testid="stPills"] button:hover{{
  border-color:var(--fg)!important;color:var(--fg)!important;
}}
div[data-testid="stPills"] button[aria-pressed="true"],
div[data-testid="stPills"] button[aria-selected="true"]{{
  background:var(--fg)!important;color:var(--bg)!important;border-color:var(--fg)!important;
}}

/* ── Main ── */
.brewf-main{{
  max-width:var(--max-w);margin:0 auto;
  padding:0 var(--gutter) 96px;
}}
.brewf-industry{{margin-bottom:56px;}}
.brewf-two-col{{display:grid;grid-template-columns:1fr 1fr;gap:48px;}}
@media(max-width:880px){{.brewf-two-col{{grid-template-columns:1fr;}}}}

/* ── Section head ── */
.brewf-feed-section{{display:flex;flex-direction:column;}}
.brewf-section-head{{
  display:flex;align-items:center;gap:14px;
  padding-bottom:16px;border-bottom:1px solid var(--line);margin-bottom:14px;
}}
.brewf-section-icon{{color:var(--fg-3);display:flex;flex:none;}}
.brewf-section-title{{
  font-family:var(--font-mono);font-size:11px;
  letter-spacing:.2em;text-transform:uppercase;color:var(--fg);
  font-weight:500;white-space:nowrap;
}}
.brewf-section-sep{{flex:1;}}
.brewf-section-count{{font-family:var(--font-mono);font-size:11px;color:var(--fg-3);letter-spacing:.12em;white-space:nowrap;}}

/* ── Article card ── */
.brewf-article{{
  background:rgba(31,28,14,.78);border:1px solid var(--line);
  border-radius:8px;padding:20px 22px;
  display:flex;flex-direction:column;gap:11px;
  transition:border-color var(--dur) var(--ease-out);
  margin-bottom:12px;
}}
.brewf-article:hover{{border-color:var(--line-2);}}
.brewf-article-meta{{
  font-family:var(--font-mono);font-size:10px;
  letter-spacing:.18em;text-transform:uppercase;color:var(--fg-3);
  display:flex;align-items:center;gap:8px;
}}
.brewf-fresh-dot{{
  width:5px;height:5px;border-radius:50%;background:var(--signal);
  box-shadow:0 0 8px rgba(201,169,97,.5);display:inline-block;flex:none;
}}
.brewf-sep{{color:var(--fg-4);}}
.brewf-article-title{{margin:0;}}
.brewf-article-title a{{
  font:500 17px/1.35 var(--font-sans);letter-spacing:-.01em;
  color:var(--fg);text-decoration:none;border:0;
  transition:color var(--dur) var(--ease-out);
}}
.brewf-article-title a:hover{{color:var(--cream);}}
.brewf-bullets{{margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:5px;}}
.brewf-bullets li{{
  color:var(--fg-2);font-size:13.5px;line-height:1.55;
  padding-left:18px;position:relative;
}}
.brewf-bullets li::before{{content:"—";color:var(--fg-4);position:absolute;left:0;}}
.brewf-tags{{display:flex;gap:6px;flex-wrap:wrap;align-items:center;}}
.brewf-tag{{
  font-family:var(--font-mono);font-size:10px;letter-spacing:.06em;
  padding:3px 9px;border-radius:999px;border:1px solid;white-space:nowrap;
}}
.brewf-tag-se  {{color:#B8B8B3;background:rgba(255,255,255,.05); border-color:rgba(255,255,255,.08);}}
.brewf-tag-ai  {{color:#C9A961;background:rgba(201,169,97,.10); border-color:rgba(201,169,97,.25);}}
.brewf-tag-sec {{color:#C97A6F;background:rgba(201,122,111,.10);border-color:rgba(201,122,111,.25);}}
.brewf-tag-data{{color:#7FA1C9;background:rgba(127,161,201,.10);border-color:rgba(127,161,201,.25);}}
.brewf-tag-cloud{{color:#9BB59F;background:rgba(155,181,159,.10);border-color:rgba(155,181,159,.25);}}
.brewf-tag-pm  {{color:#C9A1B5;background:rgba(201,161,181,.10);border-color:rgba(201,161,181,.25);}}
.brewf-take{{border-left:2px solid var(--cream-dim);padding:4px 0 4px 14px;display:flex;flex-direction:column;gap:4px;}}
.brewf-take-label{{
  font-family:var(--font-mono);font-size:10px;
  letter-spacing:.16em;text-transform:uppercase;color:var(--cream-dim);
  display:inline-flex;align-items:center;gap:6px;white-space:nowrap;
}}
.brewf-take-body{{color:var(--fg-2);font-size:13px;line-height:1.55;font-style:italic;}}
.brewf-empty{{
  padding:28px;border:1px dashed var(--line-2);border-radius:8px;
  color:var(--fg-4);font-size:12px;font-family:var(--font-mono);
  letter-spacing:.08em;text-align:center;
}}

/* ── Podcast generate button ── */
[data-testid="stButton"]>button{{
  background:var(--cream)!important;color:var(--bg)!important;border:none!important;
  border-radius:4px!important;font:600 12px/1 var(--font-mono)!important;
  letter-spacing:.12em!important;text-transform:uppercase!important;
  padding:10px 20px!important;transition:all var(--dur)!important;box-shadow:none!important;
}}
[data-testid="stButton"]>button:hover{{background:#f1ead7!important;}}

/* ── Audio ── */
audio{{border-radius:4px;width:100%;filter:invert(.9) hue-rotate(180deg) brightness(.9);}}
[data-testid="stAudio"]{{margin:0;padding:0;}}

/* ── Spinner ── */
[data-testid="stSpinner"] *{{color:var(--fg-3)!important;}}

/* ── Footer ── */
.brewf-footer{{
  max-width:var(--max-w);margin:0 auto;
  padding:24px var(--gutter) 64px;border-top:1px solid var(--line);
  display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;
  font-family:var(--font-mono);font-size:11px;color:var(--fg-4);
  letter-spacing:.14em;text-transform:uppercase;
}}

/* ── Global ── */
::-webkit-scrollbar{{width:4px;}}
::-webkit-scrollbar-track{{background:var(--bg);}}
::-webkit-scrollbar-thumb{{background:var(--line-2);border-radius:2px;}}
::selection{{background:var(--cream);color:var(--bg);}}
</style>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# Canvas background animation
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""<script>
(function(){
  if(document.getElementById('brewf-canvas'))return;
  var c=document.createElement('canvas');
  c.id='brewf-canvas';
  c.style.cssText='position:fixed;inset:0;width:100%;height:100%;z-index:0;pointer-events:none;';
  document.body.insertBefore(c,document.body.firstChild);
  var ctx=c.getContext('2d'),W=0,H=0,dpr=Math.min(window.devicePixelRatio||1,2);
  function resize(){
    W=window.innerWidth;H=window.innerHeight;
    c.width=W*dpr;c.height=H*dpr;
    c.style.width=W+'px';c.style.height=H+'px';
    ctx.setTransform(dpr,0,0,dpr,0,0);
  }
  resize();
  window.addEventListener('resize',resize,{passive:true});
  var blobs=[
    {ax:.22,ay:.30,r:460,col:'84,75,57',   a:.55,fx:.00014,fy:.00018,phx:1.2,phy:2.7,axA:.14,ayA:.10},
    {ax:.78,ay:.42,r:520,col:'66,58,40',   a:.65,fx:.00011,fy:.00021,phx:0.6,phy:3.4,axA:.12,ayA:.12},
    {ax:.50,ay:.82,r:420,col:'54,52,48',   a:.65,fx:.00017,fy:.00013,phx:2.4,phy:1.0,axA:.16,ayA:.08},
    {ax:.85,ay:.18,r:320,col:'149,150,141',a:.18,fx:.00019,fy:.00016,phx:0.3,phy:2.0,axA:.10,ayA:.10},
    {ax:.15,ay:.70,r:380,col:'31,28,14',   a:.85,fx:.00013,fy:.00020,phx:1.7,phy:0.5,axA:.12,ayA:.10},
    {ax:.35,ay:.55,r:280,col:'192,193,185',a:.10,fx:.00018,fy:.00014,phx:2.1,phy:1.6,axA:.18,ayA:.14},
    {ax:.68,ay:.72,r:240,col:'241,242,236',a:.06,fx:.00015,fy:.00019,phx:0.9,phy:2.4,axA:.16,ayA:.12},
  ];
  function draw(t){
    ctx.globalCompositeOperation='source-over';
    ctx.fillStyle='#12110E';
    ctx.fillRect(0,0,W,H);
    ctx.filter='blur(60px)';
    ctx.globalCompositeOperation='lighter';
    blobs.forEach(function(b){
      var cx=(b.ax+Math.sin(t*b.fx+b.phx)*b.axA)*W;
      var cy=(b.ay+Math.cos(t*b.fy+b.phy)*b.ayA)*H;
      var g=ctx.createRadialGradient(cx,cy,0,cx,cy,b.r);
      g.addColorStop(0,'rgba('+b.col+','+b.a+')');
      g.addColorStop(.55,'rgba('+b.col+','+(b.a*.45)+')');
      g.addColorStop(1,'rgba('+b.col+',0)');
      ctx.fillStyle=g;ctx.beginPath();ctx.arc(cx,cy,b.r,0,Math.PI*2);ctx.fill();
    });
    ctx.filter='none';ctx.globalCompositeOperation='source-over';
    var vg=ctx.createRadialGradient(W/2,H/2,Math.min(W,H)*.35,W/2,H/2,Math.max(W,H)*.75);
    vg.addColorStop(0,'rgba(18,17,14,0)');
    vg.addColorStop(1,'rgba(18,17,14,0.75)');
    ctx.fillStyle=vg;ctx.fillRect(0,0,W,H);
  }
  var raf;
  function tick(t){draw(t);raf=requestAnimationFrame(tick);}
  raf=requestAnimationFrame(tick);
  document.addEventListener('visibilitychange',function(){
    if(document.hidden)cancelAnimationFrame(raf);
    else raf=requestAnimationFrame(tick);
  });
})();
</script>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# Nav
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="brewf-nav">
  <div class="brewf-nav-inner">
    <div class="brewf-nav-left">
      <span class="brewf-wordmark">BREWF</span>
      <span class="brewf-nav-date">{day_str} · {date_str} · {time_str}</span>
    </div>
    <div class="brewf-nav-right">
      <span class="brewf-navlink active">Today</span>
      <span class="brewf-navlink">Archive</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# Hero
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="brewf-hero">
  <div class="brewf-eyebrow-pill">
    <span class="brewf-signal-dot"></span>
    <span>Brewed at 06:00 &nbsp;·&nbsp; {article_count} stories today</span>
  </div>
  <h1 class="brewf-brand">BREWF</h1>
  <p class="brewf-tagline">Tech news for CS students who'd rather be coding.</p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# Podcast player
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="brewf-podcast-wrap">
  <div class="brewf-player">
    <div class="brewf-play-circle">{SVG_PLAY}</div>
    <div class="brewf-player-meta">
      <div class="brewf-player-label">
        <span class="brewf-player-strong">Today's Brief</span>
        <span class="brewf-player-dim"> · {article_count} stories · brewed at 06:00</span>
      </div>
      <div class="brewf-waveform">{_waveform()}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

if HAS_PODCAST_MODULE:
    pod_col, _ = st.columns([2, 3])
    with pod_col:
        if os.path.exists(AUDIO_PATH):
            try:
                st.audio(load_audio_bytes(AUDIO_PATH), format="audio/mp3")
            except Exception:
                pass
        else:
            if st.button("Generate Today's Brief"):
                with st.spinner("Brewing today's podcast..."):
                    try:
                        path, _ = generate_podcast()
                        if path:
                            st.rerun()
                    except Exception as e:
                        st.error(f"Could not generate podcast: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# Interest filter
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="brewf-interests-wrap">'
    '<span class="brewf-interests-label">Your interests</span>',
    unsafe_allow_html=True,
)

selected = st.pills(
    "interests",
    options=ALL_INTERESTS,
    selection_mode="multi",
    label_visibility="collapsed",
    default=[],
)

st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# Filter & group articles
# ══════════════════════════════════════════════════════════════════════════════
if not articles:
    st.markdown(
        '<div class="brewf-main">'
        '<p class="brewf-empty">No articles yet. Run <code>python main.py</code> first.</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.stop()

selected_set = set(selected) if selected else set()

def matches(article):
    if not selected_set:
        return True
    article_tags = {t.strip() for t in (article.get("tags") or "").split(",")}
    return bool(article_tags & selected_set)

grouped = {s: [] for s in ALL_SECTIONS}
for a in articles:
    if matches(a):
        bucket = a.get("category") if a.get("category") in ALL_SECTIONS else "Industry News"
        grouped[bucket].append(a)

# ══════════════════════════════════════════════════════════════════════════════
# Feed
# ══════════════════════════════════════════════════════════════════════════════
industry_html  = render_section("Industry News",   grouped["Industry News"])
trends_html    = render_section("Tech Trends",     grouped["Tech Trends"])
companies_html = render_section("Company Updates", grouped["Company Updates"])

st.markdown(f"""
<div class="brewf-main">
  <div class="brewf-industry">{industry_html}</div>
  <div class="brewf-two-col">
    {trends_html}
    {companies_html}
  </div>
</div>

<div class="brewf-footer">
  <span>BREWF &nbsp;·&nbsp; {now.strftime("%b %Y")} &nbsp;·&nbsp; <a href="https://github.com/itisbellax/brewf" style="color:inherit;text-decoration:underline;text-underline-offset:3px;">source</a></span>
  <span>That's the brief. See you tomorrow.</span>
</div>
""", unsafe_allow_html=True)
