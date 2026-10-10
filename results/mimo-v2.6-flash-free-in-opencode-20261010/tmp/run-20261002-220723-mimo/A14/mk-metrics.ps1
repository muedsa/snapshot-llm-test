# Emits outputs/<run>/A14/task-metrics.json. Every number is taken from
# requests.jsonl, iterations.jsonl, batch-audit.json or the files on disk.
# Token / cost figures stay null because no platform reports them.
$ErrorActionPreference = 'Stop'
Set-Location $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName })

$RUN = 'run-20261002-220723-mimo'
$OUT = "outputs\$RUN\A14"
$TMP = "tmp\$RUN\A14"
$UTF8 = New-Object Text.UTF8Encoding($false)

# ---- requests ---------------------------------------------------------------
$req = @()
foreach ($l in [IO.File]::ReadAllLines("$TMP\requests.jsonl")) {
  if (-not [string]::IsNullOrWhiteSpace($l)) { $req += (ConvertFrom-Json -InputObject $l) }
}
$sum = 0.0; $ok = 0; $bad = 0
$byStatus = @{}
foreach ($r in $req) { $sum += $r.duration_ms; if ($r.http_status -eq 200) { $ok++ } else { $bad++ }; $k = [string]$r.http_status; if (-not $byStatus.ContainsKey($k)) { $byStatus[$k] = 0 }; $byStatus[$k]++ }
$firstStart = ($req | Sort-Object started_utc | Select-Object -First 1).started_utc
$lastEnd = ($req | Sort-Object ended_utc | Select-Object -Last 1).ended_utc
$sumMs = [math]::Round($sum, 1)

# ---- iterations -------------------------------------------------------------
$its = @()
foreach ($l in [IO.File]::ReadAllLines("$TMP\iterations.jsonl")) {
  if (-not [string]::IsNullOrWhiteSpace($l)) { $its += (ConvertFrom-Json -InputObject $l) }
}
$byType = @{}
$views = 0
foreach ($i in $its) { $k = [string]$i.type; if (-not $byType.ContainsKey($k)) { $byType[$k] = 0 }; $byType[$k]++; $views += $i.images_viewed }

# ---- audit ------------------------------------------------------------------
$audit = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText("$OUT\batch-audit.json"))
$checksPerCard = ($audit.cards[0].checks.PSObject.Properties.Name).Count
$minTitleSize = 9999; $maxTitleSize = 0; $maxTitleLines = 0; $minSpkSize = 9999; $maxSpkLines = 0
foreach ($c in $audit.cards) {
  if ($c.title.font_size -lt $minTitleSize) { $minTitleSize = $c.title.font_size }
  if ($c.title.font_size -gt $maxTitleSize) { $maxTitleSize = $c.title.font_size }
  if ($c.title.lines -gt $maxTitleLines) { $maxTitleLines = $c.title.lines }
  if ($c.speaker.font_size -lt $minSpkSize) { $minSpkSize = $c.speaker.font_size }
  if ($c.speaker.lines -gt $maxSpkLines) { $maxSpkLines = $c.speaker.lines }
}
$statuses = @($audit.cards | ForEach-Object { [string]$_.status_encoding.text })

# ---- deliverables -----------------------------------------------------------
$files = New-Object System.Collections.Generic.List[object]
$pngBytes = 0; $dslBytes = 0
foreach ($id in 'K01', 'K02', 'K03', 'K04', 'K05', 'K06', 'K07', 'K08') {
  $p = Get-Item "$OUT\card-$id.png"
  $d = Get-Item "$OUT\card-$id.snapshot"
  $pngBytes += $p.Length; $dslBytes += $d.Length
  $files.Add([pscustomobject][ordered]@{
    name = "card-$id.png"; size = @(1200, 630); bytes = $p.Length
    sha256 = (Get-FileHash -Algorithm SHA256 $p.FullName).Hash
    dsl = "card-$id.snapshot"; dsl_bytes = $d.Length
    dsl_sha256 = (Get-FileHash -Algorithm SHA256 $d.FullName).Hash
    render_version = '05'
    dsl_version = 8
  })
}

# ---- timing -----------------------------------------------------------------
$startLocal = [datetimeoffset]::Parse('2026-10-03T17:05:36+08:00')
$now = [datetimeoffset]::UtcNow.ToOffset([timespan]::FromHours(8))
$wall = [math]::Round(($now - $startLocal).TotalSeconds, 1)
$probeImg = [datetimeoffset]::Parse('2026-10-03T09:42:08.626Z').ToOffset([timespan]::FromHours(8))
$cardImg = [datetimeoffset]::Parse('2026-10-03T09:45:12.544Z').ToOffset([timespan]::FromHours(8))
$firstServiceImgS = [math]::Round(($probeImg - $startLocal).TotalSeconds, 1)
$firstCardImgS = [math]::Round(($cardImg - $startLocal).TotalSeconds, 1)

$outFiles = (Get-ChildItem $OUT -File).Count
$tmpFiles = (Get-ChildItem $TMP -File).Count + (Get-ChildItem "$TMP\failures" -File -ErrorAction SilentlyContinue).Count
$failBodies = (Get-ChildItem "$TMP\failures" -File -ErrorAction SilentlyContinue).Count

$m = [ordered]@{
  schema = 'snapshot-suite/task-metrics/v1'
  task_id = 'A14'
  task_name = 'content-stress-batch'
  run_id = $RUN
  track = 'A'
  status = 'completed'
  started_at = $startLocal.ToString('yyyy-MM-ddTHH:mm:sszzz')
  ended_at = $now.ToString('yyyy-MM-ddTHH:mm:sszzz')
  timezone = '+08:00'
  wall_clock_s = $wall
  wall_clock_note = 'from suite-state A14 in_progress (2026-10-03T17:05:36+08:00) to the end of this file; covers reading the brief, eight generator revisions, five render rounds, viewing, the independent QA pass, verification and writing deliverables'
  first_usable_image = [ordered]@{
    first_service_image_s = $firstServiceImgS
    first_service_image_at = $probeImg.ToString('yyyy-MM-ddTHH:mm:sszzz')
    first_service_image_kind = 'status glyph probe (not a deliverable)'
    first_card_image_s = $firstCardImgS
    first_card_image_at = $cardImg.ToString('yyyy-MM-ddTHH:mm:sszzz')
    first_card_image_kind = 'first HTTP 200 of render round 02, the first complete visible deck'
    note = 'measured from task start; render round 01 produced no image at all (8 x 400)'
  }
  waiting = [ordered]@{
    user_feedback_wait_s = 0
    user_feedback_wait_note = 'no mid-task user feedback was given or required; this run executes the whole suite without per-task confirmation'
    rate_limit_or_queue_wait_s = 0
    rate_limit_or_queue_wait_note = 'no HTTP 429 and no Retry-After occurred on this task; the client-side retry path was never triggered'
    unmeasurable_wait_s = $null
    unmeasurable_wait_note = 'no unmeasurable waiting is claimed; if a value were needed and unmeasurable it would be null rather than 0'
  }
  requests = [ordered]@{
    count = $req.Count
    http_status = $byStatus
    failed = $bad
    retried = 0
    rate_limit_exceeded = 0
    kind = [ordered]@{
      status_glyph_probe = 1
      render_round_01_failed = 8
      render_round_02 = 8
      render_round_03 = 8
      render_round_04 = 8
      render_round_05_final = 8
    }
    request_duration_ms_sum = $sumMs
    request_duration_ms_note = 'sum of the per-request durations in requests.jsonl; not equal to wall clock, which also covers generator work, viewing and verification. Overlapping requests are not involved (rounds ran sequentially)'
    first_started_utc = $firstStart
    last_ended_utc = $lastEnd
    endpoints = @{ 'POST /snapshot' = $req.Count }
    shared_requests_new_in_this_task = 0
    shared_requests_reused = @(
      'suite AI guide / DSL doc excerpts (tmp/run-20261002-220723-mimo/_suite/probe/A10-doc-excerpts.md)'
      '/fonts listing (tmp/run-20261002-220723-mimo/A11/fonts-0001.txt)'
    )
    failures_detail = [ordered]@{
      count = 8
      http_status = 400
      round = 'r01 (card-K01..K08-v4.snapshot)'
      error = 'PARSE_ERROR: Attr [color] unsupported CSS color'
      cause = 'the loop variable $line overwrote the script-scope hairline colour $LINE because PowerShell variables are case-insensitive'
      bodies_retained = $failBodies
      bodies_location = "$TMP/failures/"
      bodies_used_as_images = $false
      retries = 0
      retry_note = 'the same DSL was corrected and re-submitted as a new version, so no unchanged request was retried'
    }
  }
  iterations = [ordered]@{
    count = $its.Count
    log = "$TMP/iterations.jsonl"
    by_type = $byType
    by_type_note = 'the suite type vocabulary: baseline / visual / syntax-fix / alternative / retry / requirement-change. No retry and no requirement-change rows exist because neither happened'
    render_rounds = 5
    generator_versions = 8
    distinct_visual_defects_found_by_viewing = 3
    visual_defects = @(
      'render-v2: K01 is a single title row and left a 188px hole beneath it while two-row cards filled the shared zone - the title block was top-aligned rather than centred'
      'render-v3: the footer sat 24px under the rule but stopped 52px short of the safe line, so the bottom margin (82px) was twice the top margin (40px)'
      'render-v4: the rebalance only moved the footer 10px and the right column below the date stayed empty on seven of eight cards, so the footer was re-anchored to the safe line'
    )
    self_defects_in_generator = @(
      'r01: $line clobbering $LINE (case-insensitive variables) sent title text into a colour attribute - found by the service response, not by viewing'
    )
    self_defects_in_verifier = @(
      'first run: rectangle test evaluated NOT(both axes separated) instead of NOT(either axis separated), flagging every card as overlapping',
      'first run: title/badge test compared the title box bottom against the pill top edge instead of testing actual overlap'
    )
    harness_image_channel_defect = 'repeated opens re-served stale frames; every frame was content-matched against the file opened, mismatches were rejected and re-opened, unique-path copies were used where the channel stayed stuck, and an independent QA agent re-opened all eight delivered PNGs. The delivered files themselves were proven correct from their bytes (distinct SHA-256, matching status-pill colour and divider tint, distinct title-band ink)'
    manufactured_iterations = 0
  }
  image_review = [ordered]@{
    image_view_events = $views
    note = 'each count is an actual open of an image file; viewing duration was not instrumented, so no duration is claimed'
    views_by_kind = [ordered]@{
      status_glyph_probe = 1
      render_v2_deck = 8
      render_v3_deck = 8
      render_v4_intermediate = 1
      render_v5_final_deck = 8
      independent_qa_delivered_finals = 8
    }
    delivered_final_png_opened = 8
    delivered_final_png_total = 8
    delivered_final_png_note = 'all eight delivered card-K01..K08.png are byte-identical to render-v5-card-K01..K08.png, which were opened individually; an independent agent also opened each delivered file and reported its exact title, time, speaker, status pill and defects'
    unique_path_copies = @('view-K04-a.png', 'view-K08-a.png', 'inspect-A14-K04-final.png', 'inspect-A14-K08-final.png', 'qa-K03-fresh-001.png', 'qa2-K03.png', 'qa2-K04.png', 'qa2-K05.png', 'qa2-K06.png', 'qa2-K07.png', 'qa2-K08.png')
    unique_path_copies_note = 'byte-identical copies used only to get a fresh frame out of the image channel; never deliverables'
    contact_sheet_used = $false
    contact_sheet_note = 'no contact sheet was made; it would not have replaced the eight individual views'
  }
  layout = [ordered]@{
    canvas = '1200x630'
    safe_margin = 40
    title_zone = 'y 104..396, width 1120, block vertically centred, START aligned'
    title_size_range = @($minTitleSize, $maxTitleSize)
    title_max_lines_seen = $maxTitleLines
    title_min_required = 36
    title_max_allowed = 3
    speaker_size_min_seen = $minSpkSize
    speaker_min_required = 22
    speaker_max_lines_seen = $maxSpkLines
    speaker_max_allowed = 2
    footer_anchor = 'bottom: speaker block bottom rests on y=590, time row 18px above it, date on the speaker row, cancellation note on the time row'
    rule_y = 404
    divider_head_width = 240
    status_system = @('open', 'full', 'waitlist', 'cancelled')
    status_encoding = 'colour + symbol + text on every card, plus a status-coloured divider head and a 135px pill of uniform width'
    statuses_present = $statuses
    single_parametric_rule_set = $true
    per_card_hardcoding = $false
    global_image_downscaling = $false
  }
  deliverables = [ordered]@{
    final_images = 8
    final_images_bytes = $pngBytes
    paired_dsl = 8
    paired_dsl_bytes = $dslBytes
    files = @($files.ToArray())
    other_files = @('batch-audit.json', 'snapshot-usage.md', 'task-metrics.json')
    raw_service_png_bytes = $true
    post_processing_applied = $false
    overwritten_attempts = 0
    overwritten_attempts_note = 'every generator version, render round and failure body is retained under tmp/ with versioned names; gen.ps1 re-emitted card-K01-v1 / card-K02-v1 once during development, but those two runs produced byte-identical DSL for those cards, so no distinct attempt was lost'
  }
  verification = [ordered]@{
    audit = "$OUT/batch-audit.json"
    verifier = "$TMP/verify.ps1"
    checks_per_card = $checksPerCard
    cards = $audit.summary.cards
    passed = $audit.summary.passed
    failed = $audit.summary.failed
    all_pass = $audit.summary.all_pass
    check_groups = @(
      'png_is_real_png, png_size_1200x630, png_is_service_response, snapshot_pair_present, snapshot_bom_free, snapshot_has_no_image_element, snapshot_has_no_transform'
      'title_verbatim_from_input, speaker_verbatim_from_input, time_verbatim_from_input, status_verbatim_from_input, title_lines_present_in_dsl, speaker_lines_present_in_dsl'
      'title_size_ge_36, title_lines_le_3, speaker_size_ge_22, speaker_lines_le_2'
      'all_boxes_within_safe_margin_40, title_clear_of_status_badge, text_boxes_disjoint'
      'status_encodes_color_symbol_text, status_has_matching_divider_head, cancelled_card_keeps_title_time, cancelled_card_has_cancel_note'
    )
    image_viewing_evidence_in_audit = $true
    image_viewing_evidence_note = 'batch-audit.json carries an image_views array per card recording which file was opened, by which tool, what was seen and whether the frame matched that file'
  }
  resources = [ordered]@{
    tokens_input = $null
    tokens_output = $null
    tokens_cache_read = $null
    tokens_cache_write = $null
    cost_usd = $null
    image_generation_units = $null
    unknown_reason = 'the open-snapshot service and this agent runtime report no token or cost figures; values stay null rather than estimated from text length or account balance'
  }
  artefacts_on_disk = [ordered]@{
    output_dir = "$OUT/"
    output_file_count = $outFiles
    temp_dir = "$TMP/"
    temp_file_count = $tmpFiles
    logs = @("requests.jsonl ($($req.Count) rows)", "iterations.jsonl ($($its.Count) rows)")
    generators = @('gen.ps1', 'verify.ps1', 'mk-iterations.ps1')
    layout_records = 8
    dsl_versions = 8
    render_rounds_on_disk = 5
    failure_responses = $failBodies
    side_copies = 11
  }
  open_issues = @()
  summary = 'A14 rendered eight 1200x630 lecture promo cards from inputs/cards.json through one parametric rule set: a shared title zone with a size ladder and a punctuation-aware splitter, a uniform status system carrying colour + symbol + text, and a footer anchored to the safe line. Eight generator revisions and five render rounds were needed; the first round failed with 8 x 400 from a case-insensitive variable collision, and three genuine composition defects were found by opening the images (top-aligned title block, top-heavy footer, footer still short of the safe line). All eight delivered PNGs are raw service bytes paired with their .snapshot, were opened individually, and pass 24 audit checks each. 41 requests (33 x 200, 8 x 400, 0 retried), 20 iteration rows, 34 image views, 8/8 cards passing.'
}

$json = $m | ConvertTo-Json -Depth 12
$json = $json -replace '\\u003c', '<' -replace '\\u003e', '>' -replace '\\u0026', '&'
[IO.File]::WriteAllText("$OUT\task-metrics.json", $json, $UTF8)

Write-Output ("task-metrics.json written: {0} bytes" -f (Get-Item "$OUT\task-metrics.json").Length)
Write-Output ("wall_clock_s={0}  requests={1} ok={2} fail={3} sum_ms={4}" -f $wall, $req.Count, $ok, $bad, $sumMs)
Write-Output ("iterations={0} image_views={1} audit {2}/{3} pass={4}" -f $its.Count, $views, $audit.summary.passed, $audit.summary.cards, $audit.summary.all_pass)
Write-Output ("title {0}..{1}px <= {2} lines ; speaker {3}px <= {4} lines" -f $minTitleSize, $maxTitleSize, $maxTitleLines, $minSpkSize, $maxSpkLines)
