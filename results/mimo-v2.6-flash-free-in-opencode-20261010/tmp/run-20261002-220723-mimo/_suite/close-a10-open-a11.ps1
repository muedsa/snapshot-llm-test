$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
Set-Location $root

$now = (Get-Date).ToString('yyyy-MM-ddTHH:mm:ss+08:00')

# ---------------------------------------------------------------- suite-state
$sp = "outputs\$RUN\_suite\suite-state.json"
$s  = Get-Content $sp -Raw -Encoding UTF8 | ConvertFrom-Json

$a10 = $s.tasks | Where-Object { $_.id -eq 'A10' }
$a10.status    = 'completed'
$a10.ended_at  = '2026-10-03T13:05:51+08:00'
$a10.artifacts = @(
    'A10/compositing-lab.png',
    'A10/compositing-lab.snapshot',
    'A10/composite-audit.json',
    'A10/snapshot-usage.md',
    'A10/task-metrics.json',
    'A10/archive/compositing-lab-v01.png'
)
$a10.visual_review_evidence = @(
    'outputs/run-20261002-220723-mimo/A10/compositing-lab.png full view 2026-10-03T12:49+08:00 (v01): title "看到差异，才能说用对了", 6 x 320x240 white zones in 3 cols x 2 rows, numbers/descriptions outside the zones, card 240x160 r20, sigma 6 everywhere; panel1 overlap dark purple vs panel2 overlap periwinkle; ONE defect found - footer line 3 was soft-wrapped by <Text width> into two lines and the second line fell off the canvas bottom edge',
    'outputs/run-20261002-220723-mimo/A10/compositing-lab.png full view 2026-10-03T12:53+08:00 (v02, delivery): footer is now 4 complete single lines ending y=1076, nothing clipped; all six panels show their evidence; no further change was needed',
    'tmp/run-20261002-220723-mimo/A10/zoom-sample.png 2.2x viewed: panel1 overlap (127,63,191) dark purple, panel2 overlap (126,126,255) periwinkle, all four broken-crosshair arms present and the centre pixel (180,100) untouched',
    'tmp/run-20261002-220723-mimo/A10/zoom-card3.png 3x viewed: first crop accidentally captured panel 1 instead of panel 3 - kept as-is, then zoom-zone3/zoom-zone4 were cropped instead',
    'tmp/run-20261002-220723-mimo/A10/zoom-zone3.png 2.6x viewed: stripes outside the card crisp, stripes inside the card smoothed to a gradient, caption SHARP / BLUR and the red bar sharp, radius 20 visible',
    'tmp/run-20261002-220723-mimo/A10/zoom-zone4.png 2.6x viewed: caption and red bar blurred with the subtree, stripes outside the card still crisp - the A/B against panel 3 is unmistakable',
    'tmp/run-20261002-220723-mimo/A10/zoom-clip.png 1.8x viewed: panel5 is a golden rectangle with tinted transparent gaps and a shadow under the bottom bar; panel6 is the identical content clipped to a disc - the shape difference IS the clip boundary',
    'composite-audit.json 41/41 PASS on the delivered pair: IHDR 1440x1100, 6 zones at the planned grid coordinates, gaps 80/180, block centred (160/160), labels outside the zones, cards 240x160 r20, sigmaX=sigmaY=6 on all 4 ImageFiltered, ColorFiltered #F6B94A MULTIPLY x2, ClipOval x1, Opacity(0.5) x1, min fontSize 20, 0 embedded bitmaps; sampling (180,100) panel1 = (127,63,191) exact analytic match (delta 0,0,0), panel2 = (126,126,255) vs analytic (128,128,255) within the declared +/-2 LSB 8-bit rounding tolerance; worst channel difference between the two panels 64; stripe span outside card 107 vs inside <=40 in both panels; caption R-contrast 194 (sharp) vs 58 (blurred); tinted bbox shrinks from 236x227 (panel5) to the disc-clipped region (panel6) with an out-of-disc point measured pure white; full-canvas ink bbox fits with the last row clean'
)
$a10.unresolved_issues = @()
$a10.resume_notes = '1 completed visual iteration: the first delivery render (v01, 8077.4ms) put the 128/255-vs-0.5 explanation on one footer line, <Text> soft-wrapped it and the canvas bottom edge clipped the second line, violating "all evidence clearly visible"; split into two short lines at y=1024/1054 and moved the footer block up to y=964/994/1024/1054, re-rendered as v02 (2454.7ms) which is the delivery. 3 /snapshot requests total (2 delivery renders + 1 archive recovery), all 200, 0 failures, 0 retries; plus 2 real document requests (ai-guide.md, parser-tags) whose bodies were not persisted - only the excerpts actually relied on were retained in tmp/_suite/probe/A10-doc-excerpts.md with response_file honestly null. 2 DSL versions retained. PROCESS DEFECT RECORDED, NOT HIDDEN: the v02 render reused the delivery filename and overwrote the v01 PNG; recovered by re-rendering the identical v01 DSL into archive/compositing-lab-v01.png (247252 bytes, exactly the size recorded for the original v01 response, so the service output for this DSL is byte-stable), and appended a log_note row A10-lognote-archive-recovery to requests.jsonl (append-only, history rows untouched). 7 real image views; verify.ps1 is read-only against the delivered pair and recomputes the analytic compositing independently. 11 checker defects found and fixed honestly, including the -f operator forbidding a line break between its operands even inside parentheses.'

$a11 = $s.tasks | Where-Object { $_.id -eq 'A11' }
$a11.status = 'in_progress'
$a11.started_at = $now

$s.current_task = 'A11'
$s.current_round = $null
$s.current_case = $null
$s.updated_at = $now
$s.last_checkpoint = 'tmp/run-20261002-220723-mimo/_suite/checkpoints/state-000011.json'

$json = $s | ConvertTo-Json -Depth 10
[System.IO.File]::WriteAllText((Join-Path $root $sp), $json, [System.Text.UTF8Encoding]::new($false))
"suite-state updated -> $sp"

# ------------------------------------------------------------------- events
$ev = "tmp\$RUN\_suite\events.jsonl"
$enc = [System.Text.UTF8Encoding]::new($false)

$e1 = @{
  seq = 19; ts = $now; type = 'task_completed'; task = 'A10'
  artifacts = 6; renders = 3; views = 7; visual_iterations = 1
  note = 'Compositing lab 1440x1100: title "看到差异，才能说用对了", six 320x240 white experiment zones in a 3x2 grid at x=160/560/960 and y=270/690 with gaps 80 and 180 (both >=32) and the block centred at 160/160, numbers and 3-line descriptions in y140..260 / y560..680 - entirely outside the zones. Panel1 = #FF000080 (40,40,160,120) + #0000FF80 (120,80,160,120) blue painted last; panel2 = the same two rectangles OPAQUE inside <Opacity opacity="0.5">; panels3/4 = 240x160 radius-20 ClipRRect with caption SHARP / BLUR at fontSize 24, stripes crossing the card edge at a 16px period (8px #94A3B8 bars) staying crisp outside; panel3 blurs ONLY the stripe layer (clip outside ImageFiltered) while panel4 puts text+shape inside the same subtree; panels5/6 = ColorFiltered #F6B94A MULTIPLY then ImageFiltered sigmaX=sigmaY=6 over a subtree with transparent gaps, dark rects and a boxShadow, panel6 wrapped in ClipOval. Sampling point (180,100) in every zone; the broken crosshair arms deliberately avoid that exact pixel. 3 /snapshot requests all 200 (8077.4 + 2454.7 + 2924.5 ms, 0 failures, 0 retries) + 2 real document requests. 1 completed visual iteration: v01 footer line 3 soft-wrapped and the second line was clipped by the canvas bottom edge - split into two lines and moved the footer up. PROCESS DEFECT: v02 reused the delivery filename and overwrote the v01 PNG; recovered by re-rendering the identical v01 DSL into archive/compositing-lab-v01.png (247252 bytes = the originally recorded v01 size) and appended A10-lognote-archive-recovery. composite-audit.json 41/41 PASS: panel1 measured (127,63,191) exactly equals the analytic alpha stack (delta 0,0,0); panel2 measured (126,126,255) vs analytic (128,128,255) inside the declared +/-2 LSB tolerance with the 5x5 mean reported rather than asserted; worst channel difference between panels 1 and 2 = 64; stripe span 107 outside vs <=40 inside in both panels; caption R-contrast 194 vs 58; tinted bbox 236x227 in panel5 (ColorFiltered follows the blurred output bounds and keeps the shadow, exactly as the docs say) shrinking to the disc-clipped region in panel6 with an out-of-disc point measured pure white; min fontSize 20, no embedded bitmaps, nothing clipped. 128/255 vs 0.5 explained quantitatively: 128/255 = 0.5019607843 is 0.196% above 0.5, but the decisive difference is that panel1 composites twice (blue multiplies the already-composited backdrop by 127/255 = 0.498039) while panel2 flattens inside the group and fades exactly once. 7 real image views. 11 checker defects fixed honestly, including the PowerShell -f operator rejecting a line break between its operands even inside parentheses.'
} | ConvertTo-Json -Depth 6 -Compress

$e2 = @{
  seq = 20; ts = $now; type = 'task_started'; task = 'A11'
} | ConvertTo-Json -Depth 6 -Compress

[System.IO.File]::AppendAllText($ev, $e1 + "`n", $enc)
[System.IO.File]::AppendAllText($ev, $e2 + "`n", $enc)
"events now = " + (Get-Content $ev -Encoding UTF8).Count

# --------------------------------------------------------------- checkpoint
$cp = "tmp\$RUN\_suite\checkpoints\state-000011.json"
$copy = $s | ConvertTo-Json -Depth 10
[System.IO.File]::WriteAllText((Join-Path $root $cp), $copy, [System.Text.UTF8Encoding]::new($false))
"checkpoint written -> $cp  bytes=" + (Get-Item (Join-Path $root $cp)).Length
