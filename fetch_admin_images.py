#!/usr/bin/env python3
"""Download Mobbin web admin screen images for the admin portal mood board."""

import os, json, base64, time
import urllib.request

TOKEN = open(os.environ['CLAUDE_SESSION_INGRESS_TOKEN_FILE']).read().strip()
MCP_URL = (
    "https://api.anthropic.com/v2/ccr-sessions/cse_018Lwznj4j9nnSVfAEw6kz6p/mcp"
    "?mcp_url=https%3A%2F%2Fapi.mobbin.com%2Fmcp"
    "&mcp_server_id=abca5ed1-638b-51c2-a804-1b62f1a4fa1d"
    "&toolbox_mcp_server_id=90937760-6e11-490d-bc64-1b022732700e"
)
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "X-MCP-Server-ID": "90937760-6e11-490d-bc64-1b022732700e",
    "X-Session-UUID": "cse_018Lwznj4j9nnSVfAEw6kz6p",
}
IMG_DIR = "/home/user/claude-code-test/admin_images"
os.makedirs(IMG_DIR, exist_ok=True)

def mcp_call(payload, retries=3):
    data = json.dumps(payload).encode()
    for attempt in range(retries):
        try:
            req = urllib.request.Request(MCP_URL, data=data, headers=HEADERS, method="POST")
            lines = []
            with urllib.request.urlopen(req, timeout=120) as resp:
                buf = b""
                while True:
                    chunk = resp.read(4096)
                    if not chunk:
                        break
                    buf += chunk
                    while b"\n" in buf:
                        line, buf = buf.split(b"\n", 1)
                        decoded = line.decode("utf-8", errors="replace").strip()
                        if decoded.startswith("data:"):
                            lines.append(decoded)
            for line in lines:
                try:
                    return json.loads(line[5:].strip())
                except Exception:
                    pass
            return {}
        except Exception as e:
            print(f"  Attempt {attempt+1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(5 * (attempt + 1))
    return {}

def search_and_save(query, limit=10):
    print(f"\n>>> Searching: {query[:70]}")
    result = mcp_call({
        "jsonrpc": "2.0", "id": 2, "method": "tools/call",
        "params": {
            "name": "search_screens",
            "arguments": {"query": query, "platform": "web", "limit": limit,
                          "mode": "fast", "image_format": "jpg"}
        }
    })
    content = result.get("result", {}).get("content", [])

    metadata_list = []
    images_b64 = []

    for item in content:
        if item.get("type") == "text":
            try:
                d = json.loads(item["text"])
                if "screens" in d:
                    metadata_list = d["screens"]
            except Exception:
                pass
        elif item.get("type") == "image":
            images_b64.append((item.get("data",""), item.get("mimeType","image/jpeg")))

    saved = []
    for i, (meta, (b64, mime)) in enumerate(zip(metadata_list, images_b64)):
        sid = meta.get("id", f"unknown_{i}")
        app = meta.get("app_name", "")
        ext = "jpg" if "jpeg" in mime or "jpg" in mime else "webp"
        fname = f"{sid}.{ext}"
        fpath = os.path.join(IMG_DIR, fname)
        if not os.path.exists(fpath):
            img_bytes = base64.b64decode(b64)
            with open(fpath, "wb") as f:
                f.write(img_bytes)
            print(f"  Saved [{i}] {app} → {fname}")
        else:
            print(f"  Skip [{i}] {app} → {fname} (exists)")
        saved.append({"id": sid, "app": app, "path": f"admin_images/{fname}"})

    print(f"  Got {len(saved)} images")
    time.sleep(2)
    return saved

# All searches for admin portal mood board
SEARCHES = [
    # 1 — Overview dashboard: stats, KPIs, summary cards
    ("admin dashboard overview stats cards users active total web", 10),
    # 2 — User management table: list, search, filter, status
    ("user management table directory email role status web admin", 10),
    # 3 — Invite users: modal, email input, role selection, send invite
    ("invite team member modal email role permissions send web", 10),
    # 4 — Role & permissions settings
    ("role permissions settings access control admin configure web", 10),
    # 5 — Structured content / criteria editor: tree, form rows, rich text
    ("content editor structured form fields criteria list edit web", 10),
    # 6 — Knowledge base / guidance text editor
    ("knowledge base article editor guidance instructions rich text web", 10),
    # 7 — Certificate & document management: file list, upload, status
    ("certificate document file upload list management table web", 10),
    # 8 — Student / learner profile detail: progress, assignments, history
    ("student learner profile detail progress assignments courses web", 10),
    # 9 — Deadline & date management: scheduling, extensions, calendar
    ("deadline date schedule extension calendar management admin web", 10),
    # 10 — Settings / configuration / organisation setup
    ("settings organisation configuration account setup billing web admin", 10),
    # 11 — Onboarding / welcome / registration flow steps
    ("onboarding setup wizard welcome steps registration complete web", 10),
    # 12 — Compliance / audit log / activity history
    ("audit log activity history compliance report admin web", 8),
]

all_saved = {}
for query, limit in SEARCHES:
    results = search_and_save(query, limit)
    for r in results:
        all_saved[r["id"]] = r

print(f"\n=== Total unique admin images: {len(all_saved)} ===")

with open("/home/user/claude-code-test/admin_image_manifest.json", "w") as f:
    json.dump(all_saved, f, indent=2)
print("Manifest written to admin_image_manifest.json")
