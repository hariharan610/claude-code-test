#!/usr/bin/env python3
"""Download Mobbin screen images via the MCP API and save them locally."""

import os, json, base64, time, sys
import urllib.request, urllib.parse

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
IMG_DIR = "/home/user/claude-code-test/images"
os.makedirs(IMG_DIR, exist_ok=True)

def mcp_call(payload, retries=3):
    data = json.dumps(payload).encode()
    for attempt in range(retries):
        try:
            req = urllib.request.Request(MCP_URL, data=data, headers=HEADERS, method="POST")
            lines = []
            with urllib.request.urlopen(req, timeout=120) as resp:
                # Stream SSE line by line
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

def search(query, limit=10):
    result = mcp_call({
        "jsonrpc": "2.0", "id": 2, "method": "tools/call",
        "params": {
            "name": "search_screens",
            "arguments": {"query": query, "platform": "ios", "limit": limit,
                          "mode": "deep", "image_format": "jpg"}
        }
    })
    content = result.get("result", {}).get("content", [])
    screens = []
    for item in content:
        if item.get("type") == "text":
            try:
                d = json.loads(item["text"])
                screens.extend(d.get("screens", []))
            except Exception:
                pass
        elif item.get("type") == "image":
            # base64 image attached alongside — paired by index
            screens.append({"_img": item.get("data",""), "_mime": item.get("mimeType","image/jpeg")})
    return content, screens

def search_and_save(query, limit=10):
    """Search Mobbin, save images to disk, return list of {id, app_name, path}."""
    print(f"\n>>> Searching: {query[:60]}")
    result = mcp_call({
        "jsonrpc": "2.0", "id": 2, "method": "tools/call",
        "params": {
            "name": "search_screens",
            "arguments": {"query": query, "platform": "ios", "limit": limit,
                          "mode": "fast", "image_format": "jpg"}
        }
    })
    content = result.get("result", {}).get("content", [])

    # content alternates: text (metadata), image, text, image, ...
    # or all images together after the text. Let's parse carefully.
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
        saved.append({"id": sid, "app": app, "path": f"images/{fname}"})

    print(f"  Saved {len(saved)} images")
    time.sleep(1)
    return saved

# ── All queries needed for the mood board ──
SEARCHES = [
    ("clean white home dashboard today summary cards professional app", 10),
    ("progress tracking cards sections completion percentage", 10),
    ("task list project list minimal white clean rows", 10),
    ("job card creation form site address client date schedule", 10),
    ("grouped checklist accordion outcomes criteria compliance", 10),
    ("photo upload evidence camera attachment required sections", 10),
    ("voice recording microphone audio transcription screen", 10),
    ("certificate badge achievement progress learning qualification", 10),
    ("dark black home dashboard utility status compliance", 10),
    ("multi-step wizard form progress bar step counter compliance", 10),
    ("document upload required proof identity compliance", 10),
    ("safety checklist compliance agreement mandatory fields", 10),
]

all_saved = {}
for query, limit in SEARCHES:
    results = search_and_save(query, limit)
    for r in results:
        all_saved[r["id"]] = r

print(f"\n=== Total unique images: {len(all_saved)} ===")

# Write manifest
with open("/home/user/claude-code-test/image_manifest.json", "w") as f:
    json.dump(all_saved, f, indent=2)
print("Manifest written to image_manifest.json")
