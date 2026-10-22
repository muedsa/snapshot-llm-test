# -*- coding: utf-8 -*-
"""A17 handbook generator core.

Defines the four CORE example subtrees (each renders in a 400x240 logical
region) plus builders that wrap them into (a) a standalone 400x240 example
and (b) an inline block for a 1200x1600 handbook page. The core subtree text
is BYTE-IDENTICAL between the standalone example and the handbook page, so
print + illustration + independent render are guaranteed consistent.

The core subtrees are the "inner content" of a Stack: a list of
<Positioned>...</Positioned> lines placed in a 400x240 coordinate frame.
"""
import pathlib

TMP = pathlib.Path("tmp/run-20261011-01/A17")

# ---- the four core example subtrees (400x240 frame each) -----------------
# Each core is a list of DSL element strings (Positioned blocks). They teach:
#   ex1 = call contract: single root + one child + colored bg
#   ex2 = bounded Row/Column/Expanded + Stack absolute positioning
#   ex3 = Raw/CDATA whitespace + trailing-alpha #RRGGBBAA color
#   ex4 = subtree filter (ImageFiltered) vs background, and Opacity

CORES = {
    "01": [
        '<Positioned left="24" top="24" width="352" height="192">'
        '<Container color="#F1F5F9" borderRadius="12">'
        '<Column mainAxisAlignment="START">'
        '<Container color="#2563EB" width="352" height="80" '
        'borderRadius="12"/>'
        '<Container color="#EEF2FF" width="352" height="92" '
        'borderRadius="12"/>'
        '</Column>'
        '</Container></Positioned>',
        '<Positioned left="40" top="44" width="320" height="40">'
        '<Text fontSize="22" color="#FFFFFF" fontFamily="Inter" '
        'text="POST /snapshot"/></Positioned>',
        '<Positioned left="40" top="142" width="320" height="28">'
        '<Text fontSize="16" color="#1A2740" fontFamily="Inter" '
        'text="body = UTF-8 DSL text"/></Positioned>',
        '<Positioned left="40" top="174" width="320" height="28">'
        '<Text fontSize="16" color="#64748B" fontFamily="Inter" '
        'text="resp = image/png bytes"/></Positioned>',
    ],
    "02": [
        '<Positioned left="24" top="24" width="160" height="192">'
        '<Column mainAxisAlignment="SPACE_BETWEEN">'
        '<Container color="#2563EB" width="160" height="56" '
        'borderRadius="8"/>'
        '<Container color="#F59E0B" width="160" height="56" '
        'borderRadius="8"/>'
        '<Container color="#16A34A" width="160" height="56" '
        'borderRadius="8"/>'
        '</Column></Positioned>',
        '<Positioned left="204" top="24" width="172" height="192">'
        '<Container color="#F1F5F9" borderRadius="12"/>'
        '</Positioned>',
        '<Positioned left="300" top="152" width="60" height="44">'
        '<Container color="#DC2626" borderRadius="8"/>'
        '</Positioned>',
        '<Positioned left="220" top="40" width="140" height="28">'
        '<Text fontSize="15" color="#1A2740" fontFamily="Inter" '
        'text="Stack+Positioned"/></Positioned>',
    ],
    "03": [
        '<Positioned left="24" top="24" width="352" height="76">'
        '<Text fontSize="18" color="#1A2740" fontFamily="Inter">'
        '<Raw><![CDATA[Raw   keeps   spaces]]></Raw>'
        '</Text></Positioned>',
        '<Positioned left="24" top="116" width="352" height="44">'
        '<Container color="#FF000080" borderRadius="10"/>'
        '</Positioned>',
        '<Positioned left="24" top="172" width="352" height="44">'
        '<Container color="#FF0000" borderRadius="10"/>'
        '</Positioned>',
    ],
    "04": [
        '<Positioned left="24" top="24" width="352" height="88">'
        '<Container color="#2563EB" borderRadius="16"/>'
        '</Positioned>',
        '<Positioned left="24" top="128" width="352" height="88">'
        '<ImageFiltered sigmaX="6" sigmaY="6">'
        '<Container color="#2563EB" borderRadius="16"/>'
        '</ImageFiltered></Positioned>',
    ],
}


def core_block(core):
    """Return the core subtree as an indented list of lines (no outer
    wrapper). This exact text is shared by standalone + handbook."""
    return list(core)


def build_standalone(core):
    """Wrap a core in Snapshot+SizedBox(400x240)+Stack for a standalone
    400x240 example."""
    parts = ['<Snapshot type="png" background="#FFFFFF">',
             '  <SizedBox width="400" height="240">',
             '    <Stack alignment="TOP_LEFT" clipBehavior="NONE">']
    for line in core:
        parts.append("      " + line)
    parts += ['    </Stack>', '  </SizedBox>', '</Snapshot>', '']
    return "\n".join(parts)


def build_page(core, top):
    """Return the core subtree indented and offset to sit at page position
    `top` (left margin 48). Used inside the page's own top-level Stack."""
    # The core uses absolute coords in a 400x240 frame; to place it on the
    # 1200x1600 page at left=48, top=`top`, we wrap it in a positioned frame.
    parts = [f'<Positioned left="48" top="{top}" width="400" height="240">',
             '  <Stack alignment="TOP_LEFT" clipBehavior="NONE">']
    for line in core:
        parts.append("    " + line)
    parts += ['  </Stack>', '</Positioned>']
    return parts


def render(dsl_path, out_path, rid):
    """Render via the suite helper; logs to A17 requests.jsonl."""
    import json
    import subprocess
    import sys as _sys
    root = pathlib.Path(".")
    helper = root / "tmp/run-20261011-01/_suite/scripts/snap_render.py"
    log = TMP / "requests.jsonl"
    cmd = [_sys.executable, str(helper), "--dsl", str(dsl_path),
           "--out", str(out_path), "--log", str(log), "--rid", rid]
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(r.stdout.strip())
    if r.returncode != 0:
        print(r.stderr[-2000:])
        raise SystemExit(f"render failed for {rid}")
    return json.loads(r.stdout.strip().splitlines()[-1])


if __name__ == "__main__":
    # smoke: build standalone examples for all four cores
    (TMP / "smoke").mkdir(parents=True, exist_ok=True)
    for name, core in CORES.items():
        dsl = build_standalone(core)
        p = TMP / "smoke" / f"smoke-{name}.snapshot"
        p.write_text(dsl, encoding="utf-8")
        print(f"smoke-{name}: {len(dsl.splitlines())} lines")
