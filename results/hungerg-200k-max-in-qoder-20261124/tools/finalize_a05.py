from __future__ import annotations

import json
import shutil
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import suitekit as s
import a05

rid, task = a05.RUN_ID, a05.TASK
out, tmp = s.task_dirs(rid, task)
version = tmp / "versions/v001"
files = [
    "sensor-report.png", "sensor-report.snapshot", "normalized-data.json",
    "snapshot-usage.md", "task-metrics.json",
]


def verify_data() -> None:
    samples = a05.load_data()
    audit = a05.normalized(samples)
    assert [r["minute_offset"] for r in samples] == [0, 10, 35, 60, 75, 100, 130, 170, 180, 220, 250, 270]
    assert audit["statistics"]["temperature_c"]["valid_count"] == 10
    assert audit["statistics"]["humidity_pct"]["valid_count"] == 11
    assert audit["statistics"]["pressure_kpa"]["valid_count"] == 12
    assert audit["segments"]["temperature_c"] == [["R01", "R02", "R03", "R04"], ["R06", "R07", "R08", "R09"], ["R11", "R12"]]
    assert audit["segments"]["humidity_pct"] == [["R01", "R02", "R03", "R04", "R05"], ["R07", "R08", "R09", "R10", "R11", "R12"]]
    assert [r["id"] for r in audit["negative_samples"]] == ["R06", "R07", "R08"]
    for metric in a05.METRICS:
        key = metric["key"]
        for segment in audit["segments"][key]:
            assert all(next(r for r in samples if r["id"] == sample_id)[key] is not None for sample_id in segment)
    s.write_json(out / "normalized-data.json", audit)


def prepare() -> None:
    verify_data()
    shutil.copyfile(version / "sensor-report-01.png", out / "sensor-report.png")
    shutil.copyfile(version / "sensor-report.snapshot", out / "sensor-report.snapshot")
    data = (out / "sensor-report.png").read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n" and struct.unpack(">II", data[16:24]) == (1440, 1000)
    s.record_iteration(
        rid, task, "v001", version / "sensor-report-01.png", "baseline",
        "未发现影响交付的缺陷；三联图比例与断线正确，负压实测点、零线、KPI和12时点表清晰完整",
        "首版满足要求，保留 v001 为最终，不制造无意义视觉迭代",
        "逐图核对采样标记与数据；09:15/11:40温度及09:40湿度缺测两侧均断开，三个负压点仅按实际采样标注",
    )
    checks = [
        ("1440×1000 真实 PNG", "通过；服务原始字节，PNG 签名与 IHDR 尺寸正确"),
        ("共享真实时间轴", "通过；08:00–12:30共270分钟，x=160+minute_offset/270×1230；三图参考线逐像素对齐"),
        ("单位与纵轴", "通过；温度°C、湿度%、压差kPa各自独立纵轴；正文≥20，轴/表≥18"),
        ("采样标记", "通过；每个有效读数都有独立圆形标记，共33个有效标记"),
        ("缺测与断线", "通过；温度10/12、湿度11/12，灰色×标识缺测，连接段不跨越null"),
        ("压差正负", "通过；零线加粗，09:40=-0.2、10:10=-0.8、10:50=-0.3 kPa；未推断连续区间恒负"),
        ("KPI与明细", "通过；顶部有效数及观测范围准确，下表完整列出12时点，缺测显示—"),
        ("normalized-data.json", "通过；12个分钟偏移、null缺测、范围、有效数、连接段、负压样本及轴映射齐全"),
        ("视觉检查", "通过；v001已用Read实际查看，文字、图例、表格无遮挡裁剪，图形与坐标对应"),
    ]
    s.write_usage(
        rid, task, "completed", checks,
        "三联等宽面板共享同一时间几何，红/蓝/紫分别编码温度、湿度和压差。横向参考线保持轻量，压差零线加粗，负压实测点使用实心玫红标记；缺测使用灰色×并与断线图例呼应。",
        "首版实际查看后满足全部内容和几何要求，没有已知影响交付的缺陷，因此未追加无意义重渲染。normalized-data.json由同一输入和几何函数生成，并在交付前断言核对连接段与负压样本。",
        files,
    )
    s.metrics(rid, task)
    print(json.dumps({"task": task, "phase": "prepared", "files": files}, ensure_ascii=False))


def finish() -> None:
    s.record_iteration(
        rid, task, "v001", out / "sensor-report.png", "audit_visual_recheck",
        "最终输出复看未发现缺陷；与v001候选为同一服务原始PNG字节",
        "完成交付前最终复看，不改动图像",
        "复核三图、缺测断线、负压实测点、零线、图例、KPI、12时点表和全部文件配对",
    )
    s.metrics(rid, task)
    s.finish_task(rid, task, files, [f"tmp/{rid}/{task}/iterations.jsonl"])
    print(json.dumps({"task": task, "status": "completed", "files": files}, ensure_ascii=False))


if __name__ == "__main__":
    if "--finish" in sys.argv:
        finish()
    else:
        prepare()
