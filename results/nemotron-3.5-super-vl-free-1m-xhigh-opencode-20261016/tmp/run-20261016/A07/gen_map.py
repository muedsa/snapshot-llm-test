import math, json

W, H = 1600, 1000
STATIONS = {
    "S01": ("松林", 220, 300, "R", True),
    "S02": ("北门", 420, 300, "R", True),
    "S03": ("书院", 620, 300, "R", False),
    "S04": ("中心", 780, 300, "R/B", True),
    "S05": ("东桥", 940, 460, "R/G", False),
    "S06": ("江湾", 1140, 460, "R", True),
    "S12": ("机场", 1300, 460, "R", True),
    "S07": ("西港", 780, 900, "B", True),
    "S08": ("工坊", 780, 540, "B/G", True),
    "S09": ("花园", 940, 300, "B", False),
    "S10": ("南门", 1100, 300, "B", True),
    "S11": ("会展", 1260, 300, "B", True),
    "S13": ("石溪", 220, 900, "G", True),
    "S14": ("公园", 420, 900, "G", False),
    "S15": ("剧院", 860, 540, "G", True),
    "S16": ("研究所", 1100, 460, "G", True),
}
LINE_COLOR = {"R": "#DC2626", "B": "#2563EB", "G": "#16A34A"}
SEGMENTS = {
    "R": [("S01","S02"),("S02","S03"),("S03","S04"),("S04","S05"),("S05","S06"),("S06","S12")],
    "B": [("S07","S08"),("S08","S04"),("S04","S09"),("S09","S10"),("S10","S11")],
    "G": [("S13","S14"),("S14","S08"),("S08","S15"),("S15","S05"),("S05","S16")],
}
DOT_R = 11
LABEL_OFF = {
    "S01":(-150,-14,"RIGHT"),"S02":(-105,-14,"RIGHT"),"S03":(-105,-14,"RIGHT"),
    "S04":(16,-14,"LEFT"),"S05":(16,14,"LEFT"),"S06":(16,-14,"LEFT"),
    "S12":(16,-14,"LEFT"),"S07":(-130,14,"RIGHT"),"S08":(16,-14,"LEFT"),
    "S09":(16,-14,"LEFT"),"S10":(16,-14,"LEFT"),"S11":(16,-14,"LEFT"),
    "S13":(-130,14,"RIGHT"),"S14":(-105,14,"RIGHT"),"S15":(16,-14,"LEFT"),"S16":(16,-14,"LEFT"),
}

def seg(x1,y1,x2,y2,color,thick=6):
    dx,dy = x2-x1, y2-y1
    L = math.hypot(dx,dy)
    mx,my = (x1+x2)/2,(y1+y2)/2
    th = math.atan2(dy,dx)
    c,s = math.cos(th), math.sin(th)
    mat = f"({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,0,0,0,1)"
    return (f'      <Positioned left="{mx-L/2:.1f}" top="{my-thick/2:.1f}" width="{L:.1f}" height="{thick:.1f}">'
            f'        <Transform matrix="{mat}" origin="({L/2:.1f},{thick/2:.1f})">'
            f'          <Container width="{L:.1f}" height="{thick:.1f}" color="{color}"/>'
            f'        </Transform>'
            f'      </Positioned>')

el = []
el.append('<Snapshot background="#FFFFFF" type="png">')
el.append(f'  <SizedBox width="{W}" height="{H}">')
el.append('    <Stack alignment="TOP_LEFT" clipBehavior="NONE">')

el.append('      <Positioned left="40" top="24">')
el.append('        <Text color="#0F172A" fontSize="28" fontStyle="BOLD" fontFamily="Noto Sans CJK SC,Inter">虚构城市地铁示意图 · 三线换乘</Text>')
el.append('      </Positioned>')
el.append('      <Positioned left="40" top="62" width="1200">')
el.append('        <Text color="#475569" fontSize="20" fontFamily="Noto Sans CJK SC,Inter" softWrap="true">非地理示意图；按线路站序连接相邻站，相邻站间可双向乘车；转折角度为 45\u00b0 或 90\u00b0；实心圆点＝具备无障碍设施，白底色环＝无无障碍设施（可乘车通过，但不可作起点、终点或换乘站）。</Text>')
el.append('      </Positioned>')

for line, pairs in SEGMENTS.items():
    color = LINE_COLOR[line]
    for a,b in pairs:
        xa,ya = STATIONS[a][1], STATIONS[a][2]
        xb,yb = STATIONS[b][1], STATIONS[b][2]
        el.append(seg(xa,ya,xb,yb,color))

for sid,(name,x,y,line,acc) in STATIONS.items():
    col = LINE_COLOR[line.split("/")[0]]
    if acc:
        el.append(f'      <Positioned left="{x-DOT_R:.1f}" top="{y-DOT_R:.1f}" width="{2*DOT_R:.1f}" height="{2*DOT_R:.1f}">')
        el.append(f'        <Container color="{col}" borderRadius="{DOT_R:.1f}"/>')
        el.append(f'      </Positioned>')
    else:
        el.append(f'      <Positioned left="{x-DOT_R:.1f}" top="{y-DOT_R:.1f}" width="{2*DOT_R:.1f}" height="{2*DOT_R:.1f}">')
        el.append(f'        <Container color="#FFFFFF" border="3 SOLID {col}" borderRadius="{DOT_R:.1f}"/>')
        el.append(f'      </Positioned>')
    offx, offy, talign = LABEL_OFF[sid]
    el.append(f'      <Positioned left="{x+offx:.1f}" top="{y+offy:.1f}" width="170">')
    el.append(f'        <Text textAlign="{talign}" color="#111827" fontSize="22" fontFamily="Noto Sans CJK SC,Inter">{sid} {name}</Text>')
    el.append(f'      </Positioned>')

# legend
el.append('      <Positioned left="40" top="872" width="620">')
el.append('        <Row mainAxisAlignment="START" crossAxisAlignment="CENTER">')
el.append('          <Container width="14" height="14" color="#DC2626" borderRadius="7"/>')
el.append('          <Container width="6"/>')
el.append('          <Text color="#374151" fontSize="20" fontFamily="Noto Sans CJK SC,Inter">R 红线</Text>')
el.append('          <Container width="34"/>')
el.append('          <Container width="14" height="14" color="#2563EB" borderRadius="7"/>')
el.append('          <Container width="6"/>')
el.append('          <Text color="#374151" fontSize="20" fontFamily="Noto Sans CJK SC,Inter">B 蓝线</Text>')
el.append('          <Container width="34"/>')
el.append('          <Container width="14" height="14" color="#16A34A" borderRadius="7"/>')
el.append('          <Container width="6"/>')
el.append('          <Text color="#374151" fontSize="20" fontFamily="Noto Sans CJK SC,Inter">G 绿线</Text>')
el.append('        </Row>')
el.append('      </Positioned>')
el.append('      <Positioned left="40" top="906" width="700">')
el.append('        <Row mainAxisAlignment="START" crossAxisAlignment="CENTER">')
el.append('          <Container width="14" height="14" color="#FFFFFF" border="3 SOLID #DC2626" borderRadius="7"/>')
el.append('          <Container width="6"/>')
el.append('          <Text color="#374151" fontSize="20" fontFamily="Noto Sans CJK SC,Inter">白底色环＝无无障碍设施站（可乘车通过，不可作起点、终点或换乘站）</Text>')
el.append('        </Row>')
el.append('      </Positioned>')

el.append('    </Stack>')
el.append('  </SizedBox>')
el.append('</Snapshot>')

open("tmp/run-20261016/A07/network-map.v1.snapshot","w",encoding="utf-8").write("\n".join(el))
print("network-map DSL written")

# ---------------- routes.json ----------------
ROUTES = {
  "schema_version": 1,
  "task_id": "A07",
  "source": "inputs/network.json",
  "rule": "最少站间边数优先，边数相同则换乘最少；换乘＝改变乘坐线路，第一次上车不算；accessible=false 站可通过但不可作为起点、终点、换乘站",
  "queries": [
    {
      "query_index": 1, "from": "S01", "to": "S11",
      "from_name": "松林", "to_name": "会展",
      "route": ["S01","S02","S03","S04","S09","S10","S11"],
      "route_names": ["松林","北门","书院","中心","花园","南门","会展"],
      "segments": [{"line":"R","line_name":"R 红线","from":"S01","to":"S04"},{"line":"B","line_name":"B 蓝线","from":"S04","to":"S11"}],
      "edges": 6, "transfers": 1, "transfer_stations": ["S04"],
      "accessible": True, "accessible_reason": None,
      "note": "起点 S01、终点 S11、换乘站 S04 均具备无障碍设施"
    },
    {
      "query_index": 2, "from": "S13", "to": "S12",
      "from_name": "石溪", "to_name": "机场",
      "ordinary": {
        "route": ["S13","S14","S08","S15","S05","S06","S12"],
        "route_names": ["石溪","公园","工坊","剧院","东桥","江湾","机场"],
        "segments": [{"line":"G","line_name":"G 绿线","from":"S13","to":"S05"},{"line":"R","line_name":"R 红线","from":"S05","to":"S12"}],
        "edges": 6, "transfers": 1, "transfer_stations": ["S05"],
        "accessible": False,
        "reason": "换乘站 S05 东桥 无障碍设施不可用（accessible=false），不符合无障碍旅程"
      },
      "accessible": {
        "route": ["S13","S14","S08","S04","S05","S06","S12"],
        "route_names": ["石溪","公园","工坊","中心","东桥","江湾","机场"],
        "segments": [{"line":"G","line_name":"G 绿线","from":"S13","to":"S08"},{"line":"B","line_name":"B 蓝线","from":"S08","to":"S04"},{"line":"R","line_name":"R 红线","from":"S04","to":"S12"}],
        "edges": 6, "transfers": 2, "transfer_stations": ["S08","S04"],
        "accessible": True,
        "reason": "换乘站 S08 工坊、S04 中心均具备无障碍设施"
      },
      "accessible_final": True
    },
    {
      "query_index": 3, "from": "S07", "to": "S16",
      "from_name": "西港", "to_name": "研究所",
      "route": ["S07","S08","S15","S05","S16"],
      "route_names": ["西港","工坊","剧院","东桥","研究所"],
      "segments": [{"line":"B","line_name":"B 蓝线","from":"S07","to":"S08"},{"line":"G","line_name":"G 绿线","from":"S08","to":"S16"}],
      "edges": 4, "transfers": 1, "transfer_stations": ["S08"],
      "accessible": True, "accessible_reason": None,
      "note": "起点 S07、终点 S16、换乘站 S08 均具备无障碍设施；中间经过 S05 东桥仅为乘车通过，不影响无障碍判定"
    }
  ]
}
open("tmp/run-20261016/A07/routes.v1.json","w",encoding="utf-8").write(json.dumps(ROUTES, ensure_ascii=False, indent=2))
print("routes.json draft written")
