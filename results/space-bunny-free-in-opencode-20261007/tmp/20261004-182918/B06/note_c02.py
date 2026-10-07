# -*- coding: utf-8 -*-
"""Append case-02's real visual-iteration records."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run as R  # noqa: E402

P = os.path.join(R.TMP, "preview", "case.png")
V = "2026-10-05T%s+08:00"

R.note("case-02", "v01", "none", "syntax-fix",
       os.path.join(R.DRAFTS, "case-02-v001.snapshot"), None, None,
       "首次提交即被服务拒绝：400 PARSE_ERROR `Unexpected character '\\n' ... near <Positioned`。"
       "定位方式：报错位置 36067 落在主图的第一根柱子上。根因是本库 K.dashed() 返回的是"
       "多行字符串（多个并列 Positioned），我用了 `kids += K.dashed(...)`，等价于把字符串按字符"
       "拆进子节点列表，于是 DSL 里出现了 `<` `P` `o` `s` ... 逐字符的非法标签。"
       "同时脚本打印出 ccross=1，暴露第二个错误：我把『累计利息反超累计本金』当作交叉点，"
       "而等额本息第 1 期利息 8020 元就大于本金 3700 元，条件从第 1 期起永远成立。",
       "两处 `kids += K.dashed(...)` 改为 `kids.append(...)`；交叉点改为『累计本金首次超过累计利息』"
       "（计算得到第 270 期 / 22.5 年）。请求失败响应已保留在 tmp/B06/responses/resp-B06-req-007-*.txt",
       False)

R.note("case-02", "v02", "v01", "visual",
       os.path.join(R.DRAFTS, "case-02-v002.snapshot"), P, V % "21:05",
       "修复语法后出图，1800x1268，1590 元素，0 warnings。主图 120 列堆叠柱结构成立，"
       "但看到 5 处问题：(1)『本金』用了 mix(琥珀,黑,0.62) 得到 #4E2E1D，和棕黄叠在一起像一整块泥；"
       "(2) 50% 白色虚线上的说明文字用深灰，压在深色柱面上完全看不见；"
       "(3) 累计板块两条半透明面积互相叠加成一整片土黄，看不出哪条是哪条；"
       "(4) 决策卡三行里大数字（26px）和它下方 13px 的注解重叠；"
       "(5)『等额本金』那行与分隔线、上一行重叠，而且『每月递减』被我先 round 再格式化，显示成 22.00。",
       "本金改用 #0F766E 深青，与利息 #F59E0B 形成冷暖对比；50% 说明移进图例；"
       "累计板块改为与主图同构的堆叠柱（柱高=已付总额，内部拆本金/利息）；"
       "决策卡行高 58->66、大数字与注解分开两行、等额本金独立成段；递减额不再预先 round",
       False)

R.note("case-02", "v03", "v02", "visual",
       os.path.join(R.DRAFTS, "case-02-v003.snapshot"), P, V % "21:14",
       "第三版：主图本金/利息双色分明，『本金过半·第 12.1 年』做成白底胶囊压在琥珀区上，"
       "图例补了 50% 虚线说明。1.6 倍放大 crops/case-chk02-cum.png 检查累计板块，"
       "确认交叉点胶囊完整落在面板内、基线虚线不再压住下方两行说明文字。"
       "1.8 倍 crops/case-chk02-epi.png 核对决策卡末行数字。",
       "交叉点胶囊从标记线右侧改到左侧（原来 x=633+8 起、宽 216，末端 857 超出面板右缘 856）；"
       "累计图高度 196->178，把底部两行说明让开基线虚线", True)