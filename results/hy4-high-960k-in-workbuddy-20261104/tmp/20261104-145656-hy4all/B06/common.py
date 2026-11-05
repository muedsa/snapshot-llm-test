#!/usr/bin/env python3
"""B06 shared demo data + tiny helpers.

All figures, brands, timetables and products below are invented for the
purpose of showing a redesign. Nothing here is a real measurement, quote,
price, schedule or official rule.
"""
from __future__ import annotations
from dsl import CN, LATIN, MONO

FICTION = "自拟演示数据 / fictional demo content（非真实测量、报价、时刻或官方规则）"

DATA = {
    "med": {
        "drug": "氨氯地平片", "spec": "5mg × 24 片", "dose": "一次 1 片",
        "times": ["07:30", "13:00", "20:00"], "taken": 1,
        "colors": ["#2563EB", "#7C3AED", "#0E9F6E"],
        "note": "饭后 · 温水送服 · 忌西柚 · 两次间隔 ≥ 4 小时",
    },
    "price": [
        ("醇香燕麦", "250g", 12.90), ("谷粒多", "400g", 18.80),
        ("麦田日记", "500g", 16.50), ("早安麦片", "750g", 29.90),
        ("纤麸", "1000g", 42.00),
    ],
    "power": {
        "total": 186.40, "peak_share": 61, "month": "7 月",
        "peak": "18:00–22:00", "flat": "07:00–18:00", "valley": "22:00–07:00",
        "hourly": [0.12, 0.10, 0.09, 0.09, 0.10, 0.14, 0.30, 0.52, 0.48, 0.40,
                   0.38, 0.42, 0.55, 0.50, 0.44, 0.46, 0.58, 0.72, 0.94, 1.00,
                   0.96, 0.78, 0.40, 0.22],
        "advice": [("洗衣机 19:00 → 22:00", "省 ¥3.86"),
                   ("热水器 20:00 → 23:00", "省 ¥2.14"),
                   ("充电桩 21:00 → 23:30", "省 ¥1.92")],
    },
    "nutrition": [
        ("糖", 12, 50, "g", "#EAB308", 24),
        ("钠", 1560, 2000, "mg", "#EF4444", 78),
        ("脂肪", 22, 60, "g", "#22C55E", 37),
    ],
    "nutrition_pack": "一包 85g 香辣薯片（演示）",
    "express": {
        "waybill": "YT·20260713·0882",
        "stages": [
            ("已揽收", "07-12 09:14", "杭州 转运中心", "done"),
            ("干线运输", "07-12 21:40", "杭州 → 临江", "done"),
            ("到达派送站", "07-13 06:20", "临江 梧桐里站", "done"),
            ("派送中", "07-13 10:05", "骑手 已取件", "now"),
            ("预计签收", "今日 14:00–16:00", "梧桐里 3 栋", "eta"),
        ],
        "eta": "今日 14:00–16:00", "left": "还需 2 站 · 约 3 小时",
    },
    "lastbus": {
        "now": "22:28", "stop": "梧桐里站",
        "buses": [
            ("3 路", "3 分钟", "还来得及", "#22D3EE", True),
            ("夜 8 路", "15 分钟", "正常走", "#A78BFA", True),
            ("11 路", "37 分钟", "不急", "#34D399", True),
            ("3 路", "已发走 22:15", "赶不上", "#4B5563", False),
        ],
    },
    "waste": {
        "buckets": [("蓝", "可回收", "#2563EB"), ("绿", "厨余", "#16A34A"),
                    ("红", "有害", "#DC2626"), ("灰", "其他", "#64748B")],
        "items": [("奶茶杯", "先倒液体 → 灰", "#64748B"),
                  ("外卖餐盒", "洗净 → 蓝", "#2563EB"),
                  ("废电池", "红", "#DC2626"),
                  ("果皮", "绿", "#16A34A"),
                  ("纸箱", "蓝", "#2563EB"),
                  ("旧衣物", "蓝 / 回收箱", "#2563EB")],
        "questions": ["能卖钱吗？", "会烂吗？", "有毒有害吗？"],
    },
    "weather": [
        ("周一", "07/13", 26, 19, 10, "防晒", "#F59E0B"),
        ("周二", "07/14", 28, 20, 5, "短袖", "#FB923C"),
        ("周三", "07/15", 23, 18, 85, "带伞 + 薄外套", "#3B82F6"),
        ("周四", "07/16", 25, 19, 30, "备伞", "#60A5FA"),
        ("周五", "07/17", 22, 17, 90, "带伞 + 外套", "#2563EB"),
        ("周六", "07/18", 29, 21, 5, "短袖 + 防晒", "#F97316"),
        ("周日", "07/19", 30, 22, 0, "短袖", "#EF4444"),
    ],
    "parking": {
        "zone": "B", "row": 12, "slot": "07",
        "zones": [("A", "#1E6E5A"), ("B", "#E0A83B"), ("C", "#2C7A9E")],
        "duration": "2 小时 47 分", "fee": 18,
        "steps": [("首小时", "¥6", 6), ("之后每半小时", "¥3", 3),
                  ("24h 封顶", "¥48", 48)],
    },
    "flight": {
        "gate": "B27", "status": "现在登机", "flight": "MU 5738",
        "dest": "临江", "seat": "12A", "board": "18:35 截止",
        "takeoff": "18:55 起飞", "walk": 9,
        "stages": [("值机", "17:10"), ("安检", "17:35"),
                   ("登机口", "18:12"), ("起飞", "18:55")],
    },
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


def price_per_100g(grams, total):
    return total / (grams / 100.0)
