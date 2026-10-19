# A10 · compositing-lab（透明合成与滤镜语义实验板）— 使用记录

题面：`tasks/A10-compositing-lab/TASK.md`。1440×1100 六格实验板，六格 320×240 白底实验区（3列×2行，间距32，区外编号+三行说明），σX=σY=6 全题统一。

## 实际产物（路径基准 = 本题输出根）

| 文件 | 说明 |
| --- | --- |
| `compositing-lab.png` | 1440×1100，服务原始 PNG（285,048B，v08 定稿） |
| `compositing-lab.snapshot` | 同名完整 DSL（六格每格均为 ClipRect 包裹的 320×240 内嵌 Stack） |
| `composite-audit.json` | panels 6（原点/局部坐标/场景参数/效果节点）+ paired_scenes 2（③④、⑤⑥共用参数/唯一差异/圆剪几何）+ alpha_models 2（128/255 vs 0.5 全推导）+ samples 6 + visual_checks 6（含文档引证）+ 汇总 |
| `task-metrics.json` | renders 8（ok 8/fail 0）/ iterations 7 / views 7 |
| 过程 | `tmp/<run_id>/A10/`：build_a10.py、finalize_a10.py、patch 脚本；steps/ 24 张（v2–v8 六格+关键放大） |

## 六格实现与像素级结论

- **①逐矩形 alpha**：`color="#FF000080"/"#0000FF80"`（DSL 8 位颜色=#RRGGBBAA，末组 alpha——题面 HEX 即 DSL HEX）。模型：蓝 over 红 over 白，中间不取整、末位 floor(v+0.5)：重叠 (180,100) 理论 **(127,63,191)**——要点是红残余 G=127 被半透明蓝**二次衰减**为 (127/255)²·255≈63.25。实测 (127,63,191,255) **逐通道误差 0**；非重叠红/蓝区 (255,127,127)/(127,127,255) 亦精确。
- **②组 opacity**：`<Opacity opacity="0.5">` 包完全不透明红/蓝——组内先不透明合成（重叠=纯蓝）再整体乘 0.5：理论 (128,128,255)。实测 (126,126,255)，误差 2 ≤3（运行时把组层 alpha 量化，α_eff≈129/255，红/蓝单区与重叠区三样本一致；**推测**为 Skia saveLayer 字节量化，标注为推测）。两格 B 相差 64（191 vs 255）、G 相差 63——128/255 与 0.5 的语义差别在图上直接可辨。
- **③仅背景模糊**：`ClipRRect(r20)→BackdropFilter(6,6,CLAMP)` 从既有背景（全幅条纹）取材，玻璃 `#FFFFFF59`（白 35%）；SHARP 文字与前景条/方块清晰，卡外条纹锐利、无外溢。**④**：同 `ClipRRect(r20)→ImageFiltered(6,6,CLAMP)`，子树=白底+同相位条纹复刻+玻璃+BLUR 文字+同前景，白底+条纹+前景+文字整块糊；与③唯一差别=模糊作用层。配对共用：卡 240×160 r20 @(40,40)、条纹 #5B7395 宽28/节距56/相位0、玻璃、文字 24px、σ6。
- **⑤MULTIPLY+子树模糊**：`ColorFiltered #F6B94A blendMode=MULTIPLY → ImageFiltered(6,6)`；白→琥珀、#8EC3F0 底景→橄榄、深块近黑、#F2C94C 芯片+33% 黑阴影晕清晰可辨；绘制边界内透明间隙被一并命色（与 faq 缓存句「SRC、MULTIPLY 等混合模式还可能给绘制边界内的透明间隙着色」完全吻合）；无裁剪=铺满实验区。**⑥**：外层 `ClipOval`（盒 (60,20,200×200)→圆心(160,120) r100）：圆内=滤色+模糊、圆外=同一场景锐利原色，底景与两深块均跨圆周，边界锐利无晕。
- 条纹节距从 28 改 56：σ6 高斯对不同节距的余留对比不同（28 节距几乎均化），56 节距保留约 64% 低频对比，使「背景模糊 vs 锐利」可读。

## DSL/工具应用（本题新增语义点）

1. **8 位颜色格式 = #RRGGBBAA（末组为 alpha）**（parser-tags.txt 缓存原文：「#FF000080 是约 50% 透明红色」）。此前把 8 位当 AARRGGBB 读——`#B3FFFFFF` 实为**全不透明青色**，这是本题 ③④ 平色的根因；阴影 `#3A000000` 同理实为暗红全不透明。修正后 `#FFFFFF59`（白35%）与 `#00000055`（33%黑）语义正确。
2. **四个效果标签**（painting.txt 缓存）：`Opacity` 整子树合成一层透明度；`ColorFiltered` 绘制边界可确定时限作用范围（**合法溢出与阴影也包含在内**——芯片阴影被 MULTIPLY 命色即此）；`ImageFiltered` 按 sigma 自动提供输出边界（嵌 ColorFiltered 无需 outputBounds）；`BackdropFilter` 读取已有背景、需 ClipRect/ClipRRect 限定、背后无内容则无可见效果。
3. Stack 默认 HARD_EDGE 对「阴影/变换/更深子孙」越界不一定触发裁剪（parser-tags 缓存）→ 六格统一**显式 ClipRect** 兜底，σ6 模糊光晕不出区框。
4. estw 对「?!ASCII+CJK 混排粗体标题」仍会低估（连续两起：④、⑤ 标题实宽超估），本题把相邻列标题改短（机制名保留在说明带与 audit），WARN=0 后仍以实际渲染复查列距。

## 踩坑与修复链（7 迭代全记录）

v02 基线（首个查看版本；v01 同 DSL 先行渲染未采用）→ v03 换玻璃值（误诊，无效）→ v04 条纹节距 56（改善卡外对比）→ v05 **格式根因修复**（#RRGGBBAA）→ v06 阴影 0x55（1× 可辨）→ v07/v06 说明文字相挤两连修。每轮均有请求/放大件/复查看图留痕；v08 定稿。

## 交付与证据

- 指定 PNG+同名 .snapshot ✓；composite-audit.json 含 samples_summary（6/6 通过、max err 2、alpha 全 255）与 visual_checks（六条观察均引用缓存 docs 原文，文档缓存路径以 `path_base: suite_root` 标注）。
- 查看证据：steps/ v2_p*、v3_p3、v4_p3、v5_p3/p4/p6、v6_p1..p6+v6_chipA、v7/v8_row2desc；整图终审两次（v06、v08）。
- 无 4xx/429；八次渲染全部 200。
