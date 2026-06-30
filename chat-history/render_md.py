#!/usr/bin/env python3
"""把 opencode export 的 session.json 轉成人類可讀的 Markdown。

用法:
    uv run python chat-history/render_md.py
產出:
    chat-history/session.md
"""
import json
import pathlib
import datetime as dt

HERE = pathlib.Path(__file__).parent
SRC = HERE / "session.json"
OUT = HERE / "session.md"

# tool 名稱 → emoji 標籤
TOOL_LABEL = {
    "bash": "🖥️ bash", "edit": "✏️ edit", "write": "📝 write", "read": "📖 read",
    "glob": "🔍 glob", "grep": "🔎 grep", "webfetch": "🌐 webfetch",
    "task": "🤖 task", "todowrite": "✅ todo", "question": "❓ question",
    "skill": "🧩 skill",
}


def ts(ms):
    if not ms:
        return ""
    return dt.datetime.fromtimestamp(ms / 1000).strftime("%H:%M:%S")


def truncate(s, n=1500):
    s = s or ""
    if len(s) <= n:
        return s
    return s[:n] + f"\n… [截斷,共 {len(s):,} 字元]"


def render_tool(p):
    tool = p.get("tool", "?")
    label = TOOL_LABEL.get(tool, f"🔧 {tool}")
    state = p.get("state", {}) or {}
    inp = state.get("input", {}) or {}
    out = state.get("output", "")
    title = state.get("title", "")

    # 摘要參數(只取關鍵欄位,避免過長)
    summary = title or ""
    if not summary:
        for key in ("command", "filePath", "pattern", "url", "description", "query"):
            if key in inp:
                summary = str(inp[key])
                break
    summary = (summary or "").replace("\n", " ")[:100]

    lines = [f"<details><summary><b>{label}</b> · <code>{summary}</code></summary>", ""]
    # 輸入
    if inp:
        shown = {k: v for k, v in inp.items() if k not in ("content",)}
        if shown:
            lines += ["**input:**", "```json",
                      truncate(json.dumps(shown, ensure_ascii=False, indent=2), 800), "```"]
    # 輸出
    if out:
        lines += ["**output:**", "```", truncate(str(out), 1500), "```"]
    lines += ["", "</details>", ""]
    return "\n".join(lines)


def main():
    data = json.loads(SRC.read_text())
    info = data["info"]
    msgs = data["messages"]

    md = [
        f"# 對話記錄:{info.get('title','(untitled)')}",
        "",
        f"> Session `{info.get('id','')}` · 由 opencode export 產生 · "
        f"共 {len(msgs)} 則訊息",
        "",
        "> tool 呼叫已摺疊(點開可看);過長輸出已截斷。完整原始資料見 "
        "[`session.json`](session.json)(可用 `opencode import` 重放)。",
        "",
        "---",
        "",
    ]

    for m in msgs:
        role = m["info"]["role"]
        parts = m.get("parts", [])
        if role == "user":
            texts = [p["text"] for p in parts if p.get("type") == "text" and p.get("text")]
            if not texts:
                continue
            md.append("## 🧑 User\n")
            md.append("\n".join(texts))
            md.append("\n")
        else:  # assistant
            chunks = []
            for p in parts:
                t = p.get("type")
                if t == "text" and p.get("text"):
                    chunks.append(p["text"])
                elif t == "tool":
                    chunks.append(render_tool(p))
            if not chunks:
                continue
            md.append("## 🤖 Assistant\n")
            md.append("\n\n".join(chunks))
            md.append("\n")
        md.append("---\n")

    OUT.write_text("\n".join(md), encoding="utf-8")
    print(f"已產生 {OUT}  ({OUT.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
