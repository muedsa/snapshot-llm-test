const fs = require('fs');
const R = JSON.parse(fs.readFileSync('D:/mine/workspace/qwen3.8-flash-1m-xhigh-in-qoder/.qoder-credits/report.json', 'utf8'));
const out = [];
const p = (...a) => out.push(a.map(x => typeof x === 'number' ? String(x) : x).join(' '));
const nf = (n) => n.toLocaleString('en-US');
const pct = (a, b) => (a / b * 100).toFixed(2) + '%';

const B = R.totals.billedInputTokens;
const trips = R.byRequest;

// 1. category sum check
const catSum = R.byCategory.reduce((s, c) => s + c.tokens, 0);
p('categorySum=' + catSum + ' billed=' + B + ' diff=' + (B - catSum));
p('toolSum=' + R.byTool.reduce((s, t) => s + t.tokens, 0) + ' attrSum=' + R.byAttr.reduce((s, a) => s + a.tokens, 0));

// 2. per-trip averages
p('avgInputPerTrip=' + Math.round(B / trips.length) + ' avgCreditsPerTrip=' + (R.totals.credits / trips.length).toFixed(3));
p('creditsPerMillionInput=' + (R.totals.credits / (B / 1e6)).toFixed(3));
p('amplification=' + (B / R.totals.netContextTokens).toFixed(2));

// 3. ratio bands: how much billed comes from large contexts
const bands = [[0, 100000], [100000, 200000], [200000, 300000], [300000, 400000], [400000, 500000], [500000, 600001]];
p('--- input-size bands (tokens per request) ---');
for (const [lo, hi] of bands) {
  const in_ = trips.filter(r => r.inputTokens >= lo && r.inputTokens < hi);
  const sum = in_.reduce((s, r) => s + r.inputTokens, 0);
  p(`${lo}-${hi}: requests=${in_.length} (${pct(in_.length, trips.length)}) billed=${nf(sum)} share=${pct(sum, B)} credits=${in_.reduce((s,r)=>s+r.credits,0).toFixed(1)}`);
}
const big = trips.filter(r => r.inputTokens >= 400000);
p('>=400k requests: ' + big.length + ' (' + pct(big.length, trips.length) + ') billed share ' + pct(big.reduce((s, r) => s + r.inputTokens, 0), B));

// 4. timeline: parse local times "HH:MM" but better use index + compaction times. Use gap analysis on UTC times we can't get from byRequest (only HH:MM). Reconstruct: request #1 at startedAt, times appear local UTC+8.
const toMin = (t) => { const [h, m] = t.split(':').map(Number); return h * 60 + m; };
// session started 10:09 local (02:09Z), ended 10:21 local next day -> times wrap.
// Build absolute minutes assuming start at day0 10:09 and monotonic non-decreasing with wrap detection
let base = toMin('10:09');
const abs = [];
let prev = base;
for (const r of trips) {
  let m = toMin(r.time);
  while (m < prev) m += 1440;
  // allow small backward jitter? treat strictly
  abs.push(m);
  prev = m;
}
p('--- timeline ---');
p('startLocalMin=' + abs[0] + ' endLocalMin=' + abs[abs.length - 1] + ' spanHours=' + ((abs[abs.length - 1] - abs[0]) / 60).toFixed(2));
const gaps = [];
for (let i = 1; i < abs.length; i++) gaps.push({ i, gap: abs[i] - abs[i - 1], at: trips[i].time });
const sortedGaps = [...gaps].sort((a, b) => b.gap - a.gap);
const totalIdle = sortedGaps.reduce((s, g) => s + Math.max(0, g.gap - 1), 0);
p('sum of all inter-request gaps(min)=' + gaps.reduce((s, g) => s + g.gap, 0));
p('idle >5min total minutes=' + totalIdle + ' count>5min=' + sortedGaps.filter(g => g.gap > 5).length);
p('top 12 gaps: ' + sortedGaps.slice(0, 12).map(g => `${g.gap}min@${g.at}`).join(', '));
const activeMin = gaps.reduce((s, g) => s + Math.min(g.gap, 5), 0);
p('activeProxyMinutes(<=5min each)=' + activeMin + ' => hours=' + (activeMin / 60).toFixed(2));

// 5. hourly burn: bucket by local hour-of-day over the 24h
p('--- per-hour billed (local hour of day) ---');
const perHour = {};
for (let i = 0; i < trips.length; i++) {
  const h = Math.floor(abs[i] / 60) % 24;
  perHour[h] = perHour[h] || { req: 0, billed: 0, credits: 0 };
  perHour[h].req++; perHour[h].billed += trips[i].inputTokens; perHour[h].credits += trips[i].credits;
}
for (const h of Object.keys(perHour).sort((a, b) => perHour[b].billed - perHour[a].billed).slice(0, 8))
  p(`hour ${String(h).padStart(2,'0')}: req=${perHour[h].req} billed=${nf(perHour[h].billed)} share=${pct(perHour[h].billed, B)} credits=${perHour[h].credits.toFixed(1)}`);

// 6. segment analysis between compactions (by nextRequestIndex)
const marks = [0, ...R.compactionCost.items.map(c => c.nextRequestIndex), trips.length + 1];
p('--- segments between compactions ---');
for (let i = 0; i < marks.length - 1; i++) {
  const lo = marks[i], hi = marks[i + 1] - 1;
  const seg = trips.filter(r => r.index > lo && r.index <= hi);
  if (!seg.length) continue;
  const sum = seg.reduce((s, r) => s + r.inputTokens, 0);
  p(`seg${i + 1}: requests ${seg[0].index}-${seg[seg.length - 1].index} n=${seg.length} billed=${nf(sum)} share=${pct(sum, B)} credits=${seg.reduce((s,r)=>s+r.credits,0).toFixed(1)} peak=${nf(Math.max(...seg.map(r=>r.inputTokens)))}`);
}

// 7. compaction cost vs billed
const cc = R.compactionCost;
p('compaction preTokens sum=' + nf(cc.totals.preTokens) + ' = ' + pct(cc.totals.preTokens, B) + ' of billed; postTokens=' + nf(cc.totals.postTokens));
p('messagesSummarized sum=' + nf(cc.items.reduce((s, i) => s + i.messagesSummarized, 0)));
const cIdx = cc.items.map(i => i.nextRequestIndex);
const cTimes = cIdx.map(i => abs[Math.min(i, abs.length) - 1] !== undefined ? (abs[i - 1] || abs[abs.length - 1]) : 0);
const avgGapH = ((cTimes[cTimes.length - 1] - cTimes[0]) / (cTimes.length - 1) / 60).toFixed(2);
p('compaction request indices: ' + cIdx.join(', ') + ' avg interval hours=' + avgGapH);

// 8. file concentration
const bf = [...R.byFile].sort((a, b) => b.billed - a.billed);
const bfSum = bf.reduce((s, f) => s + f.billed, 0);
p('--- file attribution ---');
p('files=' + bf.length + ' attributedBilled=' + nf(bfSum) + ' = ' + pct(bfSum, B));
p('top10 share=' + pct(bf.slice(0, 10).reduce((s, f) => s + f.billed, 0), bfSum) + ' top50=' + pct(bf.slice(0, 50).reduce((s, f) => s + f.billed, 0), bfSum) + ' top100=' + pct(bf.slice(0, 100).reduce((s, f) => s + f.billed, 0), bfSum));
const reRead = [...bf].sort((a, b) => b.reads - a.reads).slice(0, 10);
p('most re-read files: ' + reRead.map(f => `${f.label} reads=${f.reads} billed=${nf(f.billed)}`).join(' | '));

// 9. tool call counts vs trips
p('--- tools ---');
p('toolCalls total=' + R.totals.toolCalls + ' fileReads=' + R.totals.fileReads + ' roundTrips=' + R.session.roundTrips + ' turns=' + R.session.turns);
for (const t of R.byTool) p(`${t.tool}: calls=${t.calls} billed=${nf(t.tokens)} share=${pct(t.tokens, B)} perCall=${nf(t.perCall)}`);

// 10. system prompt / attachment: constant re-send
const sysTok = R.byCategory.find(c => c.key === 'system').tokens;
const attTok = R.byCategory.find(c => c.key === 'attachment').tokens;
const csTok = R.byCategory.find(c => c.key === 'compact_summary').tokens;
p('system: ' + nf(sysTok) + ' = ' + pct(sysTok, B) + ' of billed, from a ' + nf(R.context.systemPromptTokens) + '-token prompt => re-sent ≈' + Math.round(sysTok / R.context.systemPromptTokens) + 'x (≈' + (sysTok / trips.length / 1000).toFixed(1) + 'k per request)');
p('attachment: ' + nf(attTok) + ' = ' + pct(attTok, B) + ' => avg ' + (attTok / trips.length / 1000).toFixed(1) + 'k tokens/request');
p('compact_summary: ' + nf(csTok) + ' = ' + pct(csTok, B) + ' => avg ' + (csTok / trips.length / 1000).toFixed(1) + 'k tokens/request');
const fixedPerReq = (sysTok + attTok + csTok) / trips.length;
p('fixed-overhead(system+attachment+compact)/trip = ' + Math.round(fixedPerReq) + ' = ' + pct(sysTok + attTok + csTok, B) + ' of all billed');

fs.writeFileSync('D:/mine/workspace/qwen3.8-flash-1m-xhigh-in-qoder/tmp/report-derived.txt', out.join('\n'), 'utf8');
console.log(out.join('\n'));
