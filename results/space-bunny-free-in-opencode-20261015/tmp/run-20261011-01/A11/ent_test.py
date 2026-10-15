import pathlib, subprocess, sys
d = pathlib.Path("tmp/run-20261011-01/A11/drafts")
cases = {
 "bare-amp": '<Text fontSize="32">A &amp; B</Text>',
 "bare-amp-literal": '<Text fontSize="32">A & B</Text>',
 "bare-lt-literal": '<Text fontSize="32">A < B</Text>',
 "numeric-entity": '<Text fontSize="32">A &#60; B</Text>',
 "raw-entity": '<Text fontSize="32"><Raw>A &lt; B &amp; C &gt; D</Raw></Text>',
}
for name, body in cases.items():
    dsl = ('<Snapshot type="png">\n<Container width="700" height="120" color="#FFFFFF">'
           '<Stack fit="EXPAND"><Positioned left="20" top="30" width="660" height="60">'
           f'{body}</Positioned></Stack></Container>\n</Snapshot>\n')
    p = d / f"ent-{name}.snapshot"
    p.write_text(dsl, encoding="utf-8")
    out = subprocess.run([sys.executable, "tmp/run-20261011-01/_suite/scripts/snapshot_render.py",
                          "--task", "A11", "--version", f"ent-{name}", "--dsl", p.as_posix(),
                          "--out", f"tmp/run-20261011-01/A11/preview/ent-{name}.png",
                          "--log", "tmp/run-20261011-01/A11/requests.jsonl",
                          "--responses-dir", "tmp/run-20261011-01/A11/responses"],
                         capture_output=True, text=True, encoding="utf-8")
    last = out.stdout.strip().splitlines()[-1] if out.stdout.strip() else out.stderr[-300:]
    print(f"[{name}] {last[:240]}")
