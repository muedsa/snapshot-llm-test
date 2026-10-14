# case-03 · 叠光烘焙实验室 手冲参数卡

**尺寸** 1080×1350 px ｜ **主作品** `final.png`（真实服务响应，与 `final.snapshot` 配对）｜ **完成标准引用** `tmp/<run_id>/B01/work-plan.json` v2

## 受众与使用场景

- 谁在用：站在吧台前、准备冲这一袋豆的顾客
- 要完成的事：照卡片参数复现杯测风味，并理解风味从哪里来
- 实际观看环境：随袋附送的印刷卡，也会被手机拍下

## 内容

烘焙度/产地/海拔/杯测分、风味轮、强度雷达多边形、15 秒冲煮时间轴、粉水比与水温建议；品牌与数值为自拟示例。

## 视觉选择（为什么这样画）

风味轮是真实极坐标构造：24 个扇区 × 3 环，用环形扇段路径绘制；雷达多边形与右侧柱状图共用同一组分数，因此两处永远不会互相矛盾；暖纸底色 + 咖啡色系。

## 实际自检

构建期审计 0 重叠 / 0 出界；扇区角度 360/24、多边形半径 = 分数/满分 × 半径，均在脚本中断言；看图修正了时间轴与说明文字的行距。

## 素材情况

无外部素材。

## 复现

```
python tmp/<run_id>/B01/case03_coffee.py     # 生成 final 同名 DSL 并打印布局审计
python tmp/<run_id>/_suite/scripts/render.py --dsl tmp/<run_id>/B01/case03.snapshot     --out outputs/<run_id>/B01/case-03/final.png     --log tmp/<run_id>/B01/requests.jsonl --req-id B01-case-03-final --task B01 --kind final
```

服务渲染 3 次（含修正后的重渲染），全部请求见 `tmp/<run_id>/B01/requests.jsonl`；
过程版本、草稿与失败响应保留在同一临时目录。
