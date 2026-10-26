# B01 · Snapshot DSL 使用记录

服务：open-snapshot（run-config.json 指定），端点 `POST /snapshot`，Content-Type `image/png`。

## 请求统计

- 总请求：41（含 1 次服务可用性探针）
- 成功：19（HTTP 200，平均 10.51s，累计 199.7s）
- 失败：22（累计耗时 2196.98s，均经重试或参数修复后成功）
  - HTTP 400 PARSE_ERROR ×5：Transform matrix 格式（裸 0/1、无括号包裹）不符合服务正则 `\(-?0\.\d{10}(,-?0\.\d{10}){15}\)`；修复为括号包裹 + 16 个 10 位定点小数
  - HTTP 521/522 ×5、502 ×1：服务端故障/排队，等待后重试成功
  - 网络层无状态 ×11：读超时，由重试层（200s 超时 ×4 次尝试）覆盖

## DSL 能力实际使用范围

| 能力 | 使用情况 |
|---|---|
| Container 定尺 | 10 件全部（720×1280 至 2560×1440，6 种画布比例） |
| Stack + Positioned 绝对定位 | 10 件全部；全部元素绝对定位，坐标经脚本计算 |
| Transform matrix | 旋转/斜切/缩放：进度条端点圆角、菱形温度标记、斜切动势带、雷达扫描、海拔折线段 |
| 文本 Text | 中英混排：Noto Serif/Sans CJK SC + Inter + Noto Sans Mono CJK SC（等宽数字） |
| 基本图形 | rect / circle / ellipse / polyline / polygon：环、条、曲线、剖面、星形、队徽几何自绘 |
| 滤镜 | 雾带半透明叠加（case-05）、玻璃质感面板（case-04/10） |
| Image 嵌入 | 未使用（asset_policy=dsl_only，纯 DSL 交付） |

## 实测边界与规避

1. **matrix 格式硬约束**：服务校验 `alignment="CENTER"` 写在 Transform 上，且 matrix 必须括号包裹、16 个值均带 10 位小数；裸整数或省略括号均 PARSE_ERROR。全部生成器统一由 `b01_common._bar_between` 等助手产出。
2. **HTML 实体不被解码**：源文本 ASCII `<`/`>` 经转义后按字面输出；已全局改用 Unicode `≥`/`≤`。
3. **服务间歇故障**：521/522/429/读超时需外层重试；`b01_net.py` 以 200s 超时 ×4 次尝试覆盖。
4. **文字裁切**：服务不自动缩放文本；声明盒需 ≥ 估算墨迹宽（CJK 1.0em/ASCII 0.56em）1.03 倍，逐件 dsl+像素双核对。

## 复用资产

- 共享助手：`tmp/run-20261013-174209/B01/b01_common.py`（字体、图形、matrix 助手）
- 逐用例生成器：`tmp/run-20261013-174209/B01/cases/case01_gen.py` … `case10_gen.py`
- 每份最终 `.snapshot` 完整自包含（无外部文件依赖），可独立重新提交渲染
