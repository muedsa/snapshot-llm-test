# B04 · Snapshot DSL 使用记录

服务：open-snapshot（run-config.json 指定），端点 `POST /snapshot`，
Content-Type `image/png`。

## 请求统计

- 总请求：28 次（含 0 次渲染行为探测）
- 成功：17（HTTP 200；用例渲染 17 次，
  平均 6.65s）
- 失败：11（读超时×7；其他×4）
  - 网络层（读超时/429 排队）：服务间歇性排队，由重试层覆盖
    （b04_net.py 200s 超时 ×4 次；瞬时排队时终止后单件重试即恢复）
  - PARSE_ERROR / RENDER_ERROR：DSL 边界触碰，经自检拦截后改写法

## DSL 能力实际使用范围

| 能力 | 使用情况 |
|---|---|
| Container 定尺/圆角/边框/阴影 | 11 件全部（数据卡/主图槽/芯片/清单卡） |
| Stack + Positioned 绝对定位 | 11 件全部；全部元素绝对定位，坐标经脚本计算 |
| 渐变 LINEAR/RADIAL/SWEEP | 11 件全部（纸面渐变/天空分层/范围带/徽标） |
| 折线 polyline（曲线采样） | 卷云丝缕（01/03）、毛毛雨（10）、降水幡（08/11）、闪电（11）、地平线+扇区（02/09） |
| 圆 circle / 形状 CIRCLE | 晕圈（01/05）、日轮/月轮（05/07/10）、云团 mound（01/11）、corona（06）、冰雹点（11） |
| 文本 Text | 属名 SERIF 大字、数据 MONO、清单列表、letterSpacing 属名条 |
| ClipRect/ClipRRect | 主图槽圆角（11 件全部）、芯片图标约束（01） |
| Opacity / 半透明色 | 天空分层叠加（03–11）、范围带 #FFFFFF55、图标底槽 #FFFFFF14 |
| Flex Row/Column | 三步法流程卡（02） |
| Image dataUri / 摄影图 | 未使用（纯 DSL，插画全部程序绘制并标注示意图） |

## 实测边界与规避

1. **HTML 实体不被解码**：T() 助手会把文本中的 ASCII `<`/`>` 转义为实体，
   服务原样显示——角度符号一律用全角 ＜/＞（case-02/04/05/06/09 实证，
   自检拦截 2 次后全量预防）
2. **百分比尺寸完全非法**：width/height 只接受像素浮点（B03 实证，B04 沿用）
3. **返回 list 的助手才能 extend/+=**：`n += icon` 会把返回 str 的助手按字符展开
   （case-01 实证；polyline 返回 list）
4. **插画助手必须参数自洽**：cumulus_heap 等按 (x, y, w, h) 绘制，
   芯片图标区高度不足时云团会溢出压住文字——图标区与文字区必须分层预留
   （case-01 v04 芯片加高重构实证）
5. **数据卡数值必须对表复核**：高度数值易从相邻属误植（case-10/11 两处实证），
   渲染后需与 notes §2.2 逐行比对
6. **多行文本窄箱警告**：T() 对 CJK 宽度估算对多行文本会误报 narrow，
   行高足够时 intentional 放行（case-11 三条 warning 均为 30–48px 多行盒）

## 复用资产

- 共享助手：`tmp/run-20261013-174209/B04/b04_common.py`（调色板/云形插画助手/高度轴/
  范围带/T()/foot_bar）
- 逐用例生成器：`tmp/run-20261013-174209/B04/cases/case01_gen.py` … `case11_gen.py`
- 每份最终 `.snapshot` 完整自包含（无外部文件依赖），可独立重新提交渲染
- CRLF 说明：final.snapshot 由 `write_text` 写出（Windows CRLF 换行），
  与请求体仅差换行符
