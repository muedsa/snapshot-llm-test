# case-02 · 叠光天文台 2026 月相历

**尺寸** 1200×1600 px ｜ **主作品** `final.png`（真实服务响应，与 `final.snapshot` 配对）｜ **完成标准引用** `tmp/<run_id>/B01/work-plan.json` v2

## 受众与使用场景

- 谁在用：天文台开放夜排期志愿者
- 要完成的事：按月光强弱挑出无月观测夜
- 实际观看环境：打印 A2 海报，也用于屏幕滚动预览

## 内容

12 个月历、每月新月/满月日期、逐月月面图、月龄与照明比例、近似误差说明；机构名与活动为虚构。

## 视觉选择（为什么这样画）

月龄与照明比由会合周期公式计算（age=(JD−2451550.1) mod 29.530588853），月面明暗区用两条 ClipPath 圆弧围成的月牙，凸出方向随盈亏翻转；深色夜空底 + 单一金色强调。

## 实际自检

构建期审计通过；月相过零检测复算全年新月 12 次、满月 13 次（第一版用容差窗口得到 21/23，改为过零判定后修正）；逐月看图核对明暗方向与日期一致。

## 素材情况

无外部素材。

## 复现

```
python tmp/<run_id>/B01/case02_moon.py     # 生成 final 同名 DSL 并打印布局审计
python tmp/<run_id>/_suite/scripts/render.py --dsl tmp/<run_id>/B01/case02.snapshot     --out outputs/<run_id>/B01/case-02/final.png     --log tmp/<run_id>/B01/requests.jsonl --req-id B01-case-02-final --task B01 --kind final
```

服务渲染 12 次（含修正后的重渲染），全部请求见 `tmp/<run_id>/B01/requests.jsonl`；
过程版本、草稿与失败响应保留在同一临时目录。
