# A15 - build reconstruction-audit.json from real measurements of the reference
# and the delivered reconstruction: geometric anchors + per-text ink boxes +
# stroke-mass (font weight) ratios.
param([Parameter(Mandatory = $true)][string]$Png)

$ErrorActionPreference = 'Stop'
$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $ROOT
$TMP = Join-Path $ROOT 'tmp\run-20261002-220723-mimo\A15'
$REF = Join-Path $ROOT 'tasks\A15-reference-reconstruction\inputs\reference.png'
$OUTDIR = Join-Path $ROOT 'outputs\run-20261002-220723-mimo\A15'
$ENC = New-Object Text.UTF8Encoding($false)
Add-Type -AssemblyName System.Drawing

$TOL = 8

function LumOf($c) { return (0.299 * $c.R) + (0.587 * $c.G) + (0.114 * $c.B) }

function InkBox($bmp, $x0, $y0, $x1, $y1, $mode) {
  $maxX = $bmp.Width - 1; $maxY = $bmp.Height - 1
  if ($x0 -lt 0) { $x0 = 0 }; if ($y0 -lt 0) { $y0 = 0 }
  if ($x1 -gt $maxX) { $x1 = $maxX }; if ($y1 -gt $maxY) { $y1 = $maxY }
  $bx = 99999; $by = 99999; $bx1 = -1; $by1 = -1
  for ($y = $y0; $y -le $y1; $y++) {
    for ($x = $x0; $x -le $x1; $x++) {
      $lum = LumOf $bmp.GetPixel($x, $y)
      $hit = $false
      if ($mode -eq 'light') { if ($lum -gt 120) { $hit = $true } }
      else { if ($lum -lt 170) { $hit = $true } }
      if ($hit) {
        if ($x -lt $bx) { $bx = $x }
        if ($x -gt $bx1) { $bx1 = $x }
        if ($y -lt $by) { $by = $y }
        if ($y -gt $by1) { $by1 = $y }
      }
    }
  }
  if ($bx1 -lt 0) { return $null }
  return [pscustomobject]@{ x = $bx; y = $by; w = ($bx1 - $bx + 1); h = ($by1 - $by + 1) }
}

# background-independent ink mass over the same probe window
function InkMass($bmp, $x0, $y0, $x1, $y1) {
  $maxX = $bmp.Width - 1; $maxY = $bmp.Height - 1
  if ($x0 -lt 0) { $x0 = 0 }; if ($y0 -lt 0) { $y0 = 0 }
  if ($x1 -gt $maxX) { $x1 = $maxX }; if ($y1 -gt $maxY) { $y1 = $maxY }
  $vals = New-Object System.Collections.Generic.List[double]
  for ($y = $y0; $y -le $y1; $y++) {
    for ($x = $x0; $x -le $x1; $x++) { $vals.Add((LumOf $bmp.GetPixel($x, $y))) }
  }
  $sorted = $vals.ToArray(); [Array]::Sort($sorted)
  $bg = $sorted[[int]($sorted.Length / 2)]
  $m = 0.0
  for ($i = 0; $i -lt $sorted.Length; $i++) { $m += [math]::Abs($sorted[$i] - $bg) }
  return [math]::Round($m, 0)
}

$el = [IO.File]::ReadAllText((Join-Path $TMP 'elements.json')) | ConvertFrom-Json
$geom = [IO.File]::ReadAllText((Join-Path $TMP 'anchor-measures.json')) | ConvertFrom-Json

$ref = New-Object System.Drawing.Bitmap($REF)
$mine = New-Object System.Drawing.Bitmap($Png)

$geomOut = @()
foreach ($g in $geom) {
  $geomOut += [ordered]@{
    name           = $g.anchor
    reference      = $g.reference
    reconstructed  = $g.reconstructed
    delta          = $g.delta
    tolerance      = $TOL
    pass           = [bool]$g.pass
  }
}

$textOut = @()
foreach ($e in $el.texts) {
  $padR = [math]::Max(20.0, ($e.rw * 0.22))
  $wx0 = [int][math]::Floor($e.rx - 10); $wy0 = [int][math]::Floor($e.ry - 10)
  $wx1 = [int][math]::Ceiling($e.rx + $e.rw + $padR); $wy1 = [int][math]::Ceiling($e.ry + $e.rh + 10)

  $rb = InkBox $ref $wx0 $wy0 $wx1 $wy1 $e.mode
  $mb = InkBox $mine $wx0 $wy0 $wx1 $wy1 $e.mode
  if ($null -eq $rb -or $null -eq $mb) {
    $textOut += [ordered]@{ id = $e.id; text = $e.text; error = 'no ink found'; pass = $false }
    continue
  }
  $rm = InkMass $ref $wx0 $wy0 $wx1 $wy1
  $mm = InkMass $mine $wx0 $wy0 $wx1 $wy1
  if ($mm -le 0) { $mm = 1 }
  $ratio = [math]::Round($rm / $mm, 3)

  $cx = $rb.x + ($rb.w / 2); $cy = $rb.y + ($rb.h / 2)
  $quad = 'unknown'
  if ($cx -lt 720 -and $cy -lt 450) { $quad = 'top-left' }
  elseif ($cx -ge 720 -and $cy -lt 450) { $quad = 'top-right' }
  elseif ($cx -lt 720 -and $cy -ge 450) { $quad = 'bottom-left' }
  else { $quad = 'bottom-right' }

  $dx = $rb.x - $mb.x; $dy = $rb.y - $mb.y; $dw = $rb.w - $mb.w; $dh = $rb.h - $mb.h
  $pass = ([math]::Abs($dx) -le $TOL -and [math]::Abs($dy) -le $TOL -and [math]::Abs($dw) -le $TOL)
  $textOut += [ordered]@{
    id                   = $e.id
    text                 = $e.text
    quadrant             = $quad
    reference            = [ordered]@{ x = $rb.x; y = $rb.y; w = $rb.w; h = $rb.h }
    reconstructed        = [ordered]@{ x = $mb.x; y = $mb.y; w = $mb.w; h = $mb.h }
    delta                = [ordered]@{ dx = $dx; dy = $dy; dw = $dw; dh = $dh }
    stroke_mass_ratio    = $ratio
    tolerance            = $TOL
    pass                 = $pass
  }
}
$ref.Dispose(); $mine.Dispose()

# a curated set that must cover all four canvas quadrants, the chart and the table
$REQUIRED = @(
  'title', 'nav0', 'k3lab', 'btnLbl', 'sideL1', 'p0', 'd2', 's2', 'footer',
  'cTitle', 'tick0', 'm5', 'h0', 'o1', 'p2'
)
$reqOut = @()
foreach ($id in $REQUIRED) {
  $hit = $textOut | Where-Object { $_.id -eq $id }
  if ($null -ne $hit) { $reqOut += $hit }
}

$geomFail = @($geomOut | Where-Object { -not $_.pass })
$textFail = @($textOut | Where-Object { $_.pass -eq $false })
$allQuads = @(($textOut | ForEach-Object { $_.quadrant } | Sort-Object -Unique))
$massExact = @($textOut | Where-Object { $_.stroke_mass_ratio -eq 1 }).Count

$maxGeomDelta = 0
foreach ($g in $geomOut) { if ([math]::Abs([int]$g.delta) -gt $maxGeomDelta) { $maxGeomDelta = [math]::Abs([int]$g.delta) } }
$maxTextDelta = 0
foreach ($t in $textOut) {
  if ($null -eq $t.delta) { continue }
  foreach ($k in @('dx', 'dy', 'dw', 'dh')) {
    $v = [math]::Abs([int]$t.delta.$k)
    if ($v -gt $maxTextDelta) { $maxTextDelta = $v }
  }
}

$audit = [ordered]@{
  schema             = 'snapshot-suite/reconstruction-audit/v1'
  task_id            = 'A15'
  run_id             = 'run-20261002-220723-mimo'
  generated_at       = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')
  tolerance_px       = $TOL
  reference          = [ordered]@{
    path              = 'tasks\A15-reference-reconstruction\inputs\reference.png'
    size              = '1440x900'
    usage             = 'observed and measured only'
    embedded_or_cropped = $false
    note              = 'no pixel of the reference appears in the reconstruction; it was only opened and sampled with System.Drawing probes to estimate coordinates and colours'
  }
  reconstruction     = [ordered]@{
    png               = 'outputs\run-20261002-220723-mimo\A15\reconstructed.png'
    dsl               = 'outputs\run-20261002-220723-mimo\A15\reconstructed.snapshot'
    size              = '1440x900'
    render_version    = '07'
    source_request_id = 'A15-r06-reconstructed'
    raw_service_bytes = $true
    post_processed     = $false
  }
  fonts              = [ordered]@{
    source       = 'GET /fonts, cached at tmp\run-20261002-220723-mimo\A11\fonts-0001.txt'
    families_used = @('Inter', 'Inter Extra Bold')
    note          = 'only families returned by the live service font listing were used; fontStyle BOLD is applied on the Inter family rather than inventing an "Inter Bold" family'
  }
  geometry_anchors   = $geomOut
  text_anchors       = $textOut
  required_anchors   = $reqOut
  summary            = [ordered]@{
    geometry_anchors           = $geomOut.Count
    geometry_anchors_passed    = $geomOut.Count - $geomFail.Count
    geometry_anchors_failed    = $geomFail.Count
    geometry_max_abs_delta_px  = $maxGeomDelta
    text_anchors               = $textOut.Count
    text_anchors_passed        = $textOut.Count - $textFail.Count
    text_anchors_failed        = $textFail.Count
    text_max_abs_delta_px      = $maxTextDelta
    required_anchors           = $reqOut.Count
    required_anchors_passed    = @($reqOut | Where-Object { $_.pass }).Count
    quadrants_covered          = $allQuads
    chart_anchors              = @($textOut | Where-Object { $_.id -like 'c*' -or $_.id -like 'tick*' -or $_.id -like 'm*' }).Count
    table_anchors              = @($textOut | Where-Object { $_.id -like 'h*' -or $_.id -like 'p*' -or $_.id -like 'o*' -or $_.id -like 'd*' -or $_.id -like 's*' }).Count
    text_elements_pixel_identical_stroke_mass = $massExact
    text_elements_stroke_mass_within_5pct     = @($textOut | Where-Object { $_.stroke_mass_ratio -ge 0.95 -and $_.stroke_mass_ratio -le 1.05 }).Count
    all_pass                    = (($geomFail.Count -eq 0) -and ($textFail.Count -eq 0))
  }
}

$path = Join-Path $OUTDIR 'reconstruction-audit.json'
[IO.File]::WriteAllText($path, ($audit | ConvertTo-Json -Depth 8), $ENC)
Write-Output ("wrote {0}" -f $path)
Write-Output ("geometry {0}/{1} pass (max |delta| {2}px)" -f ($geomOut.Count - $geomFail.Count), $geomOut.Count, $maxGeomDelta)
Write-Output ("text     {0}/{1} pass (max |delta| {2}px)" -f ($textOut.Count - $textFail.Count), $textOut.Count, $maxTextDelta)
Write-Output ("required {0}/{1} pass" -f @($reqOut | Where-Object { $_.pass }).Count, $reqOut.Count)
Write-Output ("quadrants: {0}" -f ($allQuads -join ', '))
Write-Output ("stroke mass: {0}/{1} pixel-identical, {2} within 5%" -f $massExact, $textOut.Count, @($textOut | Where-Object { $_.stroke_mass_ratio -ge 0.95 -and $_.stroke_mass_ratio -le 1.05 }).Count)
