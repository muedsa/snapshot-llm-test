#!/usr/bin/env python
"""B03 case-07 · 社区周报内页（编辑排版稿）。

场景（自拟）：街道社区报的排版稿，A3 竖版随报付印；读者手持约 40 cm 阅读。
独占手法：**两端对齐（textAlign="JUSTIFY"）+ 首字下沉 + REPEAT 渐变做花饰条 +
          Serif CJK 正文**。两端对齐交给服务端做（自己排行会丢掉对齐），
          所以只用它跑一段连续文字；首字下沉靠"前三行让出字宽"实现。
"""
from __future__ import annotations

from b03kit import (assert_fits, em_width, footer, gbox, guard, line_h, para, rect,
                    solid, stripes, tnum, txt, wrap, MONO, W500, W600, W400, SERIF,
                    BLACK, XBOLD, DISCLAIM)
from bsnap import (BG, DIM, INK, LINE, PANEL, SERIES, SUB, canvas, rect as R2)

W, H = 1240, 1754

PAPER, PAPER2 = "#F7F3EA", "#EFE9DB"
INK_D, INK_M, INK_L = "#1E222A", "#555C68", "#8C9199"
RULE = "#C9C0AC"
ACCENT = "#B03A2E"
SER = "Noto Serif CJK SC,Noto Serif"

M0 = 78
CW = W - 2 * M0          # 1084
COLW = (CW - 36) / 2     # 两栏各 524

TITLE = ["老旧小区加装电梯：三户人家", "卡在同一层"]
LEAD = ("加装电梯的公示贴了二十一天，八楼那户始终没来签字。三层有两户常年不住，"
        "五楼的租户换了三回。按规定这栋楼过不了，可四号楼去年就装成了。")
BODY1 = ("李阿姨在楼道里数过：三层 302 和 305 常年空着，五楼租户换过三回。"
         "居委会的台账里，八楼 802 的户主信息停在两年前的户籍地址。"
         "她说不是不愿意签，是「不知道该找谁签」——开发商、物业、居委会，"
         "三家都说要看另外两家的意见。")
BODY2 = ("争议的焦点其实不在钱。一楼住户担心采光与井道噪音，二楼担心电梯井"
         "贴到自家卧室墙上，七楼王先生提出按楼层分摊、越高分摊越少。"
         "街道办给出的方案是按建筑面积均摊，并对一二层每户补贴两千元。"
         "公示期只剩五个工作日，谁来签字仍然是问题。")

CLAIMS = [("违停占道", 38), ("噪声扰民", 24), ("漏水与供暖", 17),
          ("垃圾分类", 11), ("电梯加装", 6), ("其他", 4)]
NOTES = [
    ("本周提醒", "12 月 1 日起旧楼加装电梯咨询窗口迁至社区党群服务中心二楼，不再接受电话登记。"),
    ("供暖缴费", "南片 46 个小区本周六开始缴费，可用二维码或到社区代收点，不收现金。"),
    ("旧物回收", "下周三上午 9:00–11:30 在三号楼架空层设点，家电与图书分开回收。"),
]
COLORS = ["#B03A2E", "#C97A2B", "#5E7A9E", "#6E8F6A", "#8A6FA0", "#9A9484"]


def dropcap_lines(text, size, width, cap_lines, cap_w):
    """首字下沉：前 cap_lines 行让出 cap_w 的宽度。"""
    lines, cur, curw = [], "", 0.0
    n = 0
    limit = width - cap_w
    for ch in text:
        w = em_width(ch, size)
        if cur and curw + w > limit:
            lines.append(cur)
            n += 1
            cur, curw = "", 0.0
            limit = width - cap_w if n < cap_lines else width
        cur += ch
        curw += w
    if cur:
        lines.append(cur)
    return lines


def justify_spacing(line, size, target, max_gap=3.2):
    """中文行的「微调字距」：算出把这一行撑到 target 需要的 letterSpacing。

    服务端只能对整段做两端对齐；手动排版的行要齐尾，只能逐行微调字距
    （中文排版的常规做法）。字距超过 max_gap 说明这一行太短，不该硬撑。
    """
    n = len(line)
    if n < 2:
        return None
    s = (target - em_width(line, size)) / (n - 1)
    return s if 0 < s <= max_gap else None


def rule_line(y, double=False):
    out = R2(M0, y, CW, 2, RULE, 0)
    if double:
        out += R2(M0, y + 6, CW, 1, RULE, 0)
    return out


def build() -> str:
    b = []
    b.append(gbox(0, 0, W, H, [PAPER, "#F2ECDF"], stops="0,1",
                  begin="TOP_LEFT", end="BOTTOM_RIGHT"))
    # 纸边压线
    b.append(R2(M0 - 22, 0, 1, H, "#E4DCCB"))
    b.append(R2(W - M0 + 21, 0, 1, H, "#E4DCCB"))

    # ---------------- 报头
    b.append(txt("城南街道 · 社区报", M0, 56, 600, None, 18, ACCENT, W600))
    b.append(txt("第 214 期", W - M0 - 200, 56, 200, None, 18, INK_M, W600,
                 align="END"))
    assert_fits("城南周报", 78, CW, "报头")
    b.append(txt("城南周报", M0, 86, CW, 112, 78, INK_D, W600, family=SER))
    b.append(txt("2026 年 11 月 14 日 · 星期五 · 第 4 版 · 自拟样张", M0, 202, CW,
                 None, 19, INK_M))
    b.append(rule_line(236, True))

    # 花饰条：REPEAT 平铺渐变（报纸栏间的传统装饰带）
    b.append(stripes(M0, 256, CW, 12, ACCENT, PAPER, axis="VERTICAL", tile="REPEAT",
                     stops="0,0.42,0.58,1"))

    # ---------------- 头条
    b.append(txt("社区治理", M0, 292, 200, None, 19, "#FFFFFF", W600))
    b.append(R2(M0, 288, 108, 30, ACCENT, 0))
    b.append(txt("社区治理", M0 + 14, 292, 200, None, 19, "#FFFFFF", W600))
    for i, ln in enumerate(TITLE):
        assert_fits(ln, 44, CW, ln)
        b.append(txt(ln, M0, 336 + i * 62, CW, None, 44, INK_D, W600, family=SER))

    # 导语（两行，左侧一条竖线）
    ly = 472
    b.append(R2(M0, ly - 6, 4, 78, ACCENT, 0))
    yy = para(b, LEAD, M0 + 20, ly, CW - 20, 21, INK_M, W500, gap=6)
    b.append(txt("■ 本版责编 林可 · 版面 A4", W - M0 - 260, yy + 6, 260, None, 16,
                 INK_L, align="END"))

    # ---------------- 两栏正文（左栏首字下沉 + 逐行微调字距齐尾，右栏服务端两端对齐）
    by = yy + 40
    lh = int(19 * 1.52)
    cap_lines = 3
    cap_size = cap_lines * lh - 4
    cap_w = 80
    l1 = dropcap_lines(BODY1, 19, COLW, cap_lines, cap_w)
    l2 = wrap(BODY2, 19, COLW)

    h_left = len(l1) * lh + 8
    h_right = len(l2) * lh + 8
    assert abs(len(l1) - len(l2)) <= 1, f"两栏行数差过大：{len(l1)} vs {len(l2)}"

    # 左栏：首字 + 逐行撑到目标宽度
    b.append(txt(BODY1[0], M0, by - 6, cap_w, cap_size + 8, cap_size, ACCENT,
                 W600, family=SER))
    cur_y = by
    for i, ln in enumerate(l1):
        target = (COLW - cap_w) if i < cap_lines else COLW
        sp = justify_spacing(ln, 19, target)
        spx = f' letterSpacing="{sp:.2f}"' if sp else ""
        fam = SER
        q = f'<Positioned left="{M0 + cap_w}" top="{cur_y}" width="{COLW - cap_w}" '
        q += f'height="{lh}"><Text{spx} fontSize="19" color="{INK_D}" '
        q += f'fontFamily="{fam}">{ln}</Text></Positioned>'
        b.append(q)
        cur_y += lh

    # 右栏：整段交给服务端做两端对齐
    b.append(f'<Positioned left="{M0 + COLW + 36:.0f}" top="{by}" width="{COLW:.0f}" '
             f'height="{h_right:.0f}">'
             f'<Text textAlign="JUSTIFY" softWrap="true" fontSize="19" color="{INK_D}" '
             f'fontFamily="{SER}">{BODY2}</Text></Positioned>')
    # 两栏之间的栏间线
    b.append(R2(M0 + COLW + 17, by, 1, max(h_left, h_right) - 6, "#DED6C4"))
    guard(by + max(h_left, h_right) + 10, 0, 1120, "两栏正文")

    # ---------------- 数据图
    dy = by + max(h_left, h_right) + 40
    b.append(rule_line(dy))
    b.append(txt("本月 12345 诉求分布", M0, dy + 18, 600, None, 24, INK_D, W600,
                 family=SER))
    b.append(txt("单位：件 · 近 30 天累计 100 件 · 自拟统计", W - M0 - 400, dy + 24,
                 400, None, 17, INK_L, align="END"))
    row_y = dy + 60
    maxv = max(v for _, v in CLAIMS)
    bar_x, bar_w = M0 + 150, CW - 150 - 190
    for i, (name, v) in enumerate(CLAIMS):
        col = COLORS[i]
        b.append(txt(name, M0, row_y + 2, 140, None, 19, INK_D, W500))
        b.append(R2(bar_x, row_y + 4, bar_w, 18, "#E6DFCE", 3))
        b.append(gbox(bar_x, row_y + 4, max(4, bar_w * v / maxv), 18, [col, col],
                      radius=3))
        b.append(tnum(f"{v}", bar_x + bar_w + 24, row_y, 60, None, 22, INK_D, MONO,
                      align="END"))
        b.append(txt("%", bar_x + bar_w + 86, row_y + 3, 40, None, 17, INK_L))
        row_y += 44
    guard(row_y + 10, 0, H - 80, "数据图")

    # ---------------- 编者的话（用 REPEAT 渐变做底纹）
    ey = row_y + 20
    b.append(gbox(M0, ey, CW, 150, ["#F1EAD9", "#EAE2CE"], radius=0, stops="0,1",
                  begin="TOP_LEFT", end="BOTTOM_RIGHT"))
    b.append(stripes(M0, ey, 14, 150, ACCENT, "#F1EAD9", axis="HORIZONTAL",
                     tile="REPEAT", stops="0,0.44,0.56,1"))
    b.append(txt("编者的话", M0 + 40, ey + 20, 300, None, 22, ACCENT, W600,
                 family=SER))
    para(b, "这一期我们把版面留给一件事：三户人家和一部电梯。"
            "愿不愿意装是技术问题，愿不愿意一起谈是社区问题。"
            "下期我们继续盯这件事的进展。",
         M0 + 40, ey + 58, CW - 80, 19, INK_M, W400, gap=5)
    b.append(txt("—— 城南周报编辑部", W - M0 - 240, ey + 118, 240, None, 17, INK_L,
                 align="END"))

    # ---------------- 本周提醒
    ny = ey + 180
    b.append(rule_line(ny))
    b.append(txt("本周提醒", M0, ny + 18, 400, None, 24, INK_D, W600, family=SER))
    cw3 = (CW - 2 * 24) / 3
    for i, (t1, t2) in enumerate(NOTES):
        x = M0 + i * (cw3 + 24)
        b.append(R2(x, ny + 58, cw3, 4, COLORS[i], 0))
        b.append(txt(t1, x, ny + 72, cw3, None, 21, INK_D, W600, family=SER))
        para(b, t2, x, ny + 106, cw3, 18, INK_M, W400, gap=5)
    guard(ny + 220, 0, H - 90, "本周提醒")

    # ---------------- 编辑部（填掉页脚上的空白，同时给读者一个落点）
    my = ny + 216
    b.append(rule_line(my))
    b.append(txt("编辑部", M0, my + 18, 300, None, 24, INK_D, W600, family=SER))
    STAFF = [("主编", "林 可"), ("责任编辑", "周 牧"), ("数据", "社区服务中心"),
             ("印刷", "城南印务")]
    cw4 = (CW - 3 * 20) / 4
    for i, (role, who) in enumerate(STAFF):
        x = M0 + i * (cw4 + 20)
        b.append(txt(role, x, my + 62, cw4, None, 17, INK_L))
        b.append(txt(who, x, my + 84, cw4, None, 21, INK_D, W600, family=SER))
    b.append(txt("读者来信请寄社区党群服务中心宣传栏，或在每周三下午的值班时段当面反映。",
                 M0, my + 128, CW, None, 18, INK_M, W400))
    guard(my + 160, 0, H - 70, "编辑部")

    # ---------------- 报尾
    footer(b, M0, H - 76, CW,
           "城南周报、社区、数据与联系方式均为自拟样张，非真实出版物 · " + DISCLAIM)
    guard(H - 20, 0, H, "页脚")
    return canvas(W, H, "".join(b), bg=PAPER)


def case_note(size) -> str:
    return f"""# case-07 · 社区周报内页（编辑排版稿）

## 用户情境

- **受众**：社区居民（纸质报，手持约 40 cm 阅读），以及街道宣传干事。
- **什么时候用**：随报付印的 A3 竖版内页；干事拿排版稿和印刷厂对版。
- **真正要回答的问题**：这周社区里发生了什么？我要办的事什么时候、去哪办？
- **领域**：社区传播 / 编辑排版

## 这件独有的视觉决定

这件的重点是**排版手艺本身**，手法直接对应印刷惯例：

1. **两端对齐交给服务端**：右栏整段正文写成一个 `Text`，用
   `textAlign="JUSTIFY" softWrap="true"`。自己按字宽排行会把对齐丢掉，
   所以只有连续文字才交给服务端断行；左栏因为要首字下沉，改为自己排行。
2. **首字下沉**：前 3 行按 `宽度 − 字宽` 排（`dropcap_lines`），第 4 行起恢复整宽，
   于是那个字自然占住三行高——不需要任何"合并行"的能力。
3. **花饰条用 REPEAT 渐变**：把渐变轴缩到半宽，`gradientTileMode="REPEAT"`
   就得到两条干净的斜纹带，用在报头下方和编者的话左侧边。
4. 正文与标题用 `Noto Serif CJK SC`，数字用 `fontFeatures="tnum"` 的等宽字，
   保证 6 条数据的百分比小数点对齐。

- 画布 {W}×{H}（A3 竖版）；正文 18–19px，标题 44px，报头 78px。

## 数据的可信度

报纸、社区、事件、诉求统计与时间**全部自拟**，这份样张不代表任何真实出版物。

## 实际自检

见 `tmp/run-20261011-01/B03/iterations.jsonl` 中 case-07 的记录。

## 素材情况

纯 DSL，无 `<Image>`，无外部素材。

## 文件

| 文件 | 说明 |
|---|---|
| `final.png` | {size['width']}×{size['height']}，open-snapshot 服务真实响应 |
| `final.snapshot` | 同名完整 DSL 源码 |
| `case.md` | 本文件 |

{DISCLAIM}
"""