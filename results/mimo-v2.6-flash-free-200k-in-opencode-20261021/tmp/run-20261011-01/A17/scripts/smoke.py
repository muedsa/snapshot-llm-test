# -*- coding: utf-8 -*-
"""A17 primitive smoke test: verify Row/Expanded, Raw+CDATA, filters, and
escaped-code-as-text all render before building the four handbook pages."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from gen_a17 import CORES, build_standalone, render  # noqa: E402

TMP = pathlib.Path("tmp/run-20261011-01/A17")


def main():
    (TMP / "smoke").mkdir(parents=True, exist_ok=True)
    for name, core in CORES.items():
        dsl = build_standalone(core)
        p = TMP / "smoke" / f"smoke-{name}.snapshot"
        p.write_text(dsl, encoding="utf-8")
        out = TMP / "smoke" / f"smoke-{name}.png"
        render(p, out, f"A17-smoke-{name}")
        print(f"{name}: lines={len(dsl.splitlines())} -> {out}")


if __name__ == "__main__":
    main()
