# case · 11 · 积云 → 积雨云 Cumulus/Cumulonimbus 图鉴页（对流塔）

- 画布：1080×1920（9:16）
- 受众：图鉴读者——夏季看云长大的所有人
- 使用场景：图鉴页 9/10（压轴）：对流发展全序列
- 使用目标：沿 humilis→mediocris→congestus→Cb 四阶段读懂对流塔演化与「云的工厂」
- 主导手法：四阶段发展序列 + 砧顶/塔身/降水幡/闪电插画 + 12 km 高度轴
- 视觉主张：唯一 9:16 竖幅图鉴页；四阶段横向序列 + 发展箭头
- 内容依据：S2 WMO ICA 积云/积雨云页；S4 CIMO 表（Cu 300–1 500 m、Cb 600–1 500 m；更宽均 300–2 000 m）；S5 NOAA（日对流生消、Cb 定义）；S6 HKO（Cu→Cb 演化标志、附属云全清单）
- 主张溯源：见 `outputs/run-20261013-174209/B04/sources.json`（claims 数组按 case_id 定位）

- 最终版本：case-11-v02（request_id 7cc86f10-49c6-43ed-a7f9-2f59b0576982，耗时 5.218s，DSL 54340B）

## 完成标准与实际结果

### C-1 四阶段序列与 HKO 演化标志一致
- 实际结果：已达成
- 检查方法与证据：主图四阶段 + 数据卡「穹顶轮廓清晰（水滴）→ 顶部柔软纤维（冰晶）即 Cu→Cb」引 HKO 原文

### C-2 Cu/Cb 云底高度与 CIMO 表一致
- 实际结果：已达成
- 检查方法与证据：v02 修正：v01 误写 0.6–2 km → v02 改为 Cu 0.3–1.5 km（1 000–5 000 ft）/ Cb 0.6–1.5 km（2 000–5 000 ft），更宽 0.3–2 km；与 notes §2.2 逐行一致

### C-3 附属云清单完整（ICA via HKO）
- 实际结果：已达成
- 检查方法与证据：ICA 清单第三栏：Cu pileus；Cb incus/mamma/virga/praecipitatio/arcus/tuba/pannus/velum

## 渲染与迭代记录

- 渲染请求：4 次（成功 2，失败 2，均经自检拦截/参数修复/重试后成功）
- 版本链：v01 → v02（最终 v02）
- 迭代要点：v01 初版 → v02 数据纪律修复（CIMO 高度误植）
- [B04-c11-i01] data-discipline：v01 数据卡与 CIMO 表不符：写「Cu 0.6–2 km / Cb 0.6–2 km / 2 000–6 500 ft / Cb 更宽范围：—（砧顶可远超 12 km）」，而 notes §2.2 记录 Cumulus 常用 300–…
- 实际看图：z11-view.png v01 整图、z11-view-v02.png v02 整图
- 字节核对：final.png 与服务响应 MD5 一致（3ea701937139…）；final.snapshot 完整自包含（6dbe2f39cee1…）

## 未解决问题

无
