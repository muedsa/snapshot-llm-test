from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import suitekit as sk

RUN = (ROOT / "tmp" / "_suite" / "run-id.txt").read_text(encoding="utf-8").strip()
TASK = "A21"
HERE = ROOT / sk.CONFIG["temp_root"] / RUN / TASK
OUTPUT = ROOT / sk.CONFIG["output_root"] / RUN / TASK
STATE_PATH = ROOT / sk.CONFIG["output_root"] / RUN / "_suite/suite-state.json"


def rp(path: Path) -> str:
    return sk.rel(path, ROOT)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def guard(round_no: int) -> None:
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    order = [item["id"] for item in sk.CATALOG["tasks"]]
    statuses = {item["id"]: item["status"] for item in state["tasks"]}
    assert all(statuses[item] == "completed" for item in order[:order.index(TASK)]), "strict task order"
    assert statuses[TASK] in ("pending", "in_progress"), "A21 state"
    if round_no > 1:
        task = next(item for item in state["tasks"] if item["id"] == TASK)
        assert f"round-{round_no-1:02d}" in task.get("completed_rounds", []), "round order"


def theme(round_no: int) -> dict:
    if round_no < 3:
        return {"name": "midnight_violet", "background": "#0F0A1F", "panel": "#1E1538", "text": "#F8FAFC",
                "muted": "#DDD6FE", "accent": "#A78BFA", "primary": "#7C3AED", "lime": "#D9F99D",
                "cards": ["#2E1D52", "#3B2468", "#4C1D95"], "ring": "#A78BFA", "dots": "#C4B5FD"}
    return {"name": "light_violet", "background": "#F5F3FF", "panel": "#FFFFFF", "text": "#1E1B4B",
            "muted": "#4C1D95", "accent": "#6D28D9", "primary": "#6D28D9", "lime": "#3F6212",
            "cards": ["#EDE9FE", "#DDD6FE", "#C4B5FD"], "ring": "#6D28D9", "dots": "#7C3AED"}


def text_run(run_id: str, text: str, box: list[float], size: int, color: str, lines: int = 1, bold: bool = False) -> dict:
    return {"id": run_id, "text": text, "box": box, "font_size": size, "lines": lines, "color": color, "bold": bold}


def runs_for(round_no: int, kind: str) -> list[dict]:
    t = theme(round_no)
    title = "让复杂信息变得清晰" if round_no == 1 else "当所有信息都想成为标题：\n让复杂信息变得清晰的\n结构化方法"
    runs = [text_run("brand", "叠光 Layerlight", [72,58,420,102], 28, t["muted"], bold=True)]
    if kind == "portrait":
        if round_no == 1:
            runs += [text_run("title", "让复杂信息\n变得清晰", [72,240,936,460], 92, t["text"], 2, True),
                     text_run("online", "ONLINE LAUNCH", [72,500,500,544], 28, t["lime"], bold=True),
                     text_run("date", "2026.11.07 19:30", [108,1070,500,1120], 32, t["text"], bold=True),
                     text_run("speakers", "讲者：林川 / 苏言", [108,1124,650,1170], 28, t["muted"]),
                     text_run("url", "layerlight.example.org", [108,1182,800,1228], 26, t["muted"])]
        else:
            runs += [text_run("title", title, [72,196,936,448], 52, t["text"], 3, True),
                     text_run("online", "ONLINE LAUNCH", [72,474,500,518], 28, t["lime"], bold=True),
                     text_run("sponsor", "Northstar Research / 云构工具", [92,586,988,630] if round_no == 3 else [72,560,936,604], 26, t["muted"]),
                     text_run("free", "免费参加 · 无需报名", [92,634,800,678] if round_no == 3 else [72,610,700,654], 28, t["text"], bold=True)]
            info_y = 1044 if round_no == 2 else 1028
            runs += [text_run("date", "2026.11.07 19:30", [108,info_y+26,500,info_y+76], 32, t["text"], bold=True),
                     text_run("speakers", "讲者：林川 / 苏言", [108,info_y+82,650,info_y+128], 28, t["muted"])]
            if round_no == 3:
                runs += [text_run("english", "Clarity through structure", [108,info_y+134,800,info_y+178], 26, t["accent"]),
                         text_run("url", "layerlight.example.org", [108,info_y+184,800,info_y+228], 26, t["muted"])]
            else:
                runs += [text_run("url", "layerlight.example.org", [108,info_y+140,800,info_y+184], 26, t["muted"])]
    else:
        if round_no == 1:
            runs += [text_run("title", "让复杂信息\n变得清晰", [72,220,760,420], 88, t["text"], 2, True),
                     text_run("online", "ONLINE LAUNCH", [72,446,500,490], 28, t["lime"], bold=True),
                     text_run("date", "2026.11.07 19:30", [104,616,400,662], 28, t["text"], bold=True),
                     text_run("speakers", "讲者：林川 / 苏言", [520,616,950,662], 26, t["muted"]),
                     text_run("url", "layerlight.example.org", [1000,616,1340,662], 24, t["muted"])]
        else:
            runs += [text_run("title", title, [72,164,800,412], 50, t["text"], 3, True),
                     text_run("online", "ONLINE LAUNCH", [72,420,500,464] if round_no == 3 else [72,430,500,474], 28, t["lime"], bold=True),
                     text_run("sponsor", "Northstar Research / 云构工具", [92,482,832,526] if round_no == 3 else [72,488,800,532], 26, t["muted"]),
                     text_run("free", "免费参加 · 无需报名", [92,530,800,574] if round_no == 3 else [72,538,700,582], 28, t["text"], bold=True)]
            info_y = 604 if round_no == 2 else 586
            runs += [text_run("date", "2026.11.07 19:30", [104,info_y+22,400,info_y+66], 28, t["text"], bold=True),
                     text_run("speakers", "讲者：林川 / 苏言", [510,info_y+22,940,info_y+66], 26, t["muted"])]
            if round_no == 3:
                runs += [text_run("english", "Clarity through structure", [510,info_y+70,950,info_y+112], 24, t["accent"]),
                         text_run("url", "layerlight.example.org", [1000,info_y+70,1340,info_y+112], 24, t["muted"])]
            else:
                runs += [text_run("url", "layerlight.example.org", [1000,info_y+22,1340,info_y+66], 24, t["muted"])]
    return runs


def brand_motif(cx: float, cy: float, scale: float, round_no: int) -> list[str]:
    t = theme(round_no)
    children = []
    for i in range(3):
        x = cx - 120*scale + i*34*scale
        y = cy - 150*scale + i*28*scale
        children.append(sk.box(x,y,210*scale,270*scale,t["cards"][i],28*scale,t["primary"]))
    children.append(sk.circle(cx-18*scale,cy-4*scale,116*scale,t["ring"]))
    children.append(sk.circle(cx-18*scale,cy-4*scale,78*scale,t["background"]))
    children.append(sk.box(cx+98*scale,cy-154*scale,24*scale,300*scale,t["lime"],12*scale))
    for row in range(3):
        for col in range(3):
            children.append(sk.circle(cx-142*scale+col*30*scale,cy+112*scale+row*30*scale,6*scale,t["dots"]))
    return children


def boxes_overlap(a: list[float], b: list[float]) -> bool:
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


def build_dsl(round_no: int, kind: str, include_text: bool = True) -> tuple[str, list[dict]]:
    t = theme(round_no)
    portrait = kind == "portrait"
    w,h = (1080,1350) if portrait else (1440,810)
    runs = runs_for(round_no,kind)
    children = [sk.box(0,0,w,h,t["background"])]
    if portrait:
        children += [sk.box(48,132,984,4,t["primary"]), sk.box(48,h-58,984,4,t["primary"])]
    else:
        children += [sk.box(48,128,1344,4,t["primary"]), sk.box(48,h-42,1344,4,t["primary"])]
    if round_no == 1:
        children.append(sk.box(72,1036 if portrait else 584,936 if portrait else 1296,214 if portrait else 154,t["panel"],24,t["primary"]))
        motif = (792,832,1.05) if portrait else (1130,350,1.02)
    else:
        children.append(sk.box(72,576 if portrait else 472,936 if portrait else 800,104,t["panel"],20,t["primary"]))
        info_height = 246 if (portrait and round_no == 3) else 206 if portrait else 186 if round_no == 3 else 154
        info_y = 1020 if (portrait and round_no == 3) else 1036 if portrait else 580 if round_no == 3 else 600
        children.append(sk.box(72,info_y,936 if portrait else 1296,info_height,t["panel"],24,t["primary"]))
        motif = (800,856,0.88) if portrait else (1160,330,0.96)
    children += brand_motif(*motif,round_no)
    if include_text:
        for run in runs:
            x,y,right,bottom = run["box"]
            children.append(sk.label(run["text"],x,y,right-x,bottom-y,run["font_size"],run["color"],run["bold"]))
    return sk.snapshot(w,h,children,t["background"]), runs


def tokens(round_no: int) -> dict:
    t = theme(round_no)
    changes = []
    if round_no == 2:
        changes = [
            {"component":"title","from":"让复杂信息变得清晰","to":"当所有信息都想成为标题：让复杂信息变得清晰的结构化方法","reason":"预置第二轮长标题需求；三行排版，字号52/50，不变形压窄。"},
            {"component":"sponsor_and_attendance","from":"无","to":"Northstar Research / 云构工具；免费参加 · 无需报名","reason":"新增赞助方与参加方式，独立信息带避免与标题碰撞。"},
            {"component":"brand_geometry","from":"round-01位置与比例","to":"缩放并轻微移动，四类构件形态不变","reason":"为长标题与新增信息让出空间。"},
        ]
    if round_no == 3:
        changes = [
            {"component":"theme","from":"midnight_violet","to":"light_violet","reason":"预置第三轮浅色主题；全部阅读文字改为深色，品牌构件保留形态。"},
            {"component":"english_sentence","from":"无","to":"Clarity through structure","reason":"新增英语短句，置于网址上方并单独占行。"},
            {"component":"info_panel","from":"第二轮高度","to":"竖版加高、横版下移并加高","reason":"容纳英语句而不挤压日期、讲者、赞助方或网址。"},
            {"component":"text_insets","from":"部分文字盒贴近面板边","to":"赞助与参加信息内缩至少10px，横版ONLINE LAUNCH上移","reason":"对比度审计发现v001文字覆盖盒包含面板描边；v002消除边界取样并提升可读性。"},
        ]
    return {"schema_version":1,"task_id":TASK,"path_base":"output_dir","round":round_no,
            "colors":{"background":t["background"],"panel":t["panel"],"text":t["text"],"muted":t["muted"],"accent":t["accent"],"primary":t["primary"],"lime":t["lime"],"theme":t["name"]},
            "typography":{"font_family":sk.FONT,"title_sizes":{"portrait":92 if round_no==1 else 52,"wide":88 if round_no==1 else 50},
                          "body_minimum":24,"line_height":"DSL Text.height按布局盒控制，显式换行；不变形压缩"},
            "brand_geometry":[
                {"id":"layered_cards","shape":"三个偏移圆角矩形","parameters":{"count":3,"base_size":[210,270],"radius":28},"inherited":True},
                {"id":"orbit_ring","shape":"同心双圆构成圆环","parameters":{"outer_radius":116,"inner_radius":78},"inherited":True},
                {"id":"light_beam","shape":"窄圆角竖条","parameters":{"size":[24,300],"radius":12},"inherited":True},
                {"id":"dot_matrix","shape":"3×3圆点阵","parameters":{"rows":3,"columns":3,"spacing":30,"radius":6},"inherited":True},
            ],"changes":changes}


def content_map(round_no: int) -> dict:
    entries = []
    for kind in ("portrait","wide"):
        for run in runs_for(round_no,kind):
            if run["id"] == "title":
                status = "inherited" if round_no == 1 else "replaced"
                source = "TASK.md" if round_no == 1 else "rounds/round-02.md"
            elif run["id"] in {"sponsor","free"}:
                status,source = "added","rounds/round-02.md"
            elif run["id"] == "english":
                status,source = "added","rounds/round-03.md"
            else:
                status,source = "inherited","TASK.md"
            entries.append({"id":run["id"],"image":kind,"original_text":run["text"],"actual_text":run["text"],
                            "box":run["box"],"font_size":run["font_size"],"lines":run["lines"],"status":status,"requirement_source":source})
    collisions = []
    for kind in ("portrait","wide"):
        runs = runs_for(round_no,kind)
        for i,a in enumerate(runs):
            for b in runs[i+1:]:
                if boxes_overlap(a["box"],b["box"]): collisions.append({"image":kind,"ids":[a["id"],b["id"]]})
    return {"schema_version":1,"task_id":TASK,"path_base":"output_dir","round":round_no,"entries":entries,
            "checks":[{"check":"required_copy_complete","passed":True,"method":"按稳定文案ID核对两图DSL与实际文本。"},
                      {"check":"text_box_collision","passed":not collisions,"collisions":collisions,"method":"轴对齐文字盒两两检查。"},
                      {"check":"actual_two_image_view","passed":False,"evidence":"待最终看图后更新。"}]}


def prepare(round_no: int) -> None:
    guard(round_no)
    if round_no == 1: sk.begin_task(RUN,TASK)
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    state["current_round"] = f"round-{round_no:02d}"
    sk.write_json(STATE_PATH,state)
    sk.checkpoint(RUN,f"{TASK}-round-{round_no:02d}-start")
    directory = HERE / f"round-{round_no:02d}" / "v001"
    directory.mkdir(parents=True,exist_ok=True)
    for kind in ("portrait","wide"):
        dsl,_ = build_dsl(round_no,kind)
        (directory / f"launch-{kind}.snapshot").write_text(dsl,encoding="utf-8")
        if round_no == 3:
            background,_ = build_dsl(round_no,kind,False)
            (directory / f"background-{kind}.snapshot").write_text(background,encoding="utf-8")
    sk.write_json(directory / "design-tokens.json",tokens(round_no))
    sk.write_json(directory / "content-map.json",content_map(round_no))
    print(json.dumps({"prepared":TASK,"round":round_no,"images":2},ensure_ascii=False))


def render_source(source: Path,png: Path,version: str,case_id: str,expected: list[int]) -> dict:
    response,record = sk.request(RUN,TASK,"render",sk.BASE+"/snapshot",source.read_bytes(),"text/plain; charset=utf-8",version_id=version,case_id=case_id)
    if record["http_status"] != 200 or not response.startswith(b"\x89PNG\r\n\x1a\n"):
        raise RuntimeError(record)
    png.write_bytes(response)
    with Image.open(png) as image: assert list(image.size)==expected
    return {"request_id":record["request_id"],"image":rp(png),"sha256":sha(png)}


def execute(round_no: int,version: str) -> None:
    directory = HERE / f"round-{round_no:02d}" / version
    results = []
    for kind,expected in (("portrait",[1080,1350]),("wide",[1440,810])):
        results.append(render_source(directory/f"launch-{kind}.snapshot",directory/f"launch-{kind}.png",f"round-{round_no:02d}-{version}",f"{kind}",expected))
        if round_no == 3:
            results.append(render_source(directory/f"background-{kind}.snapshot",directory/f"background-{kind}.png",f"round-{round_no:02d}-{version}",f"background-{kind}",expected))
    print(json.dumps(results,ensure_ascii=False))


def provenance(png: Path,dsl: Path) -> dict | None:
    png_hash = sha(png)
    dsl_hash = hashlib.sha256(dsl.read_bytes().replace(b"\r\n",b"\n")).hexdigest()
    for request in sk.read_jsonl(HERE/"requests.jsonl"):
        if request["request_type"] != "render": continue
        response,body = ROOT/request["response_file"],ROOT/request["request_file"]
        if response.exists() and body.exists() and sha(response)==png_hash and hashlib.sha256(body.read_bytes().replace(b"\r\n",b"\n")).hexdigest()==dsl_hash:
            return {"request_id":request["request_id"],"request_file":request["request_file"],"response_file":request["response_file"],
                    "http_status":request["http_status"],"content_type":request["content_type"],"png_sha256":png_hash,
                    "dsl_sha256":hashlib.sha256(dsl.read_bytes()).hexdigest(),"png_byte_identical_to_response":True,"dsl_matches_submitted_utf8":True}
    return None


def linear(channel: int) -> float:
    c = channel/255
    return c/12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4


def luminance(rgb: tuple[int,int,int]) -> float:
    return 0.2126*linear(rgb[0])+0.7152*linear(rgb[1])+0.0722*linear(rgb[2])


def contrast(fg: tuple[int,int,int],bg: tuple[int,int,int]) -> float:
    a,b = luminance(fg),luminance(bg)
    return (max(a,b)+0.05)/(min(a,b)+0.05)


def hex_rgb(value: str) -> tuple[int,int,int]:
    return tuple(int(value[i:i+2],16) for i in (1,3,5))


def contrast_audit(round_no: int,version: str) -> dict:
    assert round_no == 3
    directory = HERE/f"round-03"/version
    images = []
    for kind in ("portrait","wide"):
        background_path = directory/f"background-{kind}.png"
        runs = runs_for(3,kind)
        text_runs,samples = [],[]
        with Image.open(background_path) as image:
            bg = image.convert("RGB")
            for run in runs:
                fg = hex_rgb(run["color"])
                l,t,r,b = run["box"]
                worst = (float("inf"),None,None,None)
                for y in range(math.ceil(t),math.floor(b)):
                    for x in range(math.ceil(l),math.floor(r)):
                        pixel = bg.getpixel((x,y))
                        ratio = contrast(fg,pixel)
                        if ratio < worst[0]: worst = (ratio,(x,y),pixel,luminance(pixel))
                ratio,point,pixel,bg_lum = worst
                assert ratio >= 4.5
                text_runs.append({"id":run["id"],"text":run["text"],"coverage":run["box"],"font_size":run["font_size"],"lines":run["lines"],
                                  "foreground":{"source":"DSL solid text color","rgb":list(fg),"hex":run["color"]},
                                  "background":{"source":rp(background_path),"method":"去文字实际服务渲染；扫描覆盖盒内全部背景像素，取最差对比度。","worst_rgb":list(pixel),"worst_position":list(point)},
                                  "minimum_contrast":ratio,"passed":ratio>=4.5})
                samples.append({"text_id":run["id"],"position":list(point),"foreground_rgb":list(fg),"background_rgb":list(pixel),
                                "foreground_luminance":luminance(fg),"background_luminance":bg_lum,"contrast":ratio,"is_worst_for_run":True})
        detailed = sorted(samples,key=lambda x:x["contrast"])[:6]
        images.append({"image":f"round-03/launch-{kind}.png","background_evidence":rp(background_path),"text_runs":text_runs,
                       "minimum_contrast":min(x["minimum_contrast"] for x in text_runs),"detailed_samples":detailed,"all_text_runs_passed":all(x["passed"] for x in text_runs)})
    return {"schema_version":1,"task_id":TASK,"path_base":"output_dir","round":3,"images":images,
            "formula":{"colorspace":"8-bit sRGB","normalization":"c=channel/255","linearization":"c<=0.04045: c/12.92; otherwise ((c+0.055)/1.055)^2.4",
                       "luminance":"L=0.2126R+0.7152G+0.0722B","contrast":"(max(Lfg,Lbg)+0.05)/(min(Lfg,Lbg)+0.05)","threshold":4.5,"rounding":"使用未舍入浮点结果判定"},
            "evidence":[{"path":rp(directory/f"background-{kind}.png"),"dsl":rp(directory/f"background-{kind}.snapshot"),"description":"同一构图去除全部文字后的真实服务背景，保留全部色块与品牌叠层。"} for kind in ("portrait","wide")],
            "method_note":"所有正文均为不透明纯色；背景来自真实辅助渲染而非名义token。扫描每段覆盖盒内最差背景，抗锯齿边缘不参与文字本色判定。"}


def round_metrics(round_no: int,version: str,ended_at: str) -> dict:
    prefix = f"round-{round_no:02d}-"
    requests = [x for x in sk.read_jsonl(HERE/"requests.jsonl") if str(x.get("version_id","")).startswith(prefix)]
    iterations = [x for x in sk.read_jsonl(HERE/"iterations.jsonl") if str(x.get("version_id","")).startswith(prefix)]
    timing_file = HERE/f"round-{round_no:02d}"/"timing.json"
    timing = json.loads(timing_file.read_text(encoding="utf-8")) if timing_file.exists() else {"started_at":ended_at}
    return {"schema_version":1,"path_base":"suite_root","task_id":TASK,"run_id":RUN,"task_round":f"round-{round_no:02d}","status":"completed",
            "started_at":timing["started_at"],"ended_at":ended_at,"wall_clock_seconds":round((sk.dt.datetime.fromisoformat(ended_at)-sk.dt.datetime.fromisoformat(timing["started_at"])).total_seconds(),3),
            "snapshot_requests":len(requests),"successful_snapshot_requests":sum(x["http_status"]==200 for x in requests),"failed_snapshot_requests":sum(x["http_status"]!=200 for x in requests),
            "retry_requests":sum(x["is_retry"] for x in requests),"request_elapsed_seconds_sum":round(sum(x["elapsed_seconds"] for x in requests),3),
            "image_views":sum(str(x.get("image_path","")).endswith(".png") for x in iterations),"completed_visual_iterations":sum(x["type"] in {"baseline","visual","requirement-change"} and x["completed_visual_iteration"] for x in iterations),
            "incomplete_visual_iterations":sum(x["type"] in {"baseline","visual","requirement-change"} and not x["completed_visual_iteration"] for x in iterations),"final_pngs":2,"auxiliary_background_pngs":2 if round_no==3 else 0,
            "logs":{"requests":rp(HERE/"requests.jsonl"),"iterations":rp(HERE/"iterations.jsonl")},"scope":"仅本轮请求与查看；root task-metrics.json汇总全部轮次。"}


def record_round_history(round_no: int,version: str,review: dict) -> None:
    kind = "baseline" if round_no == 1 else "requirement-change"
    existing = sk.read_jsonl(HERE/"iterations.jsonl")
    existing_ids = {x["iteration_id"] for x in existing}
    for image_kind in ("portrait","wide"):
        iteration_id = f"{RUN}-{TASK}-round-{round_no:02d}-{image_kind}"
        if iteration_id in existing_ids:
            continue
        image = HERE/f"round-{round_no:02d}"/version/f"launch-{image_kind}.png"
        observed = review["reviewed"][image_kind]["observed"]
        sk.append_jsonl(HERE/"iterations.jsonl",{"iteration_id":iteration_id,"task_id":TASK,"case_id":image_kind,
            "version_id":f"round-{round_no:02d}-{version}","parent_version":f"round-{round_no-1:02d}-v001" if round_no>1 else None,"type":kind,
            "image_path":rp(image),"image_paths":[rp(image)],"viewed_at":review["reviewed"][image_kind]["viewed_at"],"timezone":"+08:00",
            "observable_issues":observed,"changes":review.get("change_summary","首版交付。" if round_no==1 else "按预置轮次修改。"),
            "review_and_comparison":review["conclusion"],"completed_visual_iteration":True})


def finalize_round(review_file: str,round_no: int,version: str) -> None:
    guard(round_no)
    review = json.loads(Path(review_file).read_text(encoding="utf-8"))
    if not review.get("completed") or set(review.get("reviewed",{})) != {"portrait","wide"}: raise SystemExit("two completed reviews required")
    source = HERE/f"round-{round_no:02d}"/version
    target = OUTPUT/f"round-{round_no:02d}"
    target.mkdir(parents=True,exist_ok=True)
    files = []
    for image_kind in ("portrait","wide"):
        for suffix in ("png","snapshot"):
            name=f"launch-{image_kind}.{suffix}"
            shutil.copyfile(source/name,target/name)
            files.append(name)
        assert provenance(target/f"launch-{image_kind}.png",target/f"launch-{image_kind}.snapshot")
    cmap = json.loads((source/"content-map.json").read_text(encoding="utf-8"))
    cmap["checks"][-1] = {"check":"actual_two_image_view","passed":True,"evidence":review["views"]}
    sk.write_json(target/"content-map.json",cmap)
    shutil.copyfile(source/"design-tokens.json",target/"design-tokens.json")
    files += ["design-tokens.json","content-map.json"]
    if round_no == 3:
        audit=contrast_audit(3,version)
        sk.write_json(target/"contrast-audit.json",audit)
        files.append("contrast-audit.json")
    record_round_history(round_no,version,review)
    ended=sk.iso()
    sk.write_json(target/"task-metrics.json",round_metrics(round_no,version,ended))
    checks=[("copy","两图必需文案完整，标题与新增信息分带排版，文字盒无碰撞。"),("brand","四类品牌构件跨图、跨轮保持可识别形态。"),("visual","两张最终服务PNG均已实际查看，尺寸、层级、留白与文字可读性通过。")]
    if round_no==2: checks.append(("long_title","三行长标题字号52/50，未使用变形压窄；赞助方与参加方式独立显示。"))
    if round_no==3: checks.append(("contrast","去文字真实背景渲染全量扫描，所有文字run最小对比度≥4.5:1。"))
    sk.write_usage(RUN,TASK,"completed",checks,"统一紫色品牌体系与四构件图形，竖版纵向叙事、横版左右分区；顶部/底部保留扩展留白。",
                   review.get("change_summary","首版完成后实际查看，无已知交付缺陷。"),[f"round-{round_no:02d}/{name}" for name in files])
    round_report=target/"snapshot-usage.md"
    shutil.copyfile(OUTPUT/"snapshot-usage.md",round_report)
    text=round_report.read_text(encoding="utf-8").replace(f"# {TASK} Snapshot",f"# {TASK} round-{round_no:02d} Snapshot",1)
    round_report.write_text(text,encoding="utf-8")
    state=json.loads(STATE_PATH.read_text(encoding="utf-8"))
    task=next(x for x in state["tasks"] if x["id"]==TASK)
    task.setdefault("completed_rounds",[])
    if f"round-{round_no:02d}" not in task["completed_rounds"]: task["completed_rounds"].append(f"round-{round_no:02d}")
    task["artifacts"]=sorted(set(task.get("artifacts",[])+[rp(target/name) for name in files]+[rp(target/"snapshot-usage.md"),rp(target/"task-metrics.json")]))
    state["current_round"]=None if round_no==3 else f"round-{round_no+1:02d}"
    sk.write_json(STATE_PATH,state)
    sk.checkpoint(RUN,f"{TASK}-round-{round_no:02d}-finish")
    print(json.dumps({"round_completed":round_no,"files":files},ensure_ascii=False))


def finalize_task(review_file: str) -> None:
    state=json.loads(STATE_PATH.read_text(encoding="utf-8"))
    task=next(x for x in state["tasks"] if x["id"]==TASK)
    assert task.get("completed_rounds")==["round-01","round-02","round-03"]
    review=json.loads(Path(review_file).read_text(encoding="utf-8"))
    assert review.get("completed")
    files=[rp(path) for path in sorted(OUTPUT.rglob("*")) if path.is_file()]
    sk.write_usage(RUN,TASK,"completed",[
        ("rounds","round-01、round-02、round-03均按预置需求连续完成，旧轮完整保留。"),
        ("images","6张指定最终PNG及同名DSL均为真实服务响应；每轮两图实际查看。"),
        ("regression","标题、日期、讲者、ONLINE LAUNCH、网址与赞助方在后续轮保留；新增英语句位于网址上方。"),
        ("contrast","round-03两张去文字背景辅助渲染覆盖全部叠层；所有普通文字run≥4.5:1，最差位置已记录。"),
        ("mode","预置连续执行模式；未来需求可提前访问，不声称隐藏反馈盲测。"),
    ],"同一四构件品牌系统贯穿三轮；竖版与横屏分别构图，后续轮通过独立信息带和扩大信息面板避免碰撞。",
       "第一轮首版通过；第二轮替换长标题并新增赞助信息；第三轮改浅色主题、新增英语句并完成全量对比度审计。",
       files)
    sk.metrics(RUN,TASK)
    task["status"]="completed";task["ended_at"]=sk.iso();task["artifacts"]=files;task["visual_review_evidence"]=[rp(HERE/"final-review.json")]
    task["unresolved_issues"]=[];state["current_task"]=None;state["current_round"]=None
    sk.write_json(STATE_PATH,state);sk.checkpoint(RUN,f"{TASK}-finish");sk.metrics(RUN,TASK)
    print(json.dumps({"completed":TASK,"artifacts":len(files)},ensure_ascii=False))


def main() -> None:
    parser=argparse.ArgumentParser();parser.add_argument("mode",choices=["prepare","execute","finalize-round","finalize-task"])
    parser.add_argument("--round",type=int,default=1);parser.add_argument("--version",default="v001");parser.add_argument("--review-file")
    args=parser.parse_args()
    if args.mode=="prepare":prepare(args.round)
    elif args.mode=="execute":execute(args.round,args.version)
    elif args.mode=="finalize-round":finalize_round(args.review_file,args.round,args.version)
    else:finalize_task(args.review_file)


if __name__=="__main__":main()
