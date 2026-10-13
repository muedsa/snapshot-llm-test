"""Return SNAPSHOT_API_KEY from the process env, else the user-scoped Windows env.

Reads HKCU\Environment so a shell that was started before the key was set can still
use it. The value is never printed or written to disk.
"""
from __future__ import annotations

import os
import sys


def api_key() -> str | None:
    k = os.environ.get("SNAPSHOT_API_KEY")
    if k:
        return k
    if os.name != "nt":
        return None
    import winreg
    for hive, path in ((winreg.HKEY_CURRENT_USER, "Environment"),
                       (winreg.HKEY_LOCAL_MACHINE,
                        r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment")):
        try:
            with winreg.OpenKey(hive, path) as key:
                v, _ = winreg.QueryValueEx(key, "SNAPSHOT_API_KEY")
                if v:
                    return str(v)
        except OSError:
            continue
    return None


if __name__ == "__main__":
    print("present" if api_key() else "absent")
    sys.exit(0 if api_key() else 1)
