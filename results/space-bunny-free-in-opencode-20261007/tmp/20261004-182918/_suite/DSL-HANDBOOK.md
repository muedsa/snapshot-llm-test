# Snapshot DSL 工程手册（本题库实测结论）

本文件是 A01–A05 实际渲染过程中**用真实服务响应和实际看图**积累下来的结论。后续任务请直接照此执行，
不要重复踩坑。所有结论要么来自 `https://snapshot.muedsa.com/` 的官方文档，要么来自本题库自己的失败响应。

## 0. 服务

- 基地址：`https://open-snapshot.muedsa.com`（`run-config.json` 的 `service_base_url`）。
- `POST /snapshot`，请求体是 **UTF-8 纯文本 DSL**（不是 JSON），响应体是图片字节。
- **必须带浏览器 User-Agent**，否则 Cloudflare 会返回 `403 error code: 1010`：
  `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36`
- 画布尺寸由**布局**决定，不由 `<Snapshot>` 决定。永远用唯一的根 `<Container width= height=>` 定尺寸。
- 颜色支持 CSS 写法：`#RGB` / `#RGBA` / `#RRGGBB` / `#RRGGBBAA` / `rgb()` / `hsl()` / 命名色。
  **8 位十六进制按 CSS 读 `#RRGGBBAA`**（旧版 `#AARRGGBB` 读法已不适用）。要 20% 白就写 `#FFFFFF33`。
- 画布尺寸不设上限的硬编码，但元素个数和嵌套深度受服务端限制；一次请求体别太大。

## 1. 可用字体（来自真实的 `GET /fonts`）

```
Inter, Inter Black, Inter Extra Bold, Inter Extra Light, Inter Light, Inter Medium,
Inter Semi Bold, Inter Thin, Noto Sans CJK JP/KR/SC/TC/HK, Noto Sans Mono CJK …,
Noto Serif CJK JP/KR/SC/TC/HK, DejaVu Sans, DejaVu Sans Mono, DejaVu Serif, Noto Color Emoji
```

- 拉丁 + 中文混排：`fontFamily="Inter,Noto Sans CJK SC"`（Inter 优先，缺字自动回退）。
- 全中文：`fontFamily="Noto Sans CJK SC"`。等宽：`DejaVu Sans Mono`。衬线：`DejaVu Serif,Noto Serif CJK SC`。
- **不要臆造字体名**。

## 2. 会让服务报错的写法（务必避免）

| 写法 | 结果 |
|---|---|
| `<Positioned ... />` 空标签 | `400 RENDER_ERROR: ProxyWidget has no widget, can not create render box` |
| `<Positioned>` 放在 `Row`/`Column`/`Transform`/普通容器里 | `400 RENDER_ERROR: renderBox.parentData must be StackParentData`（`Positioned` 只能是 `Stack`/`IndexedStack` 的直接子节点） |
| `<Positioned>` 里塞多个子节点 | `400 PARSE_ERROR: Tag Positioned only can have one child` |
| `<Transform>` 不给 `matrix` | `400 PARSE_ERROR: Attr [matrix] must not be null`（没有 `rotate` 属性，旋转要自己算列主序 4×4） |
| `padding="24 32"` | `400 PARSE_ERROR: Attr [padding] value format error`（EdgeInsets 只接受 `"12"`、`"(8,16)"`、`"(8,12,16,20)"`） |
| `border="2 DASHED #fff"` | `400 PARSE_ERROR: No enum constant BorderStyle.DASHED`（`BorderStyle` 只有 `NONE`/`SOLID`） |
| 8 位 hex 写错位数（如 `#38BDF866FF`） | `400 PARSE_ERROR: Attr [border] color must be #RGB, #RGBA, #RRGGBB or #RRGGBBAA` |
| `Text` 同时给 `height` 和 `maxLines`，而 height < 换行后实际行高 | **不报错，但整段文字完全不渲染** |
| 根节点不是单个 widget / 布局尺寸无穷 | `400 RENDER_ERROR: Layout size is infinite` |

## 3. 静默行为（不报错，但结果不对）

- **未知属性被直接忽略**。例如 `<Snapshot width="1280" height="800">` 完全无效（探针实测：请求 1280×800，出图 400×200）；
  `<Text font-size="44">` 也完全无效（正确拼写是 `fontSize`）。**凡是"看起来没生效"的地方都要用一张对照探针图去证明。**
- **`Text` 在单行高度框里放不下时会静默丢弃溢出部分**，不会换行、不会报错。
  所以固定宽度的文本框必须留够宽度；共享库里 `dsllib.est_width()` 会估算行数并告警。

## 4. 推荐写法：全绝对定位

整屏用一个 `Stack fit="EXPAND"`，每个元素都是 `Positioned` 给出精确 `left/top/width/height`。
好处：DSL 里的坐标 = 脚本算出的坐标，不会有 Flex 隐式分配的意外；几何可复核。

```xml
<Snapshot type="png" background="#0F172AFF">
  <Container width="1600" height="1000">
    <Stack fit="EXPAND">
      <Positioned left="40" top="20" width="300" height="40">
        <Text fontSize="22" color="#0F172AFF" text="标题"/>
      </Positioned>
      <Positioned left="40" top="80" width="200" height="60">
        <Container color="#2563EBFF" borderRadius="12"/>
      </Positioned>
    </Stack>
  </Container>
</Snapshot>
```

要点：
- 矩形永远是 `Positioned > Container(...)`，**不要用空的 `Positioned`**。
- 圆角：`borderRadius="12"` 或四角 `borderRadiusTopLeft` 等；斜角用 `"0"`。
- 阴影：`boxShadow="0 2 10 0 #0F172A0F"` 或 `boxShadow="ELEVATION_4"`。
- 渐变：`gradientType="LINEAR|RADIAL|SWEEP"` + `gradientColors` + 可选 `gradientStops`/`gradientBegin`/`gradientEnd`。
- 虚线：DSL 没有虚线边框，用一串短矩形拼接（`dsllib.dashed()`）。
- 折线：没有画线图元，用沿两点连线铺一串短矩形（`dsllib` 里 A01/A04/A05 都这么做）。
- 面积填充：`dsllib.polygon()` 逐扫描行铺矩形。
- 只模糊背景而文字清晰：`ClipRRect > Container > Stack`，第一个 `Positioned` 里放
  `BackdropFilter sigmaX sigmaY` + 半透明底板，第二个 `Positioned` 里放未模糊的文字。
  （`ImageFiltered` 会模糊整棵子树，文字会跟着糊。）
- 旋转：`Transform matrix="(a,b,0,0,c,d,0,0,0,0,1,0,0,0,0,1)" origin="(0,0)" alignment="CENTER"`。
  屏幕坐标 y 向下，**逆时针 θ**：`a=cosθ, b=-sinθ, c=sinθ, d=cosθ`。例：逆时针 8° →
  `(0.990268,-0.139173,0,0,0.139173,0.990268,0,0,0,0,1,0,0,0,0,1)`。

## 5. 文本纵向位置的经验值

`text_el(x, y, …)` 里的 `y` 是**文本框顶边**。实测字形大约落在 `[y+3, y+3+1.05×fontSize]`。
所以同一行的多个文本、以及"圆角矩形里居中的文字"，要按 `y + (h - fontSize*1.2)/2` 之类换算，别想当然。

## 6. 共享工具（务必复用，不要重写）

`tmp/20261004-182918/_suite/` 下：

| 文件 | 用途 |
|---|---|
| `snapkit.py` | `configure(task, out, tmp)` → `render(dsl, name, dsl_name, final=, out_dir=)`，自动写 DSL、落图、记 `requests.jsonl`；`new_version()` 记 `iterations.jsonl`；`fetch_doc()` 拉文档 |
| `dsllib.py` | `el/box/text_el/card/hline/vline/dashed/polygon/stack/snapshot/est_width/est_lines/warnings` |
| `state.py` | 套件进度：`start_task/finish_task/checkpoint/set_current` |
| `finalize.py` | 从 `requests.jsonl`/`iterations.jsonl` 生成 `task-metrics.json` |
| `wrapup.py` | 一次调用完成"记迭代 + 出指标 + 更新套件状态" |
| `crop.py` | 放大核对：`python crop.py <png> <task> <x,y,w,h> <scale> <tag>` |

典型生成脚本骨架（把 A01–A05 的 `build_*.py` 当模板）：

```python
import os, sys, json
ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit, dsllib as D, state as S
TASK = "A06"
OUT = os.path.join(S.OUT_ROOT, TASK); TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, OUT, TMP); S.start_task(TASK)
… 计算 + kids 列表 …
dsl = D.snapshot([D.stack(kids, W, H)], W, H, bg="#F1F5F9FF")
r = snapkit.render(dsl, "xxx.png", "xxx.snapshot", final=True)
for w in D.warnings(): print("WARN", w)     # 一定要打印并逐条处理
```

## 7. 每次渲染后的自检流程（不可省略）

1. 跑生成脚本 → `render ok=True`。
2. **读 `D.warnings()` 输出**，逐条处理（文字溢出、框太小等）。
3. **用 read 工具真的打开 PNG 看**。不要只看 HTTP 200、不要只算像素。
4. 发现问题 → 改脚本 → 重渲染 → 再看。循环到满意为止。
5. 需要看细节时用 `crop.py` 放大局部。
6. 交付前把 `xxx.snapshot`（与 PNG 同名）放在输出目录，确认是**服务真实响应的原始字节**，没有后处理。
7. 写 `snapshot-usage.md`（自检表 + 问题修复表 + 未解决事项）与 `task-metrics.json`。
8. 调 `wrapup.wrapup(...)` 记迭代、更新套件状态。

## 8. 排版预算经验

- 表格列要右对齐时，列宽要比最长文本估算值多留 10–20px；估算器偏保守，实际可能放得下。
- 一行只放一个文本元素时最省心；要"同一基线多个文本"就把它们的 `y` 算成同一个值。
- 图例 chip 的宽度用 `D.est_width(label, size) + padding` 计算。
- 数据点密集时，让相邻点的数值标签**上下交替**（距离小于标签宽度就翻转），否则必然压字。
- 面板标题带很容易和上一面板底部的刻度标签打架；把标题信息放进左侧栏（gutter）通常最稳。
- 画布底部最后 20–30px 留白，脚注放在 `H-26` 左右。