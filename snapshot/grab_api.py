#!/usr/bin/env python3
"""快照 Supabase 資料 API 今日原始回應(供離線復現)。"""
import json, time, urllib.request, pathlib

SUPA = "https://lentxykytbylpxytluic.supabase.co"
KEY = "sb_publishable_W5UgIXv8SGHeo43duatMCw_0h8GbgCY"
API = pathlib.Path(__file__).parent / "api"
API.mkdir(parents=True, exist_ok=True)

H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

def call(path, out, method="GET", body=None, extra=None):
    headers = dict(H)
    if extra:
        headers.update(extra)
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(f"{SUPA}/rest/v1/{path}", data=data,
                                 headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=60) as r:
        content = r.read()
        cr = r.headers.get("Content-Range", "")
    (API / out).write_bytes(content)
    print(f"  [ok] {out}  ({len(content):,}B)  Content-Range: {cr}")

print("== 資料 API 原始回應快照 ==")
# 全表(已在 ../data 有完整版,這裡存「樣本+標頭」證據)
call("startups?select=*&order=id.asc", "startups_page1.json",
     extra={"Range": "0-999"})
call("startups?select=*&order=id.asc", "startups_page2.json",
     extra={"Range": "1000-1748"})
call("dashboard_analytics?select=*", "dashboard_analytics.json")
# RPC
call("rpc/get_total_burned", "rpc_get_total_burned.json", method="POST", body={})
call("rpc/get_startup_by_id", "rpc_get_startup_by_id_sample.json",
     method="POST", body={"p_id": 1})
time.sleep(0.2)
print("\n完成。")
