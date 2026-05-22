#!/usr/bin/env python3
"""Build admin portal mood board HTML from locally saved images."""

import json, os

with open('/home/user/claude-code-test/admin_image_manifest.json') as f:
    manifest = json.load(f)

all_screens = list(manifest.values())

# tag → section letter
# a = Overview & Navigation
# b = User Management
# c = Content Management
# d = Settings & Config
# e = Key Screens

GROUPS = [
    ("A", "Overview Dashboard — Stats & Summary Cards",
     "At-a-glance KPI panels, user counts, completion rates, and activity summaries. The admin landing screen showing platform health before drilling into any function.",
     "t-a", 0, 10),
    ("A", "User Management — Directory & Table Views",
     "Filterable data tables: student/assessor/IQA rows, email, role badge, status pill, bulk-action toolbar. The primary admin workspace for managing hundreds of accounts.",
     "t-b", 10, 10),
    ("A", "User Onboarding — Invite Modal & Email Flow",
     "Email-input modals, role-selection dropdowns, send-invite CTAs. The exact pattern for adding a new student — admin types email, assigns assessor, student gets welcome link.",
     "t-b", 20, 10),
    ("B", "Roles & Permissions — Access Control Configuration",
     "Permission matrices, role-toggle rows, access-level descriptions. Defines what assessors vs IQAs vs admins can see and do — critical for multi-tier compliance platforms.",
     "t-b", 30, 10),
    ("C", "Criteria Manager — Structured Content Editor",
     "Row/tree editors for structured data: add criteria, edit labels, set mandatory minimums, configure evidence type requirements. Updated every 2–3 years without developer involvement.",
     "t-c", 40, 10),
    ("C", "Criteria Manager — Guidance Text & Rich Text Editing",
     "Prose editors for plain-English guidance copy attached to each criterion. Assessors and learners read this to understand what evidence is required.",
     "t-c", 50, 10),
    ("D", "Certificate & Document Management — File Lists & Uploads",
     "Document tables: prior qualifications, final NVQ certificates, identity proofs. Upload zones, file type badges, status indicators. Gated unlocking — units stay locked until cert is uploaded.",
     "t-d", 60, 10),
    ("D", "Student Profile — Progress, Assignments & History",
     "Individual learner view: assigned assessor, unit progress bars, deadline dates, evidence submitted. Admin's view of a student's full NVQ journey.",
     "t-d", 70, 10),
    ("B", "Deadline & Schedule Management",
     "Date pickers, deadline rows, extension request handling, calendar overlays. Admin sets completion deadlines per student; grants extensions where required.",
     "t-b", 80, 10),
    ("E", "Settings & Organisation Configuration",
     "Organisation profile, notification preferences, integration toggles, plan/billing. The setup layer that must be completed before any student can be invited.",
     "t-e", 90, 10),
    ("E", "Onboarding & Setup Wizard",
     "Step-by-step configuration flows: invite first user, create first unit, configure settings. Maps to admin's initial platform setup before going live with students.",
     "t-e", 100, 10),
    ("E", "Audit Log & Activity History",
     "Timestamped action feeds, compliance report tables, change history. Who did what and when — essential for regulated qualification delivery and IQA oversight.",
     "t-e", 110, 8),
]

TAG_LABELS = {
    "t-a": "Direction A — Overview",
    "t-b": "Direction B — Data Tables",
    "t-c": "Direction C — Content Editor",
    "t-d": "Direction D — Profile / Docs",
    "t-e": "Key Admin Screen",
}

def card_html(screen, tag):
    path = screen['path']
    app = screen['app']
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

def section_html(letter, title, desc, tag, start, count):
    screens_slice = all_screens[start:start+count]
    cards = "\n".join(card_html(s, tag) for s in screens_slice)
    num_bg = {
        "t-a": "#1a3850",
        "t-b": "#15803d",
        "t-c": "#7c3aed",
        "t-d": "#b45309",
        "t-e": "#475569",
    }.get(tag, "#475569")
    return f'''
  <section class="sec">
    <div class="sec-head">
      <div class="sec-num" style="background:{num_bg}">{letter}</div>
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
<title>MOS Training — Admin Portal Mood Board</title>
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
  .hdr-sub {{ font-size: 15px; opacity: .7; max-width: 680px; line-height: 1.7; }}

  .breadcrumb {{ background: #fff; border-bottom: 1px solid var(--border); padding: 10px 64px; font-size: 12px; color: var(--muted); }}
  .breadcrumb a {{ color: var(--muted); text-decoration: none; }}
  .breadcrumb a:hover {{ color: var(--text); }}

  .dir-bar {{ background: #fff; border-bottom: 1px solid var(--border); padding: 16px 64px; display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }}
  .dir-label {{ font-size: 10px; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: var(--muted); margin-right: 4px; }}
  .tag {{ padding: 4px 13px; border-radius: 999px; font-size: 11px; font-weight: 600; }}
  .t-a {{ background: #dbeafe; color: #1d4ed8; }}
  .t-b {{ background: #dcfce7; color: #15803d; }}
  .t-c {{ background: #ede9fe; color: #6d28d9; }}
  .t-d {{ background: #fef9c3; color: #854d0e; }}
  .t-e {{ background: #f1f5f9; color: #475569; }}

  main {{ padding: 56px 64px 80px; }}

  .sec {{ margin-bottom: 72px; }}
  .sec-head {{ display: flex; align-items: flex-start; gap: 18px; border-bottom: 2px solid var(--border); padding-bottom: 20px; margin-bottom: 24px; }}
  .sec-num {{ width: 40px; height: 40px; border-radius: 50%; color: #fff; font-size: 15px; font-weight: 800; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 3px; }}
  .sec-meta {{ flex: 1; }}
  .sec-title {{ font-size: 22px; font-weight: 800; letter-spacing: -.01em; margin-bottom: 6px; }}
  .sec-desc {{ font-size: 13.5px; color: var(--sub); line-height: 1.65; max-width: 780px; }}

  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 18px; }}

  .card {{ background: var(--surface); border-radius: 14px; border: 1px solid var(--border); overflow: hidden; transition: box-shadow .15s, transform .15s; }}
  .card:hover {{ box-shadow: 0 10px 32px rgba(0,0,0,.11); transform: translateY(-3px); }}
  .card-img {{ background: #eae9e7; aspect-ratio: 16/10; overflow: hidden; }}
  .card-img img {{ width: 100%; height: 100%; object-fit: cover; object-position: top; display: block; }}
  .card-body {{ padding: 10px 12px 12px; display: flex; align-items: center; justify-content: space-between; gap: 8px; }}
  .card-app {{ font-size: 11px; font-weight: 700; color: var(--text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}

  footer {{ border-top: 1px solid var(--border); padding: 24px 64px; display: flex; justify-content: space-between; background: #fff; font-size: 12.5px; color: var(--muted); }}

  @media (max-width: 900px) {{
    .hdr, .dir-bar, main, footer, .breadcrumb {{ padding-left: 20px; padding-right: 20px; }}
    .hdr h1 {{ font-size: 28px; }}
    .grid {{ grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); }}
  }}
</style>
</head>
<body>
<header class="hdr">
  <div class="hdr-eye">MOS Training — NVQ Admin Portal · Web Platform</div>
  <h1>Admin Portal<br>Visual Direction Mood Board</h1>
  <p class="hdr-sub">118 curated screens from real web admin products, grouped by admin function. Use alongside the mobile app mood board to align on a consistent design language across both surfaces.</p>
</header>

<div class="breadcrumb">
  <a href="index.html">← Mobile App Mood Board</a>
  &nbsp;·&nbsp; Admin Portal Mood Board (Web)
</div>

<div class="dir-bar">
  <span class="dir-label">Screen Groups →</span>
  <span class="tag t-a">A — Overview &amp; Stats</span>
  <span class="tag t-b">B — Data Tables &amp; Users</span>
  <span class="tag t-c">C — Content &amp; Criteria Editor</span>
  <span class="tag t-d">D — Profiles &amp; Documents</span>
  <span class="tag t-e">Key Admin Screens</span>
</div>

<main>
{sections}
</main>

<footer>
  <p>MOS Training — NVQ Admin Portal &nbsp;·&nbsp; Mood Board · May 2026</p>
  <p>Screens sourced from Mobbin — real production app UI references</p>
</footer>
</body>
</html>'''

with open('/home/user/claude-code-test/admin-moodboard.html', 'w') as f:
    f.write(html)

print(f"Built admin-moodboard.html with {len(all_screens)} screens across {len(GROUPS)} sections")
