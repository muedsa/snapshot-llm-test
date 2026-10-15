# B03 作品集 · DSL 创意边界十件

生成时间：2026-10-14T10:14:40+08:00

十件的场景、品牌与数据均为自拟示例，不代表任何真实记录；全部为纯 DSL，无 <Image> 与外部素材。

| 用例 | 标题 | 场景 | 手法 |
|---|---|---|---|
| [case-01](case-01/final.png) | 七月演出海报 | 社区爵士酒吧的月度演出海报 | ClipPath 双轮廓 + fillRule="EVEN_ODD" 挖出方环，镂空处直接放… |
| [case-02](case-02/final.png) | 夜跑队服背面 | 夜跑团的队服背面大字 | Text 的 foregroundMode="STROKE" 出空心描边字，再叠一层实心字错… |
| [case-03](case-03/final.png) | 潮汐预报卡 | 海滨城市的每日潮汐 | gradientType="RADIAL" 把每小时潮位映射成从中心向外的半径，半径越长潮越… |
| [case-04](case-04/final.png) | 慢转 33⅓ 唱片封套 | 独立厂牌的黑胶唱片封套 | gradientType="SWEEP" 画扇形色盘 + 同心圆环，模拟黑胶旋转的视觉隐喻… |
| [case-05](case-05/final.png) | 降水强度浮层 | 天气 App 的分区降水浮层 | ImageFiltered 高斯模糊作用在**同一份 DSL 里真实存在的底层图元**上，换… |
| [case-06](case-06/final.png) | 丝网印刷套色校样 | 独立书店海报的印刷校样 | ColorFiltered + Skia blendMode="MULTIPLY" 模拟油墨… |
| [case-07](case-07/final.png) | 冬至日日照分析 | 住宅方案的日照分析图 | 用 `Transform` 把**投影带**绕楼体中心摆成 09/11/13/15 四个真实… |
| [case-08](case-08/final.png) | 本周骑行成就章 | 共享单车的周成就卡 | ClipPath 用带 Q/C 命令的**曲线轮廓** + EVEN_ODD 挖出四瓣花形章… |
| [case-09](case-09/final.png) | 技术提示单 | 剧场演出当晚的岗位提示表 | 把同一套「状态条 + 标签 + 数值」塞进 6 行 × 5 列高密度表格，每格再嵌一层进度条… |
| [case-10](case-10/final.png) | 年度十佳展陈主视觉 | 独立书店的年度书单展陈 | 同一句话用四层 STROKE（不同粗细、透明度）叠出层次，并把最底层整体旋转 6°，做出丝印… |

逐件手法、文档依据、试验证据与边界见 [`technique-notes.md`](technique-notes.md)；大图见 [`gallery.md`](gallery.md)。
