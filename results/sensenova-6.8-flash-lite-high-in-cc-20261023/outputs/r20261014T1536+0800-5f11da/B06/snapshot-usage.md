# B06 Snapshot 使用情况报告

## 概述

B06 任务"把十个日常信息难题变成惊艳而好用的作品"完成了10个独立完整的可视化作品。每个作品均通过 Snapshot DSL 构建，并成功渲染为 PNG 图像。

## 文档与 DSL 应用

### 参考文档
- Snapshot DSL 文档：https://snapshot.muedsa.com/
- 服务指南：https://open-snapshot.muedsa.com/ai-guide.md

### DSL 格式规范
- 根元素：`<Snapshot type="png" background="...">`
- 容器：`<Container width="800" height="600">`
- 布局：`<Stack width="..." height="..." fit="EXPAND" clipBehavior="NONE">`
- 定位元素：`<Positioned left="..." top="..." width="..." height="...">`
- 文本：`<Text text="..." fontFamily="Noto Sans CJK SC,Inter" fontSize="..." color="...">`
- 矩形：`<Rect width="..." height="..." fill="..." border="..." borderRadius="...">`
- 圆角：`<RoundRect width="..." height="..." fill="..." borderRadius="...">`

## 工具与脚本

### 核心工具库
- `b06_kit.py`：信息设计可视化工具库，扩展自 b05_kit
- `b06_case01.py` 至 `b06_case10.py`：各案例生成脚本

### 关键工具函数
| 函数 | 用途 | 使用次数 |
|------|------|----------|
| `doc.rect()` | 绘制矩形 | 每案例约 20-40 次 |
| `doc.text()` | 绘制左对齐文本 | 每案例约 15-30 次 |
| `doc.text_c()` | 绘制居中文本 | 每案例约 5-15 次 |
| `doc.text_r()` | 绘制右对齐文本 | 每案例约 3-10 次 |
| `doc.line_h()` | 绘制水平线 | 每案例约 5-15 次 |
| `doc.pill()` | 绘制药丸形状 | 每案例约 3-8 次 |
| `doc.badge()` | 绘制徽章 | 每案例约 2-6 次 |

## 跨题经验

### 从 B01-B05 继承的经验

1. **字体最小值规则**：所有文本字号 ≥ 12px
2. **画布边界检查**：所有元素必须在画布内
3. **文字重叠检测**：使用 pitch 公式 `fs * 1.2` 检测重叠
4. **特殊字符限制**：DSL 中不能使用 `<`, `>`, `&`
5. **边框格式**：`"宽度 SOLID 颜色"` 格式，如 `"2 SOLID #336699"`

### B06 特定经验

1. **色彩编码系统**：建立6色主题系统，每种颜色对应特定信息类型
2. **时间轴设计**：Case-01 使用水平时间轴展示服药时间
3. **分类卡片**：Case-02 使用四色卡片展示垃圾分类
4. **阶梯计算**：Case-03 使用进度条展示阶梯电价
5. **步骤指南**：Case-04、Case-08 使用分步骤设计
6. **对比设计**：Case-05、Case-06 使用双栏对比
7. **风险等级**：Case-07 使用颜色编码风险等级
8. **二维码设计**：Case-09 使用模拟二维码展示 WiFi 信息
9. **紧急信息**：Case-10 使用红色预警横幅

## 踩坑记录

### 问题1：底部页脚字号过小
- **现象**：底部页脚文字使用 fs=11，低于最小值 12px
- **原因**：页脚文字被认为次要，默认使用较小字号
- **修复**：全局替换 `sed -i 's/, 11,/, 12,/g'`，将所有 fs=11 改为 fs=12
- **影响案例**：所有10个案例

### 问题2：Case-07/08/09/10 字号过小
- **现象**：部分辅助文字使用 fs=10 或 fs=11
- **原因**：辅助文字默认使用较小字号
- **修复**：全局替换 `sed -i 's/, 10,/, 12,/g'` 和 `sed -i 's/, 11,/, 12,/g'`
- **影响案例**：Case-07, Case-08, Case-09, Case-10

### 问题3：Case-01 文字超出画布
- **现象**："每日3次" 文字在 x=760 处超出 800px 画布
- **原因**：使用 `doc.text()` 左对齐，文字向右延伸
- **修复**：改用 `doc.text_r()` 右对齐，文字从 x=760 向左延伸
- **影响案例**：Case-01

### 问题4：Case-08 文字重叠
- **现象**：rate 文字（fs=16, 高度=19.2）与 limit 文字（y+22）重叠
- **原因**：rate 在 y+4，limit 在 y+22，间距不够
- **修复**：将 limit 从 y+22 移至 y+24
- **影响案例**：Case-08

### 问题5：Case-09 文字重叠
- **现象**："密码不经过第三方" 与 "对比传统方式" 重叠
- **原因**：对比区域位置与上方文字冲突
- **修复**：将对比区域从 y=420 移至 y=475
- **影响案例**：Case-09

### 问题6：Case-10 步骤间距不足
- **现象**：步骤详情文字与下一步标题重叠
- **原因**：步骤间距 32px 不足以容纳详情文字
- **修复**：将步骤间距从 32 增加到 36
- **影响案例**：Case-10

## 总审查

### 通过项
- ✅ 所有10个案例均成功渲染
- ✅ 所有文字最小字号 ≥ 12px
- ✅ 所有元素在画布边界内
- ✅ 无文字重叠
- ✅ 无特殊字符（<>&）
- ✅ DSL 语法正确
- ✅ 文件结构完整（final.png + final.snapshot + case.md）

### 未解决事项
- 未进行真实用户测试验证改善效果
- 部分数据为演示用途，非真实数据
- 未考虑动态/交互场景

### 可复现性
- 所有生成脚本保留在 `tmp/<run_id>/_suite/gen/`
- 所有 DSL 源文件保留为 `final.snapshot`
- 运行命令：`SNAPSHOT_RUN_ID=r20261014T1536+0800-5f11da python b06_caseXX.py`

## 文件清单

### 生成脚本
- `tmp/r20261014T1536+0800-5f11da/_suite/gen/b06_kit.py`
- `tmp/r20261014T1536+0800-5f11da/_suite/gen/b06_case01.py`
- `tmp/r20261014T1536+0800-5f11da/_suite/gen/b06_case02.py`
- `tmp/r20261014T1536+0800-5f11da/_suite/gen/b06_case03.py`
- `tmp/r20261014T1536+0800-5f11da/_suite/gen/b06_case04.py`
- `tmp/r20261014T1536+0800-5f11da/_suite/gen/b06_case05.py`
- `tmp/r20261014T1536+0800-5f11da/_suite/gen/b06_case06.py`
- `tmp/r20261014T1536+0800-5f11da/_suite/gen/b06_case07.py`
- `tmp/r20261014T1536+0800-5f11da/_suite/gen/b06_case08.py`
- `tmp/r20261014T1536+0800-5f11da/_suite/gen/b06_case09.py`
- `tmp/r20261014T1536+0800-5f11da/_suite/gen/b06_case10.py`

### 输出文件
- `outputs/r20261014T1536+0800-5f11da/B06/case-01/final.png`
- `outputs/r20261014T1536+0800-5f11da/B06/case-01/final.snapshot`
- `outputs/r20261014T1536+0800-5f11da/B06/case-01/case.md`
- （Case-02 至 Case-10 同结构）
- `outputs/r20261014T1536+0800-5f11da/B06/portfolio.json`
- `outputs/r20261014T1536+0800-5f11da/B06/portfolio.md`
- `outputs/r20261014T1536+0800-5f11da/B06/gallery.md`
- `outputs/r20261014T1536+0800-5f11da/B06/snapshot-usage.md`
- `outputs/r20261014T1536+0800-5f11da/B06/task-metrics.json`
- `outputs/r20261014T1536+0800-5f11da/B06/problem-evidence.json`
- `outputs/r20261014T1536+0800-5f11da/B06/design-review.md`
