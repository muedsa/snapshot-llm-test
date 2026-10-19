# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
R = "20261016T164020-m1"
rows = [
    {"id": "A09-s01", "parent": None, "type": "baseline", "image": "transform-atlas.png",
     "dsl": "transform-atlas.snapshot", "request_id": "d3fa58e6-6c93-4fd0-a516-ed90fd0c8f42",
     "observable_issues": [
         "12个印章主体整体缺失于格内，离群聚集在图例带与格间缝隙（T05 完整镜像样本在(364,1080)带、T02/T06 在缝隙露头）",
         "根因：矩阵平移分量误填锚点偏移 A，渲染语义 canvas=A+M·p 造成双重平移"],
     "changes": [
         "v01 渲染 200 后整图+z0_a_gap/z0_b_legend/z0_c_T01/z0_d_T07cell 放大+色块连通域统计（probe_colors.py）逆向定位",
         "矩阵平移分量改为局部平移 t=pivot−K·pivot，锚位保持 A=C−pivot"],
     "comparison": "见 v02", "recheck": None,
     "id": "A09-s01", "seq": 1, "path_base": "suite_root", "viewed_at": "2026-10-17T14:21:31+08:00"},
    {"id": "A09-v02", "parent": "A09-s01", "type": "visual", "image": "transform-atlas.png",
     "dsl": "transform-atlas.snapshot", "request_id": "37081b07-a867-45c2-a79d-2bf2844c45f2",
     "observable_issues": [
         "12枚印章全部落格且姿态正确：T02 顺转90°红条在上墨点东南，T03/T04 反向，T07 墨点东北 vs T08 墨点西北（顺序差异可见）",
         "T10 墨点为 20×12 椭圆（随阵变换）",
         "顶部徽标（4 列×3 行·格 300×250·间距 32）尾段被裁，只显示到（间距）"],
     "changes": [
         "徽标框 320→460（END 对齐实际字宽超出估值，加强 fit 余量）",
         "v2_badge/v2_t0708/v2_t11aa/v2_t10 放大核查"],
     "comparison": "与 v01 相比：主体从离群簇回到各格中心（格心=枢轴映像），姿态与矩阵预测一致",
     "recheck": "徽标修复待 v03",
     "id": "A09-v02", "seq": 2, "path_base": "suite_root", "viewed_at": "2026-10-17T14:28:12+08:00"},
    {"id": "A09-v03", "parent": "A09-v02", "type": "visual", "image": "transform-atlas.png",
     "dsl": "transform-atlas.snapshot", "request_id": "9709540e-f4b0-46af-bfaa-826159568cf4",
     "observable_issues": ["整图定稿复查：标题/徽标/图例齐全，徽标完整显示（间距 32）"],
     "changes": [
         "无新改动（徽标加宽生效）",
         "measure_a09.py 逐格量测 72 组写回 geometry-audit.json verification"],
     "comparison": "量测：轴对齐格矩形/墨点全部 ≤1px；T11/T12 斜边最大 2.105px 且同向内收（反走样例外已文档化）；墨点质心全 ≤1.5px（暗色掩膜限定预测邻域 24px，排除格内标签文字）",
     "recheck": "passed",
     "id": "A09-v03", "seq": 3, "path_base": "suite_root", "viewed_at": "2026-10-17T14:33:05+08:00"},
]
with open("tmp/%s/A09/iterations.jsonl" % R, "w", encoding="utf-8") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print("iterations", len(rows))
