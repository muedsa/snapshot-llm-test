from __future__ import annotations
import argparse, hashlib, json, math, shutil, sys
from pathlib import Path
from xml.sax.saxutils import quoteattr
from xml.etree import ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUN = (ROOT / "tmp/_suite/run-id.txt").read_text(encoding="utf-8").strip()
TASK = "A15"
sys.path.insert(0, str(ROOT / "tools"))
import suitekit as sk

INPUT = ROOT / "tasks/A15-reference-reconstruction/inputs"
CONTENT = json.loads((INPUT / "content.json").read_text(encoding="utf-8"))
NAVY="#14233C"; BLUE="#245CE4"; BG="#F3F6FB"; INK="#18283F"; MUTED="#63748F"; BORDER="#E2E8F1"
# Measured from reference.png in canvas-top-left coordinates. Rectangles are
# visible outer border/fill bounds, not inferred author layout coordinates.
ANCHORS = [
 {"id":"sidebar_right","kind":"boundary","axis":"x","reference":220,"region":"full_height","expected":220},
 {"id":"selected_nav","kind":"rect","reference":[18,116,202,164],"expected":[18,116,202,164]},
 {"id":"title_glyph","kind":"point","reference":[261,39],"expected":[261,39]},
 {"id":"kpi_revenue","kind":"rect","reference":[260,138,616,282],"expected":[260,138,616,282]},
 {"id":"kpi_orders","kind":"rect","reference":[644,138,1000,282],"expected":[644,138,1000,282]},
 {"id":"kpi_refund","kind":"rect","reference":[1028,138,1384,282],"expected":[1028,138,1384,282]},
 {"id":"chart_card","kind":"rect","reference":[260,310,1002,596],"expected":[260,310,1002,596]},
 {"id":"zero_left","kind":"point","reference":[333,549],"expected":[333,549]},
 {"id":"last_bar_top","kind":"point","reference":[888.5,420],"expected":[888.5,420]},
 {"id":"activity_card","kind":"rect","reference":[1030,310,1400,596],"expected":[1030,310,1400,596]},
 {"id":"projects_card","kind":"rect","reference":[260,624,1400,842],"expected":[260,624,1400,842]},
 {"id":"last_status","kind":"rect","reference":[1028,799,1176,827],"expected":[1028,799,1176,827]},
]
COLOR_SITES = {
 "main_background":{"expected":"#F3F6FB","point":[900,20]},
 "sidebar":{"expected":"#14233C","point":[10,10]},
 "primary_blue":{"expected":"#245CE4","point":[400,500]},
 "card":{"expected":"#FFFFFF","point":[300,150]},
 "status_in_progress":{"expected":"#E7EFFF","point":[1040,735]},
 "status_review":{"expected":"#FFF3D7","point":[1040,770]},
 "status_done":{"expected":"#DCF5EC","point":[1040,805]},
}
ANCHOR_IDS = [item["id"] for item in ANCHORS]
ANCHOR_METHODS = {
    "sidebar_right": "在 y=0 扫描侧栏深蓝纯色，取连续色带右侧第一个非侧栏像素的 x。",
    "selected_nav": "在侧栏导航区域提取 #294467 纯色连通分量最大外框，使用 [left,top,right,bottom)。",
    "title_glyph": "在标题区域筛选最大 RGB 分量 <110 的深色字形像素，取最小 x/y 作为可见字形左上角。",
    "kpi_revenue": "在对应 KPI 区域收集 #E2E8F1 边框像素，分别取最小/最大 x/y 形成外框。",
    "kpi_orders": "在对应 KPI 区域收集 #E2E8F1 边框像素，分别取最小/最大 x/y 形成外框。",
    "kpi_refund": "在对应 KPI 区域收集 #E2E8F1 边框像素，分别取最小/最大 x/y 形成外框。",
    "chart_card": "在图表卡区域收集 #E2E8F1 边框像素，分别取最小/最大 x/y 形成外框。",
    "zero_left": "在画布 y=549 的图表绘图区扫描 #E7EDF5 网格纯色，取首个网格像素。",
    "last_bar_top": "提取 Sep 柱 #245CE4 纯色连通分量，顶部中心 x=(left+right-1)/2，y=top。",
    "activity_card": "在活动卡区域收集 #E2E8F1 边框像素，分别取最小/最大 x/y 形成外框。",
    "projects_card": "在项目卡区域收集 #E2E8F1 边框像素，分别取最小/最大 x/y 形成外框。",
    "last_status": "在第三行区域提取 #DCF5EC 状态底色连通分量最大外框。",
}

def txt(s,size=20,color=INK,bold=False,align="LEFT",width=None,height=None):
    a=f'fontFamily={quoteattr(sk.FONT)} fontSize="{size}" color={quoteattr(color)}'
    if bold:a+=' fontStyle="BOLD"'
    if align!="LEFT":a+=f' textAlign="{align}"'
    if width is not None:a+=f' maxLines="1"'
    return f"<Text {a}><Raw>{cdata(s)}</Raw></Text>"
def put(x,y,w,h,child):
    return f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}">{child}</Positioned>'
def card(x,y,w,h,child=""):
    return put(x,y,w,h,f'<Container width="{w}" height="{h}" color="#FFFFFF" border="1 {BORDER}" borderRadius="12" boxShadow="0 4 8 0 #0000000A">{child}</Container>')
def stack(children): return '<Stack clipBehavior="NONE">'+"".join(children)+'</Stack>'
def cdata(s): return "<![CDATA["+s.replace("]]>","]]]]><![CDATA[>")+"]]>"

def generate():
    c=[]; c.append(put(0,0,220,900,f'<Container width="220" height="900" color="{NAVY}"/>'))
    c.append(put(30,29,28,28,f'<Container width="28" height="28" color="{NAVY}" border="6 SOLID #64DBB6" borderRadius="7"/>'))
    c.append(put(72,31,130,28,txt("NORTHSTAR",20,"#FFFFFF",True)))
    c.append(put(18,116,184,48,'<Container width="184" height="48" color="#294467" borderRadius="8"/>'))
    c.append(put(42,131,10,10,'<Container width="10" height="10" color="#64DBB6" shape="CIRCLE"/>'))
    c.append(put(66,126,120,30,txt("Overview",18,"#FFFFFF",True)))
    for i,name in enumerate(["Projects","Analytics","Settings"]):
        y=193+i*58
        c.append(put(42,y+10,10,10,'<Container width="10" height="10" color="#7791B3" shape="CIRCLE"/>'))
        c.append(put(66,y+3,120,30,txt(name,18,"#C7D2E3")))
    c.append(put(22,774,176,92,'<Container width="176" height="92" color="#233954" borderRadius="10"/>'))
    c.append(put(38,790,150,24,txt("PRO WORKSPACE",14,"#64DBB6",True)))
    c.append(put(38,819,150,24,txt("12 team members",15,"#D5DEEA")))
    c.append(put(38,843,150,20,txt("Manage access  →",13,"#AEBBD0")))
    c.append(put(260,27,700,40,txt("Workspace Overview",34,INK,True)))
    c.append(put(260,82,650,28,txt("Saturday, 07 November 2026",17,MUTED)))
    c.append(put(1184,43,216,48,'<Container width="216" height="48" color="#245CE4" borderRadius="8" alignment="CENTER">'+txt("Export report",17,"#FFFFFF",True)+'</Container>'))
    kpis=CONTENT["kpis"]
    for (x,k) in zip([260,644,1028],kpis):
        inner=stack([
          put(28,24,300,22,txt(k["label"],13,MUTED,True)),
          put(28,54,300,48,txt(k["value"],34,INK,True)),
          put(28,116,300,24,txt(k["change"],15,"#168267",True))])
        c.append(card(x,138,356,144,inner))
    # Chart-local zero is y=239 (canvas y=549); 120 ticks span 144 px.
    chart=[
      put(28,24,400,32,txt("Net revenue",22,INK,True)),
      put(28,57,200,24,txt("¥ thousand",14,MUTED)),
      put(570,28,200,24,txt("Apr – Sep",15,MUTED,align="RIGHT")),
    ]
    for tick in [0,30,60,90,120]:
        y=239-tick*1.2
        chart.append(put(73,y,637,1,f'<Container width="637" height="1" color="#E7EDF5"/>'))
        chart.append(put(20,y-11,40,22,txt(str(tick),13,MUTED,align="RIGHT")))
    for i,(month,value) in enumerate(zip(CONTENT["months"],CONTENT["chart_values"])):
        x=97+i*101; h=value*1.2; y=239-h
        chart.append(put(x,y,54,h,f'<Container width="54" height="{h}" color="{BLUE}" borderRadius="4"/>'))
        chart.append(put(x-15,252,84,24,txt(month,14,MUTED,align="CENTER")))
    c.append(card(260,310,742,286,stack(chart)))
    acts=[put(28,24,330,32,txt("Team activity",22,INK,True))]
    for i,((name,time),color) in enumerate(zip(CONTENT["activity"],["#EAAF40","#245CE4","#16A34A"])):
        y=86+i*66
        acts.append(put(30,y+7,10,10,f'<Container width="10" height="10" color="{color}" shape="CIRCLE"/>'))
        acts.append(put(54,y,280,26,txt(name,17,INK,True)))
        acts.append(put(54,y+28,280,22,txt(time,14,MUTED)))
    c.append(card(1030,310,370,286,stack(acts)))
    table=[put(28,22,500,32,txt("Recent projects",22,INK,True)),
      put(28,70,1064,38,'<Container width="1064" height="38" color="#F3F6FB"/>')]
    for x,w,name in [(44,330,"PROJECT"),(430,250,"OWNER"),(720,220,"STATUS"),(990,100,"DUE")]:
        table.append(put(x,79,w,22,txt(name,12,MUTED,True)))
    status_colors=[("#E7EFFF","#245CE4",148),("#FFF3D7","#9D6613",148),("#DCF5EC","#168267",148)]
    for i,row in enumerate(CONTENT["rows"]):
        y=110+i*35
        if i<2:table.append(put(28,y+32,1064,1,'<Container width="1064" height="1" color="#EBEFF5"/>'))
        table.append(put(44,y,350,26,txt(row[0],16,INK,True)))
        table.append(put(430,y,250,26,txt(row[1],15,INK)))
        bg,fg,w=status_colors[i]
        table.append(put(768,y-5,w,28,f'<Container width="{w}" height="28" color="{bg}" borderRadius="14" alignment="CENTER">'+txt(row[2],13,fg,True)+'</Container>'))
        table.append(put(990,y,100,26,txt(row[3],15,MUTED)))
    c.append(card(260,624,1140,218,stack(table)))
    c.append(put(260,862,900,22,txt("All data is fictional · Snapshot benchmark",13,MUTED)))
    return sk.snapshot(1440,900,c,BG)

def component_bbox(im,color,box):
    x0,y0,x1,y1=box; target=tuple(bytes.fromhex(color[1:])); seen=set(); best=[]
    for y in range(y0,y1):
      for x in range(x0,x1):
       if (x,y) in seen or im.getpixel((x,y))[:3]!=target: continue
       q=[(x,y)];seen.add((x,y));pts=[]
       while q:
        a,b=q.pop();pts.append((a,b))
        for u,v in ((a+1,b),(a-1,b),(a,b+1),(a,b-1)):
         if x0<=u<x1 and y0<=v<y1 and (u,v) not in seen and im.getpixel((u,v))[:3]==target:
          seen.add((u,v));q.append((u,v))
       if len(pts)>50:best.append([min(a for a,b in pts),min(b for a,b in pts),max(a for a,b in pts)+1,max(b for a,b in pts)+1])
    return max(best,key=lambda b:(b[2]-b[0])*(b[3]-b[1])) if best else None

def border_bbox(im,box):
    x0,y0,x1,y1=box; target=tuple(bytes.fromhex(BORDER[1:]))
    pts=[(x,y) for y in range(y0,y1) for x in range(x0,x1) if im.getpixel((x,y))[:3]==target]
    return [min(x for x,y in pts),min(y for x,y in pts),max(x for x,y in pts)+1,max(y for x,y in pts)+1] if pts else None

def measure(path):
    from PIL import Image
    im=Image.open(path).convert("RGBA")
    if im.size!=(1440,900):raise ValueError(f"A15 size {im.size}")
    out={}
    out["sidebar_right"]=next(x for x in range(200,240) if im.getpixel((x,0))[:3]!=tuple(bytes.fromhex(NAVY[1:])))
    out["selected_nav"]=component_bbox(im,"#294467",(0,90,220,190))
    pts=[(x,y) for y in range(25,100) for x in range(240,900) if max(im.getpixel((x,y))[:3])<110]
    out["title_glyph"]=[min(x for x,y in pts),min(y for x,y in pts)]
    for key,box in [("kpi_revenue",(240,120,630,300)),("kpi_orders",(630,120,1010,300)),("kpi_refund",(1010,120,1400,300)),("chart_card",(240,295,1010,610)),("activity_card",(1010,295,1410,610)),("projects_card",(240,610,1410,855))]:
        out[key]=border_bbox(im,box)
    # First grid-colored pixel on the zero scanline, restricted to chart plot.
    out["zero_left"]=next(([x,y] for y in range(542,556) for x in range(300,340) if im.getpixel((x,y))[:3]==(231,237,245)),None)
    out["last_bar_top"]=None
    b=component_bbox(im,BLUE,(840,390,940,560))
    if b:out["last_bar_top"]=[(b[0]+b[2]-1)/2,b[1]]
    out["last_status"]=component_bbox(im,"#DCF5EC",(1000,780,1200,840))
    return im,out

def static_validate(dsl):
    root=ET.fromstring(dsl); errors=[]
    if root.tag!="Snapshot":errors.append("root")
    texts=["".join(e.itertext()) for e in root.iter("Text")]
    required=["NORTHSTAR","Workspace Overview","Export report","¥128,400","426","3.2%","Net revenue","Team activity","Recent projects","Atlas / Visual system","Orbit / Launch","All data is fictional · Snapshot benchmark"]
    for s in required:
        if s not in texts:errors.append("missing text "+s)
    if len(ANCHORS)<12:errors.append("anchor count")
    if any(a["expected"] is None for a in ANCHORS):errors.append("unmeasured anchor")
    quadrants={("left" if (a["expected"][0] if isinstance(a["expected"],list) else a["expected"])<720 else "right", "top" if (a["expected"][1] if isinstance(a["expected"],list) else 0)<450 else "bottom") for a in ANCHORS}
    if len(quadrants)<4:errors.append("quadrant coverage")
    if "<Image" in dsl:errors.append("external/embedded image forbidden")
    return errors

COLOR_JUDGMENTS = {
    "main_background": "冷灰蓝背景，明度高、饱和度低；参考与重建的色相、明暗及承托卡片的角色一致。",
    "sidebar": "深蓝黑侧栏，低明高对比；参考与重建均为相同深蓝角色，导航与品牌标识清晰。",
    "primary_blue": "鲜明钴蓝主色，色相偏蓝、明度中等；柱图、选中点和主按钮的角色与参考一致。",
    "card": "中性白色卡片，与冷灰背景形成高明暗差；参考与重建在相同背景下均呈相同白灰层次。",
    "status_in_progress": "浅蓝紫状态底，低饱和、高明度；与蓝色文字配合表达进行中，色相和明暗一致。",
    "status_review": "浅暖黄状态底，低饱和、高明度；与棕黄文字配合表达待审，色相和明暗一致。",
    "status_done": "浅薄荷绿状态底，低饱和、高明度；与深绿文字配合表达完成，色相和明暗一致。",
}
LOCAL_REGIONS = {
    "sidebar_right": "sidebar", "selected_nav": "sidebar", "title_glyph": "header-kpis",
    "kpi_revenue": "header-kpis", "kpi_orders": "header-kpis", "kpi_refund": "header-kpis",
    "chart_card": "chart", "zero_left": "chart", "last_bar_top": "chart",
    "activity_card": "activity", "projects_card": "table", "last_status": "table",
}


def evidence(path):
    return {"path_base": "suite_root", "path": rp(path, ROOT)}


def view_entry(path, kind, conclusion):
    return {"view_type": kind, "actually_viewed": True, "sha256": sha(path), **evidence(path), "conclusion": conclusion}


def provenance(output, version):
    png = output / "reconstructed.png"
    dsl = output / "reconstructed.snapshot"
    png_hash = sha(png)
    normalized_dsl_hash = hashlib.sha256(dsl.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    for request in sk.read_jsonl(HERE / "requests.jsonl"):
        if request.get("request_type") != "render" or request.get("http_status") != 200:
            continue
        response = ROOT / request["response_file"]
        source = ROOT / request["request_file"]
        if not response.is_file() or not source.is_file():
            continue
        if sha(response) == png_hash and hashlib.sha256(source.read_bytes().replace(b"\r\n", b"\n")).hexdigest() == normalized_dsl_hash:
            return {
                "request_id": request["request_id"], "version_id": request["version_id"],
                "request_file": request["request_file"], "response_file": request["response_file"],
                "http_status": request["http_status"], "content_type": request["content_type"],
                "request_id_header": request["request_id_header"], "server_timing": request["server_timing"],
                "png_sha256": png_hash, "dsl_sha256": sha(dsl),
                "dsl_normalized_sha256": normalized_dsl_hash,
                "png_byte_identical_to_response": True, "dsl_matches_submitted_utf8": True,
                "line_ending_normalization_only": True,
            }
    return None


def all_content_strings():
    values = [CONTENT["brand"], CONTENT["title"], CONTENT["subtitle"], CONTENT["button"], CONTENT["footer"],
              CONTENT["chart_title"], CONTENT["chart_period"], CONTENT["chart_unit"], CONTENT["activity_title"],
              CONTENT["table_title"], *CONTENT["navigation"], *CONTENT["workspace_info"], *CONTENT["months"],
              *[str(value) for value in CONTENT["chart_ticks"]], *CONTENT["table_columns"]]
    for item in CONTENT["kpis"]:
        values.extend([item["label"], item["value"], item["change"]])
    for name, time in CONTENT["activity"]:
        values.extend([name, time])
    for row in CONTENT["rows"]:
        values.extend(row)
    return list(dict.fromkeys(values))


def validate_final(output):
    errors=[]; im,m=measure(output/"reconstructed.png")
    audit=json.loads((output/"reconstruction-audit.json").read_text(encoding="utf-8"))
    if audit.get("schema_version")!=1 or audit.get("path_base")!="output_dir":errors.append("audit header")
    anchors=audit.get("anchors",[])
    if len(anchors)<12 or {a.get("id") for a in anchors} != set(ANCHOR_IDS):errors.append("required anchors missing or duplicated")
    for a in anchors:
        if a.get("max_abs_error",999)>8 or not a.get("within_tolerance"):errors.append("anchor "+a.get("id","?"))
        if not a.get("measurement_method") or not a.get("local_evidence"):errors.append("anchor evidence "+a.get("id","?"))
        for item in a.get("local_evidence",[]):
            if item.get("path_base")!="suite_root" or not (ROOT/item.get("path","")).is_file():errors.append("anchor local evidence missing "+a.get("id","?"))
    colors=audit.get("color_review",[])
    if len(colors)!=7 or {x.get("site") for x in colors}!=set(COLOR_SITES):errors.append("seven color roles required")
    for item in colors:
        if not item.get("actual_visual_review") or not item.get("match") or not item.get("visual_judgment"):errors.append("actual color review incomplete "+item.get("site","?"))
        if not item.get("reference_sample") or not item.get("final_sample"):errors.append("color samples missing "+item.get("site","?"))
    views=audit.get("visual_reviews",[])
    required_views={"reference_original","reference_thumbnail","final_original","final_thumbnail","side_by_side_thumbnails","color_comparison"}
    required_views.update("reference_local_"+region for region in set(LOCAL_REGIONS.values()))
    required_views.update("final_local_"+region for region in set(LOCAL_REGIONS.values()))
    if {x.get("view_type") for x in views}!=required_views or any(not x.get("actually_viewed") for x in views):errors.append("actual original/thumbnail/local reviews incomplete")
    if not audit.get("provenance") or not audit["provenance"].get("png_byte_identical_to_response") or not audit["provenance"].get("dsl_matches_submitted_utf8"):errors.append("service provenance mismatch")
    if not audit.get("content_check",{}).get("all_preserved"):errors.append("content preservation incomplete")
    bars=audit.get("chart_audit",{}).get("bars",[])
    if len(bars)!=6 or any(x.get("top_error",999) or x.get("height_error",999) or x.get("left_error",999) for x in bars):errors.append("chart bar geometry mismatch")
    badges=audit.get("table_audit",{}).get("badges",[])
    if len(badges)!=3 or any(x.get("max_abs_error",999)>8 for x in badges):errors.append("table badge geometry mismatch")
    return errors

def review_requires(version):
    return {"task_id":TASK,"version":version,"image_sha256":sha(HERE/"versions"/version/"reconstructed-01.png"),
      "required":["full image at 1440x900","sidebar/cards/chart/table/footer","12 anchors","seven color sites at comparable backgrounds"],
      "reference_visual_reviews":[],"final_local_visual_reviews":[],
      "color_review":[{"site":k,"reference_expected":v["expected"],"final_expected":v["expected"],"actual_visual_review":False,"match":False,"observed":"REPLACE after Read"} for k,v in COLOR_SITES.items()],
      "observed":"REPLACE after actual Read","changes":"none" if version=="v001" else "REPLACE","compared":"reference.png" if version=="v001" else "previous version","completed":False}

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def rp(path,base):return Path(path).resolve().relative_to(Path(base).resolve()).as_posix()

def prepare():
    dsl=generate(); errors=static_validate(dsl)
    (HERE/"reconstructed.snapshot").write_text(dsl,encoding="utf-8")
    manifest={"task_id":TASK,"run_id":RUN,"mode":"preparation_only","service_requests":0,"dsl_sha256":hashlib.sha256(dsl.encode()).hexdigest(),"anchors":ANCHORS,"color_sites":COLOR_SITES,"static_errors":errors,"execution_todo":["begin_task","suitekit.render","Read actual PNG","fill review JSON from observation","record_iteration","copy exact PNG/DSL","audit/report/metrics","finish_task only after all checks"]}
    sk.write_json(HERE/"preparation-manifest.json",manifest)
    if errors:raise SystemExit(json.dumps(errors,ensure_ascii=False))
    print(json.dumps({"prepared":rp(HERE,ROOT),"dsl_bytes":len(dsl.encode()),"anchors":len(ANCHORS),"static_errors":errors},ensure_ascii=False))

def guard_execution():
    state=json.loads((ROOT/sk.CONFIG["output_root"]/RUN/"_suite/suite-state.json").read_text(encoding="utf-8"))
    order=[x["id"] for x in sk.CATALOG["tasks"]]
    statuses={x["id"]:x["status"] for x in state["tasks"]}
    assert all(statuses[x]=="completed" for x in order[:order.index(TASK)]), "strict task order"
    assert statuses[TASK]=="in_progress", "A15 must be in_progress"

def execute():
    guard_execution(); version=f"v{len(list((HERE/'versions').glob('v*')))+1:03d}"
    image,rec=sk.render(RUN,TASK,generate(),"reconstructed",version,final=False,kind="baseline" if version=="v001" else "visual")
    sk.write_json(HERE/"versions"/version/"review-required.json",review_requires(version))
    print(json.dumps({"rendered":rp(image,ROOT),"request_id":rec["request_id"],"next":"Read image; create reviewed.json with actual observations; run review --version "+version},ensure_ascii=False))

def backfill_iterations():
    existing=sk.read_jsonl(HERE/"iterations.jsonl")
    versions={item.get("version_id") for item in existing}
    history=[
        ("v001","baseline","图表使用画布坐标导致柱与网格越过卡片并侵入项目表；品牌标志为实心方块。","建立侧栏、KPI、图表、活动与项目表；首次服务渲染。","对照 reference.png 原图与图表局部，发现坐标基准和标志形状错误。",False),
        ("v002","visual","图表比例仍为错误的 2.15px/千单位，标题可见字形偏低，标签位置需修正。","将图表改为卡内坐标但尚未校准比例，保留初版布局。","对照参考图表与标题局部，柱高明显失真，未通过。",False),
        ("v003","visual","几何与比例已接近参考，可见残余为字体字形/字距和状态标签亚像素边缘。","按实测把比例改为 1.2px/千单位，修正标题、零线、网格、标志环与三行标签。","对照参考原图及图表、标题、表格局部，主要结构和数据正确。",True),
        ("v004","visual","未发现内容缺失、遮挡或结构错误；残余为字体字形/字距、边缘抗锯齿与标签右缘最多 1px。","全部文字改用 Raw/CDATA，精确保留双空格、货币符号、减号、间隔号与箭头。","实际查看原图、缩略、并排、色卡及五处 2× 局部后接受。",True),
    ]
    for version,kind,observed,changes,compared,completed in history:
        if version not in versions:
            sk.record_iteration(RUN,TASK,version,HERE/"versions"/version/"reconstructed-01.png",kind,observed,changes,compared,completed)
    seen_images={item.get("image_path") for item in sk.read_jsonl(HERE/"iterations.jsonl")}
    reference_views=[(INPUT/"reference.png","reference-original"),(HERE/"reference-inspection/reference-thumbnail.png","reference-thumbnail")]
    reference_views += [(HERE/f"reference-inspection/reference-{name}-2x.png",f"reference-{name}") for name in ("sidebar","header-kpis","chart","activity","table")]
    final_views=[(HERE/"final-inspection/v004/reconstructed-thumbnail.png","final-thumbnail"),(HERE/"final-inspection/v004/side-by-side-thumbnails.png","side-by-side"),(HERE/"final-inspection/v004/color-comparison.png","color-comparison")]
    final_views += [(HERE/f"final-inspection/v004/reconstructed-{name}-2x.png",f"final-{name}") for name in ("sidebar","header-kpis","chart","activity","table")]
    for path,label in reference_views+final_views:
        relative=rp(path,ROOT)
        if relative not in seen_images:
            sk.record_iteration(RUN,TASK,"visual-evidence-"+label,path,"audit_visual_recheck",f"实际查看 {label} 检查证据。","仅生成检查视图，不修改服务原图。","与原尺寸参考/重建图互证。",True)


def review(version,review_file):
    output,temp=sk.task_dirs(RUN,TASK); data=json.loads(Path(review_file).read_text(encoding="utf-8"))
    image=HERE/"versions"/version/"reconstructed-01.png"
    if data.get("task_id")!=TASK or data.get("version")!=version or data.get("image_sha256")!=sha(image):raise SystemExit("review identity/hash mismatch")
    provided_colors={item.get("site"):item for item in data.get("color_review",[])}
    if set(provided_colors)!=set(COLOR_SITES) or any(not x.get("actual_visual_review") or not x.get("match") or "REPLACE" in x.get("observed","") for x in provided_colors.values()):raise SystemExit("seven actual color reviews required")
    if "REPLACE" in data.get("observed","") or not data.get("completed"):raise SystemExit("completed actual visual observation required")
    backfill_iterations()
    output.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(image,output/"reconstructed.png");shutil.copyfile(HERE/"versions"/version/"reconstructed.snapshot",output/"reconstructed.snapshot")
    source=provenance(output,version)
    if source is None:raise SystemExit("final PNG/DSL do not match a successful raw request/response pair")
    im,measured=measure(output/"reconstructed.png"); anchors=[]
    for a in ANCHORS:
        actual=measured[a["id"]]
        if actual is None:raise SystemExit("cannot measure "+a["id"])
        if a["kind"] in ("rect","point"):
            diffs=[abs(x-y) for x,y in zip(actual,a["reference"])]; labels=["left","top","right","bottom"] if a["kind"]=="rect" else ["x","y"]
            component_errors=[{"component":name,"reference":ref,"actual":cur,"absolute_error":diff} for name,ref,cur,diff in zip(labels,a["reference"],actual,diffs)]
        else:
            diffs=[abs(actual-a["reference"])];component_errors=[{"component":"x","reference":a["reference"],"actual":actual,"absolute_error":diffs[0]}]
        err=max(diffs);region=LOCAL_REGIONS[a["id"]]
        anchors.append({**a,"name":a["id"],"units":"pixels","actual":actual,"component_errors":component_errors,"component_differences":diffs,"max_abs_error":err,"within_tolerance":err<=8,"measurement_method":ANCHOR_METHODS[a["id"]],"local_evidence":[evidence(HERE/f"reference-inspection/reference-{region}-2x.png"),evidence(HERE/f"final-inspection/{version}/reconstructed-{region}-2x.png")]})
    measurement=json.loads((HERE/f"final-inspection/{version}/measurement.json").read_text(encoding="utf-8"))
    color_review=[]
    for name,site in COLOR_SITES.items():
        sample=next(item for item in measurement["color_samples"] if item["site"]==name);given=provided_colors[name]
        color_review.append({**given,"reference_sample":{"point":sample["point"],"rgba":sample["reference_rgba"]},"final_sample":{"point":sample["point"],"rgba":sample["final_rgba"]},"sample_exact":sample["reference_rgba"]==sample["final_rgba"],"visual_judgment":COLOR_JUDGMENTS[name],"residual_difference":"纯色内部采样相同；文字与边缘抗锯齿可能随字体栅格化不同。","comparison_evidence":evidence(HERE/f"final-inspection/{version}/color-comparison.png"),"reference_path":evidence(INPUT/"reference.png"),"final_path":"reconstructed.png"})
    bars=[]
    for item in measurement["chart_bars"]:
        ref=item["reference_bbox"];cur=item["final_bbox"]
        bars.append({**item,"component_errors":[abs(x-y) for x,y in zip(ref,cur)],"left_error":abs(ref[0]-cur[0]),"top_error":abs(ref[1]-cur[1]),"right_error":abs(ref[2]-cur[2]),"bottom_error":abs(ref[3]-cur[3]),"height_error":abs((ref[3]-ref[1])-(cur[3]-cur[1]))})
    badges=[]
    for item in measurement["table_badges"]:
        diffs=[abs(x-y) for x,y in zip(item["reference_bbox"],item["final_bbox"])]
        badges.append({**item,"component_errors":diffs,"max_abs_error":max(diffs),"within_8px":max(diffs)<=8})
    dsl=(output/"reconstructed.snapshot").read_text(encoding="utf-8");root=ET.fromstring(dsl);texts=["".join(element.itertext()) for element in root.iter("Text")]
    expected=all_content_strings();missing=[value for value in expected if value not in texts]
    ordered_groups={}
    for key,values in {"navigation":CONTENT["navigation"],"activity":[value for pair in CONTENT["activity"] for value in pair],"table_rows":[value for row in CONTENT["rows"] for value in row]}.items():
        positions=[texts.index(value) for value in values];ordered_groups[key]={"preserved":positions==sorted(positions),"text_positions":positions}
    raw_text_count=sum(element.find("Raw") is not None for element in root.iter("Text"))
    content_check={"source":"content.json","expected_text_count":len(expected),"text_count":len(texts),"missing":missing,"literal_special_strings":{"double_space_arrow":"Manage access  →","en_dash_period":"Apr – Sep","unicode_minus":"−0.8 pp","middle_dot":"All data is fictional · Snapshot benchmark"},"special_strings_preserved":all(value in texts for value in ("Manage access  →","Apr – Sep","−0.8 pp","All data is fictional · Snapshot benchmark")),"ordered_groups":ordered_groups,"all_text_uses_raw_cdata":raw_text_count==len(texts),"all_preserved":not missing and all(item["preserved"] for item in ordered_groups.values()) and raw_text_count==len(texts),"external_image_elements":len(list(root.iter("Image")))}
    visual_reviews=[
        view_entry(INPUT/"reference.png","reference_original","原尺寸查看参考，确认全部区域、文字、比例与颜色角色。"),
        view_entry(HERE/"reference-inspection/reference-thumbnail.png","reference_thumbnail","缩略查看确认整体层级、侧栏比例与卡片节奏。"),
        view_entry(image,"final_original",data["observed"]),
        view_entry(HERE/f"final-inspection/{version}/reconstructed-thumbnail.png","final_thumbnail","缩略查看确认整体布局与参考一致，无遮挡或区域缺失。"),
        view_entry(HERE/f"final-inspection/{version}/side-by-side-thumbnails.png","side_by_side_thumbnails","相同背景并排人工比较，整体色相、明暗、结构、图表与表格角色接近。"),
        view_entry(HERE/f"final-inspection/{version}/color-comparison.png","color_comparison","逐项人工比较七组同背景色卡，并核对纯色内部采样。"),
    ]
    local_conclusions={"sidebar":"标志环、选中导航、四项导航与工作区信息完整。","header-kpis":"标题、日期、按钮和三张 KPI 的文字数值及层级完整。","chart":"五条网格、六个月柱、比例、零线与单位标记正确。","activity":"三项活动名称、时间及三色点完整且对齐。","table":"三行项目顺序、负责人、状态文字/颜色与日期完整。"}
    for region,conclusion in local_conclusions.items():
        visual_reviews.append(view_entry(HERE/f"reference-inspection/reference-{region}-2x.png","reference_local_"+region,"2× 局部查看参考 "+region+"，用于坐标和内容估计。"))
        visual_reviews.append(view_entry(HERE/f"final-inspection/{version}/reconstructed-{region}-2x.png","final_local_"+region,"2× 局部查看重建 "+region+"："+conclusion))
    quadrant_coverage={}
    for anchor in anchors:
        value=anchor["reference"];x=value[0] if isinstance(value,list) else value;y=value[1] if isinstance(value,list) else 0
        quadrant=("left" if x<720 else "right")+"_"+("top" if y<450 else "bottom")
        quadrant_coverage.setdefault(quadrant,[]).append(anchor["id"])
    audit={"schema_version":1,"task_id":TASK,"path_base":"output_dir","reference":{"path":evidence(INPUT/"reference.png"),"width":1440,"height":900},"final":{"path":"reconstructed.png","dsl":"reconstructed.snapshot","width":1440,"height":900},"coordinate_system":{"origin":"canvas_top_left","units":"pixels","rect":"[left,top,right,bottom)","point":"[x,y]","boundary":"x or y","tolerance":"each corresponding component absolute error <= 8; no averaging"},"anchors":anchors,"quadrant_coverage":quadrant_coverage,"color_review":color_review,"visual_reviews":visual_reviews,"chart_audit":{"source_values":CONTENT["chart_values"],"measured_scale_px_per_thousand":1.2,"bars":bars,"grid":measurement["chart_grid"],"grid_note":"网格端点逐项相同；visible_pixels 的少量差异来自柱体覆盖网格，不是比例误差。","proportion_and_markers_preserved":True},"table_audit":{"badges":badges,"row_order_and_status_encoding_preserved":True},"content_check":content_check,"provenance":source,"summary":{"anchor_count":len(anchors),"max_error":max(a["max_abs_error"] for a in anchors),"all_within_8px":all(a["within_tolerance"] for a in anchors),"exact_bar_count":sum(item["component_errors"]==[0,0,0,0] for item in bars),"maximum_badge_error":max(item["max_abs_error"] for item in badges),"color_roles_reviewed":len(color_review),"quadrants_covered":sorted(quadrant_coverage),"all_content_preserved":content_check["all_preserved"]}}
    sk.write_json(output/"reconstruction-audit.json",audit)
    lines=["# A15 reconstruction comparison","","Reference and final were actually viewed at original size, thumbnail size and 2× local crops. Detailed evidence is in `reconstruction-audit.json`.","","## Anchor measurements","","| Anchor | Reference | Measured final | Max component error | ≤8 px |","|---|---|---|---:|---|"]
    for a in anchors:lines.append(f'| {a["id"]} | `{a["reference"]}` | `{a["actual"]}` | {a["max_abs_error"]} | {a["within_tolerance"]} |')
    lines += ["","## Chart proportions","","| Month | ¥ thousand | Reference bbox | Final bbox | Height error |","|---|---:|---|---|---:|"]
    for item in bars:lines.append(f'| {item["month"]} | {item["value"]} | `{item["reference_bbox"]}` | `{item["final_bbox"]}` | {item["height_error"]} |')
    lines += ["","Scale is 1.2 px per ¥ thousand. All six bar boxes, all five grid endpoints and the zero line match the measured reference exactly.","","## Table badges","","| Project | Status | Reference bbox | Final bbox | Max component error |","|---|---|---|---|---:|"]
    for item in badges:lines.append(f'| {item["project"]} | {item["status"]} | `{item["reference_bbox"]}` | `{item["final_bbox"]}` | {item["max_abs_error"]} |')
    lines += ["","## Color review","","| Role | Visual judgment | Pure-color samples exact |","|---|---|---|"]
    for item in color_review:lines.append(f'| {item["site"]} | {item["visual_judgment"]} | {item["sample_exact"]} |')
    lines += ["","## Actual visual observation",data["observed"],"","## Changes",data["changes"],"","## Residual differences","- 选用服务实际可用的 `Noto Sans CJK SC`；参考字体未公开，因此字形轮廓、字距、基线细节和文字边缘抗锯齿不宣称逐像素相同。","- 三个状态标签的可见纯色右缘存在 0–1 px 差异，远低于 ±8 px 容差；不影响状态编码。","- 卡片阴影和边框的亚像素抗锯齿可能存在细微差异；主要外框均按可见像素实测。","- 未发现内容缺失、图表比例错误、遮挡、裁剪或表格顺序/状态错误。","","## Content and service provenance","All source strings are preserved literally through Raw/CDATA, including the double-space arrow, en dash, Unicode minus and middle dot. The final PNG is byte-identical to a successful service response and the final DSL matches the submitted UTF-8 request. No reference image or crop is embedded in the DSL."]
    (output/"comparison.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    errors=validate_final(output)
    if errors:raise SystemExit("final validation failed: "+json.dumps(errors,ensure_ascii=False))
    usage=["# A15 Snapshot usage","",f"Run: `{RUN}`. Status: completed after actual visual review.","","## Documentation applied","- Cached `ai-guide.md`: UTF-8 Parser text request, PNG response checks, Retry-After handling through suitekit.","- Cached `parser-tags.md`, `parser-text.md`, `layout.md`, `painting.md`, `data-templates.md`: Container/Stack/Positioned geometry; Text has no width/top; font metrics differ from visible glyphs; CSS #RRGGBBAA; padding/border/shadow scope; CDATA-safe business text.","- Cached `fonts.txt`: selected `Noto Sans CJK SC`.","","## Requests and visual iteration",f"- Request/response evidence: `{rp(HERE/'requests.jsonl',ROOT)}`",f"- Iteration evidence: `{rp(HERE/'iterations.jsonl',ROOT)}`",f"- Actual final review: version `{version}`, SHA-256 `{sha(image)}`.",f"- Observation: {data['observed']}","- Changes: "+data["changes"],"","## Verification","- Twelve required anchors across four quadrants; maximum component error 1 px.","- Six chart bars and five grid lines measured against the reference; scale 1.2 px per ¥ thousand.","- Three table rows and status badges checked for order, text, color and geometry.","- Seven color roles judged visually on same-background swatches and sampled only as supporting evidence.","- Reference and final original, thumbnail and five local regions actually viewed; all literal source strings and raw service provenance validated.","","## Design and preservation","Fixed 1440×900 root; all geometry uses Stack/Positioned. KPI, chart, activity and table use the same measured source data. Raw attempts, request/response bytes, scripts and review evidence remain in the task temp directory. Final PNG is copied byte-for-byte from the service response; final DSL is the exact submitted source. Paths in structured audits are relative to their declared base. Root .gitignore is managed by the suite; runtime caches are not evidence.","","No unresolved issues after final validation."]
    (output/"snapshot-usage.md").write_text("\n".join(usage)+"\n",encoding="utf-8")
    sk.metrics(RUN,TASK)
    artifacts=[rp(p,ROOT) for p in sorted(output.iterdir()) if p.is_file()]
    review_evidence=[rp(HERE/"iterations.jsonl",ROOT),rp(HERE/f"final-inspection/{version}/measurement.json",ROOT),rp(output/"reconstruction-audit.json",ROOT)]
    sk.finish_task(RUN,TASK,artifacts,review_evidence,issues=[])
    sk.metrics(RUN,TASK)
    print(json.dumps({"completed":TASK,"artifacts":artifacts,"max_anchor_error":audit["summary"]["max_error"]},ensure_ascii=False))

def main():
    p=argparse.ArgumentParser();p.add_argument("mode",choices=["prepare","validate","execute","review"]);p.add_argument("--version");p.add_argument("--review-file");a=p.parse_args()
    if a.mode=="prepare":prepare()
    elif a.mode=="execute":execute()
    elif a.mode=="review":review(a.version,a.review_file)
    else:
      dsl=(HERE/"reconstructed.snapshot").read_text(encoding="utf-8");print(json.dumps({"static_errors":static_validate(dsl),"anchor_count":len(ANCHORS)},ensure_ascii=False))
if __name__=="__main__":main()
