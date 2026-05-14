#!/usr/bin/env python3
"""Build mood board HTML from locally saved images."""

import json, os

with open('/home/user/claude-code-test/image_manifest.json') as f:
    manifest = json.load(f)

# Images arrived in order of the 12 searches, 10 images each
all_screens = list(manifest.values())

# Map index → search group
GROUPS = [
    ("A", "Clean Minimal Light — Home Dashboards",
     "Pure white and off-white backgrounds, card-based layouts, readable type. The aesthetic used by GOV.UK, NHS, and HMRC digital services. Unintimidating for non-technical users on site.",
     "t-a", 0, 10),
    ("A", "Clean Minimal Light — Progress & Summary Views",
     "Clear percentage bars, section cards, today vs overall views. Shows progress without overwhelming complexity.",
     "t-a", 10, 10),
    ("A", "Clean Minimal Light — Task & Project Lists",
     "Row-based lists with clean hierarchy, counts, and disclosure patterns. Direct analogue for a list of NVQ job cards.",
     "t-a", 20, 10),
    ("B", "Structured Utility — Job Card Creation",
     "Form layouts built for task-oriented work: client fields, date pickers, address rows, green/blue CTAs. Closest to MOS Training's job card anatomy.",
     "t-b", 30, 10),
    ("B", "Structured Utility — Criteria & Grouped Checklists",
     "Accordion lists, section headers with counts, checkbox rows. The core NVQ criteria list pattern.",
     "t-b", 40, 10),
    ("📷", "Evidence Capture — Photo & Document Upload",
     "Camera attachment zones, before/after sections, numbered slots, action sheets. The moment the tradesperson photographs their work.",
     "t-e", 50, 10),
    ("🎙", "Voice to Text — Audio Capture",
     "Microphone UIs, waveform visualisers, live transcription views. Essential for gloved hands on building sites.",
     "t-e", 60, 10),
    ("🏆", "Progress & Certification — Badges & Qualifications",
     "Certificate lists, badge grids, completion states, milestone views. The learner's NVQ qualification overview.",
     "t-e", 70, 10),
    ("C", "Dark / High-Contrast — Utility Dashboards",
     "Deep black or navy backgrounds with vivid accents. Best outdoor readability on OLED screens. Technical, trusted aesthetic.",
     "t-c", 80, 10),
    ("E", "Step-by-Step Wizard Flows",
     "Progress bars, step counters, pill chains. Multi-step compliance forms and onboarding flows mapped to job card creation and evidence submission.",
     "t-d", 90, 10),
    ("D", "Enterprise Compliance — Document Upload",
     "Dashed upload zones, mandatory/optional labels, numbered requirement lists. Regulated data capture patterns.",
     "t-d", 100, 10),
    ("D", "Enterprise Compliance — Safety & Agreement Screens",
     "Tick-box checklists, warning banners, \"I Accept\" CTAs, Required* labels. The language of regulated compliance tools.",
     "t-d", 110, 7),
]

TAG_LABELS = {
    "t-a": "Direction A — Clean Minimal",
    "t-b": "Direction B — Utility / Trade",
    "t-c": "Direction C — Dark",
    "t-d": "Direction D — Enterprise",
    "t-e": "Key Screen",
}

def card_html(screen, tag):
    path = screen['path']
    app = screen['app']
    sid = screen['id']
    tag_label = TAG_LABELS.get(tag, "")
    return f'''
    <div class="card">
      <div class="card-img">
        <img src="{path}" loading="lazy" alt="{app} screen">
      </div>
      <div class="card-body">
        <div class="card-app">{app}</div>
        <span class="card-tag {tag} tag">{tag_label}</span>
      </div>
    </div>'''

def section_html(num, title, desc, tag, start, count):
    screens_slice = all_screens[start:start+count]
    cards = "\n".join(card_html(s, tag) for s in screens_slice)
    num_bg = {
        "t-a": "#1a3850",
        "t-b": "#15803d",
        "t-c": "#1e293b",
        "t-d": "#b45309",
        "t-e": "#475569",
    }.get(tag, "#475569")
    return f'''
  <section class="sec">
    <div class="sec-head">
      <div class="sec-num" style="background:{num_bg}">{num}</div>
      <div class="sec-meta">
        <h2 class="sec-title">{title}</h2>
        <p class="sec-desc">{desc}</p>
      </div>
    </div>
    <div class="grid">
{cards}
    </div>
  </section>'''

sections = "\n".join(section_html(*g) for g in GROUPS)

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MOS Training — App Mood Board</title>
<style>
  :root {{
    --bg: #f2f1ef;
    --surface: #ffffff;
    --border: #e0deda;
    --text: #111111;
    --sub: #555555;
    --muted: #888888;
    --accent: #1a3850;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: var(--bg); color: var(--text); }}

  .hdr {{ background: var(--accent); color: #fff; padding: 52px 64px 44px; }}
  .hdr-eye {{ font-size: 10.5px; font-weight: 700; letter-spacing: .14em; text-transform: uppercase; opacity: .55; margin-bottom: 12px; }}
  .hdr h1 {{ font-size: 40px; font-weight: 800; letter-spacing: -.025em; margin-bottom: 10px; line-height: 1.1; }}
  .hdr-sub {{ font-size: 15px; opacity: .7; max-width: 620px; line-height: 1.7; }}

  .dir-bar {{ background: #fff; border-bottom: 1px solid var(--border); padding: 16px 64px; display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }}
  .dir-label {{ font-size: 10px; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: var(--muted); margin-right: 4px; }}
  .tag {{ padding: 4px 13px; border-radius: 999px; font-size: 11px; font-weight: 600; }}
  .t-a {{ background: #dbeafe; color: #1d4ed8; }}
  .t-b {{ background: #dcfce7; color: #15803d; }}
  .t-c {{ background: #1e293b; color: #94a3b8; }}
  .t-d {{ background: #fef9c3; color: #854d0e; }}
  .t-e {{ background: #f3e8ff; color: #7e22ce; }}

  main {{ padding: 56px 64px 80px; }}

  .sec {{ margin-bottom: 72px; }}
  .sec-head {{ display: flex; align-items: flex-start; gap: 18px; border-bottom: 2px solid var(--border); padding-bottom: 20px; margin-bottom: 24px; }}
  .sec-num {{ width: 40px; height: 40px; border-radius: 50%; color: #fff; font-size: 15px; font-weight: 800; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 3px; }}
  .sec-meta {{ flex: 1; }}
  .sec-title {{ font-size: 22px; font-weight: 800; letter-spacing: -.01em; margin-bottom: 6px; }}
  .sec-desc {{ font-size: 13.5px; color: var(--sub); line-height: 1.65; max-width: 760px; }}

  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(165px, 1fr)); gap: 16px; }}

  .card {{ background: var(--surface); border-radius: 14px; border: 1px solid var(--border); overflow: hidden; transition: box-shadow .15s, transform .15s; }}
  .card:hover {{ box-shadow: 0 10px 32px rgba(0,0,0,.11); transform: translateY(-3px); }}
  .card-img {{ background: #eae9e7; aspect-ratio: 9/16; overflow: hidden; }}
  .card-img img {{ width: 100%; height: 100%; object-fit: cover; object-position: top; display: block; }}
  .card-body {{ padding: 10px 12px 12px; display: flex; align-items: center; justify-content: space-between; gap: 8px; }}
  .card-app {{ font-size: 11px; font-weight: 700; color: var(--text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}

  footer {{ border-top: 1px solid var(--border); padding: 24px 64px; display: flex; justify-content: space-between; background: #fff; font-size: 12.5px; color: var(--muted); }}

  @media (max-width: 900px) {{
    .hdr, .dir-bar, main, footer {{ padding-left: 20px; padding-right: 20px; }}
    .hdr h1 {{ font-size: 28px; }}
    .grid {{ grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); }}
  }}
</style>
</head>
<body>
<header class="hdr">
  <div class="hdr-eye">MOS Training — NVQ Evidence Capture App · Electricians &amp; Construction</div>
  <h1>Visual Direction<br>Mood Board</h1>
  <p class="hdr-sub">120 curated screens from real apps, grouped by visual style and key screen type. Share with the client to pick a design direction before work begins.</p>
</header>

<div class="dir-bar">
  <span class="dir-label">Visual Directions →</span>
  <span class="tag t-a">A — Clean Minimal Light</span>
  <span class="tag t-b">B — Structured Utility</span>
  <span class="tag t-c">C — Dark High Contrast</span>
  <span class="tag t-d">D — Enterprise Compliance</span>
  <span class="tag t-e">Key Screen Types</span>
</div>

<main>
{sections}
</main>

<footer>
  <p>MOS Training — NVQ Evidence Capture App &nbsp;·&nbsp; Mood Board · May 2026</p>
  <p>Screens sourced from Mobbin — real production app UI references</p>
</footer>
</body>
</html>'''

with open('/home/user/claude-code-test/moodboard.html', 'w') as f:
    f.write(html)

print(f"Built moodboard.html with {len(all_screens)} screens across {len(GROUPS)} sections")
