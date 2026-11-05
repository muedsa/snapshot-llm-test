#!/usr/bin/env python3
"""B05 shared fictional sample data + tiny helpers.

Everything here is invented demo content for a self-consistent product story;
no real people, brands, deployments or measurements are claimed.
"""
from __future__ import annotations
from dsl import CN, LATIN, MONO

FICTION = "虚构演示数据 / fictional demo content"

DATA = {
    "date": "2026-07-12",
    "weekday": "周日",
    "city": "临江市",
    "product": "泊 / ANCHOR",
    "user": "林岚",
    "user_age": 32,
    "home": "梧桐里",
    "work": "云枢大厦 · 江汉路",
    "now": "17:46",
    "alert": "暴雨红色预警",
    "rain_peak": "17:40–19:20 降雨峰值",
    "points": [
        {"name": "江汉路地铁 B 口", "cm": 45, "state": "封控"},
        {"name": "临江大道下穿", "cm": 62, "state": "封控"},
        {"name": "梧桐里东门", "cm": 12, "state": "可通行"},
        {"name": "光谷广场环岛", "cm": 28, "state": "谨慎"},
        {"name": "建设大道", "cm": 8, "state": "通畅"},
        {"name": "沿江公园", "cm": 5, "state": "通畅"},
    ],
    "routes": [
        {"name": "路线 A · 江汉路直达", "mins": 22, "water": 2, "risk": "高",
         "via": "江汉路 B 口", "note": "45cm 已封控", "best": False},
        {"name": "路线 B · 梧桐里东门", "mins": 31, "water": 1, "risk": "低",
         "via": "建设大道 → 东门", "note": "12cm 可通行", "best": True},
        {"name": "路线 C · 沿江绕行", "mins": 44, "water": 0, "risk": "低",
         "via": "沿江公园 → 南门", "note": "无积水 · 较远", "best": False},
    ],
    "shelter": {"name": "梧桐里社区中心", "cap": 120, "max": 200,
                "walk": 6, "open": True},
    "shelters": [
        {"name": "梧桐里社区中心", "walk": 6, "cap": 120, "max": 200,
         "open": True, "items": ["热水", "充电", "母婴室"], "best": True},
        {"name": "江汉街道党群站", "walk": 14, "cap": 45, "max": 60,
         "open": True, "items": ["热水", "座位"], "best": False},
        {"name": "临江体育馆", "walk": 22, "cap": 310, "max": 500,
         "open": False, "items": ["热水", "毛毯"], "best": False},
    ],
    "rider": {"name": "周骁", "code": "R-2087", "orders": 3, "reroute": 2},
    "property": {"name": "临江街道 · 梧桐里物业站", "sensors": 6,
                 "alerts": 2, "reports": 38, "shelters_open": 3},
    "family": {"mother": "林秀芳", "mother_age": 68, "child": "陈小满",
               "child_age": 8},
    "sensors": [
        ("P1 梧桐里东门", 12), ("P2 江汉路 B 口", 45),
        ("P3 临江下穿", 62), ("P4 光谷环岛", 28),
        ("P5 建设大道", 8), ("P6 沿江公园", 5),
    ],
    "log": [
        ("17:52", "P3 临江下穿 62cm", "已封控 · 推送 1,284 人"),
        ("17:48", "P2 江汉路 B 口 45cm", "已派员 · 设置围挡"),
        ("17:41", "P1 东门 12cm", "已上报 · 纳入推荐路线"),
        ("17:33", "全城红色预警", "已推送 · 启动值守"),
    ],
    "review": {"reports": 2416, "yours": 3, "helped": 1284,
               "lead_min": 18, "accept": 100, "next_lead": 30},
    "nearby_people": 1284,
}


def A(color, alpha):
    """Append CSS #RRGGBBAA alpha byte to a 6-digit hex color."""
    a = max(0, min(255, round(alpha * 255)))
    return color + "%02X" % a


def label(c, x, y, w, text, size=15, color="#7C90AC", font=MONO, align="LEFT"):
    return c.text(x, y, w, size * 1.7, text, size, color, font=font, align=align)


def rule(c, x, y, w, color="#233350", thickness=1):
    return c.hline(x, y, w, thickness, color)


def dot(c, cx, cy, r, color, border=None):
    return c.circle(cx, cy, r, color, border=border)
