"""Report each A03 request's HTTP status, response size and PNG dimensions."""
import json
import os
import struct
from pathlib import Path

root = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
rid = os.environ["SNAPSHOT_RUN_ID"]
rows = [json.loads(l) for l in
        (root / "tmp" / rid / "A03" / "requests.jsonl").read_text(encoding="utf-8").splitlines()
        if l.strip()]
PNG = b"\x89PNG\r\n\x1a\n"
for r in rows:
    dim = None
    p = r.get("out_file")
    if p:
        f = (root / p) if not Path(p).is_absolute() else Path(p)
        if f.exists():
            b = f.read_bytes()
            if b[:8] == PNG:
                w, h = struct.unpack(">II", b[16:24])
                dim = f"{w}x{h}"
            else:
                dim = "not-png"
    print(f'{r["request_id"]:48s} {r.get("http_status")} '
          f'{str(r.get("response_bytes")):>8s} {str(dim):>10s} {r.get("error_summary")}')
