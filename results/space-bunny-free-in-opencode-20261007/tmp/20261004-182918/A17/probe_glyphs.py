"""A17 probe 2: per-glyph advance table for Inter(+CJK) and DejaVu Sans Mono.

The service caps canvas height at 4096, so glyphs are rendered in batches.
Each glyph is drawn once alone (ink + left side bearing) and once repeated 20
times (advance pitch = (span - ink) / 19).  Output: probe/glyphs.json
"""
from __future__ import annotations

import json
import os
import statistics
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TASK = "A17"
OUT = os.path.join(ROOT, "outputs", RUN, TASK)
TMP = os.path.join(ROOT, "tmp", RUN, TASK)
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402

snapkit.configure(TASK, OUT, TMP)
PROBE = os.path.join(TMP, "probe")
os.makedirs(PROBE, exist_ok=True)

SIZE = 100
LATIN = [chr(c) for c in range(32, 127)]
CJK = list("画布尺寸由布局决定根节点不是单个示例与印刷同源字体文本属性忽略未知会"
           "请求响应错误契约插图对照误解尾部背景子树滤镜视觉自检可复现交付章节页码"
           "版式色板字阶代码块行号上边距安全内边距外框圆角阴影渐变透明度滤镜模糊"
           "静默丢弃溢出行高基线对齐居左居右居中网格间距标题副标题注释脚注"
           "第一二三四五章要点注意必须不能可以应该建议结论来源实测服务官方"
           "文档指南参考枚举标签解析器渲染输入输出码状态头"
           "时间缓存命中限流重试匿名凭据密钥不要写入日志文件目录名称路径"
           "色透明不透明十六进制八位四位三位缩写迁移旧新规顺序颠倒"
           "保留空白修剪原始节点段落布局属性生效失效嵌套继承覆盖层级结构"
           "位置定绝对坐轴两项规则超界裁阴影截断边缘矩椭圆"
           "毛玻璃效果只背文清晰混合模式整棵响范围馈"
           "循环查打开图片修做满意为止逐张交批量渲染参数化生成函数"
           "键值对比位齐间距标题字号粗斜体衬线等宽颜色栏右左")

items = [("latin", ch) for ch in LATIN] + [("cjk", ch) for ch in CJK]


def raw_text(s, x, y, w, h, size, font, color):
    inner = D.el("Text", {"color": color, "fontSize": size, "fontFamily": font},
                 [D.cdata(s)])
    return D.el("Positioned", {"left": x, "top": y, "width": w, "height": h}, [inner])


ROW_H = 132
BATCH = 28
W_IN = 1400
W_PITCH = 2600
result = {}


def strip_scan(im, yy, mid_off, xmax_scan):
    px = im.load()
    xmin = xmax = None
    for xr in range(0, xmax_scan):
        c = px[xr, yy + mid_off]
        if c[0] > 120 and c[1] > 120 and c[2] > 120:
            if xmin is None:
                xmin = xr
            xmax = xr
    return xmin, xmax


from PIL import Image  # noqa: E402

for bi in range(0, len(items), BATCH):
    batch = items[bi:bi + BATCH]
    # pass 1: single glyphs
    H = 20 + len(batch) * ROW_H
    kids = [D.box(0, 0, W_IN, H, color="#FFFFFFFF")]
    y = 10
    for kind, ch in batch:
        kids.append(D.box(0, y, W_IN, ROW_H - 8, color="#0F172AFF"))
        kids.append(raw_text(ch, 16, y + 12, 300, ROW_H - 32, SIZE,
                             D.UI if kind == "cjk" else D.LATIN, "#FFFFFFFF"))
        y += ROW_H
    dsl = D.snapshot([D.stack(kids, W_IN, H)], W_IN, H, bg="#FFFFFFFF")
    r = snapkit.render(dsl, "g-%02d.png" % (bi // BATCH), "g-%02d.snapshot" % (bi // BATCH),
                       final=False, out_dir=PROBE)
    assert r.get("ok"), (bi, r.get("status"), r.get("error", "")[:300])
    im = Image.open(r["image"]).convert("RGB")
    yy = 10
    inks = {}
    for kind, ch in batch:
        xmin, xmax = strip_scan(im, yy, ROW_H // 2, 600)
        inks[ch] = None if xmin is None else (xmax - xmin + 1, xmin - 16)
        result.setdefault(ch, {"kind": kind})
        if xmin is not None:
            result[ch]["ink100"] = xmax - xmin + 1
            result[ch]["bearing100"] = xmin - 16
        yy += ROW_H
    # pass 2: pitch
    H2 = 20 + len(batch) * ROW_H
    kids2 = [D.box(0, 0, W_PITCH, H2, color="#FFFFFFFF")]
    y = 10
    for kind, ch in batch:
        kids2.append(D.box(0, y, W_PITCH, 124, color="#0F172AFF"))
        kids2.append(raw_text(ch * 20, 16, y + 12, W_PITCH - 40, 100, SIZE,
                              D.UI if kind == "cjk" else D.LATIN, "#FFFFFFFF"))
        y += ROW_H
    dsl2 = D.snapshot([D.stack(kids2, W_PITCH, H2)], W_PITCH, H2, bg="#FFFFFFFF")
    r2 = snapkit.render(dsl2, "gp-%02d.png" % (bi // BATCH), "gp-%02d.snapshot" % (bi // BATCH),
                        final=False, out_dir=PROBE)
    assert r2.get("ok"), (bi, r2.get("status"), r2.get("error", "")[:300])
    im2 = Image.open(r2["image"]).convert("RGB")
    yy = 10
    for kind, ch in batch:
        xmin, xmax = strip_scan(im2, yy, 66, W_PITCH)
        rec = inks.get(ch)
        if xmin is None or not rec:
            yy += ROW_H
            continue
        span = xmax - xmin + 1
        adv_px = (span - rec[0]) / 19.0
        result[ch]["advance_em"] = round(adv_px / SIZE, 5)
        result[ch]["bearing_ratio"] = round(rec[1] / SIZE, 5)
        yy += ROW_H
    print("batch", bi // BATCH, "ok", len(batch))

json.dump({"font_size": SIZE, "glyphs": result},
          open(os.path.join(PROBE, "glyphs.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)

lat = [result[c]["advance_em"] for c in LATIN if "advance_em" in result.get(c, {})]
cj = [result[c]["advance_em"] for c in CJK if "advance_em" in result.get(c, {})]
print("latin n=%d min %.4f max %.4f mean %.4f" % (len(lat), min(lat), max(lat), statistics.mean(lat)))
print("cjk   n=%d min %.4f max %.4f mean %.4f" % (len(cj), min(cj), max(cj), statistics.mean(cj)))
print("samples:", {c: result[c].get("advance_em") for c in " AiMw#|/.,"})
print("cjk samples:", {c: result[c].get("advance_em") for c in "画布尺定角"})
print("WARN", D.warnings())