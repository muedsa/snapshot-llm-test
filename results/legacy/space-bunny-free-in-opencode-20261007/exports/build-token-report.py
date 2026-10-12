#!/usr/bin/env python3
"""汇总 opencode 主/子代理会话的 token 消耗，输出 Markdown 报告。

数据来源
  1. ccusage：npx -y ccusage@latest opencode session --json --offline
     （可加 --refresh 重新拉取，否则复用同目录缓存的 JSON）
  2. opencode 本地 SQLite 库：session 表提供父子关系、标题、时间、推理 tokens

所有路径都相对脚本自身或当前工作目录解析；用户级数据库位置通过环境变量
或各平台惯例推导，可用 OPENCODE_DB 覆盖。

用法
  python build-token-report.py                      # 用缓存 JSON
  python build-token-report.py --refresh            # 重新调用 ccusage
  python build-token-report.py --parent ses_xxx     # 指定主会话
  python build-token-report.py --db ./opencode.db   # 指定数据库
  python build-token-report.py --out ./report.md    # 指定输出
"""

import argparse
import json
import os
import sqlite3
import subprocess
import sys
from datetime import datetime

SCRIPT = os.path.basename(__file__)
RAW_NAME = "ccusage-opencode-session.json"
DEFAULT_OUT = "opencode-token-usage.md"
CCUSAGE_ARGS = ["-y", "ccusage@latest", "opencode", "session",
                "--json", "--no-color", "--offline"]

# 各平台 opencode 数据目录的相对片段，按顺序探测
DB_CANDIDATES = (
    os.path.join(".local", "share", "opencode", "opencode.db"),          # Linux / macOS / Windows(WSL-ish)
    os.path.join("AppData", "Local", "opencode", "opencode.db"),        # Windows 原生
    os.path.join("AppData", "Roaming", "opencode", "opencode.db"),      # Windows 兜底
    os.path.join("Library", "Application Support", "opencode", "opencode.db"),  # macOS 兜底
)


def user_home():
    return os.path.expanduser("~")


def resolve_db(explicit=None):
    """定位 opencode.db：显式参数 > 环境变量 > 平台惯例。"""
    if explicit:
        return os.path.abspath(explicit)
    env = os.environ.get("OPENCODE_DB")
    if env:
        return os.path.abspath(os.path.expandvars(env))
    home = user_home()
    for rel in DB_CANDIDATES:
        cand = os.path.join(home, rel)
        if os.path.isfile(cand):
            return cand
    raise SystemExit(
        "找不到 opencode.db，请用 --db 或环境变量 OPENCODE_DB 指定路径。"
    )


def pick_parent(sessions, requested=None, with_tokens=frozenset()):
    """确定主会话：显式指定 > 环境变量 > 推断出的根会话。"""
    child_counts = {}
    for r in sessions.values():
        if r.get("parent_id"):
            child_counts[r["parent_id"]] = child_counts.get(r["parent_id"], 0) + 1
    if requested:
        if requested not in sessions:
            raise SystemExit(f"主会话 {requested} 不在 opencode 数据库中")
        return requested
    env = os.environ.get("OPENCODE_SESSION_ID")
    if env:
        if env not in sessions:
            raise SystemExit(f"环境变量 OPENCODE_SESSION_ID={env} 不在 opencode 数据库中")
        return env
    # 自动推断：根会话 = 没有任何 parent 的会话；再优先“有子会话 + 有 token 记录 + 子会话最多”
    is_child = {r["id"] for r in sessions.values() if r.get("parent_id")}
    roots = [sid for sid in sessions if sid not in is_child]
    scored = sorted(
        roots,
        key=lambda sid: (child_counts.get(sid, 0) > 0,
                         sid in with_tokens,
                         child_counts.get(sid, 0)),
        reverse=True,
    )
    if scored:
        return scored[0]
    raise SystemExit("无法自动判断主会话，请用 --parent 指定")


def run_ccusage(cache_path):
    for exe in ("npx.cmd", "npx"):
        try:
            proc = subprocess.run(
                [exe] + CCUSAGE_ARGS,
                capture_output=True,
                text=True,
                shell=exe.endswith(".cmd"),
            )
        except FileNotFoundError:
            continue
        if proc.returncode == 0 and proc.stdout.strip():
            with open(cache_path, "w", encoding="utf-8") as fh:
                fh.write(proc.stdout)
            return json.loads(proc.stdout), "ccusage（本次实时拉取）"
    if os.path.isfile(cache_path):
        with open(cache_path, encoding="utf-8") as fh:
            return json.load(fh), f"ccusage（复用缓存 {os.path.basename(cache_path)}）"
    raise SystemExit("ccusage 调用失败且无缓存 JSON；请先运行 "
                     "npx -y ccusage@latest opencode session --json --offline")


def load_db(db_path):
    uri = "file:" + db_path.replace("\\", "/") + "?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, parent_id, title, agent, model, directory, time_created,"
        " time_updated, time_archived, tokens_input, tokens_output,"
        " tokens_reasoning, tokens_cache_read, tokens_cache_write, cost FROM session"
    ).fetchall()
    conn.close()
    return {r["id"]: dict(r) for r in rows}


def fmt_time(ms):
    return datetime.fromtimestamp(ms / 1000).strftime("%Y-%m-%d %H:%M") if ms else "-"


def fmt_dur(ms):
    if not ms:
        return "-"
    s = ms / 1000
    h, rem = divmod(int(s), 3600)
    m, _ = divmod(rem, 60)
    if h:
        return f"{h}h{m:02d}m"
    if m:
        return f"{m}m"
    return f"{s:.0f}s"


def num(n):
    return f"{n:,}"


def pct(part, whole):
    """百分比，分母为 0 时返回 0 而不是崩溃。"""
    return part / whole * 100 if whole else 0.0


def short(sid):
    return sid.replace("ses_", "")


def clean_title(t):
    return t.replace(" (@general subagent)", "").strip()


def show_path(path, base):
    """尽量以可搬迁的相对路径展示：cwd 相对 > ~/ 相对 > 原样。"""
    path = os.path.abspath(path)
    try:
        rel = os.path.relpath(path, base).replace("\\", "/")
        if not rel.startswith(".."):
            return rel
    except ValueError:
        pass
    home = os.path.expanduser("~")
    if path == home:
        return "~"
    if path.startswith(home + os.sep):
        return "~/" + os.path.relpath(path, home).replace("\\", "/")
    return path


def write_markdown(data, sessions, parent, db_path, raw_path, out_path, source_note, workdir):
    by_id = {s["sessionId"]: s for s in data["sessions"]}
    prow = sessions.get(parent, {})
    children = sorted(
        (r for r in sessions.values() if r.get("parent_id") == parent),
        key=lambda r: r["time_created"],
    )
    child_ids = {c["id"] for c in children}

    def reasoning(sids):
        return sum(sessions.get(sid, {}).get("tokens_reasoning") or 0 for sid in sids)

    def agg(sids):
        t = {"inputTokens": 0, "outputTokens": 0, "cacheReadTokens": 0,
             "cacheCreationTokens": 0, "totalTokens": 0, "totalCost": 0.0}
        models = {}
        for sid in sids:
            s = by_id.get(sid)
            if not s:
                continue
            for k in t:
                t[k] += s.get(k, 0) or 0
            t["totalCost"] += s.get("totalCost", 0.0) or 0.0
            for m in s.get("modelBreakdowns", []):
                e = models.setdefault(m["modelName"],
                                      {"in": 0, "out": 0, "cr": 0, "cc": 0, "priced": True})
                e["in"] += m.get("inputTokens", 0)
                e["out"] += m.get("outputTokens", 0)
                e["cr"] += m.get("cacheReadTokens", 0)
                e["cc"] += m.get("cacheCreationTokens", 0) or 0
                if m.get("missingPricing"):
                    e["priced"] = False
        for e in models.values():
            e["total"] = e["in"] + e["out"] + e["cr"] + e["cc"]
        return t, models

    with_cc = [sid for sid in child_ids if sid in by_id]
    missing = [sid for sid in child_ids if sid not in by_id]
    tree_tot, tree_models = agg([parent] + with_cc)
    parent_tot, _ = agg([parent])
    subs_tot, _ = agg(with_cc)

    ps = by_id.get(parent)
    tree_dur = fmt_dur((prow.get("time_updated") or 0) - (prow.get("time_created") or 0))
    raw_model = prow.get("model") or "-"
    try:
        raw_model = json.loads(raw_model).get("id", raw_model)
    except (ValueError, AttributeError):
        pass

    L = []
    add = L.append
    add("# opencode Token 消耗报告：主/子代理会话")
    add("")
    add(f"- 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    add(f"- 生成脚本：`{SCRIPT}`（位于 `{show_path(os.path.abspath(__file__), workdir)}`）")
    add(f"- token 数据：{source_note}")
    add(f"- 会话元数据：opencode 本地库 `{show_path(db_path, workdir)}`"
        f"（可用环境变量 `OPENCODE_DB` 覆盖）")
    add(f"- 主会话：`{parent}` — {prow.get('title', '(未知)')}")
    if prow.get("directory"):
        add(f"- 主会话工作目录：`{show_path(prow['directory'], workdir)}`")
    add(f"- 主会话时间：{fmt_time(prow.get('time_created'))} → {fmt_time(prow.get('time_updated'))}（{tree_dur}）")
    add(f"- 子代理会话数：{len(children)}（{len(with_cc)} 个有 ccusage token 记录，"
        f"{len(missing)} 个无记录）")
    add(f"- 报告输出：`{show_path(out_path, workdir)}`")
    add("")

    add("## 1. 汇总")
    add("")
    add("| 范围 | 会话数 | 输入 | 输出 | 推理 | 缓存读取 | 总 tokens | 记录成本 (USD) |")
    add("|---|---:|---:|---:|---:|---:|---:|---:|")
    add(f"| 主会话（父） | 1 | {num(parent_tot['inputTokens'])} | {num(parent_tot['outputTokens'])} | "
        f"{num(reasoning([parent]))} | {num(parent_tot['cacheReadTokens'])} | "
        f"{num(parent_tot['totalTokens'])} | {parent_tot['totalCost']:.4f} |")
    add(f"| 子代理合计 | {len(with_cc)} | {num(subs_tot['inputTokens'])} | {num(subs_tot['outputTokens'])} | "
        f"{num(reasoning(with_cc))} | {num(subs_tot['cacheReadTokens'])} | "
        f"{num(subs_tot['totalTokens'])} | {subs_tot['totalCost']:.4f} |")
    add(f"| **本会话树合计** | {1 + len(with_cc)} | **{num(tree_tot['inputTokens'])}** | "
        f"**{num(tree_tot['outputTokens'])}** | **{num(reasoning(with_cc + [parent]))}** | "
        f"**{num(tree_tot['cacheReadTokens'])}** | **{num(tree_tot['totalTokens'])}** | "
        f"**{tree_tot['totalCost']:.4f}** |")
    add("")
    add("> 推理 tokens 取自 opencode 库 `session.tokens_reasoning`；其余列取自 ccusage。"
        "ccusage 的 totalTokens 不含推理部分，两者口径不同，勿直接相减。")
    add(f"> 会话树内缓存读取占总量 "
        f"{pct(tree_tot['cacheReadTokens'], tree_tot['totalTokens']):.1f}%。")
    unpriced = [m for m in sorted(tree_models) if not tree_models[m]["priced"]]
    if unpriced:
        add("")
        add(f"> 成本说明：`{'`, `'.join(unpriced)}` 在 LiteLLM 定价表中缺失（ccusage 标记 "
            f"`missingPricing`），因此本会话树所有成本列为 0，不代表实际免费。")
    add("")

    add("## 2. 主会话明细")
    add("")
    add("| 字段 | 值 |")
    add("|---|---|")
    add(f"| Session ID | `{parent}` |")
    add(f"| 标题 | {prow.get('title', '-')} |")
    add(f"| Agent / Model | {prow.get('agent', '-')} / {raw_model} |")
    add(f"| 创建 / 最后更新 | {fmt_time(prow.get('time_created'))} / {fmt_time(prow.get('time_updated'))} |")
    if ps:
        add(f"| 输入 / 输出 tokens | {num(ps['inputTokens'])} / {num(ps['outputTokens'])} |")
        add(f"| 缓存读取 tokens | {num(ps['cacheReadTokens'])} |")
        add(f"| 总 tokens | {num(ps['totalTokens'])} |")
        add(f"| 使用模型 | {', '.join(ps.get('modelsUsed', []))} |")
    else:
        add("| token 记录 | ccusage 输出中无该会话 |")
    add("")

    add("## 3. 子代理明细（按创建时间）")
    add("")
    add("| # | 任务 | Session ID | 开始 | 时长 | 输入 | 输出 | 缓存读取 | 总 tokens | 成本 |")
    add("|---:|---|---|---|---:|---:|---:|---:|---:|---:|")
    for i, c in enumerate(children, 1):
        s = by_id.get(c["id"])
        row = (f"| {i} | {clean_title(c['title'])} | `{short(c['id'])}` | "
               f"{fmt_time(c['time_created'])} | "
               f"{fmt_dur((c.get('time_updated') or 0) - (c.get('time_created') or 0))} | ")
        if s:
            add(row + f"{num(s['inputTokens'])} | {num(s['outputTokens'])} | "
                      f"{num(s['cacheReadTokens'])} | {num(s['totalTokens'])} | "
                      f"{s.get('totalCost', 0):.4f} |")
        else:
            add(row + "– | – | – | – | – |")
    add("")
    add("> Session ID 为简写（省略 `ses_` 前缀），完整列表见附录 A。")
    add("")

    add("### 3.1 子代理 token 排行")
    add("")
    ranked = sorted(((c["id"], by_id[c["id"]]) for c in children if c["id"] in by_id),
                    key=lambda x: x[1]["totalTokens"], reverse=True)
    add("| 排名 | 任务 | Session ID | 总 tokens | 占比 |")
    add("|---:|---|---|---:|---:|")
    for rank, (sid, s) in enumerate(ranked, 1):
        share = pct(s["totalTokens"], subs_tot["totalTokens"])
        add(f"| {rank} | {clean_title(sessions.get(sid, {}).get('title', sid))} | `{short(sid)}` | "
            f"{num(s['totalTokens'])} | {share:.1f}% |")
    add("")

    add("### 3.2 按任务分组")
    add("")
    groups = {"A 类": [], "B 类": [], "其他/未知": []}
    for c in children:
        t = c["title"].upper()
        if re_task(t, "A"):
            groups["A 类"].append(c)
        elif re_task(t, "B"):
            groups["B 类"].append(c)
        else:
            groups["其他/未知"].append(c)
    add("| 类别 | 会话数 | 输入 | 输出 | 缓存读取 | 总 tokens | 占比 |")
    add("|---|---:|---:|---:|---:|---:|---:|")
    for name, g in groups.items():
        ids = [c["id"] for c in g if c["id"] in by_id]
        t, _ = agg(ids)
        share = pct(t["totalTokens"], subs_tot["totalTokens"])
        add(f"| {name} | {len(ids)} | {num(t['inputTokens'])} | {num(t['outputTokens'])} | "
            f"{num(t['cacheReadTokens'])} | {num(t['totalTokens'])} | {share:.1f}% |")
    add("")

    add("### 3.3 模型构成")
    add("")
    add("| 模型 | 会话数 | 输入 | 输出 | 缓存读取 | 总 tokens | 定价 |")
    add("|---|---:|---:|---:|---:|---:|---|")
    for model, e in sorted(tree_models.items(), key=lambda kv: -kv[1]["total"]):
        cnt = sum(1 for sid in with_cc + [parent]
                  if any(m["modelName"] == model
                         for m in by_id.get(sid, {}).get("modelBreakdowns", [])))
        add(f"| `{model}` | {cnt} | {num(e['in'])} | {num(e['out'])} | {num(e['cr'])} | "
            f"{num(e['total'])} | {'已定价' if e['priced'] else '缺失（成本按 0 计）'} |")
    add("")

    add("## 4. 观察")
    add("")
    if ranked:
        top_id, top = ranked[0]
        add(f"- 子代理最高消耗：`{clean_title(sessions.get(top_id, {}).get('title', top_id))}`"
            f"（`{short(top_id)}`），{num(top['totalTokens'])} tokens，占子代理总量 "
            f"{pct(top['totalTokens'], subs_tot['totalTokens']):.1f}%。")
        low_id, low = ranked[-1]
        add(f"- 子代理最低消耗：`{clean_title(sessions.get(low_id, {}).get('title', low_id))}`"
            f"（`{short(low_id)}`），{num(low['totalTokens'])} tokens。")
        avg = subs_tot["totalTokens"] / max(len(with_cc), 1)
        add(f"- 子代理平均每会话总 tokens {num(int(avg))}，主会话为 {num(parent_tot['totalTokens'])}，"
            f"{'主会话高于' if parent_tot['totalTokens'] > avg else '主会话低于'}子代理均值。")
    add(f"- 缓存读取占子代理总量 {pct(subs_tot['cacheReadTokens'], subs_tot['totalTokens']):.1f}%，"
        f"占主会话 {pct(parent_tot['cacheReadTokens'], parent_tot['totalTokens']):.1f}%；"
        "实际负载主要看输入+输出，缓存读取多为重复上下文复用。")
    add(f"- 输入+输出（不含缓存）合计 {num(tree_tot['inputTokens'] + tree_tot['outputTokens'])} tokens，"
        f"其中子代理占 {pct(subs_tot['inputTokens'], tree_tot['inputTokens']):.1f}% 输入、"
        f"{pct(subs_tot['outputTokens'], tree_tot['outputTokens']):.1f}% 输出——"
        "内容产出几乎全部由子代理完成，主会话主要负责调度与汇总。")
    if missing:
        add(f"- 无 ccusage token 记录的子会话（{len(missing)} 个，通常是启动后未产生模型调用的短会话）："
            + ", ".join(f"`{short(m)}`" for m in missing) + "。")
    add("- 同一任务可能对应多个子会话（首轮 + 续做），属于上下文压缩或平台中断后的续跑，"
        "统计时应按“子代理会话”而非“任务数”理解。")
    add("")

    add("## 附录 A：完整子代理 Session ID")
    add("")
    add("```")
    for c in children:
        add(f"{c['id']}  {c['title']}")
    add("```")
    add("")

    add("## 附录 B：复现方式")
    add("")
    add("```bash")
    add("# 1. 拉取 token 数据（脚本默认复用上一步的 JSON 缓存）")
    add("npx -y ccusage@latest opencode session --json --no-color --offline")
    add("")
    add("# 2. 生成报告（主会话缺省自动推断；首次运行会自动做第 1 步）")
    add(f"python {SCRIPT}")
    add("```")
    add("")
    add("会话元数据由脚本直接从 opencode 本地 SQLite 库读取（只读打开），")
    add("库位置按 `OPENCODE_DB` → 各平台惯例（`~/.local/share/opencode`、")
    add("`~/AppData/Local/opencode` 等）依次探测。手动查看：")
    add("")
    add("```bash")
    add('sqlite3 "${OPENCODE_DB:-$HOME/.local/share/opencode/opencode.db}" \\')
    add('  "select id, parent_id, title, time_created from session;"')
    add("```")
    add("")
    add("可覆盖的配置：")
    add("")
    add("| 变量 / 参数 | 作用 |")
    add("|---|---|")
    add("| `--parent` / `OPENCODE_SESSION_ID` | 主会话 ID，缺省自动推断 |")
    add("| `--db` / `OPENCODE_DB` | opencode.db 路径，缺省按平台惯例探测 |")
    add("| `--raw` | ccusage JSON 缓存路径（默认与脚本同目录） |")
    add("| `--out` | 报告输出路径（默认与脚本同目录） |")
    add("| `--refresh` | 强制重新调用 ccusage，不复用缓存 |")
    add("")

    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    return len(children), len(with_cc), missing


def re_task(title, letter):
    """标题里是否出现 A01–A24 / B01–B06 这类任务编号前缀。"""
    import re
    return re.search(rf"\b{letter}\d{{2}}\b", title) is not None


def main(argv=None):
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description="汇总 opencode 主/子代理 token 消耗")
    ap.add_argument("--parent", help="主会话 session ID")
    ap.add_argument("--db", help="opencode.db 路径")
    ap.add_argument("--raw", default=os.path.join(here, RAW_NAME),
                    help="ccusage JSON 缓存路径")
    ap.add_argument("--out", default=os.path.join(here, DEFAULT_OUT),
                    help="Markdown 报告输出路径")
    ap.add_argument("--refresh", action="store_true", help="强制重新拉取 ccusage 数据")
    args = ap.parse_args(argv)

    db_path = resolve_db(args.db)
    if args.refresh or not os.path.isfile(args.raw):
        data, note = run_ccusage(args.raw)
    else:
        with open(args.raw, encoding="utf-8") as fh:
            data = json.load(fh)
        note = f"ccusage（复用缓存 {os.path.basename(args.raw)}）"

    sessions = load_db(db_path)
    parent = pick_parent(sessions, args.parent,
                         with_tokens={s["sessionId"] for s in data["sessions"]})
    out_path = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)

    n_child, n_cc, missing = write_markdown(
        data, sessions, parent, db_path, args.raw, out_path, note, os.getcwd())
    print(f"written: {show_path(out_path, os.getcwd())}")
    print(f"parent: {parent}")
    print(f"children={n_child} with_ccusage={n_cc} missing={len(missing)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())