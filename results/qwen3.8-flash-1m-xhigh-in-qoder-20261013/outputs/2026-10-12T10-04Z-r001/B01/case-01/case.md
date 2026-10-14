# case-01 · 叠光市轨道交通网络图

**尺寸** 1600×1000 px ｜ **主作品** `final.png`（真实服务响应，与 `final.snapshot` 配对）｜ **完成标准引用** `tmp/<run_id>/B01/work-plan.json` v2

## 受众与使用场景

- 谁在用：站内看图的到访者与通勤者
- 要完成的事：五线网中找出任意两站之间的最少换乘路径与票价区间
- 实际观看环境：地铁站厅灯箱（1:1 观看）与手机缩略图

## 内容

5 条线路、26 座命名车站、5 座换乘站、河道、指北针、比例尺、线路索引与换乘矩阵；站名与线路全部自拟（叠光市为虚构城市）。

## 视觉选择（为什么这样画）

严格格点布局：所有线段只取水平、垂直或 45°，这是示意图可读性的来源；换乘站必须是两条以上线段的真实交点，由线段包含关系算出而不是手画；站名用贪心避让函数放置。

## 实际自检

构建期布局审计：0 文本重叠 / 0 出界 / 最小字号 20px；换乘对由程序枚举后与图中矩阵逐项核对；三次渲染逐次看图修正 L1 的格点错位（第一版换乘站没有共用顶点）。

## 素材情况

无外部素材（B 赛道允许辅助素材，本件用纯 DSL 完成）。

## 复现

```
python tmp/<run_id>/B01/case01_metro.py     # 生成 final 同名 DSL 并打印布局审计
python tmp/<run_id>/_suite/scripts/render.py --dsl tmp/<run_id>/B01/case01.snapshot     --out outputs/<run_id>/B01/case-01/final.png     --log tmp/<run_id>/B01/requests.jsonl --req-id B01-case-01-final --task B01 --kind final
```

服务渲染 3 次（含修正后的重渲染），全部请求见 `tmp/<run_id>/B01/requests.jsonl`；
过程版本、草稿与失败响应保留在同一临时目录。
