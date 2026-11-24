# case-02 · Crosswind cycling route poster

- 状态：completed
- 品牌与数据：FICTIONAL_DEMO：Invented Crosswind route through invented streets, five fictional turns, demo distance and caution note; not a navigable map or safety-certified route.
- 受众：Occasional urban cyclists planning a fictional low-traffic route
- 使用环境：Portrait poster at a fictional bike cooperative and community noticeboard; viewed first at 2 metres then approached for turns
- 用户目标：Follow the demo route in order, recognise key turn types and find the start, finish and caution point
- 尺寸：1080×1528

## 场景与视觉选择

Route arrows are separate transformed DSL modules rotated and translated around explicit origins, forming a diagonal path through a strict typographic grid; the geometry reads as motion without becoming an unreadable map.

## 实际自检

逆风线海报的起点、终点、五段转向、12.6公里演示距离和施工提醒完整；提示卡两行无裁切，所有箭头端点位于地图面板内。

查看时间：2026-11-24T16:53:14.592+08:00（+08:00）。最终PNG为真实服务响应，SHA-256 `79b6dc97011547b7f5f502bde136283eb2b7bca77f5e03490fe2c6424f254b5f`；同名DSL与提交UTF-8请求一致（仅允许换行归一化）。

## 标准与证据

- C01：Start, finish, five ordered turn labels, demo distance and caution note are complete and readable.；检查方法：Route inventory and full-size review.；结果：通过。
- C02：Arrow angles and endpoints visually continue the intended route order without intersecting labels.；检查方法：Inspect transformed geometry against calculated endpoint coordinates.；结果：通过。
- C03：No arrow or rotated label is accidentally clipped by its layout parent or the canvas.；检查方法：Inspect each transform's visible bounds at 100%.；结果：通过。
- C04：A prominent demo/not-for-navigation notice prevents real-world routing reliance.；检查方法：Read header and footer notices.；结果：通过。

## 素材

纯DSL主体，无外部嵌入素材；自拟品牌与演示数据不宣称实际客户部署。
