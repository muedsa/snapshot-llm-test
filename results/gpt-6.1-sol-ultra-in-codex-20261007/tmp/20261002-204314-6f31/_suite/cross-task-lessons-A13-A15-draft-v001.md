# A13–A15 跨题经验草案

运行 20261002-204314-6f31。状态 draft_pending_root_review；root审查后再整合。只读已completed记录，本次HTTP/render/view均0，既有文件不改。

A13-lesson-small-size：两个实际512方向及32缩略先看再选；选中A在32px下笔画偏细。 同一几何方案stroke32→40、radius40→48，frame/offset不变。 再次render及512/32实际查看确认笔画更稳，中央共同负空间仍开放；计1完整视觉迭代，方向B探索另计。 边界：缩略图需要真实生成/查看；不能仅凭512图推断32px表现或把方案探索计为视觉修复。

A13-lesson-alpha-exception：原alpha精确相等=false，154像素不同；both-partial条件也false，8处为0→1边缘。 保留失败判定，单独核对相同DSL几何、实际圆角边界位置、alpha255差异与>=128轮廓。 154差值最大1；8个0→1点和全部差点到几何边界≤0.6175884698832999px；无全不透明差异，>=128轮廓一致，alpha>0支持仍不同。题目允许AA，因此几何要求通过，原false不改。黑非透明像素RGB违规0。 边界：这不是全图字节相等，也未查明渲染内部原因；AA许可必须来自当前题目，不能泛化成任意误差许可。

A13-lesson-transparent-preview：纯黑透明PNG在工具黑色显示背景下看不到轮廓。 另生成白底512 QA与32缩略/最近邻放大并实际打开；不修改最终服务PNG。 root views17–21检查黑色叠框和中央开口，RGBA量化另判透明；不能从显示背景猜alpha。 边界：QA复合/裁片仅供检查，不作为最终字节，也不作为主体DSL素材。

A14-lesson-common-wrap-rule：首图K03孤字级独占末行，K07将视觉拆成视/觉检查。 按CJK1/ASCII0.55视觉units统一分档；48px档上限26→22，>26 units活动宽920，外层区域仍1072×252；无ID特例、无人工换行或源串改写。 K03改44px成为1行；K07/K08改44px且自然2行更均衡。仅3受影响卡真实重新render/view，各计1完整视觉迭代；其他5合格原服务图保留。 边界：长度权重是本版Inter/CJK布局的工程近似，须真实逐卡回归；不能由规则存在自动断言任意文案都无孤字。

A14-lesson-source-and-state：混合文案含< > &、斜线、双破折号、中英文名与中文引号；取消卡仍有应保留信息。 40叶源字段各由单个Text/Raw CDATA保留，依服务自然换行；状态用原文字+颜色+勾/方块/钟/叉编码，取消仍保留标题/讲者/13:40。 K04/K05字面特殊符号、K07长讲者与——/·、K08引号真实看图可见；源审查40字段完整，取消信息未被删除或整卡灰化。 边界：Raw保真不替代实际可读性与字符/换行检查；色彩需要文字/符号协同编码。

A15-lesson-separate-geometry-font：结构已对齐时，首图main字墨右边仍多20px，sections多11/12/14px。 独立测量卡片边界/grid/bar数据比例与字墨ROI；main/KPI34→32、sections24→22，微调y/墨色，保持所有几何/数据/原串。 18结构锚点四象限/图表/表格最大0px；grid405/441/477/513/549，0–120高144，每千元1.2px；一次字体视觉迭代后selected标题bbox匹配，KPI剩1px纵向差异。 边界：纯色墨迹bbox和阈值ROI都不是Text布局框/基线；不能因结构对齐就跳过字体检查。

A15-lesson-honest-residuals：独立阈值字墨与制作方纯色字墨方法边缘支持略有差别；最终3KPI仍低1px。 保留两种真实测量方法与原证据，comparison写明颜色/字形/AA残差；未测整图pixel residual用null。 七个选中标题/数值ROI最大误差1px只证明该子集；root最终原图、720缩略和chart/table局部真实对参考再查，未宣称逐像素全同。 边界：0px结构/部分bbox匹配不能推断全图像素误差0；QA查看复用真实记录不能计为本次新查看。

A01-lesson-new-view-metadata：早期view2/3有真实工具/时间/sha/观察但无显式reviewer；补充view4真的再次打开原交付图，误标version A01-v001。 原日志保留；新增真实view4显式root身份。另写独立metadata correction指向正确A01-v003、同一PNG hash，不重复看图、不冒称旧记录root身份。 view4实际文件sha与最终artifact/原服务图一致；更正文件正确指向A01-v003。新物理查看仅1次，版本更正不是第二次查看。 边界：身份缺字段不能从文件存在补造；元数据更正和新的物理图像感知必须分别留痕/计量。

A13-A15-lesson-actual-tools：三题实际应用Node纯DSL构造、真实Snapshot POST/view_image、Python/Pillow只读像素及QA；文档/fonts使用已真实取得缓存。 工具使用引用实际脚本输出/测量及view事件；库可用性、未调用能力不算使用。原PNG字节保留，QA不替代主体DSL。 三题顶层document/other-service请求均0；既有实际render/views按其日志统计。A13本地alpha脚本SyntaxError由v002修复，其失败不是HTTP失败或新增render。 边界：本草案没有新增HTTP/render/view，不把读取历史观察算新的感知；token/图像输入/费用未知null，不推造账单或使用记录。

详细实际request/version/view/iteration、测量字段与116个源文件指纹见[同名JSON](cross-task-lessons-A13-A15-draft-v001.json)。源路径均核对存在，引用服务字节与记录hash一致；本次没有重新看图。

关键入口：
- [A13报告](../../../outputs/20261002-204314-6f31/A13/snapshot-usage.md) · [原alpha失败](../A13/independent-analysis/alpha-rgb-audit-v001.json) · [AA补充](../A13/independent-analysis/alpha-edge-exception-evidence-v001.json)
- [A14报告](../../../outputs/20261002-204314-6f31/A14/snapshot-usage.md) · [通用规则](../A14/production/generation-rules-v002.json) · [逐卡audit](../../../outputs/20261002-204314-6f31/A14/batch-audit.json)
- [A15报告](../../../outputs/20261002-204314-6f31/A15/snapshot-usage.md) · [比较说明](../../../outputs/20261002-204314-6f31/A15/comparison.md) · [结构/残差audit](../../../outputs/20261002-204314-6f31/A15/reconstruction-audit.json)
- [A01新真实查看](../A01/supplemental-root-review-v001.json) · [独立标签更正](../A01/supplemental-root-review-metadata-correction-v001.json)

三题当前题级统计仅作草案来源快照，未加shared或A01补证，也未重加case/round；不代表全套完成。未知token/图像计费/费用为null。
