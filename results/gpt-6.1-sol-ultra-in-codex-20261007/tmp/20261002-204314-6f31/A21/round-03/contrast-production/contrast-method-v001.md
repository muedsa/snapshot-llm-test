# A21 第三轮实际背景对比度专项

结论 通过；20Text/200真实背景样本；最低比率 6.545617:1，普通文字阈值4.5:1。

使用真实PNG直接解码RGBA。源背景为整幅TOP_LEFT→BOTTOM_RIGHT不透明线性渐变，其他四光片的实际paint bbox与所有Text框不相交，无Alpha/滤镜/阴影文字。对各Text框每个像素沿等投影整数格移到源证明没有前景的原图边缘，取实际同一梯度RGBA；比率使用正确sRGB线性化/相对亮度，非仅比较两端色。

每Text确认实际PNG存在与DSL字色完全相符的前景核心；四角、四边/中心和最暗区域共10样本，每个样本的5×5全25像素均与同投影原图背景相符，排除前景/抗锯齿。另对整Text框全部重建实际背景取最差比率，覆盖实际字形下渐变。

|图|Text|字色|最低实际10样本|整框保守最差|核心像素|
|---|---|---|---|---|---|
|portrait|sponsor|#42585B|6.9073|6.9073|1285|
|portrait|free|#215E52|6.5456|6.5456|2085|
|portrait|brandCN|#1D3435|12.2470|12.2470|5553|
|portrait|brandEN|#215E52|6.8289|6.8289|2275|
|portrait|eyebrow|#42585B|6.8467|6.8341|925|
|portrait|tagline|#1D3435|11.5651|11.5651|20564|
|portrait|date|#215E52|6.6167|6.6167|4357|
|portrait|speakers|#1D3435|11.4693|11.4693|1509|
|portrait|english|#42585B|6.5789|6.5789|557|
|portrait|url|#42585B|6.5668|6.5668|994|
|wide|sponsor|#42585B|6.6975|6.6975|1285|
|wide|free|#215E52|6.5456|6.5456|2085|
|wide|brandCN|#1D3435|12.2694|12.2694|4090|
|wide|brandEN|#215E52|6.8850|6.8850|1659|
|wide|eyebrow|#42585B|6.8467|6.8467|595|
|wide|tagline|#1D3435|11.8018|11.8018|21672|
|wide|date|#215E52|6.7646|6.7646|2821|
|wide|speakers|#1D3435|11.8018|11.8018|1153|
|wide|english|#42585B|6.7739|6.7739|557|
|wide|url|#42585B|6.7739|6.7739|994|

完整证据：[contrast-audit-v001.json](contrast-audit-v001.json)、[原像素5×5样本](raw-pixel-background-samples-v001.json)、[方法脚本](compute-contrast-v001.cjs)。

unresolved=[]；all_writes_finished=true。新增HTTP/render/view均0；本计算不代替root的实际视觉回归。
