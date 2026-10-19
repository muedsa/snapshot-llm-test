# A13 · brand-delivery（品牌标志到完整活动应用）— 使用记录

题面：`tasks/A13-brand-delivery/TASK.md`。虚构品牌「叠光 / Layerlight」（概念：信息叠加后仍然清晰）；两个几何方向预览 → 选型 → 四件最终应用 + 32px 预乘审查 + 纯黑合规。

## 实际产物（路径基准 = 本题输出根）

| 文件 | 说明 |
| --- | --- |
| `symbol-color.png` + `.snapshot` | 512×512 透明彩版标志（三片 α FF/B8/CF + EVEN_ODD 孔，76,52B → v02 7,652B） |
| `symbol-black.png` + `.snapshot` | 512×512 透明纯黑版（同几何；RGB 恒 0，alpha 分层，v02 4,471B） |
| `brand-banner.png` + `.snapshot` | 1200×400 纸白横幅（v02）：左标志 f=0.375 + 「叠光 Layerlight」基线对齐 + 金/天蓝双条 + 标语 + 底线说明 |
| `launch-poster.png` + `.snapshot` | 1080×1350 墨蓝海报（v03，独立构图）：标志 260px 居中 + OPEN BETA 金 pill + 纵向双行名字 + 标语 + 2026.11.07 · ONLINE + 官网 + 金轨 |
| `brand-system.json` | 色彩/比例（片 220² r36 步进48、孔 r36@片心）/构件表（3 母形 + 负空间规则不计数）+ 计数依据 3≤6 + 各应用 DSL 映射 + 隔离区 + 32px 行为 + 审计结果 |
| `rationale.md` | 194 字（≤300）：两方向差异、看图选择依据、小尺寸改进 |
| `task-metrics.json` | renders 11 全 200 / views 4 / iterations 4 |
| 过程 | `tmp/<run_id>/A13/`：dir-a/dir-b 预览 PNG（题目要求保留于临时目录）、build/build_dirs/audit/finalize/crops 脚本、steps/（两方向纸底合成、32px 全套、lockup/mark 放大件、size-audit.json） |

## 方向探索与选型（真实看图）

- dir-a 叠层方片 / dir-b 光棱山形（双三角+日轮）各 512×512 透明渲染，纸底合成后查看：A 的三层深浅、片间 L 形缝隙与孔点在 32px 仍可辨；B 双三角缩到 32px 融为实心楔形、隐喻偏景观 → 选 A，理由与改进写入 rationale.md。

## 几何与传递

- 同一 `mark()` DSL 几何生成器产出四应用（512/symbol×2、banner f=0.375、poster f=0.5078）——只平移/缩放母坐标，不嵌任何 PNG；放大件验证同构。
- 构件计数：圆角方形 ×3 = 3 ≤ 6；负空间（片间步进露底 + EVEN_ODD 圆孔挖除）记录规则不计数。
- 小尺寸改进落实：顶层 α 45%→81%、孔 r30→36。

## 合规审计（脚本：audit_a13.py，参数入 brand-system.json）

- 黑版纯黑：非预乘解码，alpha>0 像素 RGB=0 违例 **0**；alpha 活跃区间 [1, 255]。
- 两版几何同构：64 格 alpha≥8 二值掩码对称差 **0**。
- 彩版 alpha 直方图主峰 255 / 242 / 207 / 184 与三层叠算精确对应（三片 FF、P2∩P3≈94.7%、CF 81%、B8 72% 截止设计一致）。
- 32×32 预览：预乘 → LANCZOS → 反预乘（保 alpha），浅底合成实际尺寸查看（彩/黑均通过：轮廓、三层深浅、孔点可辨），另存 8× 边缘放大件；Pillow 10.0.0，参数与管线记录于 size-audit.json。

## 迭代链（4 rounds / 11 requests，全 200）

- p00 alternative：两方向预览渲染 + 查看 → 选 A。
- v01 baseline：彩版发现孔心坐标系错误（孔成月牙伪影，位于标志右下角）。
- v02 visual：mark() 孔心改片内局部坐标，四应用同规则重渲；横幅/黑版通过，大屏发现「叠光/Layerlight」同轴碰撞。
- v03 visual：大屏标题改纵向双行 → 终审通过。

## 交付与证据

- 四终图均为真实服务 PNG + 同名 .snapshot；无 429/认证问题；无失败请求。
- 缺陷链真实留痕（孔坐标 → 同构修复 → 标题碰撞 → 纵排）。
- 未解决事项：无。
