# case-04 · 一年 · 公转周期

## 场景

- 受众：科普读者
- 使用环境：科普读物 / 展板
- 使用者要完成的事：读出公转周期从 88 天到 59,800 天并换算地球年
- 尺寸：1600 × 1000

## 内容

- 内容来源：S1 表 Orbital Period (days) 行；地球年换算为编辑计算（÷365.2）
- 关联 claim_id：C08, C09（逐条定位、口径与 basis_type 见 `sources.json`）
- 本图所有事实/数值主张均已分配 claim_id；编辑计算与解释已单独标注。

## 视觉选择

- 视觉主张：对数条让 680 倍跨度同屏可读，右侧给出天数与年数双标注
- 独到手法：对数刻度渐变条 + 10^n 网格 + 精确数值双标注
- 实际使用能力：math.log10/gradientType=LINEAR/dashed_vline/rich Raw

## 素材情况

纯 DSL 构造，无外部图片素材；无演示数据。

## 实际自检

打开 `outputs/<run_id>/B04/case-04/final.png` 实际逐区查看。v1 数据校验发现底部结论「679 个水星年」是截断（精确 59,800 ÷ 88.0 = 679.5），verify_data.py 报 1 项 FAIL；v2 改为「约 680 个水星年（59,800 ÷ 88.0 ≈ 679.5）」并同步更新 sources.json 的 C09，重渲染后复查正确，data-check 17 项全部通过。最终逐区查看：8 行对数渐变条、10^1–10^5 网格、天数与 ≈地球年双标注、163.7 地球年结论与编辑计算脚注完整。通过。

- 尺寸（PNG IHDR 实测）：1600 × 1000
- 实际渲染请求 ID：B04-final-45551-0, B04-final-48195-0, B04-final-38823-1, B04-final-39792-2
- 关联 claim_id：C08, C09（逐条定位见 sources.json）
- 完成标准：case-04-C1、case-04-C2、case-04-C3、case-04-C4 全部 passed（见 portfolio.json 的 criterion_results）
- 数据一致性：verify_data.py 从研究存档复算 17 项全部通过，图中数值未被改动；编辑计算与来源观点已分别标注。

