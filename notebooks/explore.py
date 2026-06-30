# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "pandas",
#     "plotly==5.24.1",
# ]
# ///

import marimo

__generated_with = "0.23.11"
app = marimo.App(width="medium", app_title="Loot Drop 創業墳場分析")


@app.cell
def _():
    import marimo as mo
    import json
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go

    return json, mo, pd, px


@app.cell
def _(mo):
    mo.md("""
    # 🪦 Loot Drop 創業墳場 — 互動分析

    資料來源:[loot-drop.io](https://www.loot-drop.io/) 背後 Supabase,本地 clone 共 **1749 家**倒閉公司。

    > ⚠️ 資料為 AI 生成之公開資料彙整,`total_funding` 語意不純(混募資額與公司總規模),
    > 時間趨勢含少數「未來預判」標記。詳見 `docs/04-data-quality-caveats.md`。
    >
    > 💡 本 notebook 同時支援本地執行與瀏覽器內 WASM 執行;資料從 `public/*.json` 載入。
    """)
    return


@app.cell
def _(mo, pd):
    # 從 public/ 載入資料(mo.notebook_location 在本地與 WASM 皆可用)
    _base = mo.notebook_location() / "public"
    startups = pd.read_json(str(_base / "startups.json"))
    analytics = pd.read_json(str(_base / "analytics.json"))

    # 衍生欄位
    startups["lifespan"] = startups["end_year"] - startups["start_year"]
    startups["funding_m"] = startups["total_funding"] / 1e6
    return analytics, startups


@app.cell
def _(mo, startups):
    _n = len(startups)
    _burn = startups["total_funding"].sum()
    _med_life = int(startups["lifespan"].median())
    _med_fund = startups["total_funding"].median()
    mo.hstack(
        [
            mo.stat(f"{_n:,}", label="收錄公司", bordered=True),
            mo.stat(f"${_burn/1e9:,.0f}B", label="總燒掉資金", bordered=True),
            mo.stat(f"{_med_life} 年", label="存活中位數", bordered=True),
            mo.stat(f"${_med_fund/1e6:,.1f}M", label="募資中位數", bordered=True),
        ],
        justify="space-around",
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ---
    ## 1. 死因 × 燒錢散點

    每個點是一家公司。**X = 募資額(對數)、Y = 存活年數、顏色 = 死因**。
    用下方控制項篩選。
    """)
    return


@app.cell
def _(mo, startups):
    # 互動篩選控制項
    sectors = sorted(startups["sector"].dropna().unique().tolist())
    causes = sorted(startups["primary_cause_of_death"].dropna().unique().tolist())

    sector_filter = mo.ui.multiselect(
        options=sectors, value=sectors, label="產業 Sector"
    )
    cause_filter = mo.ui.multiselect(
        options=causes, value=causes, label="死因 Cause"
    )
    min_funding = mo.ui.slider(
        start=0, stop=100, value=0, step=1,
        label="最低募資 ($M)", show_value=True,
    )
    exclude_outliers = mo.ui.switch(value=True, label="排除 ≥$5B 巨頭(資料品質)")
    mo.vstack([
        mo.hstack([sector_filter, cause_filter], justify="start"),
        mo.hstack([min_funding, exclude_outliers], justify="start"),
    ])
    return cause_filter, exclude_outliers, min_funding, sector_filter


@app.cell
def _(cause_filter, exclude_outliers, min_funding, sector_filter, startups):
    df = startups.copy()
    df = df[df["sector"].isin(sector_filter.value)]
    df = df[df["primary_cause_of_death"].isin(cause_filter.value)]
    df = df[df["funding_m"] >= min_funding.value]
    if exclude_outliers.value:
        df = df[df["total_funding"] < 5e9]
    # 只留有效壽命
    df = df[(df["lifespan"] >= 0) & (df["lifespan"] <= 40)]
    return (df,)


@app.cell
def _(df, mo, px):
    _fig = px.scatter(
        df[df["funding_m"] > 0],
        x="funding_m",
        y="lifespan",
        color="primary_cause_of_death",
        size="views",
        hover_name="name",
        hover_data={"sector": True, "country": True, "funding_m": ":.1f"},
        log_x=True,
        labels={
            "funding_m": "募資額 ($M, log)",
            "lifespan": "存活年數",
            "primary_cause_of_death": "死因",
        },
        height=520,
        title=f"篩選後 {len(df)} 家",
    )
    _fig.update_layout(legend=dict(orientation="h", y=-0.2))
    mo.ui.plotly(_fig)
    return


@app.cell
def _(mo):
    mo.md("""
    ---
    ## 2. 🗺️ 創業生態地圖(復刻 landscape_x/y 降維散點)

    這是 Loot Drop dashboard 的視覺核心 —— `analytics` 表用 NLP 把每家公司的題材
    壓成 2D 座標(UMAP/t-SNE 類)。**距離越近 = 題材越相似**,軸本身無物理意義。
    顏色 = 它分類的 `bottleneck_tag`(真正卡死的瓶頸)。

    > 僅覆蓋 596 家(全庫的 34%)。
    """)
    return


@app.cell
def _(analytics, mo, px):
    _land = analytics.dropna(subset=["landscape_x", "landscape_y"]).copy()
    _land["funding_m"] = _land["total_funding"].astype(float) / 1e6
    _fig = px.scatter(
        _land,
        x="landscape_x",
        y="landscape_y",
        color="bottleneck_tag",
        size=_land["funding_m"].clip(1, 2000),
        hover_name="startup_name",
        hover_data={
            "sector": True,
            "value_prop": True,
            "normalized_problem": True,
            "landscape_x": False,
            "landscape_y": False,
        },
        height=620,
        title="失敗新創題材地圖(landscape embedding)",
    )
    _fig.update_layout(
        legend=dict(orientation="h", y=-0.15),
        xaxis_title="(降維維度 1 — 無單位)",
        yaxis_title="(降維維度 2 — 無單位)",
    )
    mo.ui.plotly(_fig)
    return


@app.cell
def _(mo):
    mo.md("""
    ---
    ## 3. 死因深掘:平均燒錢 vs 平均壽命

    反直覺重點:**「競爭」死的公司燒最少、活最短**(紅海被輾);
    **「沒錢」死的反而燒最多、撐最久**(募巨資硬撐到斷鏈)。
    """)
    return


@app.cell
def _(px, startups):
    _g = (
        startups[startups["total_funding"] > 0]
        .groupby("primary_cause_of_death")
        .agg(
            n=("name", "count"),
            avg_funding_m=("funding_m", "mean"),
            avg_lifespan=("lifespan", "mean"),
        )
        .reset_index()
    )
    _fig = px.scatter(
        _g,
        x="avg_lifespan",
        y="avg_funding_m",
        size="n",
        color="primary_cause_of_death",
        text="primary_cause_of_death",
        labels={"avg_lifespan": "平均存活(年)", "avg_funding_m": "平均募資($M)"},
        height=480,
        title="各死因的「燒錢 × 壽命」象限(泡泡大小=家數)",
    )
    _fig.update_traces(textposition="top center")
    _fig.update_layout(showlegend=False)
    _fig
    return


@app.cell
def _(mo):
    mo.md("""
    ---
    ## 4. 最擁擠的賽道(最多人做 = 最多人死)

    進這些題材前先看看死了多少同行。
    """)
    return


@app.cell
def _(analytics, px):
    _top = (
        analytics["normalized_problem"]
        .value_counts()
        .head(15)
        .reset_index()
    )
    _top.columns = ["problem", "deaths"]
    _fig = px.bar(
        _top.sort_values("deaths"),
        x="deaths",
        y="problem",
        orientation="h",
        height=520,
        labels={"deaths": "倒閉家數", "problem": ""},
        title="最多墳墓的題材 Top 15",
    )
    _fig
    return


@app.cell
def _(mo):
    mo.md("""
    ---
    ## 5. 🔎 案例查詢器:看任一家的「付費」完整內容

    選一家公司,直接讀出它的 `the_loot`(教訓)/ `market_analysis` / `pivot_idea`
    —— 這些就是 Loot Drop 拿來賣的 Rebuild Plan 內容。
    """)
    return


@app.cell
def _(mo, startups):
    # 預設挑知名招牌案例
    _names = startups.sort_values("views", ascending=False)["name"].tolist()
    picker = mo.ui.dropdown(
        options=_names, value="WeWork" if "WeWork" in _names else _names[0],
        label="選一家公司",
    )
    picker
    return (picker,)


@app.cell
def _(json, mo, picker, startups):
    _row = startups[startups["name"] == picker.value].iloc[0]

    def _fmt_loot(raw):
        try:
            items = json.loads(raw) if isinstance(raw, str) else raw
            return "\n".join(f"{i+1}. {x}" for i, x in enumerate(items))
        except Exception:
            return str(raw)

    _loot = _fmt_loot(_row["the_loot"])
    _pivot = _row["pivot_idea"]
    try:
        _pivot = json.dumps(json.loads(_pivot), ensure_ascii=False, indent=2)
    except Exception:
        pass

    # market_analysis 在精簡版(public/)中省略以縮小體積;本地完整 db 才有
    _market = _row["market_analysis"] if "market_analysis" in _row.index else \
        "_(精簡版省略 — 完整 market_analysis 見 lootdrop.db 或原站)_"

    mo.vstack([
        mo.md(f"### {_row['name']} · {_row['sector']} · {_row['country']}"),
        mo.hstack([
            mo.stat(f"${_row['total_funding']/1e6:,.0f}M", label="募資"),
            mo.stat(f"{_row['start_year']}–{_row['end_year']}", label="存活"),
            mo.stat(_row["primary_cause_of_death"], label="死因"),
            mo.stat(f"{int(_row['views']):,}", label="瀏覽"),
        ], justify="start"),
        mo.md(f"**💎 The Loot(教訓):**\n\n{_loot}"),
        mo.md(f"**📊 Market Analysis:**\n\n{_market}"),
        mo.md(f"**🔧 Pivot Idea / Rebuild Plan:**\n\n```json\n{_pivot}\n```"),
    ])
    return


if __name__ == "__main__":
    app.run()
