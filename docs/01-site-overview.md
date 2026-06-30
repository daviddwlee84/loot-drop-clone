# 01 — 網站內容導覽:Loot Drop「創業墳場」

> 來源:<https://www.loot-drop.io/> · 探查日期:2026-06-30

## 它是什麼

一個以「**遊戲掉寶(loot)+ 墳場(graveyard)**」黑色幽默風格包裝的**失敗創業案例資料庫**。
核心主張不是看熱鬧,而是:每一家倒閉公司都留下了「**市場缺口 + 已驗證需求 + 慘痛教訓**」,
網站把這些轉成**可執行的重建藍圖(Rebuild Plans)**。

> ⚠️ 全站內容由其自述為 **AI 生成**的公開資料分析,附免責聲明:屬「模式與觀點」、
> 非經驗證之事實,可能含 AI 幻覺。

## 對外宣稱 vs 實際資料

| 項目 | 首頁宣稱 | 資料庫實際(爬取結果) |
|------|---------|----------------------|
| 收錄公司數 | ~1209 / 1670 | **1749 筆** |
| 燒掉資金 | 標示為動態 | **約 $5354 億美元**(`get_total_burned` RPC) |
| 更新頻率 | 每週二、五新增 | — |

## 功能地圖

| 頁面 | 路徑 | 用途 |
|------|------|------|
| 首頁墳場 | `/` | 搜尋 + 篩選全部案例,動態統計 |
| Learning Framework | `/why-they-fail` | **7 種失敗反模式(antipatterns)** + 互動式「風險掃描器」自測 7 題 |
| Deep Dives | `/deep-dives` | **22 種產品類別**各自的「失敗特徵」 |
| Rebuild Plans ★ | `/rebuilds` | **招牌功能**(免費):1670+ 個可執行重建計畫 |
| Top 10 Lists | `/lists.html` | 29 個「死亡榜單」(SaaS、消費…) |
| Insights / Dashboard | `/insights.html` `/dashboard.html` | 互動式鑑識數據儀表板 |
| Database View | `/database-view` | 完整資料庫檢視 |
| Ideas | `/ideas.html` | 1000+ 創業點子 |

### Rebuild Plan 的結構(每個計畫 5 段)

1. **What to Build** — 要做什麼
2. **Market Analysis** — 市場分析(對應 DB 的 `market_analysis` 長文)
3. **Build Steps** — 建構步驟
4. **Tech Stack** — 技術棧
5. **Revenue Model** — 營收模式(對應 DB 的 `pivot_idea`,結構化 JSON 含 GTM)

## 技術棧(從前端可觀察)

- **前端**:Vite 打包的 SPA(資產檔名帶 hash,如 `main-C7mngnWC.js`)
- **內容渲染**:client-side 動態載入 — 直接用 HTTP 抓 HTML 只會拿到「Loading…」骨架
- **後端**:**Supabase**(PostgreSQL + PostgREST + GoTrue),詳見 `02-supabase-discovery.md`

> 因為是純 client-side 直連資料庫,**所有資料與 API 結構對使用者天生透明**。
> 這不是漏洞,是這類架構的固有性質(見下一份文件對「透明 ≠ 漏洞」的釐清)。
