from __future__ import annotations

import json
import shutil
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import suitekit as s
import a06

rid, task = a06.RUN_ID, a06.TASK
out, tmp = s.task_dirs(rid, task)
files = [
    "dependency-map.png", "dependency-map.snapshot", "graph-audit.json",
    "snapshot-usage.md", "task-metrics.json",
]


def verify_audit() -> None:
    graph = a06.load_graph()
    result = a06.audit(graph)
    assert len(result["nodes"]) == 14
    assert len(result["prerequisite_edges"]) == 16
    assert len(result["feedback_edges"]) == 2
    assert result["longest_path"]["length_nodes"] == 11
    assert result["longest_path"]["path"] == ["N01", "N02", "N05", "N06", "N08", "N09", "N10", "N11", "N12", "N13", "N14"]
    node_by_id = {node["id"]: node for node in result["nodes"]}
    for edge in result["prerequisite_edges"]:
        assert node_by_id[edge["to"]]["topological_layer"] > node_by_id[edge["from"]]["topological_layer"]
        assert edge["from"] in node_by_id[edge["to"]]["in_neighbors"]
        assert edge["to"] in node_by_id[edge["from"]]["out_neighbors"]
    assert all(not edge["participates_in_dag"] for edge in result["feedback_edges"])
    s.write_json(out / "graph-audit.json", result)


def prepare() -> None:
    verify_audit()
    version = tmp / "versions/v003"
    shutil.copyfile(version / "dependency-map-01.png", out / "dependency-map.png")
    shutil.copyfile(version / "dependency-map.snapshot", out / "dependency-map.snapshot")
    data = (out / "dependency-map.png").read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n" and struct.unpack(">II", data[16:24]) == (1600, 1000)
    s.record_iteration(
        rid, task, "local-preflight", tmp / "preflight-error-001.txt", "syntax-fix",
        "本地交叉检测元组解包错误；尚未发送服务请求，没有可用图片",
        "修正正交线段端点解包；保留错误记录",
        "修正后拓扑、路径与节点穿越断言通过，随后取得首个真实渲染", completed=False,
    )
    s.record_iteration(
        rid, task, "v001", tmp / "versions/v001/dependency-map-01.png", "baseline",
        "14节点、16先决边与2反馈边均显示；底部最长路径被470像素文本框截断，末尾N13/N14不可见",
        "规划v002扩大路径文本框并调整说明卡布局",
        "v002复看比较",
    )
    s.record_iteration(
        rid, task, "v002", tmp / "versions/v002/dependency-map-01.png", "visual",
        "最长路径已完整；几何复核发现N02→N04/N05箭头停在节点左边框外约4像素",
        "将两个箭头端点由x=318修正到实际节点左边界x=322；审计增加S/F边ID",
        "v003复看比较",
    )
    s.record_iteration(
        rid, task, "v003", tmp / "versions/v003/dependency-map-01.png", "visual",
        "未发现影响交付的缺陷；全部节点标签、箭头、虚线反馈、交叉留白、路径与说明完整清晰",
        "保留v003为最终，不后处理图像",
        "逐边核对方向与拓扑层；N04→N13跨层线路上方绕行；F01在F02交叉处留 gap，无连接点",
    )
    checks = [
        ("1600×1000 真实 PNG", "通过；服务原始字节，PNG签名与IHDR尺寸正确"),
        ("14节点完整性", "通过；N01–N14编号和中文标签全部出现，节点字号22"),
        ("16条先决边", "通过；每条均为实线并带方向箭头，目标层严格大于源层"),
        ("2条反馈边", "通过；N09→N08、N10→N08使用玫红虚线与专用图例，不参与DAG"),
        ("交叉不误连", "通过；仅节点边框箭头端点为连接；F01/F02交叉处保留明确断口，无连接点"),
        ("并行与绕行", "通过；N02/N03、N04/N05并行；N04→N13从上方绕行；密集连接使用侧边弯折"),
        ("返工语义", "通过；图内标注‘失败后回到构建’和‘检查发现问题后修复’"),
        ("最长路径", "通过；程序动态规划得11节点，图中完整显示N01→N02→N05→N06→N08→N09→N10→N11→N12→N13→N14"),
        ("graph-audit.json", "通过；节点层/入出邻居/像素盒、每条边路径与箭头、反馈表示、交叉与计算方法齐全"),
        ("视觉检查", "通过；v001/v002/v003均实际查看；修复路径截断与箭头间隙后复看无遮挡裁剪"),
    ]
    s.write_usage(
        rid, task, "completed", checks,
        "采用11列拓扑层从左到右展开，前四列体现并行分支，后七列形成可复现交付主链。蓝/青/紫节点区分准备、构建检查、校验归档；实线灰表示先决，玫红虚线表示反馈。长跨层边走上层，反馈走下层，并在唯一反馈交叉处留断口。",
        "首次本地预检发生元组解包错误，未发请求，修正并保留记录。v001实际查看发现最长路径文本截断，v002扩大文本框修复；随后几何核对发现两个箭头与节点边界有4像素间隙，v003修正端点。最终候选实际查看确认所有边、节点、反馈语义和完整路径清晰。",
        files,
    )
    s.metrics(rid, task)
    print(json.dumps({"task": task, "phase": "prepared", "files": files}, ensure_ascii=False))


def finish() -> None:
    s.record_iteration(
        rid, task, "v003", out / "dependency-map.png", "audit_visual_recheck",
        "最终输出复看未发现缺陷；与v003候选为同一服务原始PNG字节",
        "完成交付前最终复看，不改动图像",
        "复核14节点、16实线先决、2虚线反馈、交叉无连接、完整最长路径、反馈说明及审计JSON",
    )
    s.metrics(rid, task)
    s.finish_task(rid, task, files, [f"tmp/{rid}/{task}/iterations.jsonl"])
    print(json.dumps({"task": task, "status": "completed", "files": files}, ensure_ascii=False))


if __name__ == "__main__":
    if "--finish" in sys.argv:
        finish()
    else:
        prepare()
