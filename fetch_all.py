#!/usr/bin/env python3
"""分批爬取 loot-drop.io 背後 Supabase 的完整資料,繞過 1000 筆分頁限制。"""
import json, time, urllib.request, urllib.error, pathlib

SUPA = "https://lentxykytbylpxytluic.supabase.co"
KEY  = "sb_publishable_W5UgIXv8SGHeo43duatMCw_0h8GbgCY"
OUT  = pathlib.Path(__file__).parent / "data"
PAGE = 1000  # PostgREST 預設上限

def req(path, headers=None):
    h = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
    if headers:
        h.update(headers)
    r = urllib.request.Request(f"{SUPA}/rest/v1/{path}", headers=h)
    with urllib.request.urlopen(r, timeout=60) as resp:
        return json.loads(resp.read().decode()), dict(resp.headers)

def fetch_all_table(table, select="*", order="id"):
    """用 Range header 分頁,把整張表撈完。"""
    rows, start = [], 0
    while True:
        path = f"{table}?select={select}&order={order}.asc"
        data, hdr = req(path, {"Range-Unit": "items",
                               "Range": f"{start}-{start+PAGE-1}"})
        rows.extend(data)
        cr = hdr.get("Content-Range", "")
        print(f"  [{table}] {start}-{start+len(data)-1}  (Content-Range: {cr})")
        if len(data) < PAGE:
            break
        start += PAGE
        time.sleep(0.3)  # 對人家伺服器客氣一點
    return rows

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)

    print("== 1/2 爬 startups 主表(含全部付費欄位)==")
    startups = fetch_all_table("startups", select="*")
    (OUT / "startups.json").write_text(json.dumps(startups, ensure_ascii=False, indent=2))
    print(f"  -> 共 {len(startups)} 筆,已存 startups.json\n")

    print("== 2/2 爬 dashboard_analytics ==")
    try:
        analytics = fetch_all_table("dashboard_analytics",
                                    select="*", order="startup_id")
        (OUT / "analytics.json").write_text(json.dumps(analytics, ensure_ascii=False, indent=2))
        print(f"  -> 共 {len(analytics)} 筆,已存 analytics.json")
    except urllib.error.HTTPError as e:
        print(f"  analytics 撈取失敗: {e} (改用 default order 重試)")
        analytics = fetch_all_table("dashboard_analytics", select="*", order="startup_id")
        (OUT / "analytics.json").write_text(json.dumps(analytics, ensure_ascii=False, indent=2))
        print(f"  -> 共 {len(analytics)} 筆")

    print("\n完成。")
