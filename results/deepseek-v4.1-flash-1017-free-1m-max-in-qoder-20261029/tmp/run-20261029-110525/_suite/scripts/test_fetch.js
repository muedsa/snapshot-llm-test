const fs = require('fs');
const path = process.argv[2];
const out = process.argv[3];
const url = process.env.SNAPSHOT_URL || 'https://open-snapshot.muedsa.com/snapshot';
(async () => {
  const body = fs.readFileSync(path);
  const t0 = Date.now();
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'text/plain; charset=utf-8', 'Connection': 'close' },
      body,
      signal: AbortSignal.timeout(90000),
    });
    const buf = Buffer.from(await res.arrayBuffer());
    fs.writeFileSync(out, buf);
    console.log(JSON.stringify({ status: res.status, bytes: buf.length, ms: Date.now() - t0,
      ct: res.headers.get('content-type'), len: res.headers.get('content-length'),
      reqid: res.headers.get('x-request-id'), timing: res.headers.get('server-timing') }));
  } catch (e) {
    console.log(JSON.stringify({ error: String(e), ms: Date.now() - t0 }));
  }
})();
