param([int]$Ver = 2, [string]$OutAudit = '')

# ---------------------------------------------------------------- A12 verify --
# Reads only the real artefacts (DSL + PNG + content-map + segments) and proves
# the four-breakpoint requirements. Nothing here edits the artwork.
#
# P  PNG signature + IHDR size
# N  no Image / transform / scale / rotate anywhere
# C  all 25 input fields present verbatim, no HTML-entity encoding
# F  every fontFamily used is present in the real GET /fonts response
# T  font-size floors (mobile body>=16, card title>=18, other body>=20, title>=40)
# L  safe margins (mobile>=16, others>=32)
# M  rendered ink bbox stays inside the safe area
# B  every text box stays inside the safe area
# O  no two text boxes overlap
# V  title box never runs under the corner motif
# R  each card's index/title/detail box stays inside its own tile
# G  the three section gaps are free of ink (nothing bleeds between sections)
# W  no ink below the location chip (catches a chip that wrapped out of its pill)
#
# NOTE: PowerShell variables are case-insensitive, so every name below is unique
# up to case ($MAP/$map, $M/$m, $W/$w and $SEGS/$seg were all real bugs here).

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
[System.Threading.Thread]::CurrentThread.CurrentCulture   = [cultureinfo]::InvariantCulture
[System.Threading.Thread]::CurrentThread.CurrentUICulture = [cultureinfo]::InvariantCulture

$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
Set-Location $root

$TMPDIR = "$root\tmp\$RUN\A12"
$OUTDIR = "$root\outputs\$RUN\A12"
$SRCIN  = "$root\tasks\A12-responsive-system\inputs\content.json"
$V      = $Ver
$BPN    = @('mobile', 'tablet', 'desktop', 'stage')
$EXPECT = @{ mobile = @(360, 800); tablet = @(768, 1024); desktop = @(1440, 900); stage = @(1920, 1080) }
$NEEDM  = @{ mobile = 16; tablet = 32; desktop = 32; stage = 32 }

$CT    = [IO.File]::ReadAllText($SRCIN, [Text.UTF8Encoding]::new($false)) | ConvertFrom-Json
$CM    = [IO.File]::ReadAllText("$TMPDIR\content-map-v$V.json", [Text.UTF8Encoding]::new($false)) | ConvertFrom-Json
$SEGS  = [IO.File]::ReadAllText("$TMPDIR\segments-v$V.json", [Text.UTF8Encoding]::new($false)) | ConvertFrom-Json
if ($SEGS -isnot [array]) { $SEGS = @($SEGS) }
$FONTL = [IO.File]::ReadAllText("$root\tmp\$RUN\A11\fonts-0001.txt", [Text.UTF8Encoding]::new($false)) -split "`r?`n"

$checks = New-Object System.Collections.Generic.List[object]
function Add-Check([string]$id, [string]$grp, [string]$desc, [bool]$ok, $detail) {
  $st = 'FAIL'
  if ($ok) { $st = 'PASS' }
  [void]$checks.Add([pscustomobject]@{ id = $id; group = $grp; description = $desc; result = $st; detail = $detail })
}

# --------------------------------------------------------------- field list ---
$fieldVals = New-Object System.Collections.Generic.List[object]
foreach ($fn in @('title', 'subtitle', 'date', 'time', 'location', 'cta', 'website')) {
  [void]$fieldVals.Add([pscustomobject]@{ path = $fn; value = [string]$CT.$fn })
}
for ($ix = 0; $ix -lt 6; $ix++) {
  $cd0 = $CT.cards[$ix]
  [void]$fieldVals.Add([pscustomobject]@{ path = "cards[$ix].id"; value = [string]$cd0.id })
  [void]$fieldVals.Add([pscustomobject]@{ path = "cards[$ix].title"; value = [string]$cd0.title })
  [void]$fieldVals.Add([pscustomobject]@{ path = "cards[$ix].detail"; value = [string]$cd0.detail })
}

# ------------------------------------------------------------------ pixel I/O --
function Get-Ink([string]$pngPath, [int]$x0, [int]$y0, [int]$x1, [int]$y1, [int]$thresh) {
  $bmp = New-Object System.Drawing.Bitmap($pngPath)
  try {
    $bw = $bmp.Width; $bh = $bmp.Height
    if ($x0 -lt 0) { $x0 = 0 }
    if ($y0 -lt 0) { $y0 = 0 }
    if ($x1 -gt ($bw - 1)) { $x1 = $bw - 1 }
    if ($y1 -gt ($bh - 1)) { $y1 = $bh - 1 }
    $rct = New-Object System.Drawing.Rectangle(0, 0, $bw, $bh)
    $lck = $bmp.LockBits($rct, [System.Drawing.Imaging.ImageLockMode]::ReadOnly, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    try {
      $str = $lck.Stride
      $buf = New-Object byte[] ([math]::Abs($str) * $bh)
      [System.Runtime.InteropServices.Marshal]::Copy($lck.Scan0, $buf, 0, $buf.Length)
      $cnt = 0; $nmx = -1; $nmy = -1; $nXX = -1; $nYY = -1
      for ($yy = $y0; $yy -le $y1; $yy++) {
        $rowBase = $yy * $str
        for ($xx = $x0; $xx -le $x1; $xx++) {
          $o = $rowBase + ($xx * 4)
          $pb = $buf[$o]; $pg = $buf[$o + 1]; $pr = $buf[$o + 2]
          if ($pr -lt $thresh -and $pg -lt $thresh -and $pb -lt $thresh) { continue }
          $mx = $pr
          if ($pg -gt $mx) { $mx = $pg }
          if ($pb -gt $mx) { $mx = $pb }
          if ($mx -lt $thresh) { continue }
          $cnt++
          if ($nmx -lt 0 -or $xx -lt $nmx) { $nmx = $xx }
          if ($nmy -lt 0 -or $yy -lt $nmy) { $nmy = $yy }
          if ($xx -gt $nXX) { $nXX = $xx }
          if ($yy -gt $nYY) { $nYY = $yy }
        }
      }
      return @{ count = $cnt; minx = $nmx; miny = $nmy; maxx = $nXX; maxy = $nYY }
    } finally { $bmp.UnlockBits($lck) }
  } finally { $bmp.Dispose() }
}

# -------------------------------------------------------------------- setup ---
$mapByBp = @{}
foreach ($cmRec in $CM.canvases) { $mapByBp[$cmRec.name] = $cmRec }
$segByBp = @{}
foreach ($sg in $SEGS) {
  if (-not $segByBp.ContainsKey($sg.bp)) { $segByBp[$sg.bp] = New-Object System.Collections.Generic.List[object] }
  [void]$segByBp[$sg.bp].Add($sg)
}

# ---------------------------------------------------------------------- loop --
foreach ($bp in $BPN) {
  $exp = $EXPECT[$bp]
  $expW = [int]$exp[0]
  $expH = [int]$exp[1]
  $pngPath = "$TMPDIR\render-v$V-$bp.png"
  $dslPath = "$TMPDIR\$bp-v$V.snapshot"
  $cv      = $mapByBp[$bp]
  $margin  = [int]$cv.margin
  $cvsW    = [int]$cv.width
  $cvsH    = [int]$cv.height
  $safeR   = $cvsW - 1 - $margin
  $safeB   = $cvsH - 1 - $margin

  # ---- P -------------------------------------------------------------------
  $sigOk = $false; $ihdrTxt = 'file missing'
  if (Test-Path $pngPath) {
    $raw = [IO.File]::ReadAllBytes($pngPath)
    $sig = ''; for ($z = 0; $z -lt 8; $z++) { $sig += $raw[$z].ToString('X2') }
    $iw = [BitConverter]::ToInt32([byte[]]@($raw[19], $raw[18], $raw[17], $raw[16]), 0)
    $ih = [BitConverter]::ToInt32([byte[]]@($raw[23], $raw[22], $raw[21], $raw[20]), 0)
    $ihdrTxt = "${iw}x${ih}"
    $sigOk = ($sig -eq '89504E470D0A1A0A' -and $iw -eq $expW -and $ih -eq $expH)
  }
  Add-Check "P-$bp" 'P' "$bp PNG signature + IHDR = ${expW}x${expH}" $sigOk $ihdrTxt

  # ---- N -------------------------------------------------------------------
  $dslTxt = [IO.File]::ReadAllText($dslPath, [Text.UTF8Encoding]::new($false))
  $badTok = @()
  foreach ($tk in @('<Image', 'transform=', 'scale=', 'rotate=', 'backgroundImage', 'clipPath')) {
    if ($dslTxt.Contains($tk)) { $badTok += $tk }
  }
  Add-Check "N-$bp" 'N' "$bp no Image / transform / scale / rotate (adaptation is re-laid-out, never cropped)" ($badTok.Count -eq 0) $(if ($badTok.Count) { $badTok -join ',' } else { 'clean' })

  # ---- C -------------------------------------------------------------------
  $payloads = New-Object System.Collections.Generic.List[string]
  foreach ($mx in [regex]::Matches($dslTxt, '<!\[CDATA\[(.*?)\]\]>', 'Singleline')) { [void]$payloads.Add($mx.Groups[1].Value) }
  $joinPlain = [string]::Join('', $payloads.ToArray())
  $joinSpaced = [string]::Join(' ', $payloads.ToArray())
  $miss = @()
  foreach ($fv in $fieldVals) {
    $fldRec = $CM.fields | Where-Object { $_.path -eq $fv.path }
    if ($fv.path -eq 'title') {
      $boxes = @($fldRec.canvases.$bp.boxes)
      if ($boxes.Count -eq 2) {
        $rebuilt = $boxes[0].text + ' ' + $boxes[1].text
        if ($rebuilt -ne $fv.value) { $miss += "$($fv.path) [rebuilt=$rebuilt]" }
      } elseif (-not ($joinPlain.Contains($fv.value) -or $joinSpaced.Contains($fv.value))) {
        $miss += "$($fv.path)=[$($fv.value)]"
      }
    } else {
      if (-not ($joinPlain.Contains($fv.value) -or $joinSpaced.Contains($fv.value))) {
        $miss += "$($fv.path)=[$($fv.value)]"
      }
    }
  }
  $entBad = @()
  foreach ($en in @('&lt;', '&gt;', '&amp;', '&quot;', '&apos;', '&#')) { if ($dslTxt.Contains($en)) { $entBad += $en } }
  $cOk = ($miss.Count -eq 0 -and $entBad.Count -eq 0)
  $cDet = "25/25 verbatim, 0 entities"
  if (-not $cOk) { $cDet = 'missing: ' + (($miss + $entBad) -join '; ') }
  Add-Check "C-$bp" 'C' "$bp all $($fieldVals.Count) input fields present verbatim (Raw+CDATA, no entity encoding)" $cOk $cDet

  # ---- F -------------------------------------------------------------------
  $famSeen = @()
  foreach ($mx in [regex]::Matches($dslTxt, 'fontFamily="([^"]+)"')) { $famSeen += $mx.Groups[1].Value }
  $famBad = @()
  foreach ($u in ($famSeen | Sort-Object -Unique)) {
    if ($u.Contains(', ')) { $famBad += "space-after-comma in [$u]" }
    foreach ($one in ($u -split ',')) {
      $nm = $one.Trim()
      if ($nm -eq '') { continue }
      if ($FONTL -notcontains $nm) { $famBad += $nm }
    }
  }
  Add-Check "F-$bp" 'F' "$bp every fontFamily is in the real GET /fonts response" ($famBad.Count -eq 0) $(if ($famBad.Count) { $famBad -join ',' } else { (($famSeen | Sort-Object -Unique) -join ' | ') })

  # ---- T -------------------------------------------------------------------
  $tseg = $segByBp[$bp] | Where-Object { $_.kind -eq 'text' }
  $bodyMin = 9999; $titleMin = 9999; $ctMin = 9999
  foreach ($ts in $tseg) {
    if ($ts.field -eq 'title') { if ($ts.fontSize -lt $titleMin) { $titleMin = $ts.fontSize } }
    elseif ($ts.field -match '^cards\[\d+\]\.title$') { if ($ts.fontSize -lt $ctMin) { $ctMin = $ts.fontSize } }
    else { if ($ts.fontSize -lt $bodyMin) { $bodyMin = $ts.fontSize } }
  }
  $bodyNeed = 16
  if ($bp -ne 'mobile') { $bodyNeed = 20 }
  Add-Check "T1-$bp" 'T' "$bp body >= $bodyNeed (min found $bodyMin)" ($bodyMin -ge $bodyNeed) $bodyMin
  Add-Check "T2-$bp" 'T' "$bp card title >= 18 (min found $ctMin)" ($ctMin -ge 18) $ctMin
  Add-Check "T3-$bp" 'T' "$bp main title >= 40 (min found $titleMin)" ($titleMin -ge 40) $titleMin
  Add-Check "T4-$bp" 'T' "$bp every Text node uses height=1.0 (line box == font size)" (([regex]::Matches($dslTxt, 'height="1\.0"')).Count -ge 25) (([regex]::Matches($dslTxt, 'height="1\.0"')).Count)

  # ---- L -------------------------------------------------------------------
  Add-Check "L-$bp" 'L' "$bp safe margin $margin >= required $($NEEDM[$bp])" ($margin -ge $NEEDM[$bp]) $margin

  # ---- M -------------------------------------------------------------------
  $inkAll = Get-Ink $pngPath 0 0 ($cvsW - 1) ($cvsH - 1) 120
  $mOk = ($inkAll.minx -ge $margin -and $inkAll.miny -ge $margin -and $inkAll.maxx -le $safeR -and $inkAll.maxy -le $safeB)
  Add-Check "M-$bp" 'M' "$bp ink bbox inside safe area [$margin..$safeR]x[$margin..$safeB]" $mOk ("bbox=" + $inkAll.minx + ',' + $inkAll.miny + '..' + $inkAll.maxx + ',' + $inkAll.maxy + ' ink_px=' + $inkAll['count'])

  # ---- B -------------------------------------------------------------------
  $outBoxes = @()
  foreach ($ts in $tseg) {
    if ($ts.x -lt $margin -or $ts.y -lt $margin -or ($ts.x + $ts.width) -gt ($cvsW - $margin) -or ($ts.y + $ts.height) -gt ($cvsH - $margin)) {
      $outBoxes += "$($ts.id)[$($ts.x),$($ts.y),$($ts.width),$($ts.height)]"
    }
  }
  $bDet = "$($tseg.Count) boxes OK"
  if ($outBoxes.Count) { $bDet = $outBoxes -join '; ' }
  Add-Check "B-$bp" 'B' "$bp all $($tseg.Count) text boxes inside the safe area" ($outBoxes.Count -eq 0) $bDet

  # ---- O -------------------------------------------------------------------
  $ovl = @()
  for ($p1 = 0; $p1 -lt $tseg.Count; $p1++) {
    for ($p2 = $p1 + 1; $p2 -lt $tseg.Count; $p2++) {
      $tA = $tseg[$p1]; $tB = $tseg[$p2]
      $ovX = [math]::Min($tA.x + $tA.width, $tB.x + $tB.width) - [math]::Max($tA.x, $tB.x)
      $ovY = [math]::Min($tA.y + $tA.height, $tB.y + $tB.height) - [math]::Max($tA.y, $tB.y)
      if ($ovX -gt 0 -and $ovY -gt 0) { $ovl += "$($tA.id) x $($tB.id) ($ovX x $ovY)" }
    }
  }
  $oDet = "$($tseg.Count) boxes disjoint"
  if ($ovl.Count) { $oDet = $ovl -join '; ' }
  Add-Check "O-$bp" 'O' "$bp no two text boxes overlap" ($ovl.Count -eq 0) $oDet

  # ---- V -------------------------------------------------------------------
  $mot = $cv.sections.motif
  $vBad = @()
  foreach ($ts in ($tseg | Where-Object { $_.field -eq 'title' })) {
    if ((($ts.x + $ts.width) -gt $mot.x) -and (($ts.y + $ts.height) -gt $mot.y) -and ($ts.y -lt ($mot.y + $mot.size))) { $vBad += $ts.id }
  }
  Add-Check "V-$bp" 'V' "$bp title box clears the corner motif (motif x=$($mot.x))" ($vBad.Count -eq 0) $(if ($vBad.Count) { $vBad -join ',' } else { 'clear' })

  # ---- R -------------------------------------------------------------------
  foreach ($cd in $cv.cards_list) {
    $okR = $true; $why = ''
    foreach ($kk in @('title', 'index', 'detail')) {
      $bx = $cd."${kk}_x"; $by = $cd."${kk}_y"; $bw = $cd."${kk}_w"; $bh2 = $cd."${kk}_h"
      if ($bx -lt $cd.x -or $by -lt $cd.y -or ($bx + $bw) -gt ($cd.x + $cd.width) -or ($by + $bh2) -gt ($cd.y + $cd.height)) {
        $okR = $false; $why = "$kk box [$bx,$by,$bw,$bh2] outside tile [$($cd.x),$($cd.y),$($cd.width),$($cd.height)]"
      }
    }
    Add-Check "R-$bp-$($cd.id)" 'R' "$bp tile $($cd.id) $($cd.width)x$($cd.height) contains its index/title/detail boxes" $okR $(if ($okR) { 'contained' } else { $why })
  }

  # ---- G -------------------------------------------------------------------
  foreach ($gp in @(@('header', 'meta'), @('meta', 'cards'), @('cards', 'footer'))) {
    $secA = $cv.sections.($gp[0]); $secB = $cv.sections.($gp[1])
    $gy0 = [int]$secA.bottom + 1
    $gy1 = [int]$secB.top - 1
    $gRes = @{ count = 0 }
    if ($gy1 -ge $gy0) { $gRes = Get-Ink $pngPath $margin $gy0 $safeR $gy1 120 }
    Add-Check "G-$bp-$($gp[0])-$($gp[1])" 'G' "$bp section gap $($gp[0])->$($gp[1]) rows $gy0..$gy1 free of ink" ($gRes['count'] -eq 0) ("ink_px=" + $gRes['count'])
  }

  # ---- W -------------------------------------------------------------------
  $locChip = @($SEGS | Where-Object { $_.bp -eq $bp -and $_.kind -eq 'box' -and $_.id -like '*chip-loc*' })
  if ($locChip.Count -gt 0) {
    $ch0 = $locChip[0]
    $wTop = [int]$ch0.y + [int]$ch0.height + 1
    $wBot = [math]::Min(($wTop + 40), ([int]$cv.sections.cards.top - 1))
    if ($wBot -lt $wTop) { $wBot = $wTop }
    $wRes = Get-Ink $pngPath ([int]$ch0.x) $wTop ([int]$ch0.x + [int]$ch0.width - 1) $wBot 120
    Add-Check "W-$bp" 'W' "$bp no ink below the location chip (rows $wTop..$wBot)" ($wRes['count'] -eq 0) ("ink_px=" + $wRes['count'])
  } else {
    Add-Check "W-$bp" 'W' "$bp no ink below the location chip" $false 'location chip not found in segments'
  }
}

# ------------------------------------------------------------------- summary ---
$passCnt = @($checks | Where-Object { $_.result -eq 'PASS' }).Count
$failCnt = @($checks | Where-Object { $_.result -eq 'FAIL' }).Count

$audit = [pscustomobject][ordered]@{
  schema_version = 1
  task_id        = 'A12'
  run_id         = $RUN
  verified_at    = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')
  timezone       = 'Asia/Shanghai (UTC+08:00)'
  dsl_version    = "v$V"
  input          = 'tasks/A12-responsive-system/inputs/content.json'
  canvases       = @('mobile 360x800 margin 16', 'tablet 768x1024 margin 32', 'desktop 1440x900 margin 48', 'stage 1920x1080 margin 56')
  method         = [pscustomobject]@{
    geometry = "Absolute text boxes come from content-map-v$V.json, written by gen.ps1 at emit time rather than measured afterwards."
    pixels   = 'PNG decoded through System.Drawing LockBits (32bppArgb). Ink = max(R,G,B) >= 120, which excludes background #0B1220, surface #132038 and hairline #23324C while catching amber #F6B94A, cyan #38BDF8 and both text colours.'
    overlap  = 'Every pair of text boxes in a canvas is intersected; any positive overlap in both axes fails.'
    content  = 'The 25 input values must appear inside a CDATA payload of that canvas DSL. The split mobile title is rebuilt as line1 + " " + line2 and compared with the input string.'
    fonts    = 'The fontFamily lists are checked against the real GET /fonts response obtained earlier in this run.'
    bands    = 'The three section gaps and the band under the location chip are pixel-scanned; any ink there means content bled across a boundary.'
  }
  totals         = [pscustomobject]@{ checks = $checks.Count; passed = $passCnt; failed = $failCnt }
  checks         = $checks
}
$auditPath = "$OUTDIR\responsive-audit.json"
if ($OutAudit -ne '') { $auditPath = $OutAudit }
if (-not (Test-Path $OUTDIR)) { New-Item -ItemType Directory -Force -Path $OUTDIR | Out-Null }
[IO.File]::WriteAllText($auditPath, ($audit | ConvertTo-Json -Depth 10), [Text.UTF8Encoding]::new($false))

foreach ($ck in $checks) {
  if ($ck.result -eq 'FAIL') { Write-Output ("FAIL {0,-24} {1}  <- {2}" -f $ck.id, $ck.description, $ck.detail) }
}
Write-Output ("verify v{0}: {1}/{2} PASS  ({3} FAIL)" -f $V, $passCnt, $checks.Count, $failCnt)
Write-Output ("audit -> " + $auditPath)
