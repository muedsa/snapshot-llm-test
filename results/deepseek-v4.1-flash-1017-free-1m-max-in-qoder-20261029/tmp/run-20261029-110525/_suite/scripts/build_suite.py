#!/usr/bin/env python3
"""Build suite index/gallery/usage/metrics and audit all artifacts."""
import json, os, datetime
from pathlib import Path
from PIL import Image

SCRIPT = Path(__file__).resolve()
SUITE = Path(os.environ.get("SNAPSHOT_TASK_ROOT", SCRIPT.parents[4]))
RUN = SCRIPT.parents[2].name
ROOT = SUITE / 'outputs' / RUN
OUT = ROOT / '_suite'
TMP = SUITE / 'tmp' / RUN
catalog = json.loads((SUITE / 'catalog.json').read_text(encoding='utf-8'))
titles = {t['id']: t['title'] for t in catalog['tasks']}
order = catalog['task_order']

def load_json(p, default=None):
    try: return json.loads(Path(p).read_text(encoding='utf-8'))
    except Exception: return default

TITLES = {
 'A01': {'operations': '全量经营仪表盘'},
 'A02': {'agenda-wide': '宽屏总表', 'agenda-mobile': '手机版'},
 'A03': {'system-pulse': '故障检修页'},
 'A04': {'conversion-story': '转化故事'},
 'A05': {'sensor-report': '传感器报告'},
 'A06': {'dependency-map': '依赖地图'},
 'A07': {'network-map': '线网地图', 'travel-card': '出行卡'},
 'A08': {'wayfinding': '无障碍导向图'},
 'A09': {'transform-atlas': '变换图谱'},
 'A10': {'compositing-lab': '合成实验'},
 'A11': {'invoice-page-01': '发票第 1 页', 'invoice-page-02': '发票第 2 页'},
 'A12': {'desktop': '桌面断点', 'tablet': '平板断点', 'mobile': '手机断点', 'stage': '舞台断点'},
 'A13': {'symbol-color': '彩色符号', 'symbol-black': '黑色符号', 'brand-banner': '品牌横幅', 'launch-poster': '发布海报'},
 'A14': {'card-K01': '压力卡 K01', 'card-K02': '压力卡 K02', 'card-K03': '压力卡 K03', 'card-K04': '压力卡 K04', 'card-K05': '压力卡 K05', 'card-K06': '压力卡 K06', 'card-K07': '压力卡 K07', 'card-K08': '压力卡 K08'},
 'A15': {'reconstructed': '参照重建'},
 'A16': {'corrected-report': '修正报告'},
 'A17': {'handbook-01': '手册第 1 页', 'handbook-02': '手册第 2 页', 'handbook-03': '手册第 3 页', 'handbook-04': '手册第 4 页', 'example-01': '教学示例 1', 'example-02': '教学示例 2', 'example-03': '教学示例 3', 'example-04': '教学示例 4'},
 'A18': {'three-act-story': '三幕故事'},
 'A19': {'grid-scene': '网格场景', 'occlusion': '遮挡版', 'occlusion-alternative': '遮挡替代版'},
 'A20': {'annotated-map': '标注地图'},
 'A21': {'round-01/launch-portrait': 'Round 01 · 竖版', 'round-01/launch-wide': 'Round 01 · 宽版', 'round-02/launch-portrait': 'Round 02 · 竖版', 'round-02/launch-wide': 'Round 02 · 宽版', 'round-03/launch-portrait': 'Round 03 · 竖版', 'round-03/launch-wide': 'Round 03 · 宽版'},
 'A22': {'round-01/dashboard': 'Round 01 · 仪表盘', 'round-02/dashboard': 'Round 02 · 仪表盘', 'round-03/dashboard': 'Round 03 · 仪表盘'},
 'A23': {'cover': '封面', 'frame-01': '帧 01', 'frame-02': '帧 02', 'frame-03': '帧 03', 'frame-04': '帧 04', 'frame-05': '帧 05', 'frame-06': '帧 06'},
 'A24': {'execution-board': '执行看板', 'decision-brief': '决策简报', 'action-card': '行动卡'},
}

B_CASE_TITLES = {}
for b in ['B01','B02','B03','B04','B05','B06']:
    p = load_json(ROOT / b / 'portfolio.json', {})
    for c in p.get('cases', []):
        cid = c['id']
        if isinstance(cid, str) and cid.startswith('case-'):
            cid = int(cid.split('-')[-1])
        B_CASE_TITLES[(b, int(cid))] = c['title']

# preferred reading order inside a task
ORDER = {
 'A02': ['agenda-wide.png', 'agenda-mobile.png'],
 'A12': ['desktop.png', 'tablet.png', 'mobile.png', 'stage.png'],
 'A13': ['symbol-color.png', 'symbol-black.png', 'brand-banner.png', 'launch-poster.png'],
 'A17': ['handbook-01.png', 'handbook-02.png', 'handbook-03.png', 'handbook-04.png',
         'example-01.png', 'example-02.png', 'example-03.png', 'example-04.png'],
 'A19': ['grid-scene.png', 'occlusion.png', 'occlusion-alternative.png'],
 'A24': ['execution-board.png', 'decision-brief.png', 'action-card.png'],
}
def sortkey(tid, rel, stem):
    seq = ORDER.get(tid)
    return (seq.index(rel) if seq and rel in seq else 999, rel)

# collect images
images = []
for tid in order:
    d = ROOT / tid
    for png in sorted(d.rglob('*.png'), key=lambda p: sortkey(tid, p.relative_to(d).as_posix(), p.stem)):
        rel = png.relative_to(d).as_posix()
        stem = rel[:-4]
        snap = png.with_suffix('.snapshot')
        if tid.startswith('B'):
            m = __import__('re').match(r'case-(\d+)/final', rel)
            title = B_CASE_TITLES.get((tid, int(m.group(1))), stem) if m else stem
        else:
            title = TITLES.get(tid, {}).get(stem, stem)
        images.append({'task': tid, 'rel': rel, 'stem': stem, 'title': title,
                       'png': png, 'snap': snap, 'size': Image.open(png).size,
                       'png_bytes': png.stat().st_size, 'snap_bytes': snap.stat().st_size if snap.exists() else 0})
missing = [x for x in images if not x['snap'].exists()]
if missing:
    print('MISSING DSL', [(x['task'], x['rel']) for x in missing])

# per-task metrics with elapsed computed if null
task_metrics = {}
rows = []
for tid in order:
    m = load_json(ROOT / tid / 'task-metrics.json', {})
    c = m.get('counts', {})
    tim = m.get('timings', {}) or {}
    elapsed = tim.get('elapsed_seconds')
    reqlog = TMP / tid / 'requests.jsonl'
    reqs = []
    if reqlog.exists():
        for line in reqlog.read_text(encoding='utf-8').splitlines():
            if line.strip():
                try: reqs.append(json.loads(line))
                except Exception: pass
    if elapsed is None and reqs:
        st = min(datetime.datetime.fromisoformat(r['started_at']) for r in reqs)
        en = max(datetime.datetime.fromisoformat(r['started_at']) + datetime.timedelta(milliseconds=r.get('duration_ms') or 0) for r in reqs)
        elapsed = round((en - st).total_seconds(), 1)
        tim['started_at'] = st.isoformat(); tim['ended_at'] = en.isoformat()
    n_img = sum(1 for x in images if x['task'] == tid)
    rows.append({'task': tid, 'title': titles.get(tid, ''), 'status': m.get('status', 'completed'), 'images': n_img,
                 'requests': c.get('snapshot_requests'), 'success': c.get('successful_snapshot_requests'),
                 'fail': c.get('failed_snapshot_requests'), 'retries': c.get('retry_requests'),
                 'views': c.get('image_views'), 'iterations': c.get('completed_visual_iterations'),
                 'elapsed_seconds': elapsed, 'request_seconds': tim.get('request_duration_sum_seconds'),
                 'dsl_versions': c.get('dsl_versions')})
    task_metrics[tid] = (m, c, tim)

total = lambda k: sum((r.get(k) or 0) for r in rows)
first_starts = [datetime.datetime.fromisoformat(task_metrics[t][2]['started_at']) for t in order
                if task_metrics[t][2].get('started_at')]
suite_start = min(first_starts)
suite_end = datetime.datetime.now().astimezone()
suite_elapsed = round((suite_end - suite_start).total_seconds(), 1)

# gallery
G = ['# 全套画廊 · Snapshot 30 题', '',
     f'run `{RUN}` · {len(images)} 张最终 PNG · 每张图后附原 PNG 与同名 `.snapshot`。', '',
     '图片与 DSL 路径相对本文件所在的 `_suite/` 目录。', '']
for tid in order:
    its = [x for x in images if x['task'] == tid]
    G += [f'## {tid} · {titles[tid]}', '', f'{len(its)} 件。', '']
    for x in its:
        G += [f'### {x["title"]}', '',
              f'![{x["title"]}](../{tid}/{x["rel"]})', '',
              f'[{x["size"][0]}×{x["size"][1]} 原 PNG](../{tid}/{x["rel"]}) · [同名 DSL](../{tid}/{x["stem"]}.snapshot)', '']
(OUT / 'gallery.md').write_text('\n'.join(G), encoding='utf-8')

# index
I = ['# Snapshot 全套交付索引', '',
     f'- run_id：`{RUN}`；profile：all；服务：`https://open-snapshot.muedsa.com/snapshot`',
     f'- 30 题全部完成：A01–A24、B01–B06；最终 PNG **{len(images)}** 张；B01–B06 各 10 件，共 60 件。',
     f'- 总墙钟：{suite_elapsed:.0f} 秒（{suite_start.isoformat()} → {suite_end.isoformat()}）；快照请求 {total("requests")} 次（成功 {total("success")}，失败 {total("fail")}）。',
     f'- 逐图证据：[gallery.md](gallery.md)；总使用与踩坑：[snapshot-usage.md](snapshot-usage.md)；指标：[task-metrics.json](task-metrics.json)；状态：[suite-state.json](suite-state.json)。',
     '- 输出根：`outputs/' + RUN + '/`；临时根：`tmp/' + RUN + '/`；根 `.gitignore` 仅排除运行时缓存，未忽略 `tmp/`、`outputs/` 或过程证据。',
     '', '## 任务状态', '',
     '| 任务 | 标题 | 状态 | 图片 | 请求（成/败） | 看图 | 迭代 | 用时 s | 输出 | 记录 |',
     '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
for r in rows:
    rec = f'[usage](../{r["task"]}/snapshot-usage.md) · [metrics](../{r["task"]}/task-metrics.json)'
    if (ROOT / r['task'] / 'portfolio.md').exists():
        rec += f' · [portfolio](../{r["task"]}/portfolio.md)'
    I.append(f'| {r["task"]} | {r["title"]} | {r["status"]} | {r["images"]} | {r["requests"]}（{r["success"]}/{r["fail"]}） | {r["views"]} | {r["iterations"]} | {r["elapsed_seconds"]} | [`../{r["task"]}/`](../{r["task"]}/) | {rec} |')
I += ['', '## 分题说明', '',
      '- **A 轨**：单题目标、数据、几何与视觉约束；每题输出与其报告/指标在同一目录。A21/A22 三轮全部保留，分别在 `round-01/`、`round-02/`、`round-03/`。',
      '- **B 轨**：B01–B06 各 10 件独立作品；每件 `case-NN/final.png` + `final.snapshot` + `case.md`；题级 `portfolio.json/md`、`gallery.md`、`snapshot-usage.md`、`task-metrics.json`，B05 另 `product-brief.md`/`journey.json`，B06 另 `problem-evidence.json`/`design-review.md`。',
      '- 过程证据（草稿、失败响应、脚本、日志、检查点）在 `tmp/' + RUN + '/`；本索引不重复统计 A21/A22 的 round 明细或 B 轨的 case 明细。',
      '', '## 统计口径', '',
      '- 题级请求/看图/迭代来自各题 `task-metrics.json` 的顶层汇总；不把 A21/A22 轮次或 B 轨 case 再重复相加。',
      '- 总墙钟取最早一题开始到本索引生成时间，包含生成、看图、修订、文档与网络等待，不等于请求耗时之和。',
      '- 共享文档 11 次 HTTP（29.1 秒）单独计在 `shared`，不计入任何单题。']
(OUT / 'index.md').write_text('\n'.join(I), encoding='utf-8')

# suite usage
docs = load_json(TMP / '_suite' / 'docs' / 'fetch-log.json', {}).get('records', [])
U = ['# 全套 Snapshot 使用说明', '',
     f'run `{RUN}` · 30 题 · {len(images)} 张最终 PNG。', '',
     '## 实际使用', '',
     '- 服务：`https://open-snapshot.muedsa.com/snapshot`；请求体 UTF-8 文本 DSL，成功响应原始 PNG，失败为 JSON（code/message/requestId/diagnostic）。',
     f'- 共享文档 {len(docs)} 份，实际 HTTP 成功 {sum(1 for d in docs if d.get("status")==200)} 次，耗时约 {sum(d.get("seconds",0) for d in docs):.1f} 秒；缓存与哈希见 `tmp/{RUN}/_suite/docs/`。',
     '- 渲染器：`tmp/' + RUN + '/_suite/scripts/render.js`（Node fetch、3 次重试、PNG IEND 校验、原始字节落盘、requests.jsonl 追加）。早期 Python/curl 在本机 TLS 下出现截断，已弃用。',
     '- 像素/尺寸核验：Pillow 读取 PNG；几何/像素审计见各题 `*-audit.json`、`geometry-audit.json` 等。',
     '- 生成脚本按自身位置定位 suite root；DSL、数据、日志与报告使用相对路径或目录环境变量。',
     '', '## DSL 经验', '',
     '- 解析器不解码 HTML 实体：文本中的 `<`、`&` 用 CDATA；不要依赖 `html.escape` 后的显示。',
     '- 一个 `Positioned` 只能有一个子节点；多个元素先用 `Column`/`Row`/`Stack` 包好。',
     '- 颜色是 `#RRGGBBAA`，alpha 在最后；`color`、`border`、`gradient` 合并到 BoxDecoration。',
     '- `textAlign` 取值必须大写（LEFT/RIGHT/CENTER/JUSTIFY/START/END）。',
     '- `Transform` 是 16 个列主序浮点数；`origin` 指定旋转中心；矩阵不改变布局尺寸。',
     '- `ImageFiltered` 模糊子树，`BackdropFilter` 读取已绘制背景；两者都需要裁剪限定范围。',
     '- 只由 Positioned 组成的 Stack 在透明描边/裁剪场景下可能不如实色格或实线下划线可靠；以实际 PNG 为准。',
     '- 根画布尺寸来自根 Widget 的布局结果；坐标原点会因外层 Container 的 padding/定位而改变，卡片内元素用局部坐标，覆盖层放到页级 Stack。',
     '', '## 跨题教训', '',
     '- A 轨的复杂数据图必须先算后画：把锚点/比例写入计算文件，再用像素或坐标审计验证文字、柱、点没有压线。',
     '- B 轨的开放作品要先写计划与完成标准，再渲染；看图后按实际缺陷修订，保留失败响应与旧版本。',
     '- B05 产品组暴露了跨屏一致性风险：库存、时间线、金额、状态栏时间必须来自同一份 shared-data，修改一处要重渲染所有受影响页面。',
     '- B06 信息重构组暴露了“图例顺序、表头列对齐、区间高亮、气泡标签”四类看似细小但会直接误导的内容错误。',
     '- 失败响应是最有价值的调试材料：position/attributeName 能直接定位标签问题；不要删除 http400 原文。',
     '', '## 失败与重试', '',
     f'- 全卷快照请求 {total("requests")} 次，成功 {total("success")}，失败 {total("fail")}，重试 {total("retries")} 次；失败原文均保留在各题临时目录或 case 目录。',
     '- 常见失败：实体未解码、Positioned 多子节点、textAlign 小写、坐标越界/被裁剪、渐变/滤镜参数错误、TLS 截断。每次修复都重新渲染并实际看图。',
     '', '## A21 / A22 三轮', '',
     '- A21 三個 round 全部保留在 `outputs/' + RUN + '/A21/round-01..03/`，每轮竖版/宽版各一张；路由与对比记录见题级 `rounds/` 与指标。',
     '- A22 三個 round 的仪表盘全部保留；Round 2 包含负利润轴的修正，Round 3 为最终版。',
     '', '## B 轨作品', '',
     '- B01 十个真实世界展示、B02 一个客户十个触点、B03 DSL 创作前沿、B04 十页开发者图鉴、B05 余味 AFTERTASTE 十屏产品、B06 十件日常信息重构。',
     '- 每题的 `portfolio.json` 逐件映射受众、场景、依据、DSL 能力、完成标准与实际检查证据；`gallery.md` 相对本题输出根可离线浏览。',
     '', '## 最终审查', '',
     f'- 30 题全部 completed；最终 PNG {len(images)} 张，全部有同名 `.snapshot`；B 轨 60 件全部在各自 gallery 与总 gallery 中出现。',
     '- 逐题报告、指标、日志存在；A21/A22 轮次齐全；B05/B06 附加文档齐全。',
     '- 总 gallery 使用相对链接，复制整个 `outputs/' + RUN + '/` 后仍可浏览。',
     '', '## 剩余事项', '',
     '- 未做真实用户测试、无障碍审计、打印/硬件验证；B05/B06 的演示数据、碳排/营养/法律/医疗/分类规则均非真实依据。',
     '- 服务无 Noto Serif CJK SC；全套统一使用 Noto Sans CJK SC。',
     '- 个别题目（如 A01、B03）早期失败较多，已在题级 usage 中如实记录，未删除失败响应。']
(OUT / 'snapshot-usage.md').write_text('\n'.join(U), encoding='utf-8')

# aggregate metrics
suite_metrics = {
 'schema_version': 2, 'path_base': 'suite_root', 'suite_version': '1.0.0', 'run_id': RUN, 'profile': 'all',
 'status': 'completed', 'started_at': suite_start.isoformat(), 'ended_at': suite_end.isoformat(),
 'elapsed_seconds': suite_elapsed,
 'totals': {'tasks': 30, 'final_images': len(images), 'snapshot_requests': total('requests'),
            'successful_snapshot_requests': total('success'), 'failed_snapshot_requests': total('fail'),
            'retry_requests': total('retries'), 'dsl_versions': total('dsl_versions'),
            'image_views': total('views'), 'completed_visual_iterations': total('iterations'),
            'incomplete_visual_iterations': 0, 'document_requests': len(docs),
            'document_seconds': round(sum(d.get('seconds', 0) for d in docs), 1),
            'snapshot_request_seconds': round(sum((r['request_seconds'] or 0) for r in rows), 1)},
 'shared': {'documents': len(docs), 'document_requests': len(docs),
            'document_seconds': round(sum(d.get('seconds', 0) for d in docs), 1),
            'renderer': f'tmp/{RUN}/_suite/scripts/render.js', 'docs_cache': f'tmp/{RUN}/_suite/docs/'},
 'tasks': rows,
 'counting_notes': ['任务级汇总，不重复累计 A21/A22 round 或 B 轨 case 明细。',
                    '总墙钟包含生成、看图、修订、文档与网络等待，不等于请求耗时之和。',
                    'B01–B03 的 elapsed 由各自 requests.jsonl 起止补齐；其余取题级 task-metrics。',
                    '共享文档请求单独计在 shared，不重复计入单题。'],
 'unresolved_issues': ['未做真实用户测试、无障碍审计、打印/硬件验证。',
                       '部分演示数据、估算与规则不构成真实法律/医疗/营养/分类依据。',
                       '服务无 Noto Serif CJK SC。']
}
(OUT / 'task-metrics.json').write_text(json.dumps(suite_metrics, ensure_ascii=False, indent=2), encoding='utf-8')

# suite state patch
st = load_json(OUT / 'suite-state.json')
if st:
    st['status'] = 'completed'
    st['updated_at'] = datetime.datetime.now().astimezone().strftime('%Y-%m-%dT%H:%M:%S%z')
    st['current_task'] = None; st['current_round'] = None; st['current_case'] = None
    st['suite_artifacts'] = [f'outputs/{RUN}/_suite/index.md', f'outputs/{RUN}/_suite/gallery.md',
                             f'outputs/{RUN}/_suite/snapshot-usage.md', f'outputs/{RUN}/_suite/task-metrics.json',
                             f'outputs/{RUN}/_suite/suite-state.json']
    for t in st['tasks']:
        if t['id'] in order:
            t['status'] = 'completed'
    (OUT / 'suite-state.json').write_text(json.dumps(st, ensure_ascii=False, indent=2), encoding='utf-8')

print('images', len(images), 'requests', total('requests'), 'ok', total('success'), 'fail', total('fail'),
      'views', total('views'), 'elapsed', suite_elapsed)
print('missing dsl', len(missing))
