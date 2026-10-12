import difflib, os

RUN = "20261008T1615Z-run01"


def strip_pref(raw):
    if raw.startswith(b"POST"):
        i = raw.find(b"\n\n")
        if i != -1:
            return raw[i + 2:]
    return raw


for case, ver in (("case-06", "v05"), ("case-09", "v04")):
    d = "tmp/%s/B01/%s/requests" % (RUN, case)
    fin = "outputs/%s/B01/%s/final.snapshot" % (RUN, case)
    f = open(fin, "rb").read()
    print("==", case, "final bytes", len(f))
    best = []
    for fn in sorted(os.listdir(d)):
        if ".body" not in fn.lower():
            continue
        b = strip_pref(open(os.path.join(d, fn), "rb").read())
        best.append((abs(len(b) - len(f)), fn, len(b), b))
    for diff, fn, ln, b in sorted(best):
        same = (b == f)
        print("  %-46s body=%6d delta=%5d equal=%s" % (fn[:46], ln, ln - len(f), same))
        if not same and diff <= 200:
            lo = next((i for i in range(min(len(b), len(f))) if b[i] != f[i]), None)
            print("     first diff at", lo, repr(b[max(0, lo - 40):lo + 40]), "||", repr(f[max(0, lo - 40):lo + 40]))
    print("  final head", repr(f[:60]), "tail", repr(f[-60:]))
