#!/usr/bin/env python3
"""備份 loot-drop.io 今日狀態:HTML 各頁 + 打包 JS 資產 + 資料 API 原始回應。"""
import json, re, time, urllib.request, pathlib

BASE = "https://www.loot-drop.io"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36")
SNAP = pathlib.Path(__file__).parent
HTML = SNAP / "html"
ASSETS = SNAP / "assets"
for d in (HTML, ASSETS):
    d.mkdir(parents=True, exist_ok=True)

PAGES = {
    "index": "/", "why-they-fail": "/why-they-fail", "deep-dives": "/deep-dives",
    "rebuilds": "/rebuilds", "lists": "/lists.html", "insights": "/insights.html",
    "dashboard": "/dashboard.html", "database-view": "/database-view",
    "ideas": "/ideas.html", "story": "/story.html", "roadmap": "/roadmap.html",
    "faq": "/faq",
}

def get(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
        return data if binary else data.decode("utf-8", "replace")

# 1) 抓所有 HTML 頁面
print("== HTML 頁面 ==")
all_html = ""
for name, path in PAGES.items():
    try:
        html = get(BASE + path)
        (HTML / f"{name}.html").write_text(html, encoding="utf-8")
        all_html += html
        print(f"  [ok] {name}.html  ({len(html):,}B)")
    except Exception as e:
        print(f"  [ERR] {name}: {e}")
    time.sleep(0.2)

# 2) 從所有 HTML 解析資產路徑(/assets/*.js /assets/*.css 等 + /js/*.js)
print("\n== 解析資產路徑 ==")
asset_paths = set(re.findall(r'(?:src|href)="(/(?:assets|js)/[^"]+)"', all_html))
print(f"  發現 {len(asset_paths)} 個資產")

# 3) 下載資產(JS/CSS),並遞迴抓 JS 內 import 的 chunk
print("\n== 下載資產 ==")
downloaded = set()
queue = list(asset_paths)
while queue:
    ap = queue.pop()
    if ap in downloaded:
        continue
    downloaded.add(ap)
    try:
        content = get(BASE + ap, binary=True)
        fname = ap.split("/")[-1]
        (ASSETS / fname).write_bytes(content)
        print(f"  [ok] {fname}  ({len(content):,}B)")
        # 從 JS 內找更多 chunk 引用,如 "./assets/xxx.js" 或 "/assets/xxx.js"
        if fname.endswith(".js"):
            text = content.decode("utf-8", "replace")
            for m in re.findall(r'["\'](?:\.)?(/?assets/[A-Za-z0-9_\-]+\.js)["\']', text):
                p = m if m.startswith("/") else "/" + m
                if p not in downloaded:
                    queue.append(p)
    except Exception as e:
        print(f"  [ERR] {ap}: {e}")
    time.sleep(0.15)

# 4) 寫一份 manifest
manifest = {
    "captured_from": BASE,
    "pages": {k: v for k, v in PAGES.items()},
    "assets_downloaded": sorted(f.name for f in ASSETS.iterdir()),
}
(SNAP / "MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
print(f"\n完成。HTML {len(list(HTML.glob('*.html')))} 頁,資產 {len(list(ASSETS.iterdir()))} 個。")
