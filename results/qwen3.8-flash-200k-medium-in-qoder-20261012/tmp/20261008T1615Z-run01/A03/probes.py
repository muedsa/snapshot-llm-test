"""A03 diagnostic probes: one small DSL per open semantic question.

Each probe answers exactly one thing the broken original leaves ambiguous, so the
repair log can cite a real service response instead of a guess.
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
TEMP = ROOT / "tmp" / RID / "A03"
SCRIPTS = ROOT / "tmp" / RID / "_suite" / "scripts"
sys.path.insert(0, str(SCRIPTS))

PROBES = {
    # Does <Snapshot width height> set the canvas at all?
    "root-wh": ('<Snapshot width="1280" height="800" background="#0B1220" type="png">'
                '<Container width="200" height="100" color="#38BDF8"/></Snapshot>'),
    # Is a kebab-case attribute name an error or silently ignored?
    "kebab": ('<Snapshot background="#0B1220" type="png">'
              '<Container width="420" height="120">'
              '<Text font-size="44" color="#FFFFFF">System Pulse</Text>'
              '</Container></Snapshot>'),
    # Are CSS named colours accepted by this parser?
    "named-color": ('<Snapshot background="#FFFFFF" type="png">'
                    '<Container width="420" height="120" color="white">'
                    '<Text color="white" fontSize="40">white on white = invisible</Text>'
                    '</Container></Snapshot>'),
    # Is Positioned legal inside a Row (Flex)?
    "pos-in-row": ('<Snapshot background="#0B1220" type="png">'
                   '<Container width="420" height="120"><Row>'
                   '<Container width="200" height="100" color="#38BDF8"/>'
                   '<Positioned right="20"><Text color="#FFFFFF">LIVE</Text></Positioned>'
                   '</Row></Container></Snapshot>'),
    # Does Transform accept a rotate attribute?
    "transform-rotate": ('<Snapshot background="#0B1220" type="png">'
                         '<Container width="420" height="200">'
                         '<Transform rotate="-8">'
                         '<Container width="160" height="56" color="#FFFFFF33">'
                         '<Text color="#FFFFFF" fontSize="24">REVIEW</Text></Container>'
                         '</Transform></Container></Snapshot>'),
    # Which end of an 8-digit hex is alpha?
    "alpha-hex": ('<Snapshot background="#0B1220" type="png">'
                  '<Stack alignment="TOP_LEFT" clipBehavior="NONE">'
                  '<Container width="420" height="200" color="#38BDF8"/>'
                  '<Row><Container width="200" height="200" color="#33FFFFFF"/>'
                  '<Container width="200" height="200" color="#FFFFFF33"/></Row>'
                  '</Stack></Snapshot>'),
    # Does ImageFiltered blur the subtree (including its text)?
    "imgfilt": ('<Snapshot background="#0B1220" type="png">'
                '<Stack alignment="TOP_LEFT" clipBehavior="NONE">'
                '<Container width="520" height="180" color="#0F172A"/>'
                '<ImageFiltered sigmaX="10" sigmaY="10">'
                '<Container width="500" height="150" color="#FFFFFF44">'
                '<Text color="#FFFFFF" fontSize="28">Background-only blur</Text>'
                '</Container></ImageFiltered></Stack></Snapshot>'),
    # Can BackdropFilter blur only what is behind, keeping text crisp?
    "backdrop": ('<Snapshot background="#0B1220" type="png">'
                 '<Container width="520" height="180">'
                 '<Stack alignment="TOP_LEFT" clipBehavior="NONE">'
                 '<Container width="520" height="180" color="#0F172A"/>'
                 '<Container width="6" height="180" color="#38BDF8"/>'
                 '<Container width="520" height="180" alignment="CENTER">'
                 '<ClipRRect borderRadius="24">'
                 '<BackdropFilter sigmaX="10" sigmaY="10">'
                 '<Container width="500" height="150" color="#FFFFFF14"/>'
                 '</BackdropFilter></ClipRRect></Container>'
                 '<Container width="520" height="180" alignment="CENTER">'
                 '<Text color="#FFFFFF" fontSize="28">Background-only blur</Text></Container>'
                 '</Stack></Container></Snapshot>'),
    # Is a fixed-size Container legal inside Expanded?
    "expanded-fixed": ('<Snapshot background="#0B1220" type="png">'
                       '<Container width="1200" height="200"><Row>'
                       '<Expanded flex="1">'
                       '<Container width="360" height="200" color="#334155">'
                       '<Text fontSize="28" color="#FFFFFF">USAGE 72%</Text></Container>'
                       '</Expanded>'
                       '<Expanded flex="1">'
                       '<Container color="#334155" width="360" height="200"/>'
                       '</Expanded></Row></Container></Snapshot>'),
    # Does an empty Row / childless Container collapse to zero (canvas size trap)?
    "empty-root": ('<Snapshot background="#0B1220" type="png">'
                   '<Container padding="32" borderRadius="24"><Column>'
                   '<Text fontSize="44" color="#FFFFFF">System Pulse</Text>'
                   '</Column></Container></Snapshot>'),
}


def main():
    (TEMP / "probe").mkdir(parents=True, exist_ok=True)
    results = []
    for name, dsl in PROBES.items():
        src = TEMP / "probe" / f"{name}.snapshot"
        src.write_text(dsl, encoding="utf-8")
        out = TEMP / "probe" / f"{name}.png"
        p = subprocess.run(
            [sys.executable, str(SCRIPTS / "render.py"), "--task", "A03",
             "--in", str(src.relative_to(ROOT)).replace("\\", "/"),
             "--out", str(out.relative_to(ROOT)).replace("\\", "/"),
             "--version", f"probe-{name}", "--kind", "probe",
             "--note", f"diagnostic probe: {name}",
             "--seq-dir", f"tmp/{RID}/A03"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=str(ROOT))
        results.append((name, p.returncode, p.stdout.strip()[:400], p.stderr.strip()[:200]))
        print(f"=== {name} rc={p.returncode}")
        print(p.stdout.strip()[:400] or p.stderr.strip()[:300])
    print(f"\n{len(results)} probes submitted")


if __name__ == "__main__":
    main()
