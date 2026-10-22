# -*- coding: utf-8 -*-
"""Probe the snapshot service state during the RemoteDisconnected streak.

Reports HTTP status, headers (incl. Retry-After / Server-Timing), and body
for a minimal DSL, so we can distinguish service outage from a DSL problem.
"""
import datetime
import pathlib

import requests

ROOT = pathlib.Path(__file__).resolve().parents[4]
BASE = "https://open-snapshot.muedsa.com"
MINIMAL = ('<Snapshot type="png" background="#FFFFFF">'
           '<SizedBox width="200" height="120">'
           '<Stack alignment="TOP_LEFT" clipBehavior="NONE">'
           '<Positioned left="10" top="10" width="180" height="100">'
           '<Text fontSize="24" fontFamily="Noto Sans CJK SC" color="#111111"'
           ' textAlign="LEFT" text="probe"/></Positioned>'
           '</Stack></SizedBox></Snapshot>')

for i in range(3):
    ts = datetime.datetime.now().astimezone().isoformat(timespec="milliseconds")
    try:
        r = requests.post(BASE + "/snapshot", data=MINIMAL.encode("utf-8"),
                          headers={"Content-Type": "application/xml"},
                          timeout=40)
        print("%s try%d status=%d ct=%s len=%d retry-after=%s st=%s"
              % (ts, i + 1, r.status_code, r.headers.get("Content-Type"),
                 len(r.content), r.headers.get("Retry-After"),
                 r.headers.get("Server-Timing")))
        if r.status_code != 200:
            print("   body:", r.text[:300])
        else:
            print("   PNG ok")
            break
    except Exception as e:  # noqa: BLE001 - report the real error verbatim
        print("%s try%d ERROR %r" % (ts, i + 1, e))
