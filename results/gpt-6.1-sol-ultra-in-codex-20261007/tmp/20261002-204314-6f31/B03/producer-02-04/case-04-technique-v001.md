# 潜入蓝色 · 水族馆导览

三层真正嵌套ClipOval构成舷窗里的前景/中景/远景；岩石、鱼和形态块依绘制顺序构成静态深度，三个观察任务把图形实验转为参观动作

文档依据：已实际阅读缓存shared-doc-000004-readable.txt（来自https://snapshot.muedsa.com/ Parser参考），其中ClipOval最多一个子节点且可用ANTI_ALIAS；内部Container+Stack与Positioned形成真正子树裁剪；Container支持LINEAR/RADIAL渐变，参数不混用；Transform线与Opacity色值符合Parser。共享dsl.cjs只序列化字符串，不渲染图像。

算法与数据：每个380px舷窗内，318px中景ClipOval再嵌220px远景ClipOval；先远景，再中景，再前景，按照Stack顺序遮挡。水母每组6条触须，交替6/9px每步长度，10步显式计算长短；建议每区15min共45min。

应用：沿01浅礁、02水母光廊、03深蓝窗依次观看，并通过轮廓/触须/前后层完成三项观察任务

已知边界：这是静态平面遮挡形成的深度错觉，不声称真实3D或动态视差；形态不是物种准确复原，不报告生物尺寸/数量/生境事实。观察任务针对这张演示插画。 当前未由本代理请求服务或看图，真实能力成立与视觉阅读性必须由root实图确认。元素796，低于4096。原稿与脚本保留，所有主体/文本均DSL，不含Image资产。
