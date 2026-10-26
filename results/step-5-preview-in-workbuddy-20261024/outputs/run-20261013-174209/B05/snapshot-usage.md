# B05 · Snapshot DSL 使用记录

服务：open-snapshot（run-config.json 指定），端点 `POST /snapshot`，
Content-Type `image/png`。

## 请求统计

- 总请求：23 次（含 0 次渲染行为探测）
- 成功：17（HTTP 200；用例渲染 17 次，
  平均 3.51s）
- 失败：6（PARSE_ERROR×4；其他×2）
  - PARSE_ERROR：T() 位置参数错位（case-03：align/style/family 错位致
    fontStyle 非法值），修复为重显式参数
  - 网络层：服务瞬时排队，由重试层覆盖（b05_net.py 200s 超时 ×4 次）

## DSL 能力实际使用范围

| 能力 | 使用情况 |
|---|---|
| Container 定尺/圆角/边框/阴影 | 10 件全部（卡片/按钮/磁贴/侧栏） |
| Stack + Positioned 绝对定位 | 10 件全部；界面全部绝对定位，坐标脚本计算 |
| 渐变 LINEAR/RADIAL | 纸面底（10 件）、按钮与徽章（09/10） |
| 文本 Text | SERIF 界面标题、SANS 正文、MONO 数据；letterSpacing（页头） |
| 形状 CIRCLE / borderRadius | 头像/状态点/进度点/评分条/胶囊标签 |
| polyline（折线） | 设施图标（轮椅/电梯/闸机/坡道/扶梯/列车/铃铛/人像/对勾/三角）、时间线连线、柱状图、间隙剖面 |
| Opacity / 半透明色 | 深青卡内嵌槽（#FFFFFF1A/#FFFFFF26）、时间线节点 |
| Flex Row/Column | 未使用（全部绝对定位，界面坐标已精算） |
| Image dataUri / 摄影图 | 未使用（纯 DSL，图标全部程序绘制） |
| Emoji | 未使用（界面图标自绘，避免字体依赖） |

## 实测边界与规避

1. **T() 位置参数必须显式**：T(s, left, top, w, h, size, color, align,
   style, family) —— align/style/family 错位会生成非法属性值
   （case-03 实证：fontStyle 收到字体族名 → PARSE_ERROR）
2. **HTML 实体不被解码**：文本 ASCII `<`/`>` 会被转义为实体——本任务
   全程避免使用（延续 B04 实证）
3. **两行文本必须拆条**：T() 为 softWrap=false maxLines=1，含 \n 的
   文本会窄箱告警且不换行——case-10 侧栏两行文字拆为两条 T()
4. **返回 list 的助手才能 extend/+=**（延续 B04 实证）
5. **小屏画布（440×512）可用**：手表画面验证了 Snapshot DSL 对
   非手机比例小画布的支持（圆角边框表壳 + 高对比白字）
6. **图标助手自绘需参数自洽**：图标按 (x, y, s) 绘制，容器内边距
   需预留 ≥ s*0.22（route_node/chip 内图标实证）

## 复用资产

- 共享助手：`tmp/run-20261013-174209/B05/b05_common.py`（产品调色板/状态色/界面构件
  card/status_bar/tab_bar/chip/btn/progress/score_bar/avatar/设施图标族/
  route_node/route_link/map_stub）
- 逐用例生成器：`tmp/run-20261013-174209/B05/cases/case01_gen.py` … `case10_gen.py`
- 每份最终 `.snapshot` 完整自包含（无外部文件依赖），可独立重新提交渲染
- CRLF 说明：final.snapshot 由 `write_text` 写出（Windows CRLF 换行），
  与请求体仅差换行符
