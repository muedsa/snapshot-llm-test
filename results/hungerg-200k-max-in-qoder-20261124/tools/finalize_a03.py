from __future__ import annotations
import json
import shutil
import struct
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import suitekit as s
import a03

rid, task = a03.RUN_ID, a03.TASK
out, tmp = s.task_dirs(rid, task)
# Preserve each actual view event, including probes and the failed original request.
s.record_iteration(rid, task, "v000-original", tmp / "original-broken.snapshot", "syntax-fix", "HTTP 400 PARSE_ERROR：Transform 缺少 matrix；没有可用图片", "依据诊断修改 Transform", "失败响应已保留，未当作图片", completed=False)
s.record_iteration(rid, task, "v001-v004", tmp / "versions/v004/stage4-positioned-full.snapshot", "syntax-fix", "显式 matrix 错误修复后仍报 StackParentData；四次失败响应分别保留", "逐项检查父组件、有界 Stack 和 Positioned", "通过最小探针确认 LIVE 必须位于 Row 之外", completed=False)
for name, observation in (
    ("probe-minimal", "Positioned+Stack 最小结构成功，LIVE 可见"),
    ("probe-row", "有界 Stack 内 Row+Expanded+Positioned 成功，确认 Flex 组合可行"),
    ("probe-no-positioned", "移除 LIVE 后全稿成功，定位问题在 LIVE 的父组件"),
    ("probe-col-after-row", "LIVE 放在 Row 后成功，确认正确父级"),
    ("probe-col-before-row", "LIVE 放在 Row 前也成功，确认只需直接位于 Stack"),
):
    s.record_iteration(rid, task, name, tmp / "versions" / name / f"{name}-01.png", "alternative", observation, "探针仅用于定位，不冒充最终交付", "实际打开探针 PNG，比较父级位置", completed=True)
s.record_iteration(rid, task, "v005", tmp / "versions/v005/stage5-valid-stack-01.png", "baseline", "首次显式错误全部修复；REVIEW 呈青色不透明，说明文字被 ImageFiltered 模糊", "修正 CSS alpha 顺序；改用 BackdropFilter；补全三指标与固定布局", "v006 复看验证")
s.record_iteration(rid, task, "v006-final-candidate", tmp / "versions/v006-final-candidate/system-pulse-01.png", "visual", "候选图三指标、标题、LIVE、REVIEW 与中央卡片完整；局部预览显示卡内条带柔化而文字清晰", "保留候选为最终，不后处理", "对照 1280×800、32 安全边距、44/28/24 字号及 -8° 旋转核验")

version = tmp / "versions/v006-final-candidate"
source = version / "system-pulse-01.png"
shutil.copyfile(source, out / "system-pulse.png")
shutil.copyfile(version / "system-pulse.snapshot", out / "system-pulse.snapshot")
data = (out / "system-pulse.png").read_bytes()
assert data[:8] == b"\x89PNG\r\n\x1a\n"
assert struct.unpack(">II", data[16:24]) == (1280, 800)
s.write_json(out / "repair-log.json", a03.repair_log())
checks = [
    ("原稿真实提交", "通过；未改 DSL 首次请求 400 PARSE_ERROR，原请求/响应与错误诊断保留"),
    ("显式错误恢复", "通过；Transform matrix、Positioned 父级、有界 Stack 全部修复，无删除功能区块"),
    ("静默属性", "通过；移除 Snapshot 未知 width/height；font-size 改 fontSize；根 Container 控制 1280×800"),
    ("alpha 语义", "通过；REVIEW 背景 #FFFFFF33 为白色 20%，兄弟文字 #FFFFFF 不透明"),
    ("三指标卡", "通过；USAGE 72%、LATENCY 148 ms、SUCCESS 99.2%，字号 28，宽 394/395/395"),
    ("中央背景模糊", "通过；500×150、圆角 24；彩条穿过左右边界，卡内 BackdropFilter sigma=10，卡外锐利、文字清晰"),
    ("标签与安全区", "通过；标题 44；LIVE 96×36 不盖标题；REVIEW 160×56 逆时针 8°；所有元素在 32 安全边距内"),
    ("repair-log.json", "通过；7 类问题均对应原稿行、依据、修改与验证；逐版本 DSL/响应/PNG 路径齐全"),
]
files = ["system-pulse.png", "system-pulse.snapshot", "repair-log.json", "snapshot-usage.md", "task-metrics.json"]
s.write_usage(rid, task, "completed", checks,
    "深色监控卡使用有限根画布与绝对定位保证几何精确。三张等宽指标卡形成第一阅读层；中央卡片用 BackdropFilter 隔离背景模糊，文字置于滤镜之外；LIVE 与 REVIEW 作为状态标签保持在安全区。",
    "原样提交得到 Transform matrix 必填错误；继续修复时暴露 Positioned 父级错误，并通过五个最小探针定位。v005 实际查看发现八位色 alpha 顺序导致 REVIEW 青色不透明，以及 ImageFiltered 连文字一起模糊。最终改为 #FFFFFF33、BackdropFilter+ClipRRect，文字与滤镜分层。所有失败稿和探针均保留。",
    files)
s.metrics(rid, task)
s.finish_task(rid, task, files, [f"tmp/{rid}/{task}/iterations.jsonl"])
print(json.dumps({"task": task, "status": "completed", "files": files}, ensure_ascii=False))
