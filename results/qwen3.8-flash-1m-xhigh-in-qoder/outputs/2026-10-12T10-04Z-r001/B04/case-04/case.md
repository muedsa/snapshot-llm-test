# case-04 · 文本度量：谁在决定一个字占多宽

- 形式：常数条 + 增量条图 + 精度表
- 画布：1400 × 1480，PNG 330,806 B，服务请求 `B04-case04-metrics-final`（200，3.265s）
- 页面版本：2 次渲染全部实际看图
- DSL：`case-04/final.snapshot`

## 这一页要回答的问题

- 每个增量数字给出请求 ID 与像素回读方法（42/28/10/0/22→53）
- em 常数标注为『在返回 PNG 上回读的近似』，不声称是内部实现
- smcp=0 像素变化必须与 tnum 的正增量并置，避免只讲成功
- audit overlap=0 outside=0

## 主张与来源

- **C008（测量）** CJK 1.00em、Latin 0.62em、Mono 0.52em、行距 1.46em、粗体余量 ×1.14+10px
  - 位置：五条常数｜来源：S09｜证据：B03-p2-textab、B03-p4-lineheight
  - 方法：在返回 PNG 上量墨迹范围与行顶间距，反推 em
  - 不确定：±1px，且不等于服务内部度量
- **C009（测量）** letterSpacing=6 → +42px、wordSpacing=14 → +28px、tnum → +10px、smcp → 0px
  - 位置：增量条图｜来源：—｜证据：B03-p2-textab、B03-p4-smallcaps
- **C010（测量）** 大写拉丁墨迹 ≈0.667em（模型偏小 7.6%）、小写 ≈0.538em（偏大 13.2%）、数字 ≈0.587em
  - 位置：精度表 4 行｜来源：—｜证据：B03-p2-textab
  - 不确定：墨迹宽度不含 sidebearing，只能给方向

## 自检

- 生成器审计：overlap_n=0、outside_n=0、below_min_font_n=0（文本度量：谁在决定一个字占多宽，见 `case04-metrics` 构建输出）
- 所有数字由 `b04data.py` 从真实日志计算，页面不手填数值
- 字节一致性：final.png 与服务响应 sha256 相同 = True
