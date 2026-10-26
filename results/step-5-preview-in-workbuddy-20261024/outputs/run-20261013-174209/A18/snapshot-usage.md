# A18 Snapshot DSL 使用记录（run-20261013-174209）

- 端点：`POST https://open-snapshot.muedsa.com/snapshot`（`Content-Type: text/plain` → `image/png`）
- 画布：1600×1000，`background="#FFFFFF"`；返回 PNG 为 RGBA 且 alpha 全 255（已在白底合成，
  比色前无需再合成，但脚本仍按 RGBA 白底合成防御性处理）
- 布局：`Container` + `Stack(alignment="TOP_LEFT", fit="EXPAND", clipBehavior="NONE")`，
  全部元素 `Positioned` 绝对定位（本次 45 圆 + 9 节点框 + 45 连线 + 4 文字 + 2 分隔线）
- 圆形：`Container shape="CIRCLE"` 直接出 36px 单元圆与 N01 的 44px 圆形字形
- 节点外包框：`Container borderRadius="14"`；闲置节点 `border="2 SOLID #0F172A"`
  （实测边框绘于框内 2px，视觉外包框 = 声名框，无外扩）
- 菱形（N03 字形）：32×32 方绕中心 `Transform` 旋转 45°，列主序 4×4 矩阵
  `(0.707107,0.707107,0,0,-0.707107,0.707107,0,0,0,0,1,0,0,0,0,1)`，`alignment="CENTER"`
- 任意角度连线：薄 `Container(width=线段长, height=3)` + 旋转矩阵
  `(ux,uy,0,0,-uy,ux,0,0,0,0,1,0,0,0,0,1)`，`alignment="CENTER"`；
  线段起点/终点由程序算到单元圆界与节点框外各 1.5px，保证不遮圆不压框
- 文字：`Noto Sans CJK SC` / `fontStyle="BOLD"` / `softWrap="false"` / `maxLines="1"`；
  全图仅总标题与三幕名 4 个 `Text`
- 颜色精度：`#RRGGBB` 六位全部精确渲染——45 圆 + 9 节点框 + 45 连线采样点逐一比色，
  与服务 DSL 声明值 0 误差；矩形边缘无抗锯齿，圆边缘有约 1px 过渡带
  （故直径判定用 36 向 50% 覆盖率半径均值，而非精确色包围盒）
- 规模：DSL 23102 字符 / 23159 字节（UTF-8）；
  渲染 request_id
  `a6bbc20a-5a39-4d73-8528-d009b99cdc87`（status ok，一次成功，无重试）
- 网络：预览两次渲染分别重试 3 次与 2 次后才成功（SSL 握手超时 / 读超时 /
  RemoteDisconnected），原样重试即可，全部记录于 `tmp/run-20261013-174209/A18/requests.jsonl`
