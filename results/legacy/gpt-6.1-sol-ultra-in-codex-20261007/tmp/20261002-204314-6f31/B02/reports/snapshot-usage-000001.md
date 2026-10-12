# B02 Snapshot 实际使用与踩坑

run 20261002-204314-6f31。十件已正式发布，最终task关闭与套件总审查随后执行。
输出：D:\workspaces\gpt-6.1-sol-ultra\outputs\20261002-204314-6f31\B02。临时：D:\workspaces\gpt-6.1-sol-ultra\tmp\20261002-204314-6f31\B02。

[完整作品集](portfolio.json) · [画廊](gallery.html) · [指标](task-metrics.json)

再线 / RETHREAD：让旧织物回到社区日常。十件作品把发现、参与、学习、归还、交换、反馈与协作连成可使用的视觉生态。不同任务采用各自布局，纸色、双补丁标志与缝线保持身份。

## 文档与真实服务

复用本run已真实取得、阅读的shared-doc-000001指南、shared-doc-000004 Parser和shared-doc-000006 OpenAPI及shared-fonts-000001。UTF-8纯文本POST https://open-snapshot.muedsa.com/snapshot；每个最终PNG保留原服务响应字节。字体Inter,Noto Sans CJK SC。缓存复用不增加HTTP请求。
各作品的实际标签见portfolio.json；全部主体DSL，未嵌入外部整图或素材。

## 实际生成、查看与修改

实际渲染13次，成功13，失败0；DSL13版；看图19次；完整visual3。基线/视觉修改/失败分别保留在requests.jsonl、iterations.jsonl、views.jsonl、tool-usage.jsonl。
- case-01 B02-view-000001→B02-view-000004：标题降80px/盒250、副标题下移430；说明盒75；负形领口去白圆。 比较：v001两处文字裁剪与独立小弧已解除；其他运营内容保持。
- case-10 B02-view-000005→B02-view-000008：交接带与竖线移到时间块及标签之前绘制；18:15标签保留上层。 比较：旧图13:00的文字被线穿过，新图解除；岗位、时刻和时长保持。
- case-04 B02-view-000009→B02-view-000014：剪刀改并拢刀刃与下方手柄并加关闭示意，四件改为四类工具。 比较：图文冲突与数量歧义解除，其他工具和流程保持。

实际Node参数化几何、数值计算与DSL构造、独立文件/hash/内容审计、view_image逐图观察及接触表对比已保留。无模型费用或token计量来源，不以字数或账户比例推测。

实际打开十图接触表后整集审查通过：共同双补丁标志、纸色/墨蓝/陶土色、缝线与统一中英标题使项目可识别；招募、预约、导览、工具、评估、教学、取件、交换、月报、排班各有不同任务与构图。近读密集文案须用原尺寸，接触表仅检查体系与构图。单图内容与数据依已有真实原PNG查看记录，三处视觉问题已修正。
额外项目简报、真正应用的设计系统、十触点映射见project-brief.md/design-system.json/touchpoint-map.json。所有运营/价格/人员/织物库存/日期/地址/服务数据均自拟演示。9月月报18h与10月24日班次27人时属于不同月份。
本次恢复核对并重新打开03/10/04三图，先前尚未落盘查看由摘要恢复为单独事件，原查看准确时刻不可得并已注明；重开和恢复事件均累计真实次数，不制造额外视觉修改。
本题无失败HTTP和429。工具脚本一次spawnSync EPERM已留存，改为同进程直接调用簿记函数恢复。完整visual三次：招募标题/说明裁剪修复，排班遮线修复，剪刀图文一致性修复。05/06首次提交前静态精修不计visual。

## 复现与剩余事项

发送每个final.snapshot为text/plain; charset=utf-8请求体，按Content-Type/HTTP/PNG尺寸验证响应。不要依赖脚本库重建，最终DSL已完整自包含。
每用例时段见task-metrics.json case_metrics。未测量创作起点为null，真实服务到交付间隔另列；并行创作和请求耗时之和不等于整体墙钟。未发生反馈/限流等待记录为0，服务器不可测排队为null。
独立审计：D:\workspaces\gpt-6.1-sol-ultra\tmp\20261002-204314-6f31\B02\independent-audit\audit-final-v001.json。目前单题无未解决事项；后续状态为B03:pending、B04:pending、B05:pending、B06:pending；全套最终总审查尚待完成。
