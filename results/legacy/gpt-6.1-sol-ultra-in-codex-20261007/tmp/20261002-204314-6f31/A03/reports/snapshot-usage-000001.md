# A03 · 多层语义故障恢复

制作与生产者自检完成：真实服务返回的1280×800 system-pulse.png与完整同名DSL已发布；最终路径再次实际打开。repair-log.json逐项保存原稿行列位置、真实报错、静默属性与实际视觉问题，共18项，包括所有失败响应和后续滤镜问题。主代理负责追加独立真实查看及关闭任务，本生产者未提前taskEnd。

输出目录：D:\workspaces\gpt-6.1-sol-ultra\outputs\20261002-204314-6f31\A03
临时目录：D:\workspaces\gpt-6.1-sol-ultra\tmp\20261002-204314-6f31\A03

## 原稿真实提交与错误层次

开始时先将inputs/broken.snapshot原样提交POST /snapshot。原文件、首个请求体与保存input.snapshot的SHA-256均为7490a8cd2cb36b6e101c11b533c6eb00cf205ddd8963ddbd0603a15c3955cbbe，证明没有先修稿后补造原稿过程。第1次真实400 PARSE_ERROR是padding格式错误(position92)，仅修内边距后第2次真实400是matrix缺失(position475)；补真实矩阵后第3次400 RENDER_ERROR为renderBox.parentData must be StackParentData；移动LIVE到Stack后第4次400为Layout size is infinite。四个原始JSON、requestId、请求时间、响应头与逐次DSL均保留。render错误没有源码position时记录null，不捏造解析器行号。

第5次先修有限画布后真实200并实际看图，仍见标题变小且居中、单巨大USAGE黑字、LIVE缺标签、不透明青色REVIEW且小字位置错、ImageFiltered连说明文字一起模糊、缺两项指标与背景条纹。此时不把HTTP成功当成修复完成。根Snapshot width/height、Text font-size与Transform rotate属于文档明确未知而被忽略的属性；matrix缺失则是独立真实PARSE_ERROR，两者在repair-log中分开。

## 完整需求与几何

根Container准确1280×800并先画#0B1220底。标题System Pulse字体44，左上(32,32)。三个等宽卡宽(1216−48)/3=389.3333333333333、间隔24，保留USAGE72%并补LATENCY148ms/SUCCESS99.2%，三文案均28白字。LIVE框(1152,42)96×36，独立于标题。说明卡(390,325)500×150，中心恰为(640,400)，圆角24，文字Background-only blur为28。四条4/5px彩条从x32到1248，真实同时穿过左右边界x390/890。

REVIEW未旋转框(1080,696)160×56，中心(1160,724)，使用列主序16项−8°旋转矩阵及CENTER。屏幕y向下，右向单位向量变为(0.9902680687415704,-0.13917310096006544)，右侧升高即视觉逆时针8°。绘制bbox约[1076.8817076737926,685.1386459984309]到[1243.1182923262074,762.8613540015691]，完整落在32安全区域。背景#FFFFFF33中51/255=20%透明度在末两位，Text#FFFFFF字体24不透明，没有整体Opacity降低文字。原#33FFFFFF是RGB(51,255,255)且alphaFF，不是20%白。矩阵DSL仅浮点序列化到6位小数，几何计算与独立审计一致。

## 三次真正的视觉迭代

第5次诊断PNG→第6次完整语义修复：字体/三卡/LIVE/REVIEW/alpha/安全布局与清晰前景恢复；实际全图再局部检查仍发现SRC_OVER留下卡内原锐利细线，仅增加模糊光晕。

第6次→第7次：改文档支持的BackdropFilter blendModeSRC，真实同区域裁片证明卡内锐利中心线消失、卡外仍锐利，但卡内变明亮浅色，白字对比不足。该版本保留且未接受。标题生成框top31也校正为严格32。

第7次→第8次：唯一进一步变化是在滤镜之前让根Container实际绘制不透明#0B1220底。真实全图与相同局部现在是深色柔和背景，卡内没有原锐利细线，卡外仍锐利、28白色说明字清晰。ClipRRect在BackdropFilter外层限定500×150圆角区域；Text作为未受模糊的前景子Widget。仅设置Snapshot.background在此实际服务案例中不足以给SRC过滤提供已绘制深底；结论限定于本次实际对比，不臆测更广泛实现。最终原图也已实际打开，与第8次服务PNG原字节一致。

每次visual记录都有实际before/afterview、修改与比较；baseline、syntax-fix、visual分开，重试为0。局部QA图仅保留在临时目录，不作为最终作品或后处理图片。原稿已有SystemPulse/USAGE/LIVE/REVIEW/说明块全部保留，替换的是错误布局脚手架并补足需求，没有删除出错内容块。

## 文档、能力与留痕

实际复用并阅读共享服务指南、parser注册标签/属性、真实字体列表与根代理新取得的官方BackdropFilter/Transform资料：tmp/20261002-204314-6f31/_suite/shared-doc-000001-response.txt；tmp/20261002-204314-6f31/_suite/shared-doc-000004-readable.txt；tmp/20261002-204314-6f31/_suite/shared-fonts-000001-response.txt；tmp/20261002-204314-6f31/_suite/requests/shared-request-000001/readable.txt；tmp/20261002-204314-6f31/_suite/requests/shared-request-000002/readable.txt。原请求与响应均在shared保存，本题没有把复读缓存重复计为新HTTP请求。字体使用真实Inter,Noto Sans CJK SC。纯Snapshot/Container/Stack/Positioned/Text/Raw/Transform/ClipRRect/BackdropFilter构图，无外部素材、无Image、无SVG或预绘主体资产。UTF-8纯文本POST，成功image/png才可发布；所有失败JSON准确保留且不会伪装图片。

repair-log.json保存源码定位、四个真实错误、每个版本/响应、实际几何与验证、全部实际查看事件。requests.jsonl、versions.jsonl、iterations.jsonl、views.jsonl、tool-usage.jsonl和不可覆盖的脚本/草稿/QA裁片全部保留。独立semantic-review-v02.json是文档及几何核算，原本明确没有服务/看图证据；真实错误与图片证据由本生产流程补足，不将建议位置当成实际位置。

## 真实消耗与状态

生产者Snapshot请求8：成功4、失败4、重试0。DSL版本8、语法修复版本4、完整视觉迭代3、实际看图8（其中3个局部、1次最终路径）；最终PNG1张。文档新增请求0，额外实际官方文档只累计在shared。请求耗时之和19.548206200000003秒，与任务墙钟分开；用户等待0、确认未发生限流等待0，未充分测量队列等待保持null。动态指标按真实起点计算，主代理taskEnd时才补结束时间并汇总其真实交叉查看。

平台未提供实际token、图像输入或账单费用，usage全部相关字段为null并说明来源缺失，不按字数猜费用。检查点A03-producer-finished可恢复；当前没有未解决内容/视觉问题。
