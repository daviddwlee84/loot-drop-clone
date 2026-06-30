# 06 — 新創技術選型:Supabase vs 自架 DB + 第三方 Auth

> 起因:看完 Loot Drop 用 Supabase 後的延伸討論 ——
> 「新創網站到底該用 Supabase,還是自架資料庫搭配第三方 Auth(Clerk/Auth0 等)?」

## 先講結論(TL;DR)

| 你的情況 | 建議 |
|---------|------|
| **早期、要快、團隊小** | ✅ **Supabase**(DB + Auth + Storage 一站式,最省事) |
| **Auth 需求複雜**(企業 SSO、精細權限、合規) | 自架/託管 DB + **專業 Auth(Clerk / Auth0 / WorkOS)** |
| **已有後端團隊、想要掌控** | 託管 Postgres(Neon/RDS)+ 自寫 API + 第三方 Auth |
| **純靜態 / 無使用者系統** | 兩者都不需要(像本 repo 的 snapshot,直接 GitHub Pages) |

**對「大多數早期新創」**:**先用 Supabase**。它把你最不該在早期浪費時間的東西(DB、Auth、即時、檔案)打包好,讓你專注做產品。等規模或 Auth 複雜度真的撞到天花板,再抽換——而且 Supabase 底層是標準 Postgres,遷移成本比想像低。

---

## 兩種路線是什麼

### 路線 A:Supabase(BaaS 一站式)
Postgres + 內建 Auth(email/OAuth/magic link)+ 即時訂閱 + Storage + 自動 REST/GraphQL API。
前端用 anon key 直連,**靠 RLS(Row-Level Security)在資料庫層控管權限**。

### 路線 B:自架/託管 DB + 第三方 Auth
自己準備資料庫(Neon、Supabase-as-just-DB、RDS、自架 Postgres),
**Auth 外包給專業服務**(Clerk、Auth0、WorkOS、Firebase Auth),
中間通常自己寫一層後端 API(Node/Go/Python…)。

---

## 逐項比較

| 面向 | Supabase | 自架 DB + 第三方 Auth |
|------|----------|----------------------|
| **上手速度** | ⭐ 最快,幾小時有可用後端 | 慢,要接 DB、寫 API、整合 Auth |
| **Auth 功能深度** | email/OAuth/magic link 夠用;企業 SSO/SCIM 較弱 | ⭐ Clerk/Auth0/WorkOS 在這塊專業且完整 |
| **權限控管** | RLS,強大但**學習曲線陡、容易設錯**(見 Loot Drop 案例註) | 在自己的 API 層寫,直覺但要自己負責周全 |
| **掌控度 / 客製** | 中(被平台抽象綁住一些) | ⭐ 高,想怎麼搭都行 |
| **維運負擔** | ⭐ 低(平台代管) | 高(DB 備份、擴展、Auth 整合都要顧) |
| **成本(早期)** | ⭐ 免費額度大方,起步幾乎 $0 | Auth 服務多半按 MAU 計費,長大後可能變貴 |
| **成本(規模化)** | 用量大時可能比自架貴 | DB 自架可壓成本,但人力成本高 |
| **鎖定風險** | 底層是標準 Postgres,**可遷移**;但 Auth/RLS/Realtime 有平台味 | Auth 換供應商麻煩;DB 是標準的好遷 |
| **適合團隊** | 全端少數人、前端主導 | 有後端工程能力的團隊 |

---

## 關鍵:Auth 才是真正的決策點

DB 其實沒那麼難選(Postgres 託管服務都很成熟),**真正分水嶺在 Auth 需求**:

- **需求簡單**(個人帳號、社群登入、忘記密碼)→ Supabase 內建 Auth 完全夠,沒理由多花錢接第三方。
- **需求複雜**(企業客戶要 SAML/OIDC SSO、SCIM 自動佈建、多租戶精細權限、特定合規如 SOC2/HIPAA 的身分流程)→ 這正是 **Clerk / Auth0 / WorkOS** 存在的理由,Supabase Auth 會綁手綁腳。

> 經驗法則:**做 B2C 早期 → Supabase 全包;做 B2B 且客戶會要求 SSO → DB 歸 DB、Auth 用 WorkOS/Auth0。**

---

## 把 Auth 和 DB 解耦,可不可以?可以,而且常見

一個務實的中間路線:**Supabase 當資料庫,但 Auth 用 Clerk/Auth0**。
Supabase 支援第三方 JWT —— 你用 Clerk 登入拿到 JWT,Supabase 的 RLS 直接驗證該 JWT 的 claims。
這樣同時拿到「Supabase 的好用 DB/RLS」+「Clerk 的強 Auth」。
代價是兩個服務都要付費、整合也多一層。

---

## 對應 Loot Drop 的觀察(實例註)

Loot Drop 正是「**Supabase 當公開資料庫、且不需要 Auth**」的最簡用法:

- 它**沒有使用者系統**(全站免費、無登入)→ 連 Auth 都不用,Supabase 只當「自帶 REST API 的 Postgres」。
- 對「唯讀、公開內容」的產品,這是**極省事且正確**的選擇。
- ⚠️ 但要記得:**Supabase 的 anon key 公開 + RLS 全開,只有在『資料本來就要公開』時才安全。**
  一旦你有付費/私密內容,RLS 就必須做對(見 `05-rls-security-guide.md`)——
  這是 Supabase 路線最容易出事的點。

---

## 一句話總結

> **早期新創、Auth 不複雜 → Supabase 全包,別想太多。**
> **Auth 會變複雜(尤其 B2B SSO)→ DB 用託管 Postgres、Auth 交給 Clerk/Auth0/WorkOS。**
> DB 選型很安全(都能遷),**真正要想清楚的是 Auth 的未來需求**。
