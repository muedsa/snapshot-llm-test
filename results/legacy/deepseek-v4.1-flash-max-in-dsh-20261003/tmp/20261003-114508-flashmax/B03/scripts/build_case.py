"""build_case.py - render one case script's DSL to a versioned PNG and, when asked,
promote it to outputs/<run>/<TASK>/<case>/final.png + final.snapshot.

    python build_case.py case01 v1 01              # draft render -> tmp/.../renders/
    python build_case.py case01 v2 01 --final      # render and promote to case-01/
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN = "20261003-114508-flashmax"


def main():
    case_script, ver, case_no = sys.argv[1], sys.argv[2], sys.argv[3]
    promote = "--final" in sys.argv
    task = os.environ.get("SK_TASK", "B03")
    tmp = os.path.join(ROOT, "tmp", RUN, task)
    out = os.path.join(ROOT, "outputs", RUN, task)
    subprocess.run([sys.executable, os.path.join(HERE, case_script + ".py")], check=True)
    base = f"case-{case_no}"
    dsl = os.path.join(tmp, "dsl", f"{base}.snapshot")
    keep = os.path.join(tmp, "dsl", f"{base}.{ver}.snapshot")
    shutil.copyfile(dsl, keep)
    render_dir = os.path.join(tmp, "renders")
    os.makedirs(render_dir, exist_ok=True)
    png = os.path.join(render_dir, f"{base}.{ver}.png")
    seq_file = os.path.join(tmp, "reqseq.txt")
    n = int(open(seq_file).read().strip()) if os.path.exists(seq_file) else 0
    rid = f"{task}-REQ-{n + 1:04d}"
    with open(seq_file, "w") as fh:
        fh.write(str(n + 1))
    r = subprocess.run([sys.executable, os.path.join(HERE, "render.py"), dsl, png, rid,
                        "render", f"case-{case_no}"], capture_output=True, text=True)
    print(r.stdout.strip() or r.stderr.strip())
    if r.returncode != 0:
        print(f"RENDER FAILED - kept failure body at {png}.failed.txt")
        return 1
    if promote:
        cdir = os.path.join(out, f"case-{case_no}")
        os.makedirs(cdir, exist_ok=True)
        shutil.copyfile(png, os.path.join(cdir, "final.png"))
        shutil.copyfile(dsl, os.path.join(cdir, "final.snapshot"))
        print(f"promoted -> {os.path.join(cdir, 'final.png')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
