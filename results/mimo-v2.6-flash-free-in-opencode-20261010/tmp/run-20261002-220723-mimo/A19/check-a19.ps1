param(
  [Parameter(Mandatory=$true)][string]$OutDir,
  [Parameter(Mandatory=$true)][string]$TmpDir,
  [Parameter(Mandatory=$true)][string]$AuditMd
)
$ErrorActionPreference = 'Stop'
[Threading.Thread]::CurrentThread.CurrentCulture   = [cultureinfo]::InvariantCulture
[Threading.Thread]::CurrentThread.CurrentUICulture = [cultureinfo]::InvariantCulture
$utf8 = New-Object System.Text.UTF8Encoding($false)
Add-Type -AssemblyName System.Drawing

$prob = New-Object System.Collections.Generic.List[string]
$note = New-Object System.Collections.Generic.List[string]
function Bad([string]$m) { $script:prob.Add($m) }
function Good([string]$m) { $script:note.Add($m) }
function Chk([bool]$cond, [string]$okMsg, [string]$badMsg) { if ($cond) { Good $okMsg } else { Bad $badMsg } }

# ------------------------------------------------------------------ file facts ---
function PngSize([string]$p) {
  $b = New-Object System.Drawing.Bitmap($p)
  try { return ,@($b.Width, $b.Height) } finally { $b.Dispose() }
}
function Sha([string]$p) { return (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash }

# 1 - required deliverables all present
$required = @(
  'grid-scene.png','grid-scene.snapshot','occlusion.png','occlusion.snapshot',
  'occlusion-alternative.png','occlusion-alternative.snapshot','scene-data.json',
  'questions.json','answers.json','equivalence.json'
)
foreach ($f in $required) {
  Chk (Test-Path -LiteralPath (Join-Path $OutDir $f)) "present: $f" "MISSING deliverable: $f"
}

# 2 - every PNG is a real PNG of the specified size, paired with its .snapshot
$szGrid = PngSize (Join-Path $OutDir 'grid-scene.png')
$szOccA = PngSize (Join-Path $OutDir 'occlusion.png')
$szOccB = PngSize (Join-Path $OutDir 'occlusion-alternative.png')
Chk ($szGrid[0] -eq 1600 -and $szGrid[1] -eq 1600) "grid-scene.png is 1600x1600" ("grid-scene.png is " + $szGrid[0] + "x" + $szGrid[1] + ", expected 1600x1600")
Chk ($szOccA[0] -eq 800 -and $szOccA[1] -eq 800)  "occlusion.png is 800x800"    ("occlusion.png is " + $szOccA[0] + "x" + $szOccA[1])
Chk ($szOccB[0] -eq 800 -and $szOccB[1] -eq 800)  "occlusion-alternative.png is 800x800" ("occlusion-alternative.png is " + $szOccB[0] + "x" + $szOccB[1])

foreach ($stem in @('grid-scene','occlusion','occlusion-alternative')) {
  $png = Join-Path $OutDir ($stem + '.png')
  if (Test-Path -LiteralPath $png) {
    $fs = [IO.File]::OpenRead($png)
    try {
      $hdr = New-Object byte[] 8
      [void]$fs.Read($hdr, 0, 8)
      $sig = ($hdr | ForEach-Object { $_.ToString('X2') }) -join ' '
      Chk ($sig -eq '89 50 4E 47 0D 0A 1A 0A') "$stem.png carries the PNG magic bytes" "$stem.png is NOT a PNG (header $sig)"
    } finally { $fs.Dispose() }
  }
}

# 3 - the delivered bytes are the service responses (byte-identical to the rendered attempts)
$pairs = @(
  @('grid-scene.png','grid-v03.png'), @('grid-scene.snapshot','grid-v03.snapshot'),
  @('occlusion.png','occ-a-v02.png'), @('occlusion.snapshot','occ-a-v02.snapshot'),
  @('occlusion-alternative.png','occ-b-v02.png'), @('occlusion-alternative.snapshot','occ-b-v02.snapshot'),
  @('scene-data.json','scene-v03.json'), @('questions.json','questions-v03.json'), @('answers.json','answers-v03.json')
)
foreach ($p in $pairs) {
  $o = Join-Path $OutDir $p[0]; $t = Join-Path $TmpDir $p[1]
  if ((Test-Path -LiteralPath $o) -and (Test-Path -LiteralPath $t)) {
    Chk ((Sha $o) -eq (Sha $t)) ("delivered {0} == service/authoring original {1}" -f $p[0], $p[1]) ("MISMATCH: {0} differs from {1}" -f $p[0], $p[1])
  }
}

# 4 - DSL well-formedness and no external images
foreach ($stem in @('grid-scene','occlusion','occlusion-alternative')) {
  $d = Join-Path $OutDir ($stem + '.snapshot')
  if (-not (Test-Path -LiteralPath $d)) { continue }
  $txt = [IO.File]::ReadAllText($d)
  Chk ($txt.TrimStart().StartsWith('<Snapshot')) "$stem.snapshot rooted at <Snapshot" "$stem.snapshot does not start with <Snapshot"
  Chk ($txt.TrimEnd().EndsWith('</Snapshot>')) "$stem.snapshot closed with </Snapshot>" "$stem.snapshot not closed"
  Chk (-not ($txt -match '<Image[ >]')) "$stem.snapshot embeds no external <Image> (A-track pure DSL)" "$stem.snapshot contains an <Image> tag"
  Chk (-not ($txt -match '(?i)dashed|dasharray|opacity="0\.')) "$stem.snapshot has no dashed / semi-transparent leak construct" "$stem.snapshot contains a dashed or translucent construct"
}

# ---------------------------------------------------------------- scene checks ---
$scene = [IO.File]::ReadAllText((Join-Path $OutDir 'scene-data.json')) | ConvertFrom-Json
$OBJ = @($scene.objects)
Chk ($OBJ.Count -eq 64) "scene-data.json holds exactly 64 objects" ("scene-data.json holds " + $OBJ.Count + " objects")

$idsOk = $true
for ($i = 0; $i -lt $OBJ.Count; $i++) {
  $expect = 'G{0:D2}' -f ($i + 1)
  if ($OBJ[$i].id -ne $expect) { $idsOk = $false }
}
Chk $idsOk "IDs run G01..G64 left-to-right / top-to-bottom" "ID sequence is not G01..G64 row-major"

# one subject per cell
$cellBad = 0
$cellCount = @{}
foreach ($o in $OBJ) {
  $k = "$($o.row),$($o.col)"
  if ($cellCount.ContainsKey($k)) { $cellCount[$k] = 1 + $cellCount[$k] } else { $cellCount[$k] = 1 }
}
foreach ($k in @($cellCount.Keys)) { if ($cellCount[$k] -ne 1) { $cellBad++ } }
Chk ($cellCount.Count -eq 64 -and $cellBad -eq 0) "one and only one subject in each of the 64 cells" ("cell occupancy problems: " + $cellBad + " (distinct cells " + $cellCount.Count + ")")

# colour / shape / size counts
$cBy = @{}; $sBy = @{}; $zBy = @{}
foreach ($o in $OBJ) {
  $cBy[$o.color] = 1 + $cBy[$o.color]
  $sBy[$o.shape] = 1 + $sBy[$o.shape]
  $zBy[[string]$o.size] = 1 + $zBy[[string]$o.size]
}
$colourOk = ($cBy.Count -eq 4); foreach ($k in @($cBy.Keys)) { if ($cBy[$k] -ne 16) { $colourOk = $false } }
$shapeOk  = ($sBy.Count -eq 4); foreach ($k in @($sBy.Keys)) { if ($sBy[$k] -ne 16) { $shapeOk = $false } }
Chk $colourOk ("each of the 4 colours occurs exactly 16 times (" + (($cBy.GetEnumerator() | ForEach-Object { "$($_.Name)=$($_.Value)" }) -join ' ') + ")") "colour totals are not 16/16/16/16"
Chk $shapeOk  ("each of the 4 shapes occurs exactly 16 times (" + (($sBy.GetEnumerator() | ForEach-Object { "$($_.Name)=$($_.Value)" }) -join ' ') + ")") "shape totals are not 16/16/16/16"
Chk ($zBy.Count -eq 3 -and $zBy.ContainsKey('48') -and $zBy.ContainsKey('64') -and $zBy.ContainsKey('80')) "only the sizes 48/64/80 occur (" + (($zBy.GetEnumerator() | ForEach-Object { "$($_.Name)=$($_.Value)" }) -join ' ') + ")" "unexpected size set"

# row spread >= 3 colours and >= 3 shapes
$minC = 99; $minS = 99; $badRows = 0
for ($r = 0; $r -lt 8; $r++) {
  $rc = @{}; $rs = @{}
  foreach ($o in ($OBJ | Where-Object { $_.row -eq $r })) { $rc[$o.color] = 1; $rs[$o.shape] = 1 }
  if ($rc.Count -lt 3) { $badRows++ }
  if ($rs.Count -lt 3) { $badRows++ }
  if ($rc.Count -lt $minC) { $minC = $rc.Count }
  if ($rs.Count -lt $minS) { $minS = $rs.Count }
}
Chk ($badRows -eq 0) ("every row has >= 3 distinct colours (min $minC) and >= 3 distinct shapes (min $minS)") ("$badRows row-level colour/shape spread violations")

# ring geometry: inner = outer / 2
$ringBad = 0
foreach ($o in ($OBJ | Where-Object { $_.shape -eq 'ring' })) {
  if ([double]$o.ring_inner -ne ([double]$o.size / 2)) { $ringBad++ }
}
Chk ($ringBad -eq 0 -and $minS -gt 0) "every ring has inner diameter = outer/2" ("$ringBad rings violate inner = outer/2")

# ID label outside the subject bbox
$labBad = 0
foreach ($o in $OBJ) {
  $lx0 = [double]$o.id_label_x; $ly0 = [double]$o.id_label_y
  $lx1 = $lx0 + 64; $ly1 = $ly0 + 24
  if ($lx1 -gt [double]$o.bbox_x0 -and $ly1 -gt [double]$o.bbox_y0 -and $lx0 -lt [double]$o.bbox_x1 -and $ly0 -lt [double]$o.bbox_y1) { $labBad++ }
}
Chk ($labBad -eq 0) "all 64 ID labels lie outside their subject bounding box" ("$labBad ID labels overlap their subject")

# ---------------------------------------------------------------- question files --
# NOTE: $q/$Q and $a/$A are the SAME variable in PowerShell (case-insensitive).
# The parsed documents are therefore held in $QDoc/$ADoc, and $Q/$A are the arrays.
$QDoc = [IO.File]::ReadAllText((Join-Path $OutDir 'questions.json')) | ConvertFrom-Json
$ADoc = [IO.File]::ReadAllText((Join-Path $OutDir 'answers.json')) | ConvertFrom-Json
$Q = @($QDoc.questions); $A = @($ADoc.answers)
Chk ($Q.Count -eq 14) ("questions.json holds 14 questions (12 grid + 2 occlusion)") ("questions.json holds " + $Q.Count)
Chk (@($Q | Where-Object { $_.scene -eq 'grid-scene' }).Count -eq 12) "12 grid questions" "grid question count is not 12"
Chk (@($Q | Where-Object { $_.scene -eq 'occlusion' }).Count -eq 2) "2 occlusion questions" "occlusion question count is not 2"

$noAns = $true
foreach ($qo in $Q) { if ($qo.PSObject.Properties.Name -contains 'answer') { $noAns = $false } }
Chk $noAns "questions.json contains no answer field" "questions.json leaks an answer field"

$twoStep = @($Q | Where-Object { $_.steps -ge 2 }).Count
Chk ($twoStep -ge 4) ("$twoStep questions require a two-step relation (>= 4)") ("only $twoStep two-step questions")

$cats = (($Q | ForEach-Object { $_.category }) -join ' | ').ToLower()
$cov = @(
  @('composite', '复合属性检索'),
  @('left/right', '严格中心左右关系'),
  @('distance', '距离'),
  @('ordering', '排序'),
  @('bounding', '包围框'),
  @('count', '颜色/形状计数')
)
foreach ($c in $cov) {
  Chk ($cats -like ('*' + $c[0] + '*')) ("category covered: " + $c[1]) ("category MISSING: " + $c[1])
}

# every question states a comparison standard and a coordinate origin
$stdBad = 0
foreach ($qo in $Q) {
  if (($qo.text -notmatch '坐标原点|画面左上角') -or ($qo.text -notmatch '比较标准')) { $stdBad++ }
}
Chk ($stdBad -eq 0) "every question states both the coordinate origin and the comparison standard" ("$stdBad questions lack an explicit origin/comparison standard")

Chk ($A.Count -eq 14) "answers.json holds 14 answers" ("answers.json holds " + $A.Count)
$fieldBad = 0
foreach ($ao in $A) {
  foreach ($f in @('answer','method','coordinate_tolerance','visibility_basis','uniqueness_check')) {
    if ($ao.PSObject.Properties.Name -notcontains $f) { $fieldBad++ }
    elseif ([string]::IsNullOrWhiteSpace([string]$ao.$f)) { $fieldBad++ }
  }
}
Chk ($fieldBad -eq 0) "every answer carries answer / method / coordinate_tolerance / visibility_basis / uniqueness_check" ("$fieldBad missing or empty answer fields")

$indet = @($A | Where-Object { $_.answer -eq '无法确定' }).Count
Chk ($indet -ge 1) ("$indet answer(s) are 无法确定 (>= 1)") "no 无法确定 answer"
Chk ((@($A | Where-Object { $_.id -eq 'Q13' })[0].answer) -eq '无法确定') "Q13 (hidden object count) answers 无法确定" "Q13 does not answer 无法确定"

# the hidden object count must never be a standard answer
$q13a = @($A | Where-Object { $_.id -eq 'Q13' })[0]
$numericQ13 = ($q13a.answer -is [int]) -or ($q13a.answer -is [long]) -or ($q13a.answer -is [double]) -or ($q13a.answer -is [decimal])
Chk (-not $numericQ13) ("the hidden-object-count question is not answered with a count; it answers: " + $q13a.answer) "the hidden-object-count question answers with a numeric count"
$gridAnswersMentionHidden = @($A | Where-Object { $_.id -ne 'Q13' -and ([string]$_.method -match 'hidden_A|hidden_B|hidden_objects|occ-geom|完全覆盖的') }).Count
Chk ($gridAnswersMentionHidden -eq 0) "no other answer is derived from anything behind the occlusion panel" ("$gridAnswersMentionHidden answers reference hidden-content fields")

# object-id answers must exist in the scene
$idBad = 0
$known = @{}; foreach ($o in $OBJ) { $known[$o.id] = $true }
foreach ($ao in $A) { if ($ao.answer_type -eq 'object-id' -and -not $known.ContainsKey([string]$ao.answer)) { $idBad++ } }
Chk ($idBad -eq 0) "every object-id answer exists in scene-data.json" ("$idBad answers name a non-existent object")

# numbering >= 18
$nb = $QDoc.numbering
Chk ($null -ne $nb) "questions.json carries a numbering block" "questions.json has no numbering block"
if ($null -ne $nb) {
  Chk ($nb.numbered_entities -ge 18) ("numbered entities = " + $nb.numbered_entities + " (>= 18): 64 G-ids + 6 V-ids + " + $nb.question_count + " question ids") ("numbered entities below 18: " + $nb.numbered_entities)
  Chk ($nb.meets_18 -eq $true) "numbering.meets_18 = true" "numbering.meets_18 is not true"
}
$nba = $ADoc.numbering
Chk (($null -ne $nba) -and ($nba.numbered_entities -ge 18)) "answers.json numbering block also >= 18" "answers.json numbering block missing or < 18"

# ------------------------------------------------------------------ equivalence ---
$eq = [IO.File]::ReadAllText((Join-Path $OutDir 'equivalence.json')) | ConvertFrom-Json
Chk ($eq.verdict -eq 'EQUIVALENT') "equivalence.json verdict = EQUIVALENT" ("equivalence verdict = " + $eq.verdict)
Chk ($eq.pixel_comparison.differing_pixels -eq 0) ("pixel comparison: 0 of " + $eq.pixel_comparison.pixels_compared + " pixels differ") ("differing pixels: " + $eq.pixel_comparison.differing_pixels)
Chk ($eq.pixel_comparison.identical -eq $true) "pixel_comparison.identical = true" "pixel_comparison.identical is not true"
Chk ($eq.dsl_comparison.hidden_block_differs -eq $true) "the two DSL hidden blocks differ (different hidden content)" "DSL hidden blocks are identical - no proof of differing hidden content"
Chk ($eq.dsl_comparison.shared_prefix_identical -and $eq.dsl_comparison.shared_suffix_identical) "DSL shared prefix and suffix are byte-identical" "DSL shared parts differ - equivalence would be invalid"

$shaA = Sha (Join-Path $OutDir 'occlusion.png')
$shaB = Sha (Join-Path $OutDir 'occlusion-alternative.png')
Chk ($shaA -eq $shaB) "the two occlusion PNGs are byte-identical (same SHA-256)" "occlusion PNGs differ - equivalence broken"
Chk ($eq.image_A.sha256 -eq $shaA) "equivalence.json records the delivered occlusion.png SHA-256" "equivalence.json A hash != delivered file"
Chk ($eq.image_B.sha256 -eq $shaB) "equivalence.json records the delivered occlusion-alternative.png SHA-256" "equivalence.json B hash != delivered file"
$shaDA = Sha (Join-Path $OutDir 'occlusion.snapshot'); $shaDB = Sha (Join-Path $OutDir 'occlusion-alternative.snapshot')
Chk ($shaDA -ne $shaDB) "the two occlusion DSLs differ (they must: hidden content differs)" "the two occlusion DSLs are identical - nothing is being hidden differently"

# the hidden content must genuinely differ between the two occlusion DSLs
Chk ($eq.image_A.hidden_objects -ne $eq.image_B.hidden_objects) ("the two occlusion DSLs hide different numbers of fully-covered objects (A=" + $eq.image_A.hidden_objects + ", B=" + $eq.image_B.hidden_objects + ")") ("the two occlusion DSLs hide the same number of objects: " + $eq.image_A.hidden_objects)
Chk (-not [string]::IsNullOrWhiteSpace([string]$eq.what_differs)) "equivalence.json states exactly what differs behind the panel" "equivalence.json does not describe what differs"
Chk (($eq.image_A.fully_hidden_objects -eq 2) -and ($eq.image_B.fully_hidden_objects -eq 3)) ("fully-covered counts A=" + $eq.image_A.fully_hidden_objects + ", B=" + $eq.image_B.fully_hidden_objects + " agree with answers.json Q13 (which states 2 and 3)") ("fully-covered counts disagree with answers.json Q13: got " + $eq.image_A.fully_hidden_objects + "/" + $eq.image_B.fully_hidden_objects + ", expected 2/3")

# ---------------------------------------------------------------------- process ---
foreach ($f in @('requests.jsonl','iterations.jsonl')) {
  Chk (Test-Path -LiteralPath (Join-Path $TmpDir $f)) "process log present: $f" "MISSING process log: $f"
}
$reqs = @([IO.File]::ReadAllLines((Join-Path $TmpDir 'requests.jsonl')) | ForEach-Object { $_ | ConvertFrom-Json })
$its = @([IO.File]::ReadAllLines((Join-Path $TmpDir 'iterations.jsonl')) | ForEach-Object { $_ | ConvertFrom-Json })
Good ("requests.jsonl: {0} render requests, {1} x 200, {2} x failure, request duration sum {3} ms" -f $reqs.Count, @($reqs | Where-Object { $_.http_status -eq 200 }).Count, @($reqs | Where-Object { $_.http_status -ne 200 }).Count, [Math]::Round((($reqs | Measure-Object -Property duration_ms -Sum).Sum),1))
Good ("iterations.jsonl: {0} rows (baseline {1}, visual {2}, syntax-fix {3}); {4} rows carry a rendered image" -f $its.Count, @($its | Where-Object { $_.type -eq 'baseline' }).Count, @($its | Where-Object { $_.type -eq 'visual' }).Count, @($its | Where-Object { $_.type -eq 'syntax-fix' }).Count, @($its | Where-Object { $_.image -ne $null }).Count)

foreach ($f in @('snapshot-usage.md','task-metrics.json')) {
  Chk (Test-Path -LiteralPath (Join-Path $OutDir $f)) "present: $f" "MISSING deliverable: $f"
}

# ------------------------------------------------------------------ write audit ---
$sb = New-Object System.Text.StringBuilder
[void]$sb.AppendLine('# A19 · final audit')
[void]$sb.AppendLine('')
[void]$sb.AppendLine(('Generated: ' + (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz') + ' (UTC+08:00)'))
[void]$sb.AppendLine('')
[void]$sb.AppendLine(('**problems = ' + $prob.Count + '**'))
[void]$sb.AppendLine('')
[void]$sb.AppendLine('## Problems')
[void]$sb.AppendLine('')
if ($prob.Count -eq 0) { [void]$sb.AppendLine('None.') } else { foreach ($p in $prob) { [void]$sb.AppendLine(('- ' + $p)) } }
[void]$sb.AppendLine('')
[void]$sb.AppendLine('## Checks passed (' + $note.Count + ')')
[void]$sb.AppendLine('')
foreach ($n in $note) { [void]$sb.AppendLine(('- ' + $n)) }
[void]$sb.AppendLine('')
[void]$sb.AppendLine('## Deliverables')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('| file | bytes | sha256 (first 16) |')
[void]$sb.AppendLine('|---|---|---|')
foreach ($f in ($required + @('snapshot-usage.md','task-metrics.json'))) {
  $p = Join-Path $OutDir $f
  if (Test-Path -LiteralPath $p) {
    [void]$sb.AppendLine(('| `' + $f + '` | ' + (Get-Item -LiteralPath $p).Length + ' | ' + (Sha $p).Substring(0,16) + ' |'))
  } else {
    [void]$sb.AppendLine(('| `' + $f + '` | - | MISSING |'))
  }
}
[IO.File]::WriteAllText($AuditMd, $sb.ToString(), $utf8)

Write-Output ("problems = {0}" -f $prob.Count)
foreach ($p in $prob) { Write-Output ("  PROBLEM: " + $p) }
Write-Output ("notes    = {0}" -f $note.Count)
Write-Output ("-> {0}" -f $AuditMd)
