#!/usr/bin/env node
/* Render Snapshot DSL files through the real /snapshot service.
 * Usage:
 *   node render.js --task A01 [--tag final] [--jobs 6] [--out-dir DIR] file1.snapshot ...
 *   node render.js --task A01 --dir DIR [--dir DIR2 ...]
 * Each DSL renders to <stem>.png beside it unless --out-dir is given.
 * Raw response bytes are written verbatim; requests append to tmp/<run_id>/<task>/requests.jsonl.
 */
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const SUITE_TMP = path.resolve(__dirname, '..');            // tmp/<run_id>/_suite
const SUITE_ROOT = path.resolve(SUITE_TMP, '..', '..', '..');   // suite root
const RUN_ID = path.basename(path.resolve(SUITE_TMP, '..'));
const BASE = (process.env.SNAPSHOT_URL || 'https://open-snapshot.muedsa.com').replace(/\/+$/, '');

function rel(p) { return path.relative(SUITE_ROOT, p).split(path.sep).join('/'); }
function nowLocal() {
  const d = new Date();
  const pad = n => String(Math.abs(n)).padStart(2, '0');
  const off = -d.getTimezoneOffset();
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}${off >= 0 ? '+' : '-'}${pad(Math.floor(Math.abs(off) / 60))}${pad(Math.abs(off) % 60)}`;
}
function parseArgs(argv) {
  const a = { task: null, tag: 'final', jobs: 5, outDir: null, files: [], dirs: [] };
  for (let i = 0; i < argv.length; i++) {
    const v = argv[i];
    if (v === '--task') a.task = argv[++i];
    else if (v === '--tag') a.tag = argv[++i];
    else if (v === '--jobs') a.jobs = parseInt(argv[++i], 10);
    else if (v === '--out-dir') a.outDir = path.resolve(argv[++i]);
    else if (v === '--dir') a.dirs.push(path.resolve(argv[++i]));
    else a.files.push(path.resolve(v));
  }
  return a;
}
function validImage(buf) {
  if (buf.length > 1024 && buf[0] === 0x89 && buf.toString('ascii', 1, 4) === 'PNG') {
    return buf.includes(Buffer.from('IEND'));
  }
  if (buf.length > 1024 && buf[0] === 0xff && buf[1] === 0xd8) return true;
  if (buf.length > 1024 && buf.toString('ascii', 0, 4) === 'RIFF') return true;
  return false;
}

async function renderOne(task, file, outPng, tag) {
  const body = fs.readFileSync(file);
  const dslSha = crypto.createHash('sha256').update(body).digest('hex');
  const logDir = path.join(SUITE_TMP, '..', task);
  fs.mkdirSync(logDir, { recursive: true });
  let delay = 2000;
  for (let attempt = 1; attempt <= 3; attempt++) {
    const reqId = crypto.randomBytes(6).toString('hex');
    const caseMatch = rel(file).match(/case-(\d+)/);
    const rec = { task_id: task, tag, type: 'render',
      case_id: caseMatch ? `case-${caseMatch[1]}` : null,
      dsl: rel(file), png: rel(outPng), dsl_sha256: dslSha,
      request_bytes: body.length, request_id: reqId, attempt, started_at: nowLocal(),
      url: BASE + '/snapshot' };
    const t0 = Date.now();
    try {
      const res = await fetch(BASE + '/snapshot', {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain; charset=utf-8', 'Connection': 'close',
                   'User-Agent': 'snapshot-suite/1.0' },
        body, signal: AbortSignal.timeout(120000),
      });
      const buf = Buffer.from(await res.arrayBuffer());
      rec.http_status = res.status;
      rec.server_request_id = res.headers.get('x-request-id');
      rec.content_type = res.headers.get('content-type');
      rec.server_timing = res.headers.get('server-timing');
      rec.rate_limit_remaining = res.headers.get('x-ratelimit-remaining');
      rec.duration_ms = Date.now() - t0;
      rec.response_bytes = buf.length;
      if (res.status === 200 && validImage(buf)) {
        fs.mkdirSync(path.dirname(outPng), { recursive: true });
        fs.writeFileSync(outPng, buf);
        rec.status = 'success';
        rec.png_bytes = buf.length;
        rec.ended_at = nowLocal();
        fs.appendFileSync(path.join(logDir, 'requests.jsonl'), JSON.stringify(rec) + '\n');
        return rec;
      }
      const raw = outPng + (res.status === 200 ? '.invalid.bin' : `.http${res.status}.txt`);
      fs.writeFileSync(raw, buf);
      rec.status = 'error';
      rec.raw = rel(raw);
      rec.error_body = buf.toString('utf8', 0, 4000);
      rec.ended_at = nowLocal();
      fs.appendFileSync(path.join(logDir, 'requests.jsonl'), JSON.stringify(rec) + '\n');
      if ([429, 500, 502, 503, 504].includes(res.status) && attempt < 3) {
        const ra = res.headers.get('retry-after');
        const wait = ra && /^\d+$/.test(ra) ? parseInt(ra, 10) * 1000 : delay;
        await new Promise(r => setTimeout(r, Math.min(wait, 30000) + Math.random() * 1000));
        delay *= 2; continue;
      }
      return rec;
    } catch (e) {
      rec.duration_ms = Date.now() - t0;
      rec.status = 'error';
      rec.error = String(e);
      fs.appendFileSync(path.join(logDir, 'requests.jsonl'), JSON.stringify(rec) + '\n');
      if (attempt < 3) { await new Promise(r => setTimeout(r, delay)); delay *= 2; continue; }
      return rec;
    }
  }
}

(async () => {
  const a = parseArgs(process.argv.slice(2));
  if (!a.task) { console.error('missing --task'); process.exit(2); }
  let files = a.files.slice();
  for (const d of a.dirs) {
    for (const f of fs.readdirSync(d).filter(x => x.endsWith('.snapshot')).sort())
      files.push(path.join(d, f));
  }
  if (!files.length) { console.error('no .snapshot files'); process.exit(2); }
  const results = [];
  let idx = 0;
  async function worker() {
    while (idx < files.length) {
      const i = idx++;
      const f = files[i];
      const png = a.outDir ? path.join(a.outDir, path.basename(f, '.snapshot') + '.png')
                           : f.replace(/\.snapshot$/, '.png');
      const rec = await renderOne(a.task, f, png, a.tag);
      results.push(rec);
      console.log(JSON.stringify({ dsl: rec.dsl, status: rec.status, http: rec.http_status,
        png: rec.png, ms: rec.duration_ms, err: rec.error_body || rec.error || null }));
    }
  }
  await Promise.all(Array.from({ length: Math.max(1, Math.min(a.jobs, 8)) }, worker));
  const ok = results.filter(r => r.status === 'success').length;
  console.log(`done: ${ok}/${results.length} succeeded`);
  process.exitCode = ok === results.length ? 0 : 1;
})();
