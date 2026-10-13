# case-05 · 云脊线徒步剖面卡

**尺寸** 1400×900 px ｜ **主作品** `final.png`（真实服务响应，与 `final.snapshot` 配对）｜ **完成标准引用** `tmp/<run_id>/B01/work-plan.json` v2

## 受众与使用场景

- 谁在用：出发前 5 分钟读图的徒步者
- 要完成的事：知道哪里累、哪里有水、哪一段暴露
- 实际观看环境：手机竖屏截图与打印折页

## 内容

12.4 km 路线、42 个采样点的高程剖面、累计爬升、最长坡度段、水点/观景台/暴露段标记、天气提示；路线为虚构示例。

## 视觉选择（为什么这样画）

剖面是一张真正的面积图：闭合 ClipPath 多边形 + 天空渐变 Container；所有标记按里程在同一数组上线性插值落位，摘要数字由几何反算而不是另写一遍。

## 实际自检

构建期审计通过；累计爬升/最大坡度与采样数组复算一致；看图调整了标记引线，避免与站名重叠。

## 素材情况

无外部素材。

## 复现

```
python tmp/<run_id>/B01/case05_ridge.py     # 生成 final 同名 DSL 并打印布局审计
python tmp/<run_id>/_suite/scripts/render.py --dsl tmp/<run_id>/B01/case05.snapshot     --out outputs/<run_id>/B01/case-05/final.png     --log tmp/<run_id>/B01/requests.jsonl --req-id B01-case-05-final --task B01 --kind final
```

服务渲染 3 次（含修正后的重渲染），全部请求见 `tmp/<run_id>/B01/requests.jsonl`；
过程版本、草稿与失败响应保留在同一临时目录。
