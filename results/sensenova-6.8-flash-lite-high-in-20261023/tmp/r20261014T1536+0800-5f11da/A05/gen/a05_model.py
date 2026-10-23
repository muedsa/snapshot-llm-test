"""A05 数据模型：从 readings.csv 精确计算缺测、有效数、观察极值、连接段与坐标比例。

题面关键约束在此一次性算清，后续 DSL 构建与本文件不再各自硬编码数值：
  * 空单元格是缺测，不是 0（读 CSV 时留空 → None）；
  * 连接段只在「相邻两个采样点都有值」时成立，缺测两侧绝不连接；
  * 负压差只登记实际为负的采样点，不推断「连续期间每一刻均为负」。

输出：
  outputs/<run_id>/A05/normalized-data.json   （交付物，审计字段按 templates/audit-fields.json）
  tmp/<run_id>/A05/model.json                 （同上 + 像素几何，供 builder/inspect 复用）

启动基准：总任务根（cwd）。用法：python a05_model.py
"""

from __future__ import annotations

import csv
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a05_io as IO  # noqa: F401  (确保目录环境变量与 ROOT 初始化)

HERE = Path(__file__).resolve().parent
CSV = IO.ROOT / "tasks" / "A05-irregular-sensors" / "inputs" / "readings.csv"
TASK_ID = "A05"
T0 = dt.datetime(2000, 1, 1, 8, 0)   # 仅作差用；真实时间只取 HH:MM
MIN0, MIN1 = 0, 270                 # 08:00 → 12:30，真实跨度 270 分钟

# 画布 1440×1000；与 a05_build.py 共用同一份像素常量，避免双写漂移。
PW, PH = 1440, 1000
M = 40                                # 外边距
PLOT_X0, PLOT_X1 = 178.0, 1382.0      # 共享横轴像素区间
PLOT_W = PLOT_X1 - PLOT_X0
MIN_PX = PLOT_W / MIN1                # 每分钟的像素数（三图共用）

ROWS = {
    "temperature_c": dict(
        key="temperature_c", label="温度", unit="°C", color="#2563EB",
        header_top=184, y0=214.0, y1=278.0, lo=18.0, hi=24.0,
        ticks=[18.0, 20.0, 22.0, 24.0], fmt=lambda v: f"{v:.1f}"),
    "humidity_pct": dict(
        key="humidity_pct", label="相对湿度", unit="%", color="#0F766E",
        header_top=308, y0=338.0, y1=402.0, lo=30.0, hi=45.0,
        ticks=[30.0, 35.0, 40.0, 45.0], fmt=lambda v: f"{v:.0f}"),
    "pressure_kpa": dict(
        key="pressure_kpa", label="压差", unit="kPa", color="#DB2777",
        header_top=428, y0=458.0, y1=562.0, lo=-1.5, hi=1.5,
        ticks=[-1.0, -0.5, 0.0, 0.5, 1.0], fmt=lambda v: f"{v:+.1f}"),
}


def _num(s: str):
    """空单元格 → None（缺测），绝不补 0。"""
    s = (s or "").strip()
    if s == "":
        return None
    f = float(s)
    return int(f) if f.is_integer() and "." not in s else f


def _numout(v):
    """JSON 输出：整数保持整数，保留一位小数的小数保持原样。"""
    if v is None:
        return None
    if isinstance(v, int):
        return v
    r = round(v, 10)
    return int(r) if float(r).is_integer() else r


def build() -> dict:
    raw = CSV.read_text(encoding="utf-8-sig").splitlines()
    rdr = csv.DictReader(raw)
    samples, cur = [], 0
    for r in rdr:
        hh, mm = (int(p) for p in r["time"].split(":"))
        cur = hh * 60 + mm - T0.hour * 60 - T0.minute
        samples.append({
            "sample_id": f"S{len(samples) + 1:02d}",
            "time": f"{hh:02d}:{mm:02d}",
            "minute_offset": cur,
            "temperature_c": _num(r["temperature_c"]),
            "humidity_pct": _num(r["humidity_pct"]),
            "pressure_kpa": _num(r["pressure_kpa"]),
        })

    statistics, segments = {}, {}
    for key, cfg in ROWS.items():
        vals = [s[key] for s in samples]
        v_by_id = {s["sample_id"]: v for s, v in zip(samples, vals) if v is not None}
        valid = [(s["sample_id"], v) for s, v in zip(samples, vals) if v is not None]
        statistics[key] = {
            "label": cfg["label"], "unit": cfg["unit"],
            "total_samples": len(samples),
            "valid_count": len(valid),
            "missing_count": len(samples) - len(valid),
            "missing_samples": [s["sample_id"] for s, v in zip(samples, vals)
                                if v is None],
            "observed_min": _numout(min(v for _, v in valid)),
            "observed_min_sample": min(valid, key=lambda kv: kv[1])[0],
            "observed_max": _numout(max(v for _, v in valid)),
            "observed_max_sample": max(valid, key=lambda kv: kv[1])[0],
            "axis_domain": [cfg["lo"], cfg["hi"]],
        }
        # 连接段：相邻采样点两值都非 null 才成段；缺测两侧不连接。
        by_id = {s["sample_id"]: s for s in samples}
        segs, run = [], []
        for s, v in zip(samples, vals):
            if v is None:
                if len(run) >= 2:
                    segs.append(run)
                run = []
            else:
                run.append(s["sample_id"])
        if len(run) >= 2:
            segs.append(run)
        segments[key] = [
            {"from": seg[i], "to": seg[i + 1],
             "t_from": by_id[seg[i]]["minute_offset"],
             "t_to": by_id[seg[i + 1]]["minute_offset"],
             "minutes_span": by_id[seg[i + 1]]["minute_offset"]
                             - by_id[seg[i]]["minute_offset"],
             "both_endpoints_negative": (
                 v_by_id[seg[i]] < 0 and v_by_id[seg[i + 1]] < 0)}
            for seg in segs for i in range(len(seg) - 1)]

    neg = [{"sample_id": s["sample_id"], "time": s["time"],
            "minute_offset": s["minute_offset"], "pressure_kpa": _numout(s["pressure_kpa"])}
           for s in samples if s["pressure_kpa"] is not None and s["pressure_kpa"] < 0]

    def _pv(key: str, v: float) -> float:
        """数值 → 像素 y。三行各自独立纵轴，比例由 ROWS 的 domain 与像素区间决定。"""
        cfg = ROWS[key]
        return cfg["y1"] - (v - cfg["lo"]) / (cfg["hi"] - cfg["lo"]) * (cfg["y1"] - cfg["y0"])

    # 像素坐标一律按 sample_id 索引，便于与连接段/标记对应
    x = {s["sample_id"]: PLOT_X0 + s["minute_offset"] * MIN_PX for s in samples}
    y = {k: {s["sample_id"]: (None if s[k] is None else _pv(k, s[k])) for s in samples}
         for k in ROWS}

    return {
        "samples": [
            {"sample_id": s["sample_id"], "time": s["time"],
             "minute_offset": s["minute_offset"],
             "temperature_c": _numout(s["temperature_c"]),
             "humidity_pct": _numout(s["humidity_pct"]),
             "pressure_kpa": _numout(s["pressure_kpa"])} for s in samples],
        "statistics": statistics,
        "segments": segments,
        "negative_samples": neg,
        "axes": {
            "x": {"kind": "time", "shared_by_all_three_charts": True,
                  "start_time": "08:00", "end_time": "12:30",
                  "start_minute": MIN0, "end_minute": MIN1,
                  "total_minutes": MIN1 - MIN0,
                  "is_linear_in_minutes": True,
                  "pixel_range": [PLOT_X0, PLOT_X1],
                  "pixels_per_minute": MIN_PX,
                  "major_tick_minutes": list(range(0, 271, 30)),
                  "minor_tick_minutes": list(range(15, 271, 30))},
            "y": {k: {"kind": "linear", "unit": c["unit"],
                      "domain": [c["lo"], c["hi"]],
                      "pixel_range": [c["y0"], c["y1"]],
                      "pixels_per_unit": (c["y1"] - c["y0"]) / (c["hi"] - c["lo"]),
                      "ticks": c["ticks"]} for k, c in ROWS.items()},
            "zero_line": {
                "metric": "pressure_kpa", "value": 0.0,
                "pixel_y": _pv("pressure_kpa", 0.0),
                "drawn_across": [PLOT_X0, PLOT_X1]},
        },
        # —— 交付 JSON 之外，仅模型自用（tmp/ 副本）——
        "_model_only": {
            "canvas": [PW, PH], "margin": M,
            "x_px": {sid: round(v, 3) for sid, v in x.items()},
            "y_px": {k: {sid: (None if v is None else round(v, 3))
                         for sid, v in y[k].items()} for k in ROWS},
            "rows": {k: {kk: vv for kk, vv in c.items() if kk != "fmt"}
                     for k, c in ROWS.items()},
        },
    }


AUDIT_KEYS = ["schema_version", "task_id", "path_base", "generated_at", "source",
              "constraints_applied", "samples", "statistics", "segments",
              "negative_samples", "axes", "artifacts", "quality_notes"]


def main() -> None:
    out, tmp = IO.dirs()
    model = build()
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).strftime(
        "%Y-%m-%dT%H:%M:%S+08:00")

    audit = {
        "schema_version": 1,
        "task_id": TASK_ID,
        "path_base": "output_dir",
        "generated_at": now,
        "source": {
            "path": {"path_base": "suite_root",
                     "path": "tasks/A05-irregular-sensors/inputs/readings.csv"},
            "rows": len(model["samples"]), "encoding": "utf-8-sig",
            "empty_cell_semantics": "null = 缺测，不是 0；不做任何内插/补值",
        },
        "constraints_applied": {
            "canvas_px": [PW, PH],
            "shared_time_axis": "三图共用 08:00–12:30 真实分钟比例横轴，纵向参考线对齐",
            "break_on_missing": "温度/湿度缺测采样点两侧的线段断开，不用直线或虚线补值",
            "no_interpolation": "缺测采样点不进入任何连接段",
            "zero_line": "压差可正可负，零线在像素 y="
                         f"{model['axes']['zero_line']['pixel_y']:.1f} 单列加粗绘制",
            "negative_marking": "只登记实际为负的采样点，不声称 09:40–10:50 每一刻均为负",
            "table_missing_glyph": "—",
        },
        "samples": model["samples"],
        "statistics": model["statistics"],
        "segments": model["segments"],
        "negative_samples": model["negative_samples"],
        "axes": model["axes"],
        "artifacts": {
            "sensor-report.png": {
                "path": "sensor-report.png",
                "width": PW, "height": PH, "format": "png",
                "generated_by": "open-snapshot /snapshot（POST 成功时的原始响应字节）"},
            "sensor-report.snapshot": {"path": "sensor-report.snapshot",
                                       "corresponds_to": "sensor-report.png"},
            "normalized-data.json": {"path": "normalized-data.json"},
        },
        "quality_notes": {
            "valid_readings_total": sum(v["valid_count"] for v in
                                        model["statistics"].values()),
            "observed_min_max_from_valid_only": True,
            "segment_counts": {k: sum(1 for _ in v) for k, v in
                               model["segments"].items()},
        },
    }
    for k in list(audit):
        if k not in AUDIT_KEYS:
            raise SystemExit(f"意外字段 {k}")

    (out / "normalized-data.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (tmp / "model.json").write_text(
        json.dumps({"model": model, "audit": audit}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")

    print(f"samples={len(model['samples'])}")
    for k, s in model["statistics"].items():
        print(f"  {k:15s} valid={s['valid_count']:2d}/12  min={s['observed_min']} "
              f"({s['observed_min_sample']})  max={s['observed_max']} "
              f"({s['observed_max_sample']})  missing={s['missing_samples']}")
    for k, segs in model["segments"].items():
        print(f"  seg {k}: {len(segs)}  -> " +
              " ; ".join(f"{g['from']}→{g['to']}" for g in segs))
    print("  negative:", [(n["time"], n["pressure_kpa"]) for n in model["negative_samples"]])
    print("  valid total:", audit["quality_notes"]["valid_readings_total"])
    print("  px/min =", round(model["axes"]["x"]["pixels_per_minute"], 6),
          " zero_y =", round(model["axes"]["zero_line"]["pixel_y"], 2))


if __name__ == "__main__":
    main()
