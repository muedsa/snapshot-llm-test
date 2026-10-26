# A20 Snapshot DSL 使用记录（run-20261013-174209）

服务基地址 `https://open-snapshot.muedsa.com`；请求体 `text/plain`，响应 `image/png`。

## 画布与坐标

- 画布 `Snapshot type="png" background="#FFFFFF"` → `Container width="1600" height="1100"`
  → `Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE"`，其余全部 `Positioned` 绝对定位。
- 主图底板 `(280,160,1040,760)` 固定；逻辑坐标 `(x,y)`（原点左下）→ 像素
  `(280+10.4x, 920-7.6y)`，全部使用未舍入浮点值。
- 点：`Container shape="CIRCLE"` 直径 12（半径 6）；TOP3 用 `#DC2626`，其余 `#2563EB`。
- 标签：白底圆角 8 底板（TOP3 边框 `2 SOLID #DC2626`，其余 `1 SOLID`），
  正文 `fontSize=20`，深青 `#0F172A` / TOP3 深红 `#B91C1C`。
- 引导线：`Transform matrix="(...)"` 列主序 4x4 旋转 + 薄 `Container` 画 2px 线段；
  **Transform 必须是 Positioned 的直接子节点**（外层多包一层 Container 会整条不渲染）。

## 实测结论

| 结论 | 证据 |
|---|---|
| 根只能有一个子节点，多 `Positioned` 挂根下报 PARSE_ERROR | 需 `Container` 定尺 + `Stack fit=EXPAND` |
| `Stack` 无显式尺寸时报 `Layout size is infinite` | 外层 `Container` 必须定宽高 |
| `Transform matrix` 需括号包裹 `(a,b,c,...)` | 不加括号报参数解析错误 |
| 矩形边缘无抗锯齿、框内像素与下层无关 | 标签底板可比色精确判定墨迹 |
| 圆边缘约 1px 抗锯齿带 | 点色取圆心像素精确比色即可 |

## 规模

- DSL 31328 字节
- 渲染 request_id `d452f296-2e40-4bb9-8142-90eba35f3ef5`（status ok；共 3 次请求，1 次因 matrix 未加括号报参数解析错误而重写）
- 渲染后程序化复测：24/24 点色精确、24/24 标签墨迹在盒内、8/8 引线覆盖率 >= 0.991
