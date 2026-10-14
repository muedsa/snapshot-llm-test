"""Why does the BackdropFilter card differ between the standalone example and the page?

Three renders of the same core_4 subtree at 1:1:
  A  Snapshot > Container(400x240) > core        - the delivered example layout
  B  Snapshot > Stack(400x240 white) > Positioned(core) - adds the page's wrapper only
  C  Snapshot > Stack(1200x1600, white card) > Positioned(core at 64,291) - the page's
     layer size, nothing else
Comparing the card window across A/B/C separates "wrapper changed the painting" from
"Skia blurred a bigger layer".
"""
import sys
from pathlib import Path

RUN_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_DIR / "_suite" / "scripts"))
sys.path.insert(0, str(RUN_DIR / "A17"))

from snap import C, Container, Node, Positioned, Snapshot, Stack, num  # noqa: E402
import examples as ex  # noqa: E402

core = ex.core_4()

a = Snapshot(Container(core, width=num(400), height=num(240)), type="png",
             background="#FFFFFF")
b = Snapshot(Stack(C(width="400", height="240", color="#FFFFFF"),
                   Positioned(core, left="0", top="0"),
                   alignment="TOP_LEFT", clipBehavior="HARD_EDGE"),
             type="png", background="#FFFFFF")
c = Snapshot(Stack(C(width="1200", height="1600", color="#F6F7FA"),
                   C(width="432", height="384", color="#FFFFFF", borderRadius="14"),
                   Positioned(core, left="64", top="291"),
                   alignment="TOP_LEFT", clipBehavior="HARD_EDGE"),
             type="png", background="#F6F7FA")
# Container with no children still needs its own node for the card in C
c = Node("Snapshot", {"type": "png", "background": "#F6F7FA"},
         [Node("Stack", {"alignment": "TOP_LEFT", "clipBehavior": "HARD_EDGE"},
               [C(width="1200", height="1600", color="#F6F7FA"),
                C(width="432", height="384", color="#FFFFFF", borderRadius="14"),
                Positioned(core, left="64", top="291")])])

for name, doc in (("a", a), ("b", b), ("c", c)):
    (RUN_DIR / "A17" / f"probe-backdrop-{name}.snapshot").write_text(
        doc.render() + "\n", encoding="utf-8")
print("written probe-backdrop-a/b/c.snapshot")
