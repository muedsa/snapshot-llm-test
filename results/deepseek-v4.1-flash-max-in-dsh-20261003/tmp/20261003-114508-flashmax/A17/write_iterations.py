import json, os, sys
sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\_suite\shared")
from suite_common import append_jsonl_nobom, write_json, ROOT
TMP = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A17"
p = os.path.join(TMP, "iterations.jsonl")
open(p, "w", encoding="utf-8").close()
def it(**kw):
    kw.setdefault("run_id", "20261003-114508-flashmax")
    kw.setdefault("task_id", "A17")
    append_jsonl_nobom(p, kw)

it(iteration_id="A17-IT-01", version="probe-metrics/probe-advance/probe-size", parent=None,
   type="baseline", purpose="量测服务端真实字形度量，作为全部排版计算的基础",
   images=["probe-metrics.png", "probe-adv.png", "probe-size.png"],
   viewed_at="2026-10-03T13:00:00+08:00",
   observed="等宽字步进=0.603x字号，CJK=1.0x字号，大写字高=0.75x字号；dslkit 的 0.60 与实测一致",
   change="把这些比例固化进 hbkit.adv()/text_w()，所有文字宽度先算后放",
   recheck="probe-adv.json 用墨迹列回归验证；后续 4 页再未出现因算错宽度导致的换行")
it(iteration_id="A17-IT-02", version="probe-alpha/probe-cdata/probe-ltgt2", parent="A17-IT-01",
   type="alternative", purpose="确认 Tail alpha 与 Raw/CDATA 语义",
   images=["probe-alpha.png", "probe-cdata.png", "t-ltgt2.png"],
   viewed_at="2026-10-03T13:01:00+08:00",
   observed="&lt; 不被解码（渲染成字面 &lt;）；Raw+CDATA 保留空白与尖括号；#1D4ED800 不绘制；letterSpacing 生效",
   change="第 3 页结论改为“必须用 CDATA”，并把实体不解码写进正文与示例",
   recheck="example-03 最终图里同时出现裸写与 CDATA 两种写法的实际结果")
it(iteration_id="A17-IT-03", version="handbook-01.v1", parent=None, type="baseline",
   purpose="首版 4 页 + 4 示例全量渲染",
   images=["handbook-01.v1.png", "handbook-02.v1.png", "handbook-03.v1.png", "handbook-04.v1.png",
           "example-01.v1.png", "example-02.v1.png", "example-03.v1.png", "example-04.v1.png"],
   viewed_at="2026-10-03T13:02:30+08:00",
   observed="Page1 卡片1 文字溢出卡片、第 3 条要点被插图盖住；代码块退化成 &lt; 实体；example-02/04 报 Layout size is infinite",
   change="改用 CDATA 输出代码；example 根节点加 Container 定尺寸；引入 layout_check.py",
   recheck="见 A17-IT-04")
it(iteration_id="A17-IT-04", version="handbook-01.v5", parent="handbook-01.v1", type="visual",
   purpose="验证溢出修复",
   images=["handbook-01.v5.png"], viewed_at="2026-10-03T13:03:30+08:00",
   observed="要点 4/5 重新可见、代码块显示真实尖括号；但示例插图标题与画布右边缘相撞",
   change="插图整体右移到 x=848，标题字号 19→17，卡片高度按度量重排",
   recheck="v7/v8 复看：layout_check.py 报 OK，图上无越界")
it(iteration_id="A17-IT-05", version="handbook-02.v9", parent="handbook-02.v1", type="visual",
   purpose="第 2 页布局复核",
   images=["handbook-02.v9.png"], viewed_at="2026-10-03T13:05:00+08:00",
   observed="卡片2 的两行要点互相压字（行距 46 < 两行所需 63）；卡片4 代码块超出卡片下沿",
   change="两行要点固定 68 行距并按需增高卡片；代码块字号 20→18，片段裁到 9 行，标题位置由 Page.code 返回高度决定",
   recheck="v10–v21 复看：要点分行清晰、代码块与标题均在卡片内")
it(iteration_id="A17-IT-06", version="handbook-03.v14", parent="handbook-03.v1", type="visual",
   purpose="第 3 页文字与颜色复核",
   images=["handbook-03.v14.png"], viewed_at="2026-10-03T13:07:00+08:00",
   observed="二栏标题“CDATA 才是正”被 148px 标签列截断换行；正文出现 &lt; 实体；色块图注与卡片边界接近",
   change="标签列加宽到 184px；正文避免实体写法；色块图整体右移并收窄到 516px",
   recheck="handbook-03.v21/final 复看：标题完整、无实体、图注与卡片留白正常")
it(iteration_id="A17-IT-07", version="example-04.v23", parent="example-04.v1", type="visual",
   purpose="让两种模糊在同一张图里可见",
   images=["example-04.v21.png", "example-04.v23.png", "example-04.v24.png"],
   viewed_at="2026-10-03T13:08:30+08:00",
   observed="v21 的 BackdropFilter 落在白底上，背后无内容，完全看不出效果；sigma=8 时糊痕过强像条纹",
   change="把 BackdropFilter 移到跨越两块彩色卡片的位置，sigma 8→3；ImageFiltered 白卡压在第三块上",
   recheck="v24/final 复看：左侧磨砂面板清晰可辨，右侧白卡与字一起糊，对比成立")
print("iterations.jsonl written")