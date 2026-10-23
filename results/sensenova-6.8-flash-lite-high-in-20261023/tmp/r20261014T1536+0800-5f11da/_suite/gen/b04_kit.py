"""B04 kit - extends b01_kit for B04 tasks (Solar System Planet Comparison)."""
import sys, os, json, pathlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b01_kit as K
K.TASK = "B04"
ROOT = K.ROOT
RUN_ID = K.RUN_ID
K.OUT = ROOT / "outputs" / RUN_ID / "B04"
K.TMP = ROOT / "tmp" / RUN_ID / "B04"
from b01_kit import (
    Doc, dry_run, assert_gates, save_gates, render_case,
    contrast, d_e, check_palette, tool_call, append_jsonl,
    rel, now, ring, tw, pitch, fmt, esc, FONT
)

# ============================================================ Planetary Data
# Source: NASA Planetary Fact Sheet (https://nssdc.gsfc.nasa.gov/planetary/factsheet/)
# Last Updated: 18 March 2025

PLANETS = {
    "Mercury": {
        "name_cn": "水星", "diameter": 4879, "mass_24kg": 0.330, "distance_106km": 57.9,
        "orbital_period_days": 88.0, "rotation_hours": 1407.6, "moons": 0,
        "gravity_ms2": 3.7, "mean_temp_c": 167, "density_kg_m3": 5427,
        "orbital_velocity_kms": 47.4, "escape_velocity_kms": 4.3,
        "surface_pressure_bars": 0, "atmosphere": "无（trace）",
        "discovery_year": "古代", "discovery_note": "人类最早发现的行星之一",
        "color": "#B8860B", "type": "岩石"
    },
    "Venus": {
        "name_cn": "金星", "diameter": 12104, "mass_24kg": 4.87, "distance_106km": 108.2,
        "orbital_period_days": 224.7, "rotation_hours": 5832.5, "moons": 0,
        "gravity_ms2": 8.9, "mean_temp_c": 464, "density_kg_m3": 5243,
        "orbital_velocity_kms": 35.0, "escape_velocity_kms": 10.4,
        "surface_pressure_bars": 92, "atmosphere": "CO₂ 96.5%, N₂ 3.5%",
        "discovery_year": "古代", "discovery_note": "人类最早发现的行星之一",
        "color": "#FF8C00", "type": "岩石"
    },
    "Earth": {
        "name_cn": "地球", "diameter": 12756, "mass_24kg": 5.97, "distance_106km": 149.6,
        "orbital_period_days": 365.2, "rotation_hours": 23.9, "moons": 1,
        "gravity_ms2": 9.8, "mean_temp_c": 15, "density_kg_m3": 5513,
        "orbital_velocity_kms": 29.8, "escape_velocity_kms": 11.2,
        "surface_pressure_bars": 1, "atmosphere": "N₂ 78.08%, O₂ 20.95%, Ar 0.93%",
        "discovery_year": "古代", "discovery_note": "我们的家园",
        "color": "#4169E1", "type": "岩石"
    },
    "Mars": {
        "name_cn": "火星", "diameter": 6792, "mass_24kg": 0.642, "distance_106km": 228.0,
        "orbital_period_days": 687.0, "rotation_hours": 24.6, "moons": 2,
        "gravity_ms2": 3.7, "mean_temp_c": -65, "density_kg_m3": 3934,
        "orbital_velocity_kms": 24.1, "escape_velocity_kms": 5.0,
        "surface_pressure_bars": 0.01, "atmosphere": "CO₂ 95.32%, N₂ 2.7%, Ar 1.6%",
        "discovery_year": "古代", "discovery_note": "人类最早发现的行星之一",
        "color": "#CD5C5C", "type": "岩石"
    },
    "Jupiter": {
        "name_cn": "木星", "diameter": 142984, "mass_24kg": 1898, "distance_106km": 778.5,
        "orbital_period_days": 4331, "rotation_hours": 9.9, "moons": 95,
        "gravity_ms2": 23.1, "mean_temp_c": -110, "density_kg_m3": 1326,
        "orbital_velocity_kms": 13.1, "escape_velocity_kms": 59.5,
        "surface_pressure_bars": None, "atmosphere": "H₂ 89.8%, He 10.2%",
        "discovery_year": "古代", "discovery_note": "太阳系最大行星",
        "color": "#DEB887", "type": "气态巨行星"
    },
    "Saturn": {
        "name_cn": "土星", "diameter": 120536, "mass_24kg": 568, "distance_106km": 1432.0,
        "orbital_period_days": 10747, "rotation_hours": 10.7, "moons": 274,
        "gravity_ms2": 9.0, "mean_temp_c": -140, "density_kg_m3": 687,
        "orbital_velocity_kms": 9.7, "escape_velocity_kms": 35.5,
        "surface_pressure_bars": None, "atmosphere": "H₂ 96.3%, He 3.25%",
        "discovery_year": "古代", "discovery_note": "拥有壮观光环系统",
        "color": "#F4A460", "type": "气态巨行星"
    },
    "Uranus": {
        "name_cn": "天王星", "diameter": 51118, "mass_24kg": 86.8, "distance_106km": 2867.0,
        "orbital_period_days": 30589, "rotation_hours": 17.2, "moons": 28,
        "gravity_ms2": 8.7, "mean_temp_c": -195, "density_kg_m3": 1271,
        "orbital_velocity_kms": 6.8, "escape_velocity_kms": 21.3,
        "surface_pressure_bars": None, "atmosphere": "H₂ 82.99%, He 15.1%, CH₄ 2.3%",
        "discovery_year": "1781", "discovery_note": "威廉·赫歇尔发现",
        "color": "#87CEEB", "type": "冰巨行星"
    },
    "Neptune": {
        "name_cn": "海王星", "diameter": 49528, "mass_24kg": 102, "distance_106km": 4515.0,
        "orbital_period_days": 59800, "rotation_hours": 16.1, "moons": 16,
        "gravity_ms2": 11.0, "mean_temp_c": -200, "density_kg_m3": 1638,
        "orbital_velocity_kms": 5.4, "escape_velocity_kms": 23.5,
        "surface_pressure_bars": None, "atmosphere": "H₂ 80.2%, He 19.0%, CH₄ 1.8%",
        "discovery_year": "1846", "discovery_note": "勒维耶预测位置后发现",
        "color": "#4169E1", "type": "冰巨行星"
    }
}

PLANET_ORDER = ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]
