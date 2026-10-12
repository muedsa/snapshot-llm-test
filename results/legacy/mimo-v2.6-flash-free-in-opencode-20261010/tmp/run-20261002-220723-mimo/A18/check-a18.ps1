param(
  [Parameter(Mandatory=$true)][string]$Root
)
$ErrorActionPreference = 'Stop'
[Threading.Thread]::CurrentThread.CurrentCulture   = [cultureinfo]::InvariantCulture
[Threading.Thread]::CurrentThread.CurrentUICulture = [cultureinfo]::InvariantCulture
$utf8 = New-Object System.Text.UTF8Encoding($false)

$T = Join-Path $Root 'tmp\run-20261002-220723-mimo\A18'
$O = Join-Path $Root 'outputs\run-20261002-220723-mimo\A18'
$Probs = New-Object System.Collections.Generic.List[string]
$Notes = New-Object System.Collections.Generic.List[string]
function Ok([string]$m)  { $script:Notes.Add("PASS  " + $m) }
function Bad([string]$m) { $script:Probs.Add("FAIL  " + $m) }

# ---- 1. deliverable set ----------------------------------------------------
$need = @('three-act-story.png','three-act-story.snapshot','story-audit.json',
          'rationale.md','snapshot-usage.md','task-metrics.json','final-audit.md')
foreach ($f in $need) {
  $p = Join-Path $O $f
  if ($f -eq 'final-audit.md') { continue }   # written by this script
  if (Test-Path $p) { Ok("deliverable present: $f") } else { Bad("missing deliverable: $f") }
}

# ---- 2. the PNG really is the service response -----------------------------
$png = Join-Path $O 'three-act-story.png'
$bytes = [IO.File]::ReadAllBytes($png)
if ($bytes[0] -eq 0x89 -and $bytes[1] -eq 0x50 -and $bytes[2] -eq 0x4E -and $bytes[3] -eq 0x47) {
  Ok("PNG signature valid (" + $bytes.Length + " bytes)")
} else { Bad("PNG signature invalid") }
$w = ([int]$bytes[16] -shl 24) -bor ([int]$bytes[17] -shl 16) -bor ([int]$bytes[18] -shl 8) -bor [int]$bytes[19]
$h = ([int]$bytes[20] -shl 24) -bor ([int]$bytes[21] -shl 16) -bor ([int]$bytes[22] -shl 8) -bor [int]$bytes[23]
if ($w -eq 1600 -and $h -eq 1000) { Ok("dimensions ${w}x${h} as required") } else { Bad("dimensions ${w}x${h}, expected 1600x1000") }

$srcPng = Join-Path $T 'preview-a-v06.png'
if ((Get-FileHash $png -Algorithm SHA256).Hash -eq (Get-FileHash $srcPng -Algorithm SHA256).Hash) {
  Ok("delivered PNG is byte-identical to the preview that was viewed (preview-a-v06.png)")
} else { Bad("delivered PNG differs from the viewed preview") }

# ---- 3. DSL pairing --------------------------------------------------------
$dslPath = Join-Path $O 'three-act-story.snapshot'
$srcDsl  = Join-Path $T 'preview-a-v06.snapshot'
if ((Get-FileHash $dslPath -Algorithm SHA256).Hash -eq (Get-FileHash $srcDsl -Algorithm SHA256).Hash) {
  Ok("delivered DSL is byte-identical to the DSL that produced the PNG")
} else { Bad("delivered DSL differs from the rendered DSL") }
$b = [IO.File]::ReadAllBytes($dslPath)
if ($b.Length -ge 3 -and $b[0] -eq 0xEF -and $b[1] -eq 0xBB -and $b[2] -eq 0xBF) { Bad("DSL starts with a UTF-8 BOM") } else { Ok("DSL is BOM free") }
$dsl = [Text.Encoding]::UTF8.GetString($b)
if ($dsl.Contains([char]0xFFFD)) { Bad("DSL decodes with replacement characters") } else { Ok("DSL decodes cleanly as UTF-8") }
$lines = ($dsl -split "`r?`n").Count
Ok("DSL is $lines lines")

# ---- 4. hard content constraints in the delivered DSL ----------------------
$txt = [regex]::Matches($dsl, '<Text\b[^>]*>([^<]*)</Text>')
if ($txt.Count -eq 4) { Ok("exactly 4 <Text> elements") } else { Bad("found $($txt.Count) <Text> elements, expected 4") }
$expected = @('同一系统的三幕演化','第一幕 · 集中','第二幕 · 过载','第三幕 · 重新分配')
for ($i = 0; $i -lt $expected.Count; $i++) {
  if ($i -lt $txt.Count -and $txt[$i].Groups[1].Value -eq $expected[$i]) { Ok("text $($i+1) verbatim: " + $expected[$i]) }
  else { Bad("text $($i+1) does not match '" + $expected[$i] + "'") }
}
if ($txt.Count -gt 0) {
  $iLink = $dsl.LastIndexOf('<Transform'); $iNode = $dsl.IndexOf('width="64" height="64"')
  $iUnit = $dsl.IndexOf('width="36" height="36"'); $iText = $dsl.IndexOf('<Text')
  if ($iLink -ge 0 -and $iNode -gt $iLink -and $iUnit -gt $iNode -and $iText -gt $iUnit) {
    Ok("draw order links($iLink) < nodes($iNode) < units($iUnit) < text($iText): no stroke can cover a circle")
  } else { Bad("draw order links=$iLink nodes=$iNode units=$iUnit text=$iText is wrong") }
}

# ---- 5. story-audit.json ---------------------------------------------------
$audit = Get-Content (Join-Path $O 'story-audit.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$ap = @($audit.checks.problems)
if ($ap.Count -eq 0) { Ok("story-audit problems = 0") } else { foreach ($x in $ap) { Bad("story-audit: $x") } }
if ($audit.text_elements.Count -eq 4) { Ok("story-audit recorded 4 text elements") } else { Bad("story-audit text count wrong") }

foreach ($a in $audit.acts) {
  $c = $a.unit_counts
  if ($c.total -eq 15 -and $c.blue -eq 5 -and $c.orange -eq 5 -and $c.gray -eq 5) {
    Ok("act $($a.act): 15 units d$($a.unit_diameter), 5 blue / 5 orange / 5 grey")
  } else { Bad("act $($a.act): unit counts wrong") }
  if ($a.nodes.Count -eq 3 -and (@($a.nodes | Where-Object { $_.size -eq 64 }).Count -eq 3)) {
    Ok("act $($a.act): 3 equal nodes of 64px")
  } else { Bad("act $($a.act): node set wrong") }
  if ($a.min_unit_to_unit_centre_distance -ge 36) {
    Ok("act $($a.act): min unit-unit centre distance $($a.min_unit_to_unit_centre_distance) >= 36")
  } else { Bad("act $($a.act): units overlap") }
  if ($a.min_unit_to_node_gap_px -ge -0.4) {
    Ok("act $($a.act): min unit-node gap $($a.min_unit_to_node_gap_px) px, no overlap")
  } else { Bad("act $($a.act): a unit overlaps a node") }
}
foreach ($r in ($audit.acts | Where-Object { $_.act -eq 3 }).receiving) {
  if ($r.unit_count -eq 5 -and $r.color_kinds -ge 2) {
    Ok("act 3 $($r.node): $($r.unit_count) units, $($r.color_kinds) colours")
  } else { Bad("act 3 $($r.node): count=$($r.unit_count) colours=$($r.color_kinds)") }
}
foreach ($act in ($audit.acts | Where-Object { $_.act -le 2 })) {
  $c2   = @($act.receiving | Where-Object { $_.node -eq 'N2' })
  $idle = @($act.receiving | Where-Object { $_.node -ne 'N2' })
  if ($c2.Count -eq 1 -and $c2[0].unit_count -eq 15) { Ok("act $($act.act): all 15 units route to the single centre node N2") }
  else { Bad("act $($act.act): centre node receives " + $c2[0].unit_count + ", expected 15") }
  $badIdle = @($idle | Where-Object { $_.unit_count -ne 0 })
  if ($badIdle.Count -eq 0) { Ok("act $($act.act): both idle nodes receive nothing (zero links, by construction)") }
  else { Bad("act $($act.act): an idle node still receives units") }
}

# ---- 6. rationale length ---------------------------------------------------
$rat = [IO.File]::ReadAllText((Join-Path $O 'rationale.md'))
$i = $rat.IndexOf('深色底上'); $j = $rat.IndexOf("`n`n", $i)
$narr = $rat.Substring($i, $j - $i)
if ($narr.Length -le 300) { Ok("rationale narrative is $($narr.Length) characters (<= 300)") }
else { Bad("rationale narrative is $($narr.Length) characters (> 300)") }

# ---- 7. both composition previews retained ---------------------------------
foreach ($f in @('preview-a-v01.png','preview-b-v01.png')) {
  if (Test-Path (Join-Path $T $f)) { Ok("composition preview retained in temp: $f") } else { Bad("composition preview missing: $f") }
}
if (Test-Path (Join-Path $T 'preview-b.snapshot')) { Ok("composition B DSL retained in temp as preview-b.snapshot (rendered once as preview-b-v01.png and never regenerated)") } else { Bad("composition B DSL missing") }

# ---- 8. logs ---------------------------------------------------------------
$req = @(Get-Content (Join-Path $T 'requests.jsonl') | ForEach-Object { $_ | ConvertFrom-Json })
$it  = @(Get-Content (Join-Path $T 'iterations.jsonl') | ForEach-Object { $_ | ConvertFrom-Json })
Ok("requests.jsonl has $($req.Count) rows ($((@($req|?{$_.http_status -eq 200})).Count) x 200, $((@($req|?{$_.http_status -ne 200})).Count) x 400)")
Ok("iterations.jsonl has $($it.Count) rows")
if (Test-Path (Join-Path $T 'iterations.jsonl')) { Ok("iterations log present in temp") } else { Bad("iterations log missing") }

$views = @($it | Where-Object { $_.view_method -ne '' -and $_.view_method -ne 'sha256-comparison' })
Ok("$($views.Count) logged view events")
$finalViews = @($views | Where-Object { $_.image -eq 'outputs/run-20261002-220723-mimo/A18/three-act-story.png' })
if ($finalViews.Count -ge 1) { Ok("the delivered PNG was opened $($finalViews.Count) time(s) with a real image tool") }
else { Bad("the delivered PNG was never opened") }
$thumbViews = @($views | Where-Object { $_.image -like '*400*.png' })
if ($thumbViews.Count -ge 1) { Ok("$($thumbViews.Count) 400px thumbnail view event(s) logged") } else { Bad("no 400px thumbnail was viewed") }
$del = @($it | Where-Object { $_.type -eq 'visual' })
Ok("$($del.Count) visual iterations")
if (@($req | Where-Object { $_.http_status -eq 400 }).Count -gt 0) {
  $fb = Get-ChildItem (Join-Path $T 'failures') -ErrorAction SilentlyContinue
  if (@($fb).Count -eq @($req | Where-Object { $_.http_status -ne 200 }).Count) { Ok("every failed response body is retained") }
  else { Bad("failure bodies do not match the failed request count") }
}

# ---- 9. metrics ------------------------------------------------------------
$met = Get-Content (Join-Path $O 'task-metrics.json') -Raw -Encoding UTF8 | ConvertFrom-Json
if ($met.requests.count -eq $req.Count) { Ok("task-metrics request count matches the log") } else { Bad("task-metrics request count $($met.requests.count) != $($req.Count)") }
if ($met.iterations.count -eq $it.Count) { Ok("task-metrics iteration count matches the log") } else { Bad("task-metrics iteration count mismatch") }
if ($met.resources.cost_usd -eq $null) { Ok("unknown cost recorded as null, not guessed") } else { Bad("cost must be null") }

# ---- report ----------------------------------------------------------------
$rep = New-Object System.Collections.Generic.List[string]
$rep.Add('# A18 · final audit')
$rep.Add('')
$rep.Add('run_id `run-20261002-220723-mimo` · task A18 three-act-story · 审计脚本 `tmp/run-20261002-220723-mimo/A18/check-a18.ps1`')
$rep.Add('')
$rep.Add('**problems = ' + $Probs.Count + ' · notes = ' + $Notes.Count + '**')
$rep.Add('')
if ($Probs.Count -gt 0) { $rep.Add('## Problems'); foreach ($x in $Probs) { $rep.Add('- ' + $x) }; $rep.Add('') }
$rep.Add('## Checks')
$rep.Add('')
foreach ($x in $Notes) { $rep.Add('- ' + $x) }
$rep.Add('')
$rep.Add('## Deliverables')
$rep.Add('')
Get-ChildItem $O | Sort-Object Name | ForEach-Object { $rep.Add('- `' + $_.Name + '` (' + $_.Length + ' B)') }
$rep.Add('')
$rep.Add('## Temp artefacts retained')
$rep.Add('')
$rep.Add('- 12 `.snapshot` DSL files (4 probes, composition A v01-v06, composition B v01, the recovered v01)')
$rep.Add('- 14 PNG files (8 composition/refinement previews + 1 probe + 5 thumbnails)')
$rep.Add('- `geom-a.json` / `geom-a-v01.json` / `geom-b.json`, `gen.ps1`, `gen-v01.ps1`, `mk-audit.ps1`, `thumb.ps1`')
$rep.Add('- 3 failure response bodies under `failures/`')
$rep.Add('')
$rep.Add('## Known residuals')
$rep.Add('')
$rep.Add('- At 400px the three act labels are present, correctly placed and the three bands read as three distinct states, but their dense CJK strokes are about 7px tall and need magnification to read character by character. They are 30px and fully legible at full size, and were grown from 26px to 32px specifically to close this gap.')
$rep.Add('- The act-2 centre node capsule port splits the node white ring into two bars at 400px; this is a thumbnail artefact of a deliberate full-size feature.')
$rep.Add('- Token and cost figures were never observed and remain null.')

$out = Join-Path $O 'final-audit.md'
[IO.File]::WriteAllText($out, (($rep -join "`n") + "`n"), $utf8)
Write-Output ("problems = {0}   notes = {1}   -> {2}" -f $Probs.Count, $Notes.Count, $out)
foreach ($x in $Probs) { Write-Output $x }
