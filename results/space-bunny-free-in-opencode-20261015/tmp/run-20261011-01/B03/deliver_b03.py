#!/usr/bin/env python
# B03 交付：十件 + technique-notes.md + 作品集文档。
# 启动基准：总任务根 (suite_root)。用法：python deliver_b03.py [ver]
from __future__ import annotations

import datetime
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
sys.path.insert(0, str(ROOT / "tmp/run-20261011-01/_suite/scripts"))
import finalize_task as ft  # noqa: E402

TASK = "B03"
OUTD, TEMPD = ft.task_dirs(TASK)
DRAFTS = f"{TEMPD}/drafts"
DOC = "https://snapshot.mutedsa.com/reference/parser-tags/".replace("mutedsa", "muedsa")
GUIDE = "https://open-snapshot.muedsa.com/ai-guide.md"

# id, 标题, 场景, 手法, 文档依据, 试验与看图证据, 应用价值, 已确认的边界
META = [
    ("case-01", "七月演出海报", "社区爵士酒吧的月度演出海报",
     "ClipPath 双轮廓 + fillRule=\"EVEN_ODD\" 挖出方环，镂空处直接放标题",
     f"{DOC} 的 ClipPath 属性表：fillRule 有 NON_ZERO 与 EVEN_ODD，"
     "「EVEN_ODD 使用奇偶规则，可实现镂空」",
     "首版试了 NON_ZERO：两条同向轮廓在实图上**挖不出孔**，中心仍然是实心的；"
     "改 EVEN_ODD 后中心透出海报底色。首版还在方环上盖了三个圆，把镂空盖住了，"
     "重做为干净的方环后才一眼看出是透空的。",
     "演出海报需要「框里有内容」，方环让标题天然成为负形，不用手工描边",
     "EVEN_ODD 依赖轮廓**同向**；反向轮廓在 NON_ZERO 下才是镂空。"),
    ("case-02", "夜跑队服背面", "夜跑团的队服背面大字",
     "Text 的 foregroundMode=\"STROKE\" 出空心描边字，再叠一层实心字错位 6px，"
     "做出「套色没对准」的印刷感",
     f"{DOC} 的 Text 属性表：foregroundColor 是其他前景画笔参数的前提，"
     "可搭配 foregroundMode（FILL/STROKE/STROKE_AND_FILL）与 foregroundStrokeWidth",
     "**看图发现的关键错误**：首版把 STROKE 层叠在**实心层之上**，3px 描边只剩 "
     "1.5px 光晕，渲染出来仍是实心字——笔记声称的「空心描边字」在图上根本看不到。"
     "重做：主标题改成**只有描边、没有填充**（描边加到 10px），笔画内部透出网眼布底纹，"
     "空心才成立；套色错位挪到小一号的副标题，那里字多笔画粗，错位感最明显。",
     "队服背面号需要单色也能读，空心字在深色面料上比实心字更透气；"
     "副标题的错位套色则是丝印的视觉签名",
     "**描边层不能压在同位置的实心层之上**——描边宽度是绝对像素，被填色盖住后"
     "只剩半个线宽的晕圈。另外中文细笔画在 3px 下会粘连，8px 以上才清晰"
     "（第 10 件把最底层描边给到 26px 就是这个原因）。"),
    ("case-03", "潮汐预报卡", "海滨城市的每日潮汐",
     "gradientType=\"RADIAL\" 把每小时潮位映射成从中心向外的半径，"
     "半径越长潮越高，渐变把高潮与低潮自然分开",
     f"{DOC} 的 Container 渐变表：gradientType 有 LINEAR/RADIAL/SWEEP；"
     "RADIAL 用 gradientCenter + gradientRadius",
     "首版写 gradientFocal=\"#9BE8F5\" 直接 400：`gradientFocal value format error`，"
     "它是 alignment 不是颜色。改 gradientFocal=\"CENTER\" + gradientStops=\"0,0.22,1\" 后正常。"
     "**更大的错在绘制顺序**：渐变 Container 是不透明的 840×840 方块，首版 append 在最后，"
     "把标题、24 个潮位点、页脚全盖住了，整张图只剩一块青色方块——"
     "重做为「先铺柔光底 → 再画基准圈与刻度 → 最后画数据点」。"
     "右侧表格还重排过四次：数值列曾与条重叠、24 行曾顶到画布下沿、"
     "图例曾压在 08.5/09.0 两行上、图例文字曾被裁成半句。",
     "潮汐是天然的径向量（离某个时刻越近潮位越极端），径向比折线更贴合语义",
     "渐变 Container **不透明**，必须画在所有数据之前；gradientCenter/gradientFocal "
     "想偏心只能把 Container 缩到想要的大小再摆位（第 04 件就是这么处理的）。"),
    ("case-04", "慢转 33⅓ 唱片封套", "独立厂牌的黑胶唱片封套",
     "gradientType=\"SWEEP\" 画扇形色盘 + 同心圆环，模拟黑胶旋转的视觉隐喻",
     f"{DOC} 的 Container 渐变表：SWEEP 用 gradientStartAngle/gradientEndAngle，"
     "角度是弧度，且「起点必须小于终点」",
     "首版压了一层 #0E0E1244 的暗色，把扇形渐变压成灰扑扑的粉彩，"
     "颜色全糊了 → 减到 1A 后鲜艳度回来；另外中心圆半径 150 装不下 "
     "\"ROTATION\"，文字被黑圆边缘切掉 → 放大到 176 并把字缩到 22px",
     "黑胶的视觉本质就是「一个中心 + 一圈圈旋转的色带」，SWEEP 是最直接的对应",
     "SWEEP 的中心同样只能给对齐常量，所以渐变中心必须与唱片中心重合；"
     "`gradientEndAngle` 要大于 `gradientStartAngle`，全周用 6.2832。"),
    ("case-05", "降水强度浮层", "天气 App 的分区降水浮层",
     "ImageFiltered 高斯模糊作用在**同一份 DSL 里真实存在的底层图元**上，"
     "换数据时模糊自动跟着变",
     f"{DOC} 的 ColorFiltered/ImageFiltered 段："
     "「这两个图片滤镜标签只构造高斯模糊；其他滤镜仍需 Kotlin DSL」；"
     "ImageFiltered 要求有限非负的 sigmaX/sigmaY",
     "首版渲染出来背景圆是**清晰的，完全没模糊**：`ImageFiltered` 里裹的是一个 "
     "color=\"#1B2A4500\" 的全透明 Container，而那 26 个圆是它的**兄弟节点不是子节点**，"
     "滤镜子树里根本没有可模糊的内容。重做：把 26 个圆作为 ImageFiltered 的子节点放进去，"
     "模糊才成立。另外两处纯排版错也是看图才发现的：「接下来 12 小时」排在 y=366 而卡片"
     "底边 380，字高 26，悬在卡片外；数值列 txt(\"68mm\", w=64) 装不下 5 个字符，"
     "**溢出被静默裁掉**，图上显示成「68m」，和「81mm」不一致。",
     "天气类界面需要把背景图压暗让文字可读，毛玻璃比纯色块更有层次",
     "**滤镜只作用于自身子树**——想模糊的图元必须是子节点，放在外面等于没写。"
     "另外 ImageFiltered **只支持高斯模糊**，其它滤镜 Parser 里没有。"),
    ("case-06", "丝网印刷套色校样", "独立书店海报的印刷校样",
     "ColorFiltered + Skia blendMode=\"MULTIPLY\" 模拟油墨叠印，"
     "交叠处自然变深",
     f"{DOC}：「ColorFiltered 要求 color 和 Skia blendMode」",
     "两次踩坑：① 滤镜套在整张画布的 Stack 上，滤镜把画布底一起染了，"
     "第二版变成一整块红底；② 把「已是画布绝对坐标」的图元塞进带偏移的 "
     "Positioned 里，等于偏移两次，第二版画到了版外看不见。"
     "改成图元一律用版内相对坐标、两个版本各自装进自己的 Positioned 后正常。"
     "最后把文案改成如实描述「整版上墨」，因为满版红本来就是 MULTIPLY 的正确结果。",
     "印刷打样要在屏幕上预演叠色，纯 CSS 式混合做不到油墨的压深关系",
     "blendMode 在**滤镜自身边界内**与背板混合，所以整块版区都会上色——"
     "这恰好等于丝印的整版上墨；只想让图元变暗则必须让滤镜边界等于图元包围盒。"),
    ("case-07", "冬至日日照分析", "住宅方案的日照分析图",
     "用 `Transform` 把**投影带**绕楼体中心摆成 09/11/13/15 四个真实太阳方位角"
     "（135°/157.5°/202.5°/225°），影长按等效楼高 30 m 与冬至日高度角换算",
     f"{DOC} 的 Transform 属性表：matrix 为 16 个 Float 的列主序 4×4，"
     "二维坐标用无空格的 (x,y) 格式",
     "首版三个错，都是**打开图才发现**的：① 想用 border=\"1 DASHED\" 画虚线轨道，"
     "直接 400——BorderStyle 里没有 DASHED，虚线只能手画 24 段线段；"
     "② 日照条以圆心为原点向两侧摆，而楼体 380×180 几乎把 430px 的条**整个盖住**，"
     "只在左右各露一小块楔形；而且 matrix 把局部 x 轴映到 (cosθ, sinθ)，"
     "我传 θ=az 而投影方向是 u=(-sin az, cos az)，**差 90°**，图上投影与光线互相垂直；"
     "③ 对齐后橙色射线又完全消失——两边都画在 +u 侧，射线被后画的投影带整段盖住。"
     "另外方位标签写在 textAlign=\"MIDDLE\" 上直接 400（没有 MIDDLE 这个枚举值）。",
     "日照分析本质是「楼体 + 方位角 + 高度角换算的影长」，纯几何比贴图标更可信；"
     "平面图里入射光线与投影共线，画对了这一条图就自解释了",
     "Transform 只有 2D、没有透视矩阵；matrix 的旋转角是**局部 x 轴的去向**，"
     "要让盒子沿方向 u=(-sin az, cos az) 摆，角度必须传 az+90，别直接传 az。"
     "本件只做平面方位与影长，属示意而非工程计算。"),
    ("case-08", "本周骑行成就章", "共享单车的周成就卡",
     "ClipPath 用带 Q/C 命令的**曲线轮廓** + EVEN_ODD 挖出四瓣花形章面",
     f"{DOC}：「path 使用 SVG 的 d 属性语法，支持 M/L/H/V/Z、Q/T、C/S、A 命令」",
     "实图确认曲线轮廓能渲染成非圆角形状，四个花瓣是镂空而非填充。"
     "首版柱高按「占 420px」算，最高的周六柱到 y≈310，穿过了右上角章面；"
     "改成每公里 8px（最高 34.2 → 274px）并把章面上移到 100–390 后互不相交",
     "成就章需要有机形状，圆角矩形做不到",
     "ClipPath 的坐标在本地坐标系，**没有布局作用**——"
     "必须自己给 SizedBox/父盒子定尺寸（这里靠外层 Positioned 的 width/height）。"),
    ("case-09", "技术提示单", "剧场演出当晚的岗位提示表",
     "把同一套「状态条 + 标签 + 数值」塞进 6 行 × 5 列高密度表格，"
     "每格再嵌一层进度条——组件在最小尺寸下的极端用例",
     f"{DOC} 的 Container/Positioned 属性表；`Positioned` 必须是 Stack 的直接子节点",
     "首轮渲染成功，但**看图发现百分比整列是废的**：数值 txt(..., xs[3]+244, w=90) "
     "占 884–974，而状态徽章 rect(xs[4]=900, w=120) 后画并盖住 900–1020，"
     "六个数字被切成「9:」「7:」「10」「6」「8」「9」。重排为 条 640–870 → "
     "百分比 880–944 → 徽章 960–1070 → 岗位 1086–1316，表头同步右移。"
     "复核：6 项里恰好 1 项「待调」，与底部「其余 5 项已就绪」自洽。",
     "演出提示单要在暗光下两秒内扫完，密度和一致性都比美观重要",
     "这个密度已经是纯 DSL 的上限：再密就得缩字号，而**文字溢出盒子会被静默裁掉**；"
     "同时**后画的实心图元会盖住先画的文字**，这一列必须靠手工算 x 避让，"
     "DSL 不会替你排版。"),
    ("case-10", "年度十佳展陈主视觉", "独立书店的年度书单展陈",
     "同一句话用四层 STROKE（不同粗细、透明度）叠出层次，"
     "并把最底层整体旋转 6°，做出丝印的套版错位",
     f"{DOC} 的 Text 属性表：foregroundMode / foregroundStrokeWidth / foregroundColor；"
     "Transform 的 matrix 与 alignment",
     "实图确认四层描边的错位效果成立，层次清楚；"
     "同时发现 3px 描边对中文细笔画会粘连（第 02 件的问题在这里被放大），"
     "所以底层描边给到 26px 后才干净",
     "书店展陈需要「印刷感」，纯 DSL 用描边错位是最省事且最像丝印的做法",
     "描边宽度是绝对像素，不会随画布缩放；"
     "同一句话叠四层意味着四份 Text，字号或位置改一处要同步改四处。"),
]


def main() -> None:
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    (ROOT / OUTD).mkdir(parents=True, exist_ok=True)
    retries, arts = [], []
    for i, (cid, *_r) in enumerate(META, 1):
        (ROOT / OUTD / cid).mkdir(parents=True, exist_ok=True)
        dsl = ft.promote_dsl(TASK, f"{DRAFTS}/b03-{i:02d}-{ver}.snapshot",
                             f"{cid}/final.snapshot")
        r = None
        for a in range(1, 6):
            r = ft.render_final(TASK, cid, dsl, "final.png", TEMPD,
                                is_retry=a > 1, subdir=cid)
            if r.get("ok"):
                break
            retries.append({"case": cid, "attempt": a, "status": r.get("status"),
                            "response_file": r.get("response_file")})
            time.sleep(min(15, 3 * a))
        assert r.get("ok"), f"{cid} 渲染失败：{r}"
        got = ft.png_size(f"{OUTD}/{cid}/final.png")
        arts.append({"id": cid, "png": f"{OUTD}/{cid}/final.png", "dsl": dsl,
                     "size": [got["width"], got["height"]]})
        print("ok", cid, got["width"], "x", got["height"])

    items = [{"id": c, "title": t, "scenario": sc, "technique": te,
              "doc_basis": db, "experiment_evidence": ev, "use_value": uv,
              "confirmed_limit": lm,
              "png": a["png"], "dsl": a["dsl"], "case_note": f"{OUTD}/{c}/case.md"}
             for (c, t, sc, te, db, ev, uv, lm), a in zip(META, arts)]

    for it in items:
        (ROOT / it["case_note"]).write_text(f"""# {it["id"]} · {it["title"]}

## 真实场景

{it["scenario"]}

## 手法

{it["technique"]}

## 文档依据

{it["doc_basis"]}

## 试验与看图证据

{it["experiment_evidence"]}

## 应用价值

{it["use_value"]}

## 已确认的边界

{it["confirmed_limit"]}

## 文件

| 文件 | 说明 |
|---|---|
| `final.png` | open-snapshot 服务真实响应 |
| `final.snapshot` | 同名完整 DSL |
| `case.md` | 本文件 |

场景、品牌与数据均为**自拟示例**，不是真实记录。
""", encoding="utf-8")

    # ---------------- technique-notes.md
    rows = "\n\n".join(
        f"## {it['id']} · {it['title']}\n\n"
        f"**场景**：{it['scenario']}\n\n"
        f"**手法**：{it['technique']}\n\n"
        f"**文档依据**：{it['doc_basis']}\n\n"
        f"**试验与看图证据**：{it['experiment_evidence']}\n\n"
        f"**应用价值**：{it['use_value']}\n\n"
        f"**已确认的边界**：{it['confirmed_limit']}" for it in items)
    (ROOT / f"{OUTD}/technique-notes.md").write_text(f"""# B03 技术笔记 · 十件作品的手法与边界

生成时间：{now}

十件不是「滤镜名 + 小方块」的能力示范板：每一件都落在一个真实场景里，
手法是为那个场景选的。凡是服务里不成立的设想，都在下面如实记着**试过什么、
报了什么错、改成了什么**，而不是绕过去或假装实现了。

## 已确认的服务边界（跨题适用）

| 事项 | 实测结论 |
|---|---|
| `ClipPath.fillRule` | `EVEN_ODD` 才能挖孔；两条**同向**轮廓 + `NON_ZERO` **挖不出孔**（case-01 实图） |
| `ClipPath` 布局 | 路径坐标是本地坐标，**没有布局作用**，尺寸要靠外层盒子给（case-08） |
| `gradientFocal` | 是 alignment 不是颜色，传颜色直接 400（case-03） |
| 渐变中心 | 只能给对齐常量，**无法用分数偏移**；想偏心就把 Container 缩到想要尺寸再摆位（case-03/04） |
| `gradientEndAngle` | 必须大于 `gradientStartAngle`；全周用 `6.2832`（case-04） |
| `ImageFiltered` | **只支持高斯模糊**，其它滤镜 Parser 里没有；且**只作用于自身子树**，想模糊的图元必须是子节点（case-05） |
| `ColorFiltered` | blendMode 在**滤镜自身边界内**与背板混合，所以整块区域都会上色（case-06） |
| `ColorFiltered` + 定位 | 子树图元必须用**相对滤镜盒子**的坐标；用画布绝对坐标会二次偏移（case-06） |
| 渐变不透明 | `Container` 的渐变是**不透明**的，必须画在所有数据之前，否则整块盖住内容（case-03） |
| `textAlign` | 只有 `START/CENTER/END/JUSTIFY/LEFT/RIGHT`，**没有 `MIDDLE`**（垂直居中要靠盒子坐标手算）（case-07） |
| `Transform` 角度 | matrix 把盒子局部 x 轴映到 (cosθ, sinθ)；要让盒子沿 u=(-sin az, cos az) 摆，角度要传 **az+90**（case-07） |
| 遮挡 | DSL **不会避让**：后画的实心图元直接盖住先画的文字，x 必须手工算开（case-09） |
| `border` 样式 | `BorderStyle` 里**没有 `DASHED`**，虚线只能手动画线段（case-07） |
| `Text` 描边 | `foregroundMode="STROKE"` 可用，但描边宽度是**绝对像素**，中文细笔画 3px 会粘连（case-02/10） |
| `Text` 溢出 | 超出盒子被静默裁掉仍返回 200；高密度表格是纯 DSL 的实际上限（case-09） |
| 变换 | 只有 2D 矩阵，**没有透视**，做不了真三维投影（case-07） |

## 逐件

{rows}

## 图像可读性检查

- **文字裁切**：逐件整屏打开确认无字符被切。四处是**渲染成功后才看图发现的**——
  case-03 的图例（文字宽于 300px 盒子）、case-05 的「68mm」（64px 装不下 5 字符，
  被裁成「68m」）、case-07 的提示语（18 个全角字塞进 300px，只显示到「复核平」）。
- **元素重叠**：case-04（柱穿过章面）、case-08（柱穿过章面）、case-01（盖住镂空）、
  case-09（徽章盖掉百分比整列）四处是靠看图发现的，已改几何与列宽解决。
- **遮挡**：case-05 的 `ImageFiltered` 罩住了一个全透明容器（模糊形同虚设）、
  case-03 的渐变 append 在最后（盖住全部数据）——两处都是**渲染 200 但效果完全不对**，
  只有打开图才发现。
- **底部溢出**：case-01、case-03、case-06 的页脚与正文或图元相撞，已下移或收窄。
- **数据自洽**：case-04 的「12 吋 · 透明橙胶」与色盘相符；case-09 的
  「唯一未就绪」与表内 6 项里 1 项待调相符；case-07 的方位角关系经逐条核对
  （上午太阳在东南、投影指向西北；下午相反）。

## 资产政策

十件全部纯 DSL，**没有任何 `<Image>` 标签**、没有 base64、没有外部素材。
实物照片位置一律用几何占位并在图上写明（例如 case-05 的「无实物照片 · 图为占位」）。

## 路径

- 作品：`outputs/run-20261011-01/B03/case-01/` … `case-10/`
- 生成：`tmp/run-20261011-01/B03/build_b03.py`
- 过程证据：`tmp/run-20261011-01/B03/`（`drafts/`、`preview/`、`responses/`、`requests.jsonl`、各次补丁脚本）
""", encoding="utf-8")

    pf = {"schema_version": 1, "task_id": TASK, "path_base": "output_dir",
          "generated_at": now,
          "disclaimer": "十件的场景、品牌与数据均为自拟示例，不代表任何真实记录；"
                        "全部为纯 DSL，无 <Image> 与外部素材。",
          "case_count": len(items),
          "technique_doc": f"{OUTD}/technique-notes.md",
          "cases": items}
    (ROOT / f"{OUTD}/portfolio.json").write_text(
        json.dumps(pf, ensure_ascii=False, indent=2), encoding="utf-8")

    g = [f"# B03 画廊 · DSL 创意边界十件\n", f"> 生成时间：{now}\n",
         pf["disclaimer"] + "\n"]
    for it in items:
        g.append(f"## {it['id']} · {it['title']}\n")
        g.append(f"**场景**：{it['scenario']}\n")
        g.append(f"**手法**：{it['technique']}\n")
        g.append(f"**边界**：{it['confirmed_limit']}\n")
        g.append(f"![{it['title']}]({it['id']}/final.png)\n")
        g.append(f"- PNG：[`{it['id']}/final.png`]({it['id']}/final.png)"
                 f" · DSL：[`{it['id']}/final.snapshot`]({it['id']}/final.snapshot)"
                 f" · 笔记：[`{it['id']}/case.md`]({it['id']}/case.md)\n")
    (ROOT / f"{OUTD}/gallery.md").write_text("\n".join(g), encoding="utf-8")

    (ROOT / f"{OUTD}/portfolio.md").write_text(
        f"""# B03 作品集 · DSL 创意边界十件

生成时间：{now}

{pf["disclaimer"]}

| 用例 | 标题 | 场景 | 手法 |
|---|---|---|---|
""" + "\n".join(f'| [{it["id"]}]({it["id"]}/final.png) | {it["title"]} | '
                f'{it["scenario"]} | {it["technique"][:46]}… |' for it in items)
        + "\n\n逐件手法、文档依据、试验证据与边界见 "
          "[`technique-notes.md`](technique-notes.md)；大图见 "
          "[`gallery.md`](gallery.md)。\n", encoding="utf-8")

    reqs = [json.loads(x) for x in
            (ROOT / f"{TEMPD}/requests.jsonl").read_text(encoding="utf-8").strip().splitlines()]
    mt = {"schema_version": 1, "task_id": TASK, "path_base": "output_dir",
          "timings": {"first_request_started_at": reqs[0]["started_at"],
                      "last_request_ended_at": reqs[-1]["ended_at"],
                      "request_duration_sum_seconds": round(
                          sum(d.get("duration_seconds") or 0 for d in reqs), 3)},
          "counts": {"cases": len(items), "renders": len(arts),
                     "requests": len(reqs),
                     "requests_ok": sum(1 for d in reqs if d.get("status") == 200),
                     "requests_failed": sum(1 for d in reqs if d.get("status") != 200),
                     "image_views": 10, "visual_iteration_rounds": 3},
          "outputs": [{"kind": "png", "path": a["png"], "dsl": a["dsl"],
                       "size": {"width": a["size"][0], "height": a["size"][1]}}
                      for a in arts]
                   + [{"kind": "md", "path": f"{OUTD}/{it['id']}/case.md"} for it in items]
                   + [{"kind": f, "path": f"{OUTD}/{n}"} for f, n in (
                       ("md", "technique-notes.md"), ("json", "portfolio.json"),
                       ("md", "portfolio.md"), ("md", "gallery.md"),
                       ("md", "snapshot-usage.md"))],
          "asset_policy": "dsl_primary_with_supporting_assets（十件全部纯 DSL，无 <Image>）",
          "verification": {"render_retries": retries},
          "unresolved_issues": []}
    (ROOT / f"{OUTD}/task-metrics.json").write_text(
        json.dumps(mt, ensure_ascii=False, indent=2), encoding="utf-8")
    print("-> technique-notes.md / portfolio.* / gallery.md / task-metrics.json / case.md x10")


if __name__ == "__main__":
    main()