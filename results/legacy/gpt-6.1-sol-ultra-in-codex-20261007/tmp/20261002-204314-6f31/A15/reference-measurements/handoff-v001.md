# A15 参考图独立像素测量

源图 `tasks/A15-reference-reconstruction/inputs/reference.png`，1440×900。SHA256 `225cb5c61063a60a6b7248cdeea54dc1d704e5c1cb5989c0d58cf81afcba0d09`。只读原PNG，不访问参考生成源码或评分资料。

`reference-pixels-v001.json`保存18个准确采样点、颜色分布、逐行/列纯色run和13个纯色连通域。`reference-anchors-v001.json`有30个锚点，含四象限、图表零线和表格。矩形右/下坐标采用exclusive；连通域栅格bbox在像素文件中明确采用inclusive。重建坐标与误差保留null，待制作方/root量实际服务PNG。

|区域|实际参考矩形 [左,上,右,下)|方法|
|---|---|---|
|Revenue|[260,138,616,282)|局部#E2E8F1边框像素min/max|
|Orders|[644,138,1000,282)|同上|
|Refund Rate|[1028,138,1384,282)|同上|
|Net revenue|[260,310,1002,596)|同上|
|Team activity|[1030,310,1400,596)|同上|
|Recent projects|[260,624,1400,842)|同上|
|Overview选中|[18,116,202,164)|#294467连通域|
|Export按钮|[1184,43,1400,91)|#245CE4连通域|
|Workspace卡|[22,752,198,868)|#233954连通域|
|Table header|[284,688,1374,722)|#F3F6FB连通域|

侧栏背景#14233C、主背景#F3F6FB、白卡#FFFFFF、边框#E2E8F1、主体墨色#18283F、薄荷#64DBB6、按钮/柱#245CE4、grid#E7EDF5、表格分隔线#EBEFF5。状态pill蓝/黄/绿fill分别#E7EFFF/#FFF3D7/#DCF5EC。

图表x[333,970)，网格y405/441/477/513/549，zero549；6柱宽54，几何centerx384+101i。实测纯色bbox上端y485/463/474/441/452/420，底端inclusive548。依据真实数据和测得144px图高推导的几何top为484.2/462.6/473.4/441/451.8/419.4，明确属于亚像素估计，不声称知道参考DSL。

两条表格分隔线x[284,1374)，y760/795；status pill[1028,729/764/799,1176,757/792/827)。标题纯色墨迹bbox[261,39,594,69)，图标题[286,336,413,352)，表标题[286,646,453,666)，这些是排除AA外沿的墨迹边界，不能等同Text block原点/基线或据此断言字体。

真实视觉检查共7次：原始PNG、720×450缩略、top-left/chart/table/right-card/workspace-bottom五块QA。`actual-reference-views-v001.json`保存各真实工具调用时间和观察。QA复制原图保留源字节，所有裁片只供检查，禁止作为复刻DSL的Image素材。没有服务请求、渲染、修改最终图或失败；Pillow getdata弃用警告保存在执行记录。该独立查看记录尚未自动并入题级views日志，由root归并一次。
