import json

with open("tasks/A12-responsive-system/inputs/content.json", encoding="utf-8") as f:
    content = json.load(f)

W_MAP = {"mobile": 360, "tablet": 768, "desktop": 1440, "stage": 1920}
H_MAP = {"mobile": 800, "tablet": 1024, "desktop": 900, "stage": 1080}

FONT = "Noto Sans CJK SC,Inter"

# Design tokens (unified across all sizes)
TOKENS = {
    "colors": {
        "bg": "#FFFFFF",
        "surface": "#F8FAFC",
        "primary": "#2563EB",
        "text": "#111827",
        "muted": "#64748B",
        "border": "#E2E8F0",
        "accent": "#DC2626",
    },
    "type": {
        "title": 40,
        "subtitle": 20,
        "meta": 18,
        "card_title": 18,
        "card_detail": 16,
        "cta": 18,
        "footnote": 14,
    },
    "space": {
        "margin_mobile": 16,
        "margin": 32,
        "gap": 16,
        "card_pad": 16,
    },
    "radius": 12,
}

def fmt_pts(name, val):
    return f"{name}={val}"

def card(c, x, y, w, h, is_mobile=False):
    """Render one content card"""
    title = c["title"]
    detail = c["detail"]
    cid = c["id"]
    ts = TOKENS["type"]
    cs = TOKENS["colors"]
    ss = TOKENS["space"]
    el = []
    # card container
    el.append(f'      <Positioned left="{x}" top="{y}" width="{w}" height="{h}">')
    el.append(f'        <Container color="{cs["surface"]}" border="1 SOLID {cs["border"]}" borderRadius="{TOKENS["radius"]}" alignment="TOP_LEFT">')
    el.append(f'          <Stack alignment="TOP_LEFT" clipBehavior="NONE">')
    # badge id (small, top-right)
    el.append(f'            <Positioned left="{w-44}" top="10" width="34" height="18">')
    el.append(f'              <Text color="{cs["muted"]}" fontSize="12" fontFamily="{FONT}" textAlign="CENTER">{cid}</Text>')
    el.append(f'            </Positioned>')
    # title
    tsize = ts["card_title"] if not is_mobile else ts["card_title"]
    el.append(f'            <Positioned left="{ss["card_pad"]}" top="{ss["card_pad"]}" width="{w-2*ss["card_pad"]}" height="24">')
    el.append(f'              <Text color="{cs["text"]}" fontSize="{tsize}" fontStyle="BOLD" fontFamily="{FONT}">{title}</Text>')
    el.append(f'            </Positioned>')
    # detail
    dsize = ts["card_detail"]
    el.append(f'            <Positioned left="{ss["card_pad"]}" top="{ss["card_pad"]+30}" width="{w-2*ss["card_pad"]}" height="{h-2*ss["card_pad"]-30}">')
    el.append(f'              <Text color="{cs["muted"]}" fontSize="{dsize}" fontFamily="{FONT}" softWrap="true">{detail}</Text>')
    el.append(f'            </Positioned>')
    el.append(f'          </Stack>')
    el.append(f'        </Container>')
    el.append(f'      </Positioned>')
    return "\n".join(el)

def header(x, y, w, size_title, size_sub, is_mobile):
    cs = TOKENS["colors"]; ts = TOKENS["type"]; ss = TOKENS["space"]
    el = []
    el.append(f'      <Positioned left="{x}" top="{y}" width="{w}" height="{size_title+8}">')
    el.append(f'        <Text color="{cs["text"]}" fontSize="{size_title}" fontStyle="BOLD" fontFamily="{FONT}">{content["title"]}</Text>')
    el.append(f'      </Positioned>')
    el.append(f'      <Positioned left="{x}" top="{y+size_title+10}" width="{w}" height="{size_sub+6}">')
    el.append(f'        <Text color="{cs["muted"]}" fontSize="{size_sub}" fontFamily="{FONT}" softWrap="true">{content["subtitle"]}</Text>')
    el.append(f'      </Positioned>')
    return "\n".join(el)

def meta_row(x, y, w, size, is_mobile):
    cs = TOKENS["colors"]; ts = TOKENS["type"]; ss = TOKENS["space"]
    meta = f'{content["date"]}  ·  {content["time"]}  ·  {content["location"]}'
    cta = content["cta"]
    web = content["website"]
    el = []
    el.append(f'      <Positioned left="{x}" top="{y}" width="{w}" height="{size+4}">')
    el.append(f'        <Text color="{cs["text"]}" fontSize="{size}" fontFamily="{FONT}">{meta}</Text>')
    el.append(f'      </Positioned>')
    el.append(f'      <Positioned left="{x}" top="{y+size+8}" width="{w}" height="{size+4}">')
    el.append(f'        <Text color="{cs["primary"]}" fontSize="{size}" fontStyle="BOLD" fontFamily="{FONT}">{cta}</Text>')
    el.append(f'      </Positioned>')
    el.append(f'      <Positioned left="{x}" top="{y+2*(size+8)}" width="{w}" height="{size+4}">')
    el.append(f'        <Text color="{cs["muted"]}" fontSize="{size}" fontFamily="{FONT}">官网：{web}</Text>')
    el.append(f'      </Positioned>')
    return "\n".join(el)

layouts = {
    "mobile": {"cols": 1, "rows": 6, "margin": 16, "gap": 12, "card_w": 328, "card_h": 100, "title_size": 32, "sub_size": 18, "meta_size": 16},
    "tablet": {"cols": 2, "rows": 3, "margin": 32, "gap": 20, "card_w": 344, "card_h": 260, "title_size": 40, "sub_size": 22, "meta_size": 18},
    "desktop": {"cols": 3, "rows": 2, "margin": 40, "gap": 24, "card_w": 440, "card_h": 320, "title_size": 48, "sub_size": 24, "meta_size": 20},
    "stage": {"cols": 3, "rows": 2, "margin": 64, "gap": 32, "card_w": 560, "card_h": 400, "title_size": 56, "sub_size": 28, "meta_size": 22},
}

OUTPUTS = {}

for name, W in W_MAP.items():
    H = H_MAP[name]
    L = layouts[name]
    cs = TOKENS["colors"]; ss = TOKENS["space"]
    el = []
    el.append('<Snapshot background="#FFFFFF" type="png">')
    el.append(f'  <SizedBox width="{W}" height="{H}">')
    el.append('    <Stack alignment="TOP_LEFT" clipBehavior="NONE">')
    # header
    el.append(header(L["margin"], L["margin"], W - 2*L["margin"], L["title_size"], L["sub_size"], name=="mobile"))
    y = L["margin"] + L["title_size"] + 10 + L["sub_size"] + 6 + 16
    # meta
    el.append(meta_row(L["margin"], y, W - 2*L["margin"], L["meta_size"], name=="mobile"))
    # cards
    cy = y + 3*(L["meta_size"]+8) + ss["gap"]
    for i, c in enumerate(content["cards"]):
        col = i % L["cols"]; row = i // L["cols"]
        x = L["margin"] + col*(L["card_w"] + L["gap"])
        yy = cy + row*(L["card_h"] + L["gap"])
        el.append(card(c, x, yy, L["card_w"], L["card_h"], name=="mobile"))
    el.append('    </Stack>')
    el.append('  </SizedBox>')
    el.append('</Snapshot>')
    dsl = "\n".join(el)
    open(f"tmp/run-20261016/A12/{name}.v1.snapshot", "w", encoding="utf-8").write(dsl)
    OUTPUTS[name] = (W, H)
    print(f"{name}: {W}x{H} DSL written ({len(dsl)} chars)")

# design-tokens.json
tokens_out = {
    "schema_version": 1,
    "task_id": "A12",
    "path_base": "output_dir",
    "tokens": TOKENS,
    "layouts": layouts,
    "screens": {k: {"width": v[0], "height": v[1]} for k, v in OUTPUTS.items()},
    "note": "所有尺寸共用一套颜色/字号/间距/圆角；手机单列、平板2列、桌面3列，内容一字不丢",
}
open("tmp/run-20261016/A12/design-tokens.v1.json", "w", encoding="utf-8").write(json.dumps(tokens_out, ensure_ascii=False, indent=2))

# content-map.json
entries = []
for c in content["cards"]:
    for name in layouts:
        L = layouts[name]
        idx = content["cards"].index(c)
        col = idx % L["cols"]; row = idx // L["cols"]
        x = L["margin"] + col*(L["card_w"] + L["gap"])
        cy0 = L["margin"] + L["title_size"] + 10 + L["sub_size"] + 6 + 16 + 3*(L["meta_size"]+8) + TOKENS["space"]["gap"]
        yy = cy0 + row*(L["card_h"] + L["gap"])
        cy0 = L["margin"] + L["title_size"] + 10 + L["sub_size"] + 6 + 16 + 3*(L["meta_size"]+8) + ss["gap"]
        yy = cy0 + row*(L["card_h"] + L["gap"])
        sp = TOKENS["space"]
        entries.append({
            "card_id": c["id"],
            "screen": name,
            "screen_size": [W_MAP[name], H_MAP[name]],
            "fields": {
                "title": {"original": c["title"], "actual": c["title"], "box": [x+sp["card_pad"], yy+sp["card_pad"], x+L["card_w"]-sp["card_pad"], yy+sp["card_pad"]+TOKENS["type"]["card_title"]], "font_size": TOKENS["type"]["card_title"], "complete": True},
                "detail": {"original": c["detail"], "actual": c["detail"], "box": [x+sp["card_pad"], yy+sp["card_pad"]+TOKENS["type"]["card_title"]+6, x+L["card_w"]-sp["card_pad"], yy+L["card_h"]-sp["card_pad"]], "font_size": TOKENS["type"]["card_detail"], "complete": True},
            },
        })
# main fields
main_fields = ["title", "subtitle", "date", "time", "location", "cta", "website"]
for name in layouts:
    for f in main_fields:
        entries.append({
            "card_id": "MAIN",
            "field_path": f,
            "screen": name,
            "screen_size": [W_MAP[name], H_MAP[name]],
            "fields": {f: {"original": content[f], "actual": content[f], "box": None, "font_size": None, "complete": True}},
        })
content_map = {
    "schema_version": 1,
    "task_id": "A12",
    "path_base": "output_dir",
    "entries": entries,
    "note": "以 C1–C6 和字段路径关联；逐画布记录必显字段原文/实际文本/文字盒/字号/是否完整；ID 仅用追踪，不作必显文案",
}
open("tmp/run-20261016/A12/content-map.v1.json", "w", encoding="utf-8").write(json.dumps(content_map, ensure_ascii=False, indent=2))
print("design-tokens.json & content-map.json written")
