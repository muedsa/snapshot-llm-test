# case-01 · 特辑封面 · 下潜 DEEP DIVE

- 画布尺寸：1200×1600
- 受众：博物馆科普观众与中学课堂；移动端转发阅读
- 使用场景/观看环境：展览迎宾导览页 / 手机转发首图（0.4–3 米观展距离、竖屏）
- 希望读者完成：20 秒内看懂本特辑的十件结构并决定从『02 全深度总标尺』开始按由浅入深逐件下潜
- 内容与数据依据：两主数 3,682/10,935 [S01]；五带界值 [S02][S22]；带区 tag 逐条锚点
- 视觉主旨：等高五带脊柱（示意）作『下潜入口』同色阶梯，右侧九行目录给出下一件入口
- DSL 能力使用：rect 分带脊、chip 徽标、exhibit 信息卡、大数 num、页脚锚点条

## 本件使用的 claims（对应 sources.json claims 数组）
cl-avg、cl-max、cl-z-su、cl-z-tw、cl-z-mi、cl-z-ab、cl-z-ha、cl-fishery、cl-bio、cl-4c、cl-aby3q、cl-had-name、demo-spine（分类见 sources.json 的 cls：fact/calc/demo）

## 完成标准（plan v1/v2，依据见 plan-v1.md）
- 标准1：五带色带与总标尺同色同步（BAND5 常量同一） —— 核对结果：通过（证据见下）
- 标准2：目录含 c02–c10 共 9 行 —— 核对结果：通过（证据见下）
- 标准3：刊头含特辑名与实抓来源范围声明 —— 核对结果：通过（证据见下）

## 实际自检记录
v1 合格保留：五带色 BAND5 与 c02 完全同值（代码同常量表）；目录 9 行齐全含阅读顺序；五带 tag 与目录副题逐条可映射 claims； sightings 另一行『sources fetched 2026-10-18』居右上（未遮挡）。

看图证据（相对总任务根）：sheet-1.png（含 v1 全幅审览）

## 素材情况
无外部素材；本件为纯 DSL 构成（asset_policy_by_track：B 类允许局部辅助素材，本刊未使用）。

## 复现
- 同名完整 DSL：final.snapshot（同一渲染请求对应的响应保存于 final.png，为服务原始字节）
- DSL 源码生成脚本（相对总任务根）：tmp/20261016T164020-m1/b04_cases_a.py（c01–c05）/ b04_cases_b.py（c06–c10），公共构件 b04_common.py
