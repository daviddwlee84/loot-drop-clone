# 02 — Supabase 逆向發現與安全分析

> 探查日期:2026-06-30 · 方法:讀取前端打包 JS + 直接呼叫其公開 API

## TL;DR

1. **能看出它用 Supabase** → 跟 key 外洩無關,是 client-side 架構的固有透明性。
2. **anon key 出現在前端** → **正常設計**,Supabase 本就要你公開它。
3. **anon 可讀到 `startups` 全部欄位(含 the_loot/market_analysis/pivot_idea)** →
   **不是漏洞**。經實證,Loot Drop 全站內容免費、無 paywall/登入/金流(見第三節),
   所以這些欄位本來就該對匿名訪客公開,行為符合設計。

> ⚠️ **更正紀錄**:本文初版曾把上述行為定性為「付費內容裸奔的安全漏洞」。
> 那是基於「Rebuild Plans 是付費產品」的**錯誤假設**。後續實證(前端無任何
> paywall/auth/金流邏輯)推翻了該假設,定性已更正為「公開資料、行為正常」。
> 保留此更正紀錄,作為「先驗證再下定性」的提醒。

---

## 一、怎麼逆向出來的

前端首頁 HTML 直接引用了這些打包資產:

```
/assets/supabaseClient-CuYTLnyz.js   ← 關鍵
/assets/top10data-bqRFPz5T.js
/assets/main-C7mngnWC.js
```

`supabaseClient-*.js` 是 `@supabase/supabase-js` v2.90.1 的打包輸出,檔尾明文寫死:

```js
const Sn = "https://lentxykytbylpxytluic.supabase.co",
      kn = "sb_publishable_W5UgIXv8SGHeo43duatMCw_0h8GbgCY",
      ue = mn(Sn, kn);   // createClient(url, anonKey)
```

| 項目 | 值 |
|------|-----|
| Supabase URL | `https://lentxykytbylpxytluic.supabase.co` |
| Project Ref | `lentxykytbylpxytluic` |
| anon / publishable key | `sb_publishable_W5UgIXv8SGHeo43duatMCw_0h8GbgCY` |

同一支檔案還洩漏了完整資料存取邏輯:表名、RPC 名、欄位、甚至前端的快取(`sessionStorage`, TTL 5 分鐘)與簡易 rate-limit(2 秒 5 次)。

### 資料存取面(從 JS 還原)

| 類型 | 名稱 | 回傳 |
|------|------|------|
| Table | `startups` | 主表,**含全部付費欄位** |
| Table | `dashboard_analytics` | NLP 分析(bottleneck/value-prop/landscape 座標) |
| Table | `site_requests` | 使用者提交的「補檔/功能請求」(只 insert) |
| RPC | `get_total_burned` | 總燒掉資金 |
| RPC | `get_startup_by_id(p_id)` | 單一公司完整資料 |

---

## 二、為什麼「anon key 在前端」是正常的

這是最常見的誤解,必須講清楚:

- Supabase 的安全模型 = **公開的 anon key + 資料庫層的 Row-Level Security (RLS)**。
- anon key **不是密鑰**,它只是「我是哪個專案、我是匿名訪客」的識別證,等同於
  前端放 Google Maps API key。官方文件明確說它可公開。
- 真正把關的是 **RLS policy**:每張表要定義「anon 角色能讀/寫哪些列」。

> 所以「key 在前端」本身 0 問題。問題永遠在 **RLS 有沒有做對**。

### 「能逆向 = 漏洞」嗎?不是

任何 **client-side 直連資料庫** 的架構(Supabase / Firebase / 任何 BaaS),
打包後的 JS 與瀏覽器 Network 分頁必然暴露:後端網址、API 路徑(`rest/v1`、`auth/v1`)、
表名、查詢結構。這是架構選型的**固有性質**,不分免費版或付費版、自架或雲端。
要「不透明」就得在前端與 DB 之間加一層自己的後端 API。

---

## 三、資料公開性評估:符合設計(初版誤判已更正)

### 觀察到的行為

`startups` 一張表用 anon key `select=*` 即回傳所有欄位,包含內容最豐富的:

```bash
SUPA="https://lentxykytbylpxytluic.supabase.co"
KEY="sb_publishable_W5UgIXv8SGHeo43duatMCw_0h8GbgCY"

curl -s "$SUPA/rest/v1/startups?select=name,the_loot,market_analysis,pivot_idea&limit=5" \
  -H "apikey: $KEY" -H "Authorization: Bearer $KEY"
```

回傳:
- `the_loot` — 結構化教訓陣列(平均 5.4 條/家)
- `market_analysis` — 數百字市場分析長文
- `pivot_idea` — 結構化 JSON,含 GTM 進入策略
- `founders` / `investors` — 完整名單

### 為什麼這「不是」漏洞

要構成「付費內容外洩」漏洞,前提是這些內容**本該收費或需登入才能看**。
經實證,**前提不成立**:

| 驗證項 | 結果 |
|--------|------|
| 前端是否有 paywall / 訂閱牆 | ❌ 無(`rebuilds` 等頁面 JS 內零權限邏輯) |
| 是否有登入 / auth 流程 | ❌ 無(`signInWith*` 僅 Supabase SDK 內建庫碼,本站未調用) |
| 是否有金流(Stripe/checkout) | ❌ 無(`faq.html` 出現 "Stripe/pricing" 是**內容文案**在分析創業定價失敗,非自身金流) |
| `/rebuilds` 實際瀏覽 | 直接可讀,免費免登入 |

→ 既然全站內容**本來就免費公開**,那麼 anon 讀得到 `startups` 全欄位就是
**完全符合預期的設計**,行為正常,不構成資料外洩。

> **沒有獨立的 `rebuilds`/`plans` 表**(GET 皆 404),Rebuild Plans 就是前端直接讀
> `startups` 表組裝的。對「免費公開」的產品而言,這是合理且常見的單表設計。

### 初版誤判的覆盤(留作教訓)

本文初版把上述行為寫成「付費內容裸奔的安全漏洞」。錯誤鏈是:

1. 看到 "Rebuild Plans v2.0 新功能"、商業模式像 SaaS → **假設**它是付費產品;
2. 在「付費」假設下,anon 能讀全欄位 → 推導成「漏洞」;
3. **跳過了「先確認它到底收不收費」這一步**。

使用者實際點 `/rebuilds` 發現免費可讀,促使回頭做前端取證,才推翻假設。
**教訓:資安定性必須建立在實證上,不能從商業模式腦補。**

---

## 四、定性結論

| 觀察 | 性質 |
|------|------|
| 看得出是 Supabase | ⚪ 中性(架構固有透明) |
| anon key 在前端 | ✅ 正常設計 |
| 公開資料 anon 可讀(含 the_loot/pivot_idea) | ✅ 合理 — 全站本就免費公開 |
| 1000 筆分頁可被 Range header 繞過 | ⚪ 非保護機制,只是 PostgREST 預設分頁 |
| **整體** | **未發現安全漏洞;行為符合「免費公開資料庫」的設計** |

### 唯一仍可討論的點:有沒有「想保護卻沒保護」的東西?

由於全站免費,目前**找不到任何「應受保護卻外洩」的資料**,故無漏洞。
要說有改進空間,僅在於通用最佳實務(與本站是否「出事」無關):

- `site_requests` 這類**寫入**端點應確認有 RLS 限制(僅允許 `insert`、擋讀取與灌垃圾)。
- 若**未來**要對部分內容收費,屆時才需要做免費/付費隔離(做法見 `05-rls-security-guide.md`,
  該文現定位為「通用教學」,而非指控本站有漏洞)。

### 「是不懂技術的 vibe coder 嗎?」

**無從也無需如此判斷。** 既然沒有安全問題,單表存放公開資料 + anon 直讀是
**簡潔合理**的架構選擇,反而看不出任何業餘痕跡。先前以此推論「RLS 全開的疏失」
同樣是建立在錯誤的「付費」前提上,一併撤回。

---

## 五、本次取證的「客氣」程度說明

- 僅使用其**公開**的 anon key 與**公開**端點,無破解、無提權、無寫入。
- 主表用 `Range` 分頁 2 次請求完成(未逐筆打 1749 次 RPC),對其伺服器負載最小。
- 爬蟲內建 `time.sleep(0.3)` 節流。
- 資料僅作本地分析與安全研究用途,未再散布。
