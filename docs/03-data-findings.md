# 03 — 資料分析發現

> 資料:`lootdrop.db`(startups 1749 筆 / analytics 596 筆)· 由 `analyze.py` 產生
> ⚠️ 先讀 `04-data-quality-caveats.md` 了解三個資料陷阱再看數字。

## 總覽

| 指標 | 數值 |
|------|------|
| 收錄公司 | **1749 家** |
| 總燒掉資金 | **約 $5354 億美元**($535,377,014,047) |
| 募資中位數 | **$500 萬**(平均 $3.06 億 — 嚴重右偏) |
| 存活中位數 | **3 年**(平均 5.2 年) |
| 死亡高峰 | **2024 年(203 家)** |
| 資料完整度 | the_loot/pivot_idea/views/funding 皆 100% 非空 |

---

## 1. 死因排行(`primary_cause_of_death`)

```
901  ██████████████████████████████████  Competition          ← 過半!
269  ██████████                          Unit Economics
205  ████████                            Ran Out of Cash
203  ████████                            No Market Need
 86  ███                                 Legal/Regulatory
 70  ███                                 Product/Tech Failure
 13                                      Team/Founder Conflict
```

**超過一半被歸因於「競爭」。** 但這個粗標籤會誤導 —— 見第 5 節的瓶頸細分。

## 2. 「競爭」的真相:燒得少、死得快

各死因的平均燒錢與平均壽命交叉後,故事完全變了:

| 死因 | 數量 | 平均燒($M) | 平均壽命 |
|------|------|-----------|---------|
| Ran Out of Cash | 205 | **1390.1** | 6.8y |
| Legal/Regulatory | 86 | 789.7 | 8.1y |
| Unit Economics | 269 | 393.2 | 6.9y |
| Product/Tech Failure | 70 | 224.9 | 6.7y |
| Team/Founder Conflict | 13 | 193.2 | 5.5y |
| No Market Need | 203 | 73.4 | 4.4y |
| **Competition** | **901** | **48.3** | **4.5y** |

> **解讀**:
> - 「競爭」死的公司平均只燒 $48M、活 4.5 年 → 多是**小本、做了沒差異化的紅海題目**,被同質對手/大廠輾過。
> - 真正的**燒錢黑洞是「沒錢」($1390M)** —— 募了巨資硬撐到資金鏈斷裂(WeWork、Northvolt、Byju's 那一掛)。
> - 一般人以為新創死於缺錢,但**「缺錢」其實是撐最久、燒最兇的少數**;多數是默默被競爭淘汰。

## 3. 最燒錢 Top 12(Biggest Burns)

| 公司 | 燒掉 | 死因 | 註 |
|------|------|------|-----|
| Silicon Valley Bank | $209B | Ran Out of Cash | ⚠️ 是總資產非募資 |
| Wirecard | $28B | Legal/Regulatory | 金融詐欺 |
| WeWork | $22B | Unit Economics | 共享辦公,單位經濟崩壞 |
| Northvolt | $15B | Ran Out of Cash | 瑞典電池廠 |
| Ezubao | $7.6B | Legal/Regulatory | P2P 龐氏 |
| Byju's | $6B | Ran Out of Cash | 印度教育獨角獸 |
| LeEco | $6B | Ran Out of Cash | 樂視 |
| WM Motor | $5.8B | Unit Economics | 威馬汽車 |

## 4. 集中度:產業 / 國家

```
產業          國家
447 通訊服務   728 美國 ████████████████████████████
417 消費       102 中國 ████
408 IT          32 英國 █
157 金融        29 印度 █
146 工業        11 加拿大
104 醫療         9 印尼 / 澳洲
```

美國壓倒性過半;中國第二(且 view 數最高的多是中國共享單車/教培題材)。

---

## 5. 智慧分析層(analytics 表的 NLP 分類)

> 僅覆蓋 596 / 1749 ≈ 34% 公司。這是它 dashboard 用、但介面沒明說的細分。

### 真正卡死的瓶頸(`bottleneck_tag`)— 比 cause_of_death 更精準

```
318  ██████████████████████████████████  Outcompeted
101  ███████████                         Unit Economics
 95  ██████████                          product-market fit
 26  ███                                 Regulation
 26  ███                                 Burn Rate
 23  ██                                  Product problems
  6                                      Internal conflicts
```

### 難度類型(`difficulty_category`)

```
221 Operational ████████████████████████████████  ← 死於「做不出來/做不順」
208 Financial   ██████████████████████████████    ← 死於「算不過來/燒太兇」
102 Technical
 36 Regulatory
 24 Behavioral
```

> 兩大死因類別其實是 **營運執行** 與 **財務模型**,技術反而排第三。
> 「點子能不能做出來」遠不如「能不能營運 + 算得過來」致命。

### 價值主張類型(`value_prop_category`)

```
108 SaaS                          ████████████████████████████████
 91 Aggregation / Marketplace     █████████████████████████████
 52 P2P / Sharing                 ████████████████
 52 Content / Media               ████████████████
 41 Data / Intelligence Tools
 41 Automation / Optimization
 37 Financial Services
```

### 最擁擠的題目(`normalized_problem`)— 最多人做 = 最多人死

```
31 協作/專案管理工具
30 線上借貸與金融市集
28 數位內容與社群互動
23 內容創作多媒體平台
21 社群媒體管理聚合 / 醫療診斷科技 / AI 物流
20 即時通訊 / 隨需外送
```

> 這幾個是「最多墳墓」的絞肉機題材 — 若你要創業,進這些賽道前先看看這裡死了多少同行。

---

## 6. 投資人「踩雷王」Top 15(投到最多倒閉公司的 VC)

> 投得多自然踩得多,不代表眼光差;但可看出最活躍的早期投資人。

```
336  ████████████████████████████  Y Combinator
129  ███████████                   Andreessen Horowitz (a16z)
128  ███████████                   Sequoia Capital
 89  ███████                       SV Angel
 47  ████                          500 Startups
 26  ██                            First Round Capital
 21  ██                            Accel Partners
 18  ██                            Greylock Partners
 17  █                             CrunchFund
 16  █                             Google Ventures
```

---

## 7. 最受關注(`views`)Top 10

| # | 公司 | views | 產業 |
|---|------|-------|------|
| 1 | Plenty Unlimited | 13,413 | Materials(室內農業) |
| 2 | Xiaoming Bike | 7,276 | Industrials(共享單車) |
| 3 | 23andMe | 4,372 | Health Care(基因檢測) |
| 4 | Yuanfudao | 2,685 | 教培 |
| 5 | Magic Ears | 2,516 | 線上英語 |

共享單車、中國教培/電商題材關注度特別高(對應其資料來源與讀者興趣)。

---

## 復現方式

```bash
cd ~/Documents/Program/loot-drop-clone
uv run python fetch_all.py    # 重新爬(可選,data/ 已含結果)
uv run python build_db.py     # data/*.json -> lootdrop.db
uv run python analyze.py      # 印出本文所有統計
```
