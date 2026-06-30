# loot-drop-clone 常用操作
# 用法:just <recipe>   (just --list 看全部)

set shell := ["bash", "-cu"]

# 預設:列出所有指令
default:
    @just --list

# === 環境 ===

# 安裝/同步依賴
sync:
    uv sync

# === 資料 pipeline ===

# 重新爬取資料(會打 loot-drop.io 的 Supabase,內建節流)
fetch:
    uv run python fetch_all.py

# 從 data/*.json 重建 SQLite
db:
    uv run python build_db.py

# CLI 統計分析(印出 docs/03 的數字)
analyze:
    uv run python analyze.py

# === 快照 ===

# 重抓網站快照(HTML + 打包 JS)
snapshot-site:
    uv run python snapshot/grab_site.py

# 重抓 Supabase API 原始回應
snapshot-api:
    uv run python snapshot/grab_api.py

# === 網站 / notebook ===

# 開互動 notebook(本地 edit 模式,瀏覽器)
notebook:
    uv run marimo edit notebooks/explore.py

# 建靜態 HTML 網站(docs/reports -> site/)
site:
    uv run python build_site.py

# export 靜態版 notebook 到 site/
notebook-static:
    uv run marimo export html notebooks/explore.py -o site/notebook.html

# 產生 WASM 版 notebook(精簡資料 + Pyodide export)
wasm:
    uv run python build_wasm.py

# 一次建好整個 site/(db + 靜態站 + 靜態notebook + WASM)
build-all: db site notebook-static wasm
    @echo "site/ 已就緒,可本地預覽:just serve"

# 本地預覽 site/(http://localhost:8000)
serve:
    uv run python -m http.server 8000 --directory site

# 重新產生 OG 預覽圖(需 rsvg-convert)
og:
    rsvg-convert -w 1200 -h 630 site/og-image.svg -o site/og-image.png

# === 部署 ===

# 觸發 GitHub Pages 部署 workflow
deploy:
    gh workflow run deploy-pages.yml
    @echo "部署已觸發,看狀態:just deploy-status"

# 看最近的部署狀態
deploy-status:
    gh run list --workflow=deploy-pages.yml --limit 5

# === 對話記錄 ===

# 重新 export 本次 session(需傳 SESSION=ses_xxx),並轉 Markdown
chat SESSION:
    opencode export {{SESSION}} > chat-history/session.json
    uv run python chat-history/render_md.py

# === 資料 Release ===

# 從 GitHub Release 下載現成的 lootdrop.db(免跑 build)
download-db:
    gh release download data-2026-06-30 -p lootdrop.db -R daviddwlee84/loot-drop-clone
