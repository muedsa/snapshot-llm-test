# Emits tmp/<run>/A14/iterations.jsonl from the real A14 process record.
# Timestamps are only filled in where they are genuinely recoverable:
#  - generator versions  -> layout-vN.json / gen.ps1 file mtimes
#  - render rounds       -> requests.jsonl started_utc / ended_utc
#  - image views         -> the render-completion and next-render bounds
# Anything else stays null with an explicit note; nothing is invented.
$ErrorActionPreference = 'Stop'
Set-Location $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName })

$RUN = 'run-20261002-220723-mimo'
$rel = "tmp/$RUN/A14"
$UTF8 = New-Object Text.UTF8Encoding($false)
$outPath = "tmp\$RUN\A14\iterations.jsonl"

$rows = New-Object System.Collections.Generic.List[object]
$seq = 0

function Add-Row([hashtable]$h) {
  $script:seq++
  $o = [ordered]@{
    id           = ('A14-iter-{0:D3}' -f $script:seq)
    seq          = $script:seq
    task         = 'A14'
    type         = $h.type
    category     = $h.category
    stage        = $h.stage
    target       = $h.target
    action       = $h.action
    finding      = $h.finding
    outcome      = $h.outcome
    request_id   = $h.request_id
    started_at   = $h.started_at
    ended_at     = $h.ended_at
    duration_ms  = $h.duration_ms
    view_window  = $h.view_window
    images_viewed = $h.images_viewed
    evidence     = $h.evidence
    note         = $h.note
  }
  $script:rows.Add([pscustomobject]$o)
}

$nullReq = $null
$nullMs = $null
$zero = 0
$one = 1
$eight = 8

# ---------------------------------------------------- generator development --
Add-Row @{
  type = 'syntax-fix'; category = 'generator'; stage = 'dev'
  target = 'gen.ps1-attempt-1'
  action = 'first run of the parametric generator'
  finding = 'PowerShell parsed U+2018 / U+2019 / U+201C / U+201D as quote delimiters while reading the no-start and prefer-break punctuation sets, so the script failed to parse before it produced anything'
  outcome = 'fixed by constructing both punctuation sets from [char] code points instead of literal glyphs'
  request_id = $nullReq; started_at = $nullReq; ended_at = $nullReq; duration_ms = $nullMs
  view_window = 'between task start 2026-10-03T17:05:36+08:00 and the first successful generator run 2026-10-03T17:34:29.918+08:00'
  images_viewed = $zero
  evidence = "$rel/gen.ps1"
  note = 'local script edit, no service request, exact wall-clock not captured'
}

Add-Row @{
  type = 'syntax-fix'; category = 'generator'; stage = 'dev'
  target = 'gen.ps1-attempt-2'
  action = 'ran the generator against inputs/cards.json'
  finding = 'ConvertFrom-Json returns a JSON array as a single pipeline object, so @() wrapped the whole deck as one element and the loop saw a card whose id was an array'
  outcome = 'assign the parsed value first, then normalise with a -is [array] test'
  request_id = $nullReq; started_at = $nullReq; ended_at = $nullReq; duration_ms = $nullMs
  view_window = 'same window as gen.ps1-attempt-1'
  images_viewed = $zero
  evidence = "$rel/gen.ps1"
  note = 'local script edit, no service request'
}

Add-Row @{
  type = 'syntax-fix'; category = 'generator'; stage = 'dev'
  target = 'gen.ps1-attempt-3'
  action = 'computed per-line widths inside an array literal'
  finding = 'PowerShell binds the comma tighter than + and -, so an expression of the form "total - preferred[k]" written inside @() was parsed as an Object[] subtraction'
  outcome = 'compute each operand into a temp variable first, then combine'
  request_id = $nullReq; started_at = $nullReq; ended_at = $nullReq; duration_ms = $nullMs
  view_window = 'same window as gen.ps1-attempt-1'
  images_viewed = $zero
  evidence = "$rel/gen.ps1"
  note = 'local script edit, no service request'
}

Add-Row @{
  type = 'baseline'; category = 'generator'; stage = 'dev'
  target = 'layout-v1'
  action = 'first generator run that produced a complete 8-card deck'
  finding = 'deck generated but CJK-heavy titles were under-sized because the width estimator padded every glyph by a flat 1.08: K03=80/2, K05=80/2, K06=88/2, K08=64/2'
  outcome = 'accepted as the first complete baseline and kept for comparison'
  request_id = $nullReq; started_at = $nullReq; ended_at = '2026-10-03T17:34:29.918+08:00'; duration_ms = $nullMs
  view_window = $nullReq
  images_viewed = $zero
  evidence = "$rel/layout-v1.json"
  note = 'ended_at is the layout-v1.json file mtime (local, UTC+08:00); generator run duration was not measured'
}

Add-Row @{
  type = 'alternative'; category = 'generator'; stage = 'measurement'
  target = 'layout-v2-per-class-width'
  action = 'replaced the flat width pad with per-class pads (CJK 1.05 because Noto Sans CJK fullwidth advance is exactly 1em, latin 1.10)'
  finding = 'K03 80 -> 88 and K06 88 -> 96; latin-heavy titles unchanged at this step'
  outcome = 'accepted, larger type on the CJK-heavy cards'
  request_id = $nullReq; started_at = $nullReq; ended_at = '2026-10-03T17:36:19.977+08:00'; duration_ms = $nullMs
  view_window = $nullReq
  images_viewed = $zero
  evidence = "$rel/layout-v2.json"
  note = 'ended_at is the layout-v2.json file mtime'
}

Add-Row @{
  type = 'alternative'; category = 'generator'; stage = 'line-breaking'
  target = 'layout-v3-natural-break'
  action = 'added a natural-break pass: take the largest ladder size that fits in at most 2 rows AND splits on punctuation or a space, falling back to a balanced split only when no size offers one'
  finding = 'K05 80 -> 72 (splits after the slash), K08 64 -> 56 (after the colon), K06 96 -> 88 (after the comma) - but K02 regressed 112/2 -> 88/1 because a single-row fit at a smaller size outranked the larger two-row break'
  outcome = 'rejected for K02; recorded as the defect to fix next'
  request_id = $nullReq; started_at = $nullReq; ended_at = '2026-10-03T17:39:36.208+08:00'; duration_ms = $nullMs
  view_window = $nullReq
  images_viewed = $zero
  evidence = "$rel/layout-v3.json"
  note = 'ended_at is the layout-v3.json file mtime'
}

Add-Row @{
  type = 'alternative'; category = 'generator'; stage = 'line-breaking'
  target = 'layout-v4-single-row-vs-break'
  action = 'made the single-row case report preferred_break = 0 so it can never outrank a larger size broken at punctuation'
  finding = 'K02 restored to 112/2 splitting after the full-width comma; K03 and K04 after the colon, K06 after the comma, K05 after the slash, K07 after the em-dash pair, K08 after the colon. Every title now at least 36px and at most 2 rows'
  outcome = 'accepted - layout frozen for the first render attempt'
  request_id = $nullReq; started_at = $nullReq; ended_at = '2026-10-03T17:41:45.745+08:00'; duration_ms = $nullMs
  view_window = $nullReq
  images_viewed = $zero
  evidence = "$rel/layout-v4.json"
  note = 'ended_at is the layout-v4.json file mtime'
}

# ------------------------------------------------------------- status probe --
Add-Row @{
  type = 'baseline'; category = 'render'; stage = 'probe'
  target = 'status-glyph-probe'
  action = 'rendered a small probe holding all four status labels before committing the 8-card batch'
  finding = 'U+25CB, U+25C6, U+25B3 and U+00D7 all render with no missing-glyph box in Noto Sans CJK SC, each in its own status colour, so the color + symbol + text encoding is safe to bake into every card'
  outcome = 'accepted - badge vocabulary proven before the batch'
  request_id = 'A14-p01-probe-badges'
  started_at = '2026-10-03T09:42:06.694Z'; ended_at = '2026-10-03T09:42:08.626Z'
  duration_ms = 1925.8
  view_window = 'viewed between 2026-10-03T09:42:08.626Z and the first card render 2026-10-03T09:43:21.657Z'
  images_viewed = $one
  evidence = "$rel/render-v1-probe-badges.png; $rel/probe-badges-v4.snapshot"
  note = 'viewed_at itself was not captured; the window above is bounded by the render it followed and the request that succeeded it'
}

# ------------------------------------------------------------- render round 1 --
Add-Row @{
  type = 'syntax-fix'; category = 'render'; stage = 'r01'
  target = 'render-round-1'
  action = 'posted all eight card-K01..K08-v4.snapshot files to /snapshot'
  finding = '8 x HTTP 400 PARSE_ERROR "Attr [color] unsupported CSS color" - the script-scope hairline colour $LINE was overwritten by the loop variable $line because PowerShell variables are case-insensitive, so title text reached the colour attribute'
  outcome = 'fixed by renaming the loop variables to $tline and $sline; the 8 error bodies are retained and never used as images'
  request_id = 'A14-r01-card-K01 .. A14-r01-card-K08 (8 rows)'
  started_at = '2026-10-03T09:43:21.657Z'; ended_at = '2026-10-03T09:43:35.040Z'
  duration_ms = 11601.9
  view_window = $nullReq
  images_viewed = $zero
  evidence = "$rel/failures/A14-r01-card-K01.body .. A14-r01-card-K08.body; requests.jsonl"
  note = 'no image was produced by this round, so nothing could be viewed'
}

# ------------------------------------------------------------- render round 2 --
Add-Row @{
  type = 'baseline'; category = 'render'; stage = 'r02'
  target = 'render-round-2'
  action = 're-rendered all eight cards from card-K01..K08-v5.snapshot'
  finding = '8 x HTTP 200, real 1200x630 PNG bytes written to render-v2-card-K01..K08.png - first complete visible deck'
  outcome = 'accepted as the visible baseline'
  request_id = 'A14-r02-card-K01 .. A14-r02-card-K08 (8 rows)'
  started_at = '2026-10-03T09:45:12.544Z'; ended_at = '2026-10-03T09:45:31.765Z'
  duration_ms = 17571.7
  view_window = $nullReq
  images_viewed = $zero
  evidence = "$rel/render-v2-card-K01.png .. render-v2-card-K08.png; requests.jsonl"
  note = 'render row; the viewing of these files is the following iteration'
}

Add-Row @{
  type = 'visual'; category = 'view'; stage = 'view-r02'
  target = 'render-v2-deck'
  action = 'opened each of the eight render-v2 cards with the real image tool and read its title, time, speaker, status pill and footer off the pixels'
  finding = 'content and status colours all correct, but K01 has a single title row and left a 188px hole under it while every two-row card filled the shared zone - the title block was top-aligned instead of centred'
  outcome = 'title block changed to vertically centred inside the shared zone 104..396, emitted as card-K01..K08-v6.snapshot'
  request_id = $nullReq
  started_at = '2026-10-03T09:45:31.765Z'; ended_at = '2026-10-03T09:50:10.884Z'
  duration_ms = $nullMs
  view_window = 'after render round 2 ended 2026-10-03T09:45:31.765Z, before render round 3 started 2026-10-03T09:50:10.884Z'
  images_viewed = $eight
  evidence = "$rel/render-v2-card-K01.png .. render-v2-card-K08.png; $rel/layout-v6.json"
  note = 'started_at / ended_at are the surrounding render bounds, not the exact open times, which were not captured'
}

# ------------------------------------------------------------- render round 3 --
Add-Row @{
  type = 'visual'; category = 'render'; stage = 'r03'
  target = 'render-round-3'
  action = 'rendered the centred-title deck from card-K01..K08-v6.snapshot'
  finding = '8 x HTTP 200 -> render-v3-card-K01..K08.png'
  outcome = 'accepted for viewing'
  request_id = 'A14-r03-card-K01 .. A14-r03-card-K08 (8 rows)'
  started_at = '2026-10-03T09:50:10.884Z'; ended_at = '2026-10-03T09:50:28.736Z'
  duration_ms = 16176.3
  view_window = $nullReq
  images_viewed = $zero
  evidence = "$rel/render-v3-card-K01.png .. render-v3-card-K08.png; requests.jsonl"
  note = 'render row'
}

Add-Row @{
  type = 'visual'; category = 'view'; stage = 'view-r03'
  target = 'render-v3-deck'
  action = 'opened all eight render-v3 cards individually and checked content, badge, title zone, divider and footer'
  finding = 'titles now centred and every status readable as colour + symbol + text, but the footer sat only 24px below the rule and stopped 52px short of the safe line, so the bottom margin (82px) was twice the top margin (40px)'
  outcome = 'footer rows rebalanced to TIME_Y = 442 and SPK_Y = 516 (38px under the rule, 42px above the safe line), emitted as card-K01..K08-v7.snapshot'
  request_id = $nullReq
  started_at = '2026-10-03T09:50:28.736Z'; ended_at = '2026-10-03T10:01:23.123Z'
  duration_ms = $nullMs
  view_window = 'after render round 3 ended 2026-10-03T09:50:28.736Z, before render round 4 started 2026-10-03T10:01:23.123Z'
  images_viewed = $eight
  evidence = "$rel/render-v3-card-K01.png .. render-v3-card-K08.png; $rel/layout-v7.json"
  note = 'started_at / ended_at are the surrounding render bounds'
}

# ------------------------------------------------------------- render round 4 --
Add-Row @{
  type = 'visual'; category = 'render'; stage = 'r04'
  target = 'render-round-4'
  action = 'rendered the rebalanced footer from card-K01..K08-v7.snapshot'
  finding = '8 x HTTP 200 -> render-v4-card-K01..K08.png'
  outcome = 'accepted for viewing'
  request_id = 'A14-r04-card-K01 .. A14-r04-card-K08 (8 rows)'
  started_at = '2026-10-03T10:01:23.123Z'; ended_at = '2026-10-03T10:01:47.733Z'
  duration_ms = 22932.5
  view_window = $nullReq
  images_viewed = $zero
  evidence = "$rel/render-v4-card-K01.png .. render-v4-card-K08.png; requests.jsonl"
  note = 'render row'
}

Add-Row @{
  type = 'visual'; category = 'view'; stage = 'view-r04'
  target = 'render-v4-card-K01'
  action = 'opened render-v4-card-K01.png with the image tool'
  finding = 'the rebalance only moved the footer 10px: the bottom band was still 82px against a 40px top margin, and the right column below the date stayed empty on seven of the eight cards'
  outcome = 'footer re-anchored to the bottom: the speaker block rests on the safe line (block bottom = 590), the time row sits 18px above it, the date moved onto the speaker row and the cancellation note onto the time row, giving every card 40/40 top and bottom margins plus a complete bottom row. A 2-line speaker is 69px tall and still lands on 590, so the rule cannot overflow'
  request_id = $nullReq
  started_at = '2026-10-03T10:01:47.733Z'; ended_at = '2026-10-03T10:07:00.949Z'
  duration_ms = $nullMs
  view_window = 'after render round 4 ended 2026-10-03T10:01:47.733Z, before render round 5 started 2026-10-03T10:07:00.949Z'
  images_viewed = $one
  evidence = "$rel/render-v4-card-K01.png; $rel/layout-v8.json"
  note = 'only K01 was opened at this intermediate version; the change is a single shared rule set, so it was re-verified card by card on the full final deck in the iterations that follow'
}

# ------------------------------------------------------------- render round 5 --
Add-Row @{
  type = 'visual'; category = 'render'; stage = 'r05'
  target = 'render-round-5-final'
  action = 'rendered the bottom-anchored deck from card-K01..K08-v8.snapshot'
  finding = '8 x HTTP 200 -> render-v5-card-K01..K08.png, each 1200x630 with distinct SHA-256, status-pill colour and divider tint matching its own card'
  outcome = 'accepted as the final render round'
  request_id = 'A14-r05-card-K01 .. A14-r05-card-K08 (8 rows)'
  started_at = '2026-10-03T10:07:00.949Z'; ended_at = '2026-10-03T10:08:10.205Z'
  duration_ms = 15796.2
  view_window = $nullReq
  images_viewed = $zero
  evidence = "$rel/render-v5-card-K01.png .. render-v5-card-K08.png; requests.jsonl"
  note = 'render row; the final deck is byte-identical to the eight delivered card-K01..K08.png'
}

Add-Row @{
  type = 'visual'; category = 'view'; stage = 'view-r05'
  target = 'render-v5-deck-final'
  action = 'opened the eight final render-v5 PNGs one at a time with the real image tool'
  finding = 'the image channel re-served stale frames on repeated opens, so every frame was matched against the expected content of the file that had been opened; mismatched frames were rejected, the file was re-opened, and unique-path copies were made where the channel stayed stuck. Confirmed on the delivered bytes: four status pills with colour + symbol + text, the planned title breaks, the bottom-anchored footer with the date on the speaker row, and the cancellation note on the time row'
  outcome = 'all eight finals confirmed visually; no clipping, no overlap, no missing glyph, title never touches the status pill'
  request_id = $nullReq
  started_at = '2026-10-03T10:08:10.205Z'; ended_at = '2026-10-03T10:33:58.929Z'
  duration_ms = $nullMs
  view_window = 'after render round 5 ended 2026-10-03T10:08:10.205Z, before the verifier was finished 2026-10-03T10:33:58.929Z'
  images_viewed = $eight
  evidence = "$rel/render-v5-card-K01.png .. render-v5-card-K08.png; $rel/inspect-A14-K04-final.png; $rel/inspect-A14-K08-final.png"
  note = 'started_at / ended_at bound the session; individual open times were not captured. See batch-audit.json image_views for the per-card record'
}

Add-Row @{
  type = 'baseline'; category = 'verification'; stage = 'independent-qa'
  target = 'independent-visual-qa'
  action = 'an independent QA agent opened all eight delivered final PNGs one at a time and reported the exact title lines, time, speaker, status pill colour + symbol + text, date row and any defect'
  finding = '8 of 8 match the required text; no clipping, no overlap, no missing glyph, title never touches the pill; measured content bounding box (40,40)-(1158,589) confirms the 40px safe margin on all four edges'
  outcome = 'all eight passed an inspection independent of the generator'
  request_id = 'session ses_efebc9497ffe0pb21lQxrPA8I7'
  started_at = $nullReq; ended_at = $nullReq; duration_ms = $nullMs
  view_window = 'after render round 5 ended 2026-10-03T10:08:10.205Z, before 2026-10-03T10:33:58.929Z'
  images_viewed = $eight
  evidence = 'outputs/' + $RUN + '/A14/batch-audit.json (image_viewing.independent_qa)'
  note = 'the sub-agent reported the number of attempts each file needed before its own artwork appeared, which is how the stale-frame issue was bounded'
}

# ------------------------------------------------------------------ verifier --
Add-Row @{
  type = 'syntax-fix'; category = 'verification'; stage = 'verify-v1'
  target = 'verify.ps1-first-run'
  action = 'ran the batch auditor over the eight delivered files'
  finding = 'reported 8 failures that were bugs in the verifier, not in the artwork: the rectangle test evaluated NOT(both axes separated) instead of NOT(either axis separated), and the title/badge test compared the title box against the pill top edge instead of testing overlap'
  outcome = 'replaced with the same overlap-width test the generator already uses; no artwork was changed'
  request_id = $nullReq; started_at = $nullReq; ended_at = $nullReq; duration_ms = $nullMs
  view_window = $nullReq
  images_viewed = $zero
  evidence = "$rel/verify.ps1"
  note = 'local script fix, no service request'
}

Add-Row @{
  type = 'baseline'; category = 'verification'; stage = 'verify-v2'
  target = 'batch-audit'
  action = 're-ran the batch auditor'
  finding = '8 of 8 cards PASS, 24 checks each: real PNG 1200x630, HTTP 200 service response, BOM-free .snapshot with no Image and no Transform, title/speaker/time/status verbatim from inputs/cards.json, title >= 36px and <= 3 rows, speaker >= 22px and <= 2 rows, all text boxes inside the 40px safe margin and mutually disjoint, status encoding carrying colour + symbol + text with a matching divider head, cancellation card keeping its full title and time plus the cancellation note'
  outcome = 'batch-audit.json written with all_pass = true'
  request_id = $nullReq; started_at = $nullReq; ended_at = $nullReq; duration_ms = $nullMs
  view_window = $nullReq
  images_viewed = $zero
  evidence = 'outputs/' + $RUN + '/A14/batch-audit.json'
  note = 'derived check over already-rendered bytes; no new service request'
}

# ------------------------------------------------------------------- emit ----
$sb = New-Object System.Text.StringBuilder
foreach ($r in $rows) {
  $j = $r | ConvertTo-Json -Depth 6 -Compress
  $j = $j -replace '\\u003c', '<' -replace '\\u003c', '<' -replace '\\u003e', '>' -replace '\\u0026', '&'
  [void]$sb.AppendLine($j)
}
[IO.File]::WriteAllText($outPath, $sb.ToString(), $UTF8)

Write-Output ("iterations.jsonl written: {0} rows, {1} bytes" -f $rows.Count, (Get-Item $outPath).Length)
$byType = $rows | Group-Object type | Sort-Object Name
foreach ($g in $byType) { Write-Output ("  {0,-16} {1}" -f $g.Name, $g.Count) }
$sumView = ($rows | Measure-Object -Property images_viewed -Sum).Sum
Write-Output ("  images_viewed total = {0}" -f $sumView)
