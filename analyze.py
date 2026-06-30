#!/usr/bin/env python3
"""
復刻 + 延伸 loot-drop.io 的分析維度。
分兩部分:
  A. 基礎統計(死因/產業/國家/燒錢/存活)—— 對應它首頁 & dashboard
  B. 智慧分析層(bottleneck/value-prop/problem 分類)—— 對應它 analytics 表
"""
import sqlite3, json, collections

conn = sqlite3.connect("lootdrop.db")
c = conn.cursor()

def bar(v, mx, width=34):
    if not mx:
        return ""
    n = int(round(v / mx * width))
    return "█" * max(0, min(n, width))  # clamp，避免畫爆

def rank(sql, title, money=False):
    rows = c.execute(sql).fetchall()
    if not rows: return
    mx = max(v for _, v in rows)  # 取真正最大值，不假設第一筆最大
    print(f"\n=== {title} ===")
    for name, v in rows:
        val = f"${v/1e9:.1f}B" if money else f"{v}"
        print(f"  {val:>9}  {bar(v, mx)} {name}")

print("="*60)
print("  LOOT DROP 本地資料庫分析報告")
print("="*60)

tot = c.execute("SELECT COUNT(*) FROM startups").fetchone()[0]
burn = c.execute("SELECT SUM(total_funding) FROM startups").fetchone()[0]
print(f"\n總公司數: {tot}")
print(f"總燒掉資金: ${burn/1e9:,.1f}B (${burn:,})")

# ---------- A. 基礎統計 ----------
print("\n" + "─"*60 + "\n  A. 基礎統計（對應首頁/dashboard）\n" + "─"*60)

rank("""SELECT primary_cause_of_death, COUNT(*) c FROM startups
        WHERE primary_cause_of_death IS NOT NULL
        GROUP BY 1 ORDER BY c DESC""", "死因排行 Cause of Death")

rank("""SELECT sector, COUNT(*) c FROM startups
        WHERE sector IS NOT NULL GROUP BY 1 ORDER BY c DESC LIMIT 12""",
     "產業排行 Sector")

rank("""SELECT country, COUNT(*) c FROM startups
        WHERE country IS NOT NULL GROUP BY 1 ORDER BY c DESC LIMIT 12""",
     "國家排行 Country")

rank("""SELECT name, total_funding f FROM startups
        WHERE total_funding IS NOT NULL ORDER BY f DESC LIMIT 12""",
     "最燒錢 Biggest Burns", money=True)

# 存活年數
spans = [r[0] for r in c.execute(
    """SELECT end_year-start_year FROM startups
       WHERE end_year IS NOT NULL AND start_year IS NOT NULL
       AND end_year>=start_year""")]
spans.sort()
print(f"\n=== 存活年數 Lifespan ===")
print(f"  平均 {sum(spans)/len(spans):.1f} 年 / 中位數 {spans[len(spans)//2]} 年 "
      f"/ 最短 {spans[0]} / 最長 {spans[-1]}")

# 每年死亡數
rank("""SELECT CAST(end_year AS TEXT), COUNT(*) c FROM startups
        WHERE end_year>=2015 GROUP BY end_year ORDER BY end_year DESC LIMIT 12""",
     "近年各年死亡數 Deaths/Year")

# ---------- B. 智慧分析層 ----------
print("\n" + "─"*60 + "\n  B. 智慧分析層（它 analytics 表的 NLP 分類）\n" + "─"*60)

rank("""SELECT bottleneck_tag, COUNT(*) c FROM analytics
        WHERE bottleneck_tag IS NOT NULL GROUP BY 1 ORDER BY c DESC LIMIT 12""",
     "真正卡死的瓶頸 Bottleneck Tag")

rank("""SELECT value_prop_category, COUNT(*) c FROM analytics
        WHERE value_prop_category IS NOT NULL GROUP BY 1 ORDER BY c DESC LIMIT 12""",
     "價值主張類型 Value Prop Category")

rank("""SELECT difficulty_category, COUNT(*) c FROM analytics
        WHERE difficulty_category IS NOT NULL GROUP BY 1 ORDER BY c DESC LIMIT 10""",
     "難度類型 Difficulty Category")

rank("""SELECT normalized_problem, COUNT(*) c FROM analytics
        WHERE normalized_problem IS NOT NULL GROUP BY 1 ORDER BY c DESC LIMIT 12""",
     "最擁擠的題目 Normalized Problem（最多人做＝最多人死）")

# ---------- C. 交叉分析（它網站沒有，加值） ----------
print("\n" + "─"*60 + "\n  C. 加值交叉分析\n" + "─"*60)

print("\n=== 各死因 平均燒錢 / 平均壽命 ===")
rows = c.execute("""
    SELECT primary_cause_of_death,
           COUNT(*) n,
           AVG(total_funding)/1e6 avg_m,
           AVG(end_year-start_year) avg_life
    FROM startups
    WHERE primary_cause_of_death IS NOT NULL AND total_funding IS NOT NULL
    GROUP BY 1 ORDER BY avg_m DESC""").fetchall()
print(f"  {'死因':<22}{'數量':>5}{'平均燒($M)':>12}{'平均壽命':>10}")
for cause, n, avgm, life in rows:
    print(f"  {cause:<22}{n:>5}{avgm:>12.1f}{(life or 0):>9.1f}y")

print("\n=== 投資人「踩雷王」Top 15（投到最多倒閉公司的 VC）===")
inv = collections.Counter()
for (raw,) in c.execute("SELECT investors FROM analytics WHERE investors IS NOT NULL"):
    try:
        for name in json.loads(raw):
            if name and name.strip():
                inv[name.strip()] += 1
    except Exception:
        pass
mx = inv.most_common(1)[0][1]
for name, n in inv.most_common(15):
    print(f"  {n:>4}  {bar(n, mx, 28)} {name}")

conn.close()
print("\n" + "="*60)
