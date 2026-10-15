import pathlib, subprocess, sys
d = pathlib.Path("tmp/run-20261011-01/A11/drafts")
cases = {
 "attr-entity":  '<Text fontSize="32" text="A &lt; B &amp; C &gt; D"/>',
 "attr-bare":    '<Text fontSize="32" text="A < B & C > D"/>',
 "cdata":        '<Text fontSize="32"><![CDATA[A < B & C > D]]></Text>',
 "bare-gt-text": '<Text fontSize="32">A > B</Text>',
 "attr-cjk":     '<Text fontSize="32" text="\u6279\u6b21\uff1a  A  07"/>',
}
for name, body in cases.items():
    dsl = ('<Snapshot type="png">\n<Container width="700" height="120" color="#FFFFFF">'
           '<Stack fit="EXPAND"><Positioned left="20" top="30" width="660" height="60">'
           f'{body}</Positioned></Stack></Container>\n</Snapshot>\n')
    p = d / f"ent2-{name}.snapshot"
    p.write_text(dsl, encoding="utf-8")
    out = subprocess.run([sys.executable, "tmp/run-20261011-01/_suite/scripts/snapshot_render.py",
                          "--task", "A11", "--version", f"ent2-{name}", "--dsl", p.as_posix(),
                          "--out", f"tmp/run-20261011-01/A11/preview/ent2-{name}.png",
                          "--log", "tmp/run-20261011-01/A11/requests.jsonl",
                          "--responses-dir", "tmp/run-20261011-01/A11/responses"],
                         capture_output=True, text=True, encoding="utf-8")
    last = out.stdout.strip().splitlines()[-1] if out.stdout.strip() else out.stderr[-300:]
    print(f"[{name}] {last[:200]}")
