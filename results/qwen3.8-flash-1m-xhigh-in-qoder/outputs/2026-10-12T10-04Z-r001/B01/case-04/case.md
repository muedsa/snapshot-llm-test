# case-04 · 叠光城市环境观测台 24 小时空气看板

**尺寸** 1920×1080 px ｜ **主作品** `final.png`（真实服务响应，与 `final.snapshot` 配对）｜ **完成标准引用** `tmp/<run_id>/B01/work-plan.json` v2

## 受众与使用场景

- 谁在用：早高峰通勤者与学校校医
- 要完成的事：一眼判断今天能否进行户外活动
- 实际观看环境：大厅 65 寸屏 / 网页首屏，远距离阅读

## 内容

当前 AQI 仪表、24 小时 × 8 站点热力矩阵、四项污染物相对国标限值柱状、五日趋势条、分级建议；站点与数据为演示生成。

## 视觉选择（为什么这样画）

所有图元来自同一份小时级数据集：仪表弧、色带、数字与建议共用同一个等级函数，杜绝“数字说优、颜色说差”；深色底 + 高饱和等级色。

## 实际自检

构建期审计通过；指针角 = 270·(v/vmax)−135 与弧长同参数，看图发现第一版把仪表弧画成了左半圆（donut_segment 起始角未减 90°），修正后复看；等级阈值与色带逐项对照。

## 素材情况

无外部素材。

## 复现

```
python tmp/<run_id>/B01/case04_air.py     # 生成 final 同名 DSL 并打印布局审计
python tmp/<run_id>/_suite/scripts/render.py --dsl tmp/<run_id>/B01/case04.snapshot     --out outputs/<run_id>/B01/case-04/final.png     --log tmp/<run_id>/B01/requests.jsonl --req-id B01-case-04-final --task B01 --kind final
```

服务渲染 5 次（含修正后的重渲染），全部请求见 `tmp/<run_id>/B01/requests.jsonl`；
过程版本、草稿与失败响应保留在同一临时目录。
