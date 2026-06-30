# loot-drop-clone

[loot-drop.io](https://www.loot-drop.io/)(失敗創業案例庫「創業墳場」)的本地資料 clone、
快照備份與分析。資料經其前端公開的 Supabase anon API 取得,共 **1749 家**倒閉公司。

> ⚠️ 全部內容為 **AI 生成之公開資料彙整**,僅供研究/學習。`total_funding` 等欄位語意不純,
> 分析前請先讀 [`docs/04-data-quality-caveats.md`](docs/04-data-quality-caveats.md)。

## 這個 repo 有什麼

```
.
├── data/                       爬下來的原始資料(JSON)
│   ├── startups.json           1749 家完整資料(含 the_loot/market_analysis/pivot_idea)
│   └── analytics.json          596 家的 NLP 分析(bottleneck/value-prop/landscape 座標)
├── snapshot/                   2026-06-30 網站今日狀態快照(離線可復現)
│   ├── html/                   12 個頁面 HTML
│   ├── assets/                 26 個打包 JS/CSS(含 supabaseClient、各頁 chunk)
│   ├── api/                    Supabase API 原始回應(證據)
│   ├── grab_site.py            重抓網頁+資產
│   └── grab_api.py             重抓資料 API
├── docs/                       發現與分析文件(見下)
├── reports/
│   └── it-sector-deep-dive.md  IT 產業 408 家失敗深度報告 + 5 招牌案例拆解
├── notebooks/
│   └── explore.py              Marimo 互動 notebook(散點地圖+案例查詢器)
├── fetch_all.py                爬蟲:分頁繞過 1000 筆限制
├── build_db.py                 data/*.json → lootdrop.db (SQLite)
└── analyze.py                  CLI 統計分析(印出 docs/03 的數字)
```

> `lootdrop.db`(SQLite,衍生物)與 `snapshot/api/startups_page*.json`(大檔,與 data/ 重複)
> 不進版控,用下方指令可一鍵重建/重抓。

## 文件導覽(`docs/`)

| 檔案 | 內容 |
|------|------|
| [01-site-overview](docs/01-site-overview.md) | 網站是什麼、功能地圖、宣稱 vs 實際 |
| [02-supabase-discovery](docs/02-supabase-discovery.md) | 怎麼逆向出 Supabase、**資料公開性評估(含初版誤判的覆盤)** |
| [03-data-findings](docs/03-data-findings.md) | 資料分析發現(死因/燒錢/瓶頸/投資人) |
| [04-data-quality-caveats](docs/04-data-quality-caveats.md) | **分析前必讀**:三個會扭曲結論的資料陷阱 |
| [05-rls-security-guide](docs/05-rls-security-guide.md) | 通用教學:Supabase 免費/付費內容的 RLS 隔離 |

## 快速開始

需要 [uv](https://docs.astral.sh/uv/)。

```bash
# 1. 建環境(自動讀 pyproject.toml / uv.lock)
uv sync

# 2. 從 data/*.json 重建 SQLite
uv run python build_db.py

# 3. CLI 統計分析
uv run python analyze.py

# 4. 開互動 notebook(瀏覽器)
uv run marimo edit notebooks/explore.py
```

重新爬取/重抓快照(可選,資料已在 repo):

```bash
uv run python fetch_all.py                 # 重爬資料
uv run python snapshot/grab_site.py        # 重抓網頁+JS
uv run python snapshot/grab_api.py         # 重抓 API 回應
```

## 主要發現速覽

- **1749 家**倒閉、總燒 **$535B**、存活中位數 **3 年**、死亡高峰 **2024(203 家)**。
- 死因第一是 **Competition(901 家,52%)**;但「競爭」死的燒最少($48M)、活最短(4.5y),
  真正的燒錢黑洞是 **Ran Out of Cash($1390M)**。
- **IT 產業 64% 死於競爭**(全庫 52%),軟體紅海最殘酷 —— 詳見產業報告。
- 技術面:其前端用 **Supabase + anon key**(正常設計),全站內容免費,**未發現安全漏洞**。

## 資料來源與分寸

- 僅使用其**公開**端點與**公開** anon key,無破解、無提權、無寫入。
- 爬蟲內建節流;資料僅作本地研究,未再散布。
- 本 repo 為技術研究用途,尊重原站;如原作者有疑慮應移除。
