#!/usr/bin/env python3
"""把爬下來的 JSON 灌進本地 SQLite,JSON/陣列欄位轉成 TEXT 存。"""
import json, sqlite3, pathlib

ROOT = pathlib.Path(__file__).parent
DATA = ROOT / "data"
DB   = ROOT / "lootdrop.db"

def load(name):
    return json.loads((DATA / name).read_text())

def norm(v):
    """list/dict 轉 JSON 字串,其餘原樣。"""
    if isinstance(v, (list, dict)):
        return json.dumps(v, ensure_ascii=False)
    return v

def make_table(cur, table, rows):
    if not rows:
        print(f"  {table}: 空,跳過")
        return
    cols = list({k for r in rows for k in r.keys()})  # 聯集所有欄位
    cur.execute(f"DROP TABLE IF EXISTS {table}")
    cur.execute(f"CREATE TABLE {table} ({', '.join(f'\"{c}\"' for c in cols)})")
    placeholders = ", ".join("?" * len(cols))
    cur.executemany(
        f"INSERT INTO {table} VALUES ({placeholders})",
        [[norm(r.get(c)) for c in cols] for r in rows],
    )
    print(f"  {table}: {len(rows)} 筆 / {len(cols)} 欄")

if __name__ == "__main__":
    if DB.exists():
        DB.unlink()
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    print("== 灌資料進 SQLite ==")
    make_table(cur, "startups", load("startups.json"))
    make_table(cur, "analytics", load("analytics.json"))

    # 建幾個常用索引
    cur.execute("CREATE INDEX idx_cause ON startups(primary_cause_of_death)")
    cur.execute("CREATE INDEX idx_sector ON startups(sector)")
    cur.execute("CREATE INDEX idx_country ON startups(country)")
    cur.execute("CREATE INDEX idx_funding ON startups(total_funding)")
    conn.commit()

    # 驗證
    n = cur.execute("SELECT COUNT(*) FROM startups").fetchone()[0]
    print(f"\n驗證: startups 共 {n} 筆")
    print(f"DB 檔: {DB}  ({DB.stat().st_size/1024/1024:.1f} MB)")
    conn.close()
