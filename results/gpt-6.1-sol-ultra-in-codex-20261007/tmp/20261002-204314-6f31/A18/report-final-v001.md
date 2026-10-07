# A18 · 守恒对象的三幕视觉叙事

完成两个1600×1000真实预览，对各自原图与400宽缩略实际查看后选A，再真实视觉完善为v002。当前final原图与缩略root审查通过，正式completed以随后完整文件检查为准。

## 构图与真实看图

A为横排五路汇聚→紧密3×5队列→三扇面；B为纵排宽上游通道→近端密团/弯折出口→三路通道。两种proposal在各自HTTP前保存，真实preview请求分别A18-request-000002/000001，均200/image/png、1600×1000，原PNG与完整.snapshot保留临时concept-A/B和requests/versions。

选A依据：横排空间疏密变化更直观；B提供显式传输通道对照。选型记录[concept-selection.json](concept-selection.json)。最终原图及400缩略：

- A18-view-000013：真实打开1600×1000选中A v002最终原响应：箭头加深加粗及闲置节点轮廓增强，首幕五路汇同中心、第二同15圆3×5紧队列仍给同中心、第三三接收扇面各5混色清晰。15圆/9节点形状尺寸坐标与preview一致，圆不重叠且连线未见遮圆，只有总标题+三幕名。
- A18-view-000014：真实打开400×250最终缩略，与原preview对比：中性箭头和闲置轮廓更清楚，集中路径/紧密拥堵/三扇面分配仍立即可辨；未引入圆重叠或额外文字。

## 硬约束与几何

每幕同15个稳定ID，蓝/橙/灰各5、全部圆直径36；3个处理节点均64×64，节点与单元不带说明文字。首两幕均唯一接收N2；第三每节点5且均含至少两色。首幕串联的五条中性通路都唯一汇同中心；第三圆有独立箭头指向接收节点，关系不只靠颜色。完整单元ID/色/坐标/receiver及实际箭头各segment见[story-audit.json](story-audit.json)。

三幕最小圆中心距54.501/40/41.332px，最紧队列圆缘留4px；最终实际线和箭头头部逐段对全45圆验算，最小净距0.5px（已减半径18和半stroke），各圆完整在面板内且不与节点相交。数量、色、直径、坐标和9个节点几何与被选preview完全一致。程序核验支持真实看图，不取代视觉感知。

## 迭代、文档与过程

沿实际已看A预览将中性箭头2.5→3px、#71869F→#526D8C，闲置节点轮廓和内部几何横槽#A7B5C8→#8094AD；随后真实重新渲染、原图/400图再次查看比较，完成1次视觉迭代。两个方案是alternative，不重复算视觉迭代。

复用本run实际官方guide/parser-tags/layout/fonts缓存：有限1600×1000 Container+Stack、Positioned、shape=CIRCLE的36px单元、64px圆角Container处理节点、Transform直线箭头、Text/Raw只印标题和幕名；Inter,Noto Sans CJK SC来自真实字体查询。无外部素材或Image、无最终PNG后处理。只读Pillow缩略为QA衍生图，final始终原服务字节。

A首次本地几何自检发现第三幕扇面间圆重叠，发送HTTP前调整扇面半径及三幕统一节点位置；原失败脚本与local-geometry-failure-v001.json保留。独立B核验第一次猜测audit文件名不存在，已保存ENOENT记录并读取实际story-audit-draft-v001.json修复，不是HTTP失败。root早期B真实查看的版本简称不准确，已单列[元数据更正](../../../tmp/20261002-204314-6f31/A18/root-preview-B-version-label-correction-v001.json)，原查看不改、不重计。

本题真实渲染3次（成功3、失败0），新HTTP文档请求0；请求/版本/看图/迭代与字节消耗见[task-metrics.json](task-metrics.json)。首次成功preview与当前final可用时间分开记录，墙钟总耗时不等同请求耗时之和。token、图像输入计费和费用未知为null；未解决事项无。[rationale.md](rationale.md)计168字符≤300。
