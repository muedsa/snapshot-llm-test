# B06-case-09 · What Decision Affects My Block?

- 状态：completed
- 品牌与数据：{'problem_evidence': 'Agendas are ordered by procedure and department, not by who is affected or what action residents can take. Design hypothesis only.', 'type': 'fictional demonstration', 'demo_values': {'meeting': 'District 4 Community Meeting (fictional)', 'items': [{'item': 'School crossing timing', 'impact': 'families on Oak Street', 'decision': 'approve trial timing', 'comment_by': '2026-12-01'}, {'item': 'Park hours', 'impact': 'evening park users', 'decision': 'extend closing to 22:00', 'comment_by': '2026-12-03'}, {'item': 'Bus lane pilot', 'impact': 'drivers and bus riders on 3rd Avenue', 'decision': 'approve six-month pilot', 'comment_by': '2026-12-04'}, {'item': 'Tree removal request', 'impact': 'residents near Cedar Court', 'decision': 'approve or deny removal', 'comment_by': '2026-12-05'}]}, 'limitations': 'Meeting, district, locations, decisions, and deadlines are fictional. The map is an agenda reordering demonstration, not an official notice.'}
- 受众：A resident scanning a long public-meeting agenda
- 使用环境：Landscape civic agenda map before a neighborhood meeting
- 用户目标：Find agenda items by personal impact, understand what decision is being made, and know when and how to comment.
- 尺寸：1600×1200

## 场景与视觉选择

A neighborhood impact map surrounded by four agenda cards, each connected to the place and people affected; a comment-deadline rail makes participation concrete.

## 实际自检

四项议程均显示地点/受影响人群、决定和Dec 01/03/04/05评论截止日；地图标为示意边界，参与说明不承诺结果改变，底部卡片已离开页脚线。

查看时间：2026-11-24T18:23:16.169+08:00（+08:00）。最终PNG为真实服务响应，SHA-256 `af2f1d24692a9efd2aa749d45f46f242a87c9b3261f00efb8126690b45c0333d`；同名DSL与提交UTF-8请求一致（仅允许换行归一化）。

## 标准与证据

- B06-09-C1：Each agenda item shows the decision, affected group/place, and comment deadline without procedural jargon.；检查方法：Read all four cards and compare with demo_values.；结果：通过。
- B06-09-C2：The map makes impact geography visible without implying exact boundaries or real district data.；检查方法：Inspect map labels, impact connections, and demo notice.；结果：通过。
- B06-09-C3：Participation actions and deadlines are visible, and the artwork does not claim that public comment changes a predetermined outcome.；检查方法：Inspect the deadline rail and participation wording.；结果：通过。
- B06-09-C4：Cards, map labels, and connectors remain readable with no overlap or clipped deadlines.；检查方法：Review full PNG, 50% thumbnail, and crops around each card-map connection.；结果：通过。

## 素材

纯DSL主体，无外部嵌入素材；自拟品牌与演示数据不宣称实际客户部署。
