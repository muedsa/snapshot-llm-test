# B02 · Snapshot DSL 使用记录

服务：open-snapshot（run-config.json 指定），端点 `POST /snapshot`，Content-Type `image/png`。

## 请求统计

- 总请求：45（含 4 次渲染行为探测）
- 成功：30（HTTP 200；用例渲染 26 次，平均 "
6.71s）
- 失败：15（均经重试或参数修复后成功）
  - 网络层读超时 ×10、连接中断 ×2、SSL 错误 ×1：服务间歇故障，由重试层覆盖
  - HTTP 400 PARSE_ERROR ×2：Transform matrix 格式（裸 0/1、无括号包裹）不符合服务正则
    `\(-?0\.\d{10}(-?0\.\d{10}){15}\)`；修复为括号包裹 + 16 个 10 位定点小数

## DSL 能力实际使用范围

| 能力 | 使用情况 |
|---|---|
| Container 定尺 | 10 件全部（600×800 至 1920×1080，8 种画布比例） |
| Stack + Positioned 绝对定位 | 10 件全部；全部元素绝对定位，坐标经脚本计算 |
| Transform matrix | 曲线折线段（水波/雁阵/芦苇/鸟形）、进度条、菱形与圆点标记、鸟形翼弧 |
| 文本 Text | 中英混排：Noto Serif/Sans CJK SC + Inter + Noto Sans Mono CJK SC（等宽数字）；BOLD/NORMAL |
| 基本图形 | rect（圆角）/ circle / polyline：徽记、雁阵、芦苇剪影、水烛植株、地图折线、集章圆、条码 |
| Image 嵌入 | 未使用（asset_policy=dsl_only，纯 DSL 交付） |

## 实测边界与规避

1. **matrix 格式硬约束**：服务校验 `alignment="CENTER"` 写在 Transform 上，且 matrix 必须
   括号包裹、16 个值均带 10 位小数；裸整数或省略括号均 PARSE_ERROR。全部生成器统一由
   `b02_common._bar_between` 等助手产出。
2. **HTML 实体不被解码**：源文本 ASCII `<`/`>` 经转义后按字面输出；已全局改用 Unicode `≥`/`≤`。
3. **`+=` 字符展开陷阱**：返回 `str` 的助手（rect/text_node/chip/circle）若用 `out += helper(...)`
   会把字符串按字符展开进列表，生成「字符间插换行」的损坏 DSL；返回 `list` 的助手
   （polyline/logo/wave/reed_cluster 等）必须 `out +=`。已在 case-04/09 实际踩中并修复。
4. **CENTER 对齐的 left 参数**：服务 CENTER 行为正常（probe-align 探测证实），但 left 必须是
   `(容器宽-文本宽)/2` 而非容器中心 x；case-05 主标题曾因 left=W/2 导致右半溢出被裁。
5. **服务间歇故障**：读超时/连接中断/51x/52x 需外层重试；`b02_net.py` 以 200s 超时 ×4 次尝试覆盖。
6. **文字裁切**：服务不自动缩放文本；声明盒需 ≥ 估算墨迹宽（CJK 1.0em/ASCII 0.56em）1.03 倍，
   case-10 生成器内置宽度自检 + 旋转包围盒边界断言（0 警告）。
7. **曲线连续渲染**：圆头 pill 段端相切产生「扇贝串珠」；方头端端相接有抗锯齿接缝；
   方头 + 端部向外重叠 thick*0.3 后接缝被邻段覆盖，曲线连续（probe-poly/bar 探测 + 4x 放大验证）。

## 复用资产

- 共享助手：`tmp/run-20261013-174209/B02/b02_common.py`（字体、调色板、徽记/雁阵/芦苇/水波/页脚带组件）
- 逐用例生成器：`tmp/run-20261013-174209/B02/cases/case01_gen.py` … `case10_gen.py`
- 每份最终 `.snapshot` 完整自包含（无外部文件依赖），可独立重新提交渲染
- CRLF 说明：final.snapshot 由 `write_text` 写出（Windows CRLF 换行），与请求体仅差换行符
