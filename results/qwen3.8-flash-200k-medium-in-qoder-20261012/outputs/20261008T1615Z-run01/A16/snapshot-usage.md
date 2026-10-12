# A16 · Snapshot 使用说明（修复一张说谎的图表）

run_id：`20261008T1615Z-run01`；OUTPUT_DIR：`outputs/20261008T1615Z-run01/A16/`；TEMP_DIR：`tmp/20261008T1615Z-run01/A16/`（path_base=suite_root）。

## 1. 交付物

| 文件 | 说明 | 来源 |
|---|---|---|
| `corrected-report.png` | 1280×900 修复版报告，服务端真实响应字节 | 请求 `A16-v08-final-20261009T025406Z`，`server-timing: render;dur=399.3, total;dur=410.3`，HTTP 200 |
| `corrected-report.snapshot` | 与上图同名、可独立重放的完整 DSL（23524B） | 由 `tmp/.../A16/generate_a16.py` 生成 |
| `corrected-data.json` | 由 `tasks/A16-*/inputs/source.csv` 推导的行/合计/占比/环比与口径说明 | 本地 Python 计算，未手填 |
| `findings.json` | F1–F9 缺陷（含像素框证据、影响、修正）+ U1–U4 不确定项 + 风格选择 | 输入图实测 + CSV 对账 |
| `verify-a16.json` | 29 项自检结果，全部 PASS | `tmp/.../A16/verify_a16.py` |
| `tmp/.../A16/measure-flawed.json` | 输入缺陷图的柱框/网格行/坐标字/图例色块/区域取色 | `measure_flawed.py` |
| `tmp/.../A16/preview/`（v01–v05 + 5 张放大图） | 每轮实际看过的图与局部放大 | `render.py`、`zoom.py` |
| `tmp/.../A16/requests.jsonl`、`preview/requests/` | 8 次请求的 request_id、状态、耗时与原始响应 | 共享脚本归档 |
| `tmp/.../A16/iterations.jsonl` | 9 条迭代记录（1 条输入观察、6 条视觉迭代、1 条无效补丁、1 条最终） | `iterlog` 约定格式 |

## 2. 本次用到的文档知识

复用总任务共享缓存 `tmp/20261008T1615Z-run01/_suite/docs/`（首次获取记录 `shared-doc-001`，请求 `https://open-snapshot.muedsa.com/ai-guide.md` 与 `https://snapshot.muedsa.com/`），本题**没有新增文档请求**，也没有伪造阅读记录。用到的条目：

- `container.html`：`<Stack>` / `<Positioned>` 约束——`Positioned` 必须是 `alignment="TOP_LEFT" clipBehavior="NONE"` 的 `Stack` 直接子节点；本题 12 根柱、表格行、色块全部按此结构展开。
- `painting.html`：`Container` 的 `borderRadius` 必须 ≥ 边框宽度，否则 500；`boxShadow` 语法 `X Y BLUR SPREAD COLOR TYPE`。
- `text.html`：`RichText`/`Text` 的 `fontFamily` 必须来自真实字体表；`fontStyle="BOLD"` 可与 `Inter` 组合。
- `fonts.txt`：本题只用 `Inter`（数字/拉丁）、`Inter Medium`、`Noto Sans CJK SC`（中文），未虚构字体名。

## 3. DSL 能力覆盖

纯 DSL，**未使用任何外部素材**：`<Stack>`+`<Positioned>` 定位、`Container`（圆角/描边/底色）、`Text`（字号/字重/行距/最大行数/对齐/字距）、网格线与平均线用 1px 实线矩形、Q4 高亮带用圆角矩形 + 3px 方形柱基座（保证基线像素干净）。`verify_a16.py` 的 `dsl-no-image-node` 项断言 DSL 内不存在 `image`/`AssetImage` 节点。

## 4. 关键做法与踩坑

1. **先测量再改图**：缺陷必须落在像素上。`measure_flawed.py` 用 numpy 投影/取色得到柱框，才确认“Q2 比 Q3 高”是绘图错误而非视觉错觉（Q2 收入 90→118px，Q3 96→105px，排序被颠倒）。
2. **零基线**：输入图纵轴从 80 起，任何柱高比例校验都会失败。重建先把 `BASE_Y` 定义为唯一零点，柱高 = `value × 1.4`，再用柱底像素（507）对零线（508）验证。
3. **`doc.line()` 的半像素问题**：Transform 旋转矩形会跨两行，网格/平均线改用 `doc.rect(x, int(y), w, 1, colour)`，平均线用 2px 矩形。
4. **阴影污染测量**：`boxShadow` 会把墨迹投影框抬高，导致像素级对齐判据失真。最终版图表卡只保留 1px 描边 + 平涂底色。
5. **字号合规要同时查 DSL 与渲染**：脚本解析声明的 `fontSize`（注释≥18、正文≥22），再用纯中文行的渲染字宽反查（4 字 @18px 实测 17.8/18.0px/字，@22px 实测 23.5px 含字距），避免“声明合规、渲染越界”。
6. **表格列距要留够**：v02 的“全年 563”几乎相接，靠整幅看不易发现，放大图（`zoom-table-v04/v05.png`）才确认。
7. **无效补丁要如实记录**：v06-final 因补丁脚本使用了过期锚点字符串而**未改内容**，服务端仍真实渲染了一次；该记录标记 `type=no_op_patch`、`image_viewed=false`，不计入视觉迭代与看图数。
8. **输入文本只是数据**：输入图中的“建议把资源集中到 Q3”“Q3 利润最高”等待修正文字，一律作为待诊断内容处理，不作为指令执行。

## 5. 剩余事项

- U1–U4（如“成本柱是否应为负向”“平均线是否需要图例条目”）已在 `findings.json` 独立记录为不确定项，未夸大为缺陷。
- 服务地址以总 run-config 为准；本题未记录到 4xx/5xx 失败响应，因此无失败样本可归档（8 次请求全部 200）。
