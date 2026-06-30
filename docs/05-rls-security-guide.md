# 05 — RLS 安全指南:免費展示 vs 付費內容的正確隔離

> **定位:通用教學,非針對 Loot Drop 的指控。**
> 經實證,Loot Drop 全站內容免費、無 paywall,**未發現安全漏洞**(見 `02`)。
> 本文是「**假如**你要做一個『有付費內容』的 Supabase 產品,該怎麼設 RLS」的一般性參考。

## 核心原則

> **anon key 一定會公開**,所以**絕對不能把『不該被匿名讀到的資料』放進
> anon 角色 RLS policy 允許的範圍**。保護必須在**資料庫層**,不能靠前端隱藏。

(註:Loot Drop 因內容全免費,不存在「不該被匿名讀到的資料」,故無此問題。
以下為「**若有**付費內容」的通用做法。)

---

## 方案 A:欄位切分到不同表(推薦,最簡單清晰)

把免費預覽與付費正文拆成兩張表,RLS 分別設。

```sql
-- 免費預覽表:anon 可讀
create table startups_public (
  id            bigint primary key,
  name          text,
  sector        text,
  country       text,
  total_funding numeric,
  condensed_value_prop text,   -- 只放「鉤子」摘要
  primary_cause_of_death text
);

-- 付費正文表:anon 不可讀
create table startups_premium (
  id              bigint primary key references startups_public(id),
  the_loot        jsonb,
  market_analysis text,
  pivot_idea      jsonb
);

-- 開啟 RLS(預設拒絕一切)
alter table startups_public  enable row level security;
alter table startups_premium enable row level security;

-- 公開表:任何人可讀
create policy "public read"
  on startups_public for select
  to anon, authenticated
  using (true);

-- 付費表:只有「已付費」的登入使用者可讀
create policy "paid users read"
  on startups_premium for select
  to authenticated
  using (
    exists (
      select 1 from subscriptions s
      where s.user_id = auth.uid()
        and s.status = 'active'
    )
  );
-- 注意:沒有給 anon 任何 policy → anon 一律讀不到 premium
```

前端:免費頁查 `startups_public`;付費頁(登入後)查 `startups_premium`。
匿名 `curl` 打 `startups_premium` 只會回空陣列。

---

## 方案 B:同表 + 用 View/RPC 控制欄位曝光

保留單表,但**不開放 anon 直接 `select *`**,改走一個只回安全欄位的 View 或
`security definer` RPC。

```sql
alter table startups enable row level security;
-- 不給 anon 對 startups 的 select policy(直接查表 = 空)

-- 對外只暴露安全欄位的 view
create view startups_preview as
  select id, name, sector, country, total_funding,
         condensed_value_prop, primary_cause_of_death
  from startups;

-- 或用 RPC,登入且付費才回完整內容
create or replace function get_startup_full(p_id bigint)
returns setof startups
language sql security definer
as $$
  select * from startups
  where id = p_id
    and exists (
      select 1 from subscriptions
      where user_id = auth.uid() and status = 'active'
    );
$$;
```

> ⚠️ 用 `security definer` 時要特別小心,函式內務必自己檢查 `auth.uid()` 與付費狀態,
> 否則等於繞過 RLS 開後門。

---

## 方案 C:付費內容根本不放 Supabase,走自己的後端

最保守:Supabase 只存免費資料;付費正文由你自己的 server(帶金流驗證)發。
適合內容是核心資產、不容任何洩漏的產品。代價是要自己維運一層 API。

---

## 通用檢查清單

- [ ] **每張表都 `enable row level security`**(Supabase 建表預設不開!)
- [ ] anon 角色只在「確定要公開」的表/欄位上有 `select` policy
- [ ] 付費/私密內容要嘛分表、要嘛走 RPC,**絕不讓 anon 直接 `select *`**
- [ ] 寫入端點(如 `site_requests`)限制 `insert` 且驗證內容,避免被灌垃圾
- [ ] 用「匿名 curl」自己滲透測試:
      ```bash
      curl "$URL/rest/v1/<每張表>?select=*&limit=1" \
        -H "apikey: $ANON" -H "Authorization: Bearer $ANON"
      ```
      凡是「不該匿名看到卻回了資料」的,就是漏洞。
- [ ] 分頁不是保護 — `Range` header 能撈穿,別以為「預設只回 1000 筆」擋得住爬蟲。

---

## 一句話總結

> **公開 key + 嚴格 RLS = 安全;公開 key + RLS 全開 = 把資料庫掛在公網。**
> 後者只有在「資料本來就要公開」時才沒問題 —— Loot Drop 正屬此例(全免費),
> 故無虞。但**若你的產品有任何付費/私密內容**,務必用上面任一方案把它隔離出
> anon 的可讀範圍。
