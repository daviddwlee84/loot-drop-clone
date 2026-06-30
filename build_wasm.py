#!/usr/bin/env python3
"""產生 WASM 版 notebook(本地與 CI 共用)。

步驟:
  1. 從 lootdrop.db 產生精簡版 notebooks/public/*.json(縮小 WASM 載入體積)
  2. marimo export html-wasm 到 site/notebook-wasm/

用法:
  uv run python build_wasm.py
前置:lootdrop.db 需存在(沒有的話先跑 build_db.py)。
"""
import json
import pathlib
import sqlite3
import subprocess
import sys

ROOT = pathlib.Path(__file__).parent
DB = ROOT / "lootdrop.db"
PUBLIC = ROOT / "notebooks" / "public"
OUT = ROOT / "site" / "notebook-wasm"


def make_public_data():
    if not DB.exists():
        sys.exit(f"找不到 {DB},請先執行 build_db.py")
    PUBLIC.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB)
    cur = con.cursor()

    # 精簡 startups:保留分析欄位 + the_loot/pivot_idea(案例查詢器需要),
    # 去掉超長的 market_analysis 全文以縮小體積。
    cols = ["id", "name", "sector", "country", "start_year", "end_year",
            "total_funding", "primary_cause_of_death", "difficulty",
            "scalability", "market_potential", "views", "condensed_value_prop",
            "condensed_cause_of_death", "the_loot", "pivot_idea"]
    rows = cur.execute(f"SELECT {','.join(cols)} FROM startups").fetchall()
    startups = [dict(zip(cols, r)) for r in rows]
    (PUBLIC / "startups.json").write_text(
        json.dumps(startups, ensure_ascii=False), encoding="utf-8")

    acols = [d[1] for d in cur.execute("PRAGMA table_info(analytics)")]
    arows = cur.execute(f"SELECT {','.join(acols)} FROM analytics").fetchall()
    analytics = [dict(zip(acols, r)) for r in arows]
    (PUBLIC / "analytics.json").write_text(
        json.dumps(analytics, ensure_ascii=False), encoding="utf-8")
    con.close()

    s = (PUBLIC / "startups.json").stat().st_size / 1024
    a = (PUBLIC / "analytics.json").stat().st_size / 1024
    print(f"  public/startups.json  {s:,.0f} KB ({len(startups)} 筆)")
    print(f"  public/analytics.json {a:,.0f} KB ({len(analytics)} 筆)")


def export_wasm():
    import shutil
    if OUT.exists():
        shutil.rmtree(OUT)
    cmd = ["marimo", "export", "html-wasm", "notebooks/explore.py",
           "-o", str(OUT), "--mode", "run", "--no-show-code"]
    print("  $ " + " ".join(cmd))
    subprocess.run(cmd, check=True, cwd=ROOT)


if __name__ == "__main__":
    print("== 1/2 產生精簡 public 資料 ==")
    make_public_data()
    print("== 2/2 export WASM ==")
    export_wasm()
    total = sum(f.stat().st_size for f in OUT.rglob("*")) / 1024 / 1024
    print(f"\n完成。site/notebook-wasm/ 約 {total:.0f} MB")
