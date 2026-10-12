"""B03 wrap-up review - fold the three re-render fixes into portfolio.{json,md} + gallery.html.

The wrap-up review opened all ten final.png files and found three real defects:
  case-01  the moon label ("亏凸月 · 照亮 72%") matched neither the drawn crescent
           nor the board's own timestamp -> phase is now computed from the
           timestamp and the terminator is filled by real geometry
  case-02  ticket B printed 合计 86 元 for lines summing to 62 元, and was
           labelled 外带/堂食 on a proof the sheet calls 取餐牌 B
  case-09  the summary claimed "没有引入新的破坏性变更…七项修复" while the
           changelog holds 2 BREAKING / 2 DEPRECATED / 3 ADDED / 5 FIXED
Sizes, element counts and PNG bytes are re-measured from the delivered files.
"""
import io

p = "build_portfolio.py"
s = io.open(p, encoding="utf-8").read()
n = 0


def rep(old, new):
    global s, n
    assert old in s, old[:80]
    s = s.replace(old, new, 1)
    n += 1


# ---- case-01 --------------------------------------------------------------
rep('basis="六个真实分潮调和数（M2/S2/N2/K1/O1/MS4）合成潮位，MSL 2.05 m；'
    '其余站位/风/浪/月相为自拟演示值"',
    'basis="六个真实分潮调和数（M2/S2/N2/K1/O1/MS4）合成潮位，MSL 2.05 m；'
    '月相由本页时间戳 2026-10-05 09:45 +08:00 的月球距角 D=285.0° 真实算出'
    '（k=(1−cos D)/2=37.0%，残月）；其余站位/风/浪/日出日落为自拟演示值"')

rep('intent="渐变承担编码：潮位柱「顶透明→底实」的高度、水深 8 级同一色相的 alpha、'
    '月面 focal 高光"',
    'intent="渐变承担编码：潮位柱「顶透明→底实」的高度、水深 8 级同一色相的 alpha、'
    '月面逐行 Lambert 明暗（晨昏线由 R(1−2k) 半椭圆解析填充，不是画一个偏移圆）"')

rep('review="crops/final-c01-tide.png、crops/final-c01-tidezoom.png"',
    'review="crops/final-c01-tide.png、crops/final-c01-tidezoom.png；'
    '收尾审查 crops/final-review-c01-moon.png（3.4×，发现月相标签与图形矛盾）'
    '与 crops/final-review2-c01-moon.png（3.0×，复验修好的残月）"')

rep('iters=["v001-case-01", "v002-case-01"],',
    'iters=["v001-case-01", "v002-case-01", "B03-wrapup-c01-moon"],')

rep('unresolved=["月相亮暗分界用一个偏移的 CIRCLE 近似真实晨昏线，几何不严格",\n'
    '                   "海面剖面 η(x) 是三个正弦的示意叠加，不是真实海浪谱"],',
    'unresolved=["月面的明暗是 Lambert 近似（b=s·n 后取 0.55 次幂），不是光度学渲染；'
    '三块月海是半透明圆片，边界是硬边",\n'
    '                   "潮位用六个分潮的固定调和常数合成，没有做气压/风致增水订正",\n'
    '                   "海面剖面 η(x) 是三个正弦的示意叠加，不是真实海浪谱"],')

# ---- case-02 --------------------------------------------------------------
rep('review="crops/（case-02 无需放大即全部可读；尺寸标注在 100% 下核对）"',
    'review="100% 下全表可读；收尾审查用 crops/final-review-c02-cardA.png / '
    'final-review-c02-cardB.png（2.6×）逐行核金额，'
    '发现 B 牌合计 86 元与三行 62 元不符；'
    'final-review2-c02-total.png（2.8×）复验 62 元"')

rep('iters=["v001-case-02", "v002-case-02", "v003-case-02", "v004-case-02"],',
    'iters=["v001-case-02", "v002-case-02", "v003-case-02", "v004-case-02",\n'
    '               "B03-wrapup-c02-total"],')

# ---- case-09 --------------------------------------------------------------
rep('review="crops/final-c09-mid.png（1.7× 核对代码块与装饰线）、'
    'crops/final-c09-deco.png（4× 核对四态装饰线）"',
    'review="crops/final-c09-mid.png（1.7× 核对代码块与装饰线）、'
    'crops/final-c09-deco.png（4× 核对四态装饰线）；收尾审查数了 12 枚 chip，'
    '发现摘要写「没有破坏性变更…七项修复」与列表矛盾，'
    'crops/final-review2-c09-summary.png（1.8×）复验改后的 2/2/3/5"')

rep('iters=["B03-v356+（正式渲染 5 版，见 iterations.jsonl）"],',
    'iters=["B03-v356+（正式渲染 5 版，见 iterations.jsonl）",\n'
    '               "B03-wrapup-c09-counts"],')

# ---- overall review note --------------------------------------------------
rep('"- 本轮整体审查新发现并修掉的问题：case-09 的矩阵末列越界、case-09 第 12 条"\n'
    '          "被摘要带盖住、case-10 剖面被压成 12 px、case-10 太阳光线压穿进深条标题、"\n'
    '          "case-10 月柱高算出负数（两处：漏 `degrees()`、下界设错）。",',
    '"- 制作期整体审查修掉的问题：case-09 的矩阵末列越界、case-09 第 12 条被摘要带盖住、"\n'
    '          "case-10 剖面被压成 12 px、case-10 太阳光线压穿进深条标题、"\n'
    '          "case-10 月柱高算出负数（两处：漏 `degrees()`、下界设错）。",\n'
    '          "- 收尾复审（把十张 `final.png` 逐张重新打开）新发现并修掉三处'
    '**图与字互相打脸**的问题：case-01 的月相标签写着「亏凸月 · 照亮 72%」而画面是'
    '一弯约 20% 的右侧蛾眉（且与本页时间戳的真实月相 37.0% 残月不符），'
    '已改为按时间戳计算相位、并用 R(1−2k) 半椭圆逐行填充晨昏线；"\n'
    '          "case-02 的 B 号取餐牌印「合计 86 元」而三行是 32+18+12=62 元，'
    '且票面写着「外带 TAKEAWAY / 堂食」与本稿自己的标题和尺寸表矛盾，'
    '已改为由明细求和并统一成取餐牌；"\n'
    '          "case-09 摘要写「没有引入新的破坏性变更，仅有两项弃用与七项修复」，'
    '而 12 条清单里就有 2 条 BREAKING、5 条 FIXED，已改为从清单实算 2/2/3/5。",\n'
    '          "- 复审也**排除**了三处疑似缺陷：case-02 左侧竖排「346 px」是旋转 -90° '
    '的正常尺寸标注（用 `rotcheck.py` 旋正后确认）；case-04 B 区 05 排左块里那条'
    '空心小格是刻意的「本排座位放大条」（选中 24 号），不是错位元素；"\n'
    '          "case-10 的「±9.45/±6.30/±3.15/±0.00」在 3.2× 下确认是 ± 不是 ≤/≥。",')

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("patched", n, "blocks")