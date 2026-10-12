import os, re, json, glob, hashlib, sys

RUN = "20261008T1615Z-run01"
ROOT = "outputs/" + RUN
SUITE = ROOT + "/_suite/"
F = json.load(open("tmp/%s/_suite/suite-facts.json" % RUN, encoding="utf-8"))
ORDER = json.load(open("catalog.json", encoding="utf-8"))["task_order"]
T = F["tasks"]
SEP = os.sep


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(65536), b""):
            h.update(c)
    return h.hexdigest()


def md5b(b):
    return hashlib.md5(b).hexdigest()


def lf(b):
    return b.replace(b"\r\n", b"\n")


def prefix_strip(raw):
    if raw.startswith(b"POST"):
        for sep in (b"\r\n\r\n", b"\n\n"):
            i = raw.find(sep)
            if i != -1:
                return raw[i + len(sep):]
    return raw


def body_bytes(fp):
    """Retained request body: strip the saved POST request line + headers, then
    normalize line endings (a few early .body.txt files were written in text mode
    so CRLF was inserted by the OS; the bytes actually sent used LF)."""
    return lf(prefix_strip(open(fp, "rb").read()))


def norm(p):
    return os.path.normpath(p).replace(SEP, "/")


R = []


def check(name, ok, detail=""):
    R.append({"check": name, "result": "PASS" if ok else "FAIL", "detail": detail})
    print(("PASS " if ok else "FAIL ") + name + ("  " + detail if detail else ""))
    return bool(ok)


ok_all = True

need = ["index.md", "gallery.md", "snapshot-usage.md", "task-metrics.json", "suite-state.json"]
have = [f for f in need if os.path.exists(SUITE + f)]
ok_all &= check("套件五件交付齐备", len(have) == 5, "现有 " + ",".join(have))

gtxt = open(SUITE + "gallery.md", encoding="utf-8").read()
bad = [l for l in re.findall(r"\]\(([^)]+)\)", gtxt)
       if not l.startswith("http") and not os.path.exists(os.path.normpath(os.path.join(SUITE, l)))]
ok_all &= check("gallery.md 链接全部可解析", not bad, "失效 %d：%s" % (len(bad), bad[:5]))

img_count = sum(len(T[t]["images"]) for t in ORDER)
missing = []
for tid in ORDER:
    for im in T[tid]["images"]:
        if "../" + im["png"] not in gtxt or "../" + im["snapshot"] not in gtxt:
            missing.append(im["rel"])
ok_all &= check("画廊逐图覆盖 %d 张（预览 + PNG + DSL 链接齐全）" % img_count, not missing, "缺链 %s" % missing[:6])

itxt = open(SUITE + "index.md", encoding="utf-8").read()
ibad = [l for l in re.findall(r"\]\(([^)]+)\)", itxt)
        if not l.startswith("http") and not os.path.exists(os.path.normpath(os.path.join(SUITE, l)))]
ok_all &= check("index.md 链接全部可解析", not ibad, "失效 %s" % ibad[:5])

prov, orphan = {}, []
n_bin = n_prev = 0
for tid in ORDER:
    pool_bin, pool_prev = {}, {}
    for g in ("tmp/%s/%s" % (RUN, tid), "outputs/%s/%s" % (RUN, tid), "outputs/%s/requests" % RUN):
        if not os.path.isdir(g):
            continue
        for root, dirs, files in os.walk(g):
            for fn in files:
                fp = norm(os.path.join(root, fn))
                low = fn.lower()
                try:
                    if low.endswith(".bin") or ".response" in low:
                        pool_bin[md5(fp)] = fp
                    elif low.endswith(".png"):
                        base = os.path.basename(fp)
                        if fp.endswith("/final.png") or base.startswith("zoom") or base.startswith("qa-") or "/qa/" in fp:
                            continue
                        pool_prev[md5(fp)] = fp
                except Exception:
                    pass
    for im in T[tid]["images"]:
        if im["png_md5"] in pool_bin:
            prov[im["rel"]] = "raw_response_bin:" + pool_bin[im["png_md5"]]
            n_bin += 1
        elif im["png_md5"] in pool_prev:
            prov[im["rel"]] = "served_response_preview:" + pool_prev[im["png_md5"]]
            n_prev += 1
        else:
            orphan.append(im["rel"])
ok_all &= check("每张最终 PNG 的 md5 对到留存的服务响应字节（.bin %d 张 / 响应落盘预览 %d 张）" % (n_bin, n_prev),
                not orphan, "找不到来源 %d：%s" % (len(orphan), orphan[:12]))
json.dump(prov, open("tmp/%s/_suite/png-provenance.json" % RUN, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

dsl_prov, mismatch = {}, []
for tid in ORDER:
    bodies = {}
    for g in ("tmp/%s/%s" % (RUN, tid), "outputs/%s/%s" % (RUN, tid)):
        if not os.path.isdir(g):
            continue
        for root, dirs, files in os.walk(g):
            for fn in files:
                low = fn.lower()
                if not (low.endswith(".snapshot") or ".body" in low):
                    continue
                fp = norm(os.path.join(root, fn))
                try:
                    bodies.setdefault(md5b(body_bytes(fp)), []).append(fp)
                except Exception:
                    pass
    for im in T[tid]["images"]:
        fp = norm(os.path.join(ROOT, im["snapshot"]))
        final_bytes = open(fp, "rb").read()
        m = md5b(lf(final_bytes))
        cands = [p for p in bodies.get(m, []) if p != fp]
        hit = cands[0] if cands else bodies.get(m, [fp])[0]
        if cands:
            exact = any(prefix_strip(open(p, "rb").read()) == final_bytes for p in cands)
            dsl_prov[im["snapshot"]] = ("retained_request:" if exact else "retained_request_lf_normalized:") + hit
        else:
            dsl_prov[im["snapshot"]] = "self-only:" + fp
            mismatch.append(im["snapshot"])
n_retained = sum(1 for v in dsl_prov.values() if not v.startswith("self-only"))
n_norm = sum(1 for v in dsl_prov.values() if v.startswith("retained_request_lf_normalized"))
ok_all &= check("每张最终 DSL 与留存请求体/工作 DSL 字节一致（独立留存 %d/%d，其中 %d 张留存文件为 CRLF 写入需换行归一）"
                % (n_retained, img_count, n_norm),
                not mismatch, "无独立留存 %d：%s" % (len(mismatch), mismatch[:8]))
json.dump(dsl_prov, open("tmp/%s/_suite/dsl-provenance.json" % RUN, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

badmag = []
for tid in ORDER:
    for im in T[tid]["images"]:
        with open(os.path.join(ROOT, im["rel"]), "rb") as f:
            head = f.read(8)
        if head != b"\x89PNG\r\n\x1a\n" or not (im["width"] and im["height"]):
            badmag.append(im["rel"])
ok_all &= check("最终图为合法 PNG 且 IHDR 尺寸可读", not badmag, str(badmag[:5]))

short = [(t, T[t]["final_images"], T[t]["minimum_final_pngs"]) for t in ORDER
         if T[t]["final_images"] < (T[t]["minimum_final_pngs"] or 1)]
ok_all &= check("每题最终图 ≥ 题内最低要求", not short, str(short))
tot = sum(T[t]["final_images"] for t in ORDER)
ok_all &= check("全套最终图 %d ≥ 题库最低 %d" % (tot, F["totals"]["minimum_required"]),
                tot >= F["totals"]["minimum_required"])

bcase = {t: len({i["rel"].split("/")[1] for i in T[t]["images"] if "/case-" in i["rel"]})
         for t in ORDER if t.startswith("B")}
ok_all &= check("B01–B06 各 ≥10 个独立用例", all(v >= 10 for v in bcase.values()), json.dumps(bcase))

tu = {}
for t in [x for x in ORDER if x.startswith("B")]:
    p = "tmp/%s/%s/tool-usage.jsonl" % (RUN, t)
    tu[t] = sum(1 for _ in open(p, encoding="utf-8")) if os.path.exists(p) else 0
ok_all &= check("B 轨每题 tool-usage.jsonl 存在且非空", all(v > 0 for v in tu.values()), json.dumps(tu))

rounds = {t: sorted(os.path.basename(p) for p in glob.glob("%s/%s/round-*" % (ROOT, t))) for t in ("A21", "A22")}
ok_all &= check("A21/A22 三个预置轮次目录齐备", all(len(v) == 3 for v in rounds.values()), json.dumps(rounds))

nolog = [t + "/" + f for t in ORDER for f in ("requests.jsonl", "iterations.jsonl")
         if not os.path.exists("tmp/%s/%s/%s" % (RUN, t, f))]
ok_all &= check("每题 requests.jsonl + iterations.jsonl 存在", not nolog, str(nolog[:8]))

gi = open(".gitignore", encoding="utf-8").read()
bad_rules = [x for x in ("tmp/", "outputs/", "*.log", "cache/", ".cache/") if re.search(r"(?m)^%s" % re.escape(x), gi)]
ok_all &= check("根 .gitignore 未忽略过程证据", not bad_rules, str(bad_rules))

MACHINE_PATH = re.compile(r"(?:^|[^A-Za-z0-9+/\-])[A-Za-z]:[\\/](?!/)|/home/\w|\\\\[\w.$]+\W|C:Users")
pat = MACHINE_PATH
leak = []
for f in need:
    p = SUITE + f
    if os.path.exists(p):
        for n, line in enumerate(open(p, encoding="utf-8"), 1):
            if pat.search(line):
                leak.append("%s:%d" % (f, n))
ok_all &= check("套件交付文件无机器绝对路径/用户目录", not leak, str(leak[:6]))

pat2 = MACHINE_PATH
dsl_hits = []
for tid in ORDER:
    for im in T[tid]["images"]:
        p = os.path.join(ROOT, im["snapshot"])
        for line in open(p, encoding="utf-8", errors="replace"):
            if pat2.search(line):
                dsl_hits.append(im["snapshot"])
                break
ALLOWED_PATH_TEXT = {"A11/invoice-page-02.snapshot"}
unexpected_path = [h for h in dsl_hits if h not in ALLOWED_PATH_TEXT]
ok_all &= check("交付 DSL 内不写机器路径（题面点名要逐字保真的输入样本除外）",
                not unexpected_path,
                "命中 %d 个文件；白名单外 %s。白名单理由：A11 要求 4 行特殊字样逐字保真，其中一行原文即含盘符路径"
                % (len(dsl_hits), unexpected_path[:4]))

forbidden = re.findall(r"\]\(\.\./[^)]*(?:-preview\.png|/zoom-|/qa-|probe-)[^)]*\)", gtxt)
ok_all &= check("画廊只列最终作品（无 preview/zoom/qa/probe 链接）", not forbidden, str(forbidden[:4]))

json.dump(R, open("tmp/%s/_suite/final-review-checks.json" % RUN, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\nSUMMARY %d/%d PASS" % (sum(1 for x in R if x["result"] == "PASS"), len(R)))
