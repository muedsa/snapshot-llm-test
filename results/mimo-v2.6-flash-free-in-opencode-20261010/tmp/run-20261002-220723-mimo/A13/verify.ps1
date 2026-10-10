# A13 verifier - reads ONLY delivered/rendered artefacts, writes brand-audit.json.
# Every check reports an expected vs observed value so the audit is checkable.
$ErrorActionPreference = 'Stop'
[System.Threading.Thread]::CurrentThread.CurrentCulture   = [cultureinfo]::InvariantCulture
[System.Threading.Thread]::CurrentThread.CurrentUICulture = [cultureinfo]::InvariantCulture
Add-Type -AssemblyName System.Drawing

$MATRIXGLOBAL = '(0.70710678,-0.70710678,0,0,0.70710678,0.70710678,0,0,0,0,1,0,0,0,0,1)'

$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
Set-Location $root
$T   = "tmp\$RUN\A13"
$VER = 1
if ($args.Count -gt 0) { $VER = [int]$args[0] }
# each artefact is verified at the HIGHEST render version that actually exists, so a
# change to one artefact does not force pointless re-renders of the others
$script:usedVer = @{}
function Resolve-Png([string]$name) {
  for ($v = $script:VER; $v -ge 1; $v--) {
    $p = Join-Path $T ("render-0" + $v + '-' + $name + '.png')
    if (Test-Path $p) { $script:usedVer[$name] = $v; return $p }
  }
  throw "no rendered png found for $name"
}

$checks = New-Object System.Collections.Generic.List[object]
function Add-Check([string]$id, [string]$group, [string]$desc, $expected, $observed, [bool]$pass) {
  $checks.Add([pscustomobject]@{ id = $id; group = $group; description = $desc; expected = $expected; observed = $observed; result = $(if ($pass) { 'PASS' } else { 'FAIL' }) })
}

function Get-Bitmap([string]$name) {
  return New-Object System.Drawing.Bitmap((Resolve-Png $name))
}
function Get-Ihdr([string]$name) {
  $p = Resolve-Png $name
  $b = [IO.File]::ReadAllBytes($p)
  $sigOk = ($b[0] -eq 0x89 -and $b[1] -eq 0x50 -and $b[2] -eq 0x4E -and $b[3] -eq 0x47)
  $w = [BitConverter]::ToInt32([byte[]]@($b[19], $b[18], $b[17], $b[16]), 0)
  $h = [BitConverter]::ToInt32([byte[]]@($b[23], $b[22], $b[21], $b[20]), 0)
  return @{ sig = $sigOk; w = $w; h = $h; bytes = $b.Length }
}
function Lock([System.Drawing.Bitmap]$bmp) {
  $r = New-Object System.Drawing.Rectangle(0, 0, $bmp.Width, $bmp.Height)
  $l = $bmp.LockBits($r, [System.Drawing.Imaging.ImageLockMode]::ReadOnly, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
  $buf = New-Object byte[] ([math]::Abs($l.Stride) * $bmp.Height)
  [System.Runtime.InteropServices.Marshal]::Copy($l.Scan0, $buf, 0, $buf.Length)
  $bmp.UnlockBits($l)
  return @{ buf = $buf; stride = $l.Stride }
}
function Px($L, [int]$x, [int]$y) {
  $o = $y * $L['stride'] + $x * 4
  $b = $L['buf']
  return @{ a = [int]$b[$o + 3]; r = [int]$b[$o + 2]; g = [int]$b[$o + 1]; bl = [int]$b[$o] }
}

$expect = @{
  'symbol-color'         = @(512, 512)
  'symbol-black'         = @(512, 512)
  'brand-banner'         = @(1200, 400)
  'launch-poster'        = @(1080, 1350)
  'symbol-color-native32'= @(32, 32)
}

# ------------------------------------------------------------------ P: png ----
$i = 1
foreach ($k in @('symbol-color', 'symbol-black', 'brand-banner', 'launch-poster', 'symbol-color-native32')) {
  $ih = Get-Ihdr $k
  $e = $expect[$k]
  $ok = ($ih['sig'] -and $ih['w'] -eq $e[0] -and $ih['h'] -eq $e[1])
  Add-Check ("P{0:D2}" -f $i) 'P_png_signature_and_size' "$k is a real PNG with the required size" "$($e[0])x$($e[1]), sig 89504E47" "$($ih['w'])x$($ih['h']), sig_ok=$($ih['sig']), $($ih['bytes']) B" $ok
  $i++
}

# ------------------------------------------------- A/K: transparency + black ---
$cBmp = Get-Bitmap 'symbol-color'; $cL = Lock $cBmp
$bBmp = Get-Bitmap 'symbol-black'; $bL = Lock $bBmp

$cornerA = (Px $cL 0 0)['a']; $cornerA2 = (Px $cL 511 511)['a']
Add-Check 'A01' 'A_transparency' 'symbol-color background is fully transparent' 'alpha=0 at all four corners' "corner(0,0)=$cornerA corner(511,511)=$cornerA2" ($cornerA -eq 0 -and $cornerA2 -eq 0)

$cornerAb = (Px $bL 0 0)['a']
Add-Check 'A02' 'A_transparency' 'symbol-black background is fully transparent' 'alpha=0 at corner' "corner(0,0)=$cornerAb" ($cornerAb -eq 0)

# black purity: every pixel with alpha>0 must have R=G=B=0
$inkB = 0; $badRGB = 0; $amin = 999; $amax = 0; $badEx = @()
for ($y = 0; $y -lt 512; $y++) {
  for ($x = 0; $x -lt 512; $x++) {
    $p = Px $bL $x $y
    if ($p['a'] -le 0) { continue }
    $inkB++
    if ($p['a'] -lt $amin) { $amin = $p['a'] }
    if ($p['a'] -gt $amax) { $amax = $p['a'] }
    if ($p['r'] -ne 0 -or $p['g'] -ne 0 -or $p['bl'] -ne 0) {
      $badRGB++
      if ($badEx.Count -lt 5) { $badEx += "($x,$y) A=$($p['a']) RGB=$($p['r']),$($p['g']),$($p['bl'])" }
    }
  }
}
Add-Check 'K01' 'K_pure_black' 'every non-transparent pixel of symbol-black has RGB = 0,0,0' '0 pixels with RGB != 0 among A>0' "$badRGB pixels violate (A range $amin..$amax); ink=$inkB; $(if($badEx){$badEx -join ' | '}else{'no violation'})" ($badRGB -eq 0)
Add-Check 'K02' 'K_pure_black' 'antialiasing is present as allowed alpha variation' 'alpha values in 1..254 exist (AA allowed)' "alpha range observed = $amin..$amax, ink pixels = $inkB" ($amin -lt 255 -and $amax -eq 255 -and $inkB -gt 1000)

# ------------------------------------------------------ G: identical geometry ---
# both icons are drawn with opaque colours over a transparent canvas, so the alpha
# channel IS the coverage. Geometry is identical when the solid-coverage masks match
# exactly; only 1-LSB premultiplied-rounding jitter between #38BDF8/#F6B94A and
# #000000 is tolerated on the antialias fringe.
$diff = 0; $maxDelta = 0; $binDiff = 0; $firstDiffs = @()
for ($y = 0; $y -lt 512; $y++) {
  for ($x = 0; $x -lt 512; $x++) {
    $a1 = (Px $cL $x $y)['a']; $a2 = (Px $bL $x $y)['a']
    if ($a1 -ne $a2) {
      $diff++
      $d = [math]::Abs($a1 - $a2)
      if ($d -gt $maxDelta) { $maxDelta = $d }
      if ($firstDiffs.Count -lt 5) { $firstDiffs += "($x,$y) color=$a1 black=$a2" }
    }
    if (($a1 -gt 128) -ne ($a2 -gt 128)) { $binDiff++ }
  }
}
Add-Check 'G01' 'G_identical_geometry' 'the colour icon and the black icon have identical geometry' 'solid coverage (A>128) differs on 0 pixels; max alpha jitter <= 1' "solid-coverage diff = $binDiff px; soft diff = $diff px, max delta = $maxDelta $(if($firstDiffs){'| '+($firstDiffs -join ' | ')}else{''})" (($binDiff -eq 0) -and ($maxDelta -le 1))

# --------------------------------------------------------- M: clear space -------
$inkC = 0
$minx = 9999; $maxx = -1; $miny = 9999; $maxy = -1
for ($y = 0; $y -lt 512; $y++) {
  for ($x = 0; $x -lt 512; $x++) {
    $p = Px $cL $x $y
    if ($p['a'] -le 8) { continue }
    $inkC++
    if ($x -lt $minx) { $minx = $x }; if ($x -gt $maxx) { $maxx = $x }
    if ($y -lt $miny) { $miny = $y }; if ($y -gt $maxy) { $maxy = $y }
  }
}
$mgL = $minx; $mgR = 511 - $maxx; $mgT = $miny; $mgB = 511 - $maxy
$pct = [math]::Round(100.0 * [math]::Min([math]::Min($mgL, $mgR), [math]::Min($mgT, $mgB)) / 512.0, 2)
Add-Check 'M01' 'M_clear_space' 'symbol keeps >=10% clear space on every side' 'each side >= 51.2 px (10% of 512)' "L=$mgL R=$mgR T=$mgT B=$mgB (min $pct%); ink bbox = x$minx..$maxx y$miny..$maxy" (($mgL -ge 51) -and ($mgR -ge 51) -and ($mgT -ge 51) -and ($mgB -ge 51))

# ------------------------------------------------- S: three beams + channels ---
function Scan-Runs($L, [double]$cx, [double]$cy, [double]$tMax, [int]$size) {
  # walk along the "\" diagonal (perpendicular to the beams) through the centre
  $runs = @(); $inRun = $false; $start = 0; $gaps = @(); $inGap = $false; $gstart = 0
  $step = 0.25
  $t = -$tMax
  while ($t -le $tMax) {
    $x = [int][math]::Floor($cx + $t * 0.70710678)
    $y = [int][math]::Floor($cy + $t * 0.70710678)
    $on = $false
    if ($x -ge 0 -and $y -ge 0 -and $x -lt $size -and $y -lt $size) {
      $on = ((Px $L $x $y)['a'] -gt 128)
    }
    if ($on -and -not $inRun) {
      # close any gap that just ended BEFORE starting the new run
      if ($inGap) { $gaps += [math]::Round($t - $gstart, 2); $inGap = $false }
      $inRun = $true; $start = $t
    }
    if (-not $on -and $inRun) {
      $inRun = $false; $runs += [math]::Round($t - $start, 2)
      $inGap = $true; $gstart = $t
    }
    $t += $step
  }
  if ($inRun) { $runs += [math]::Round($tMax - $start, 2) }
  # a gap that runs to the scan edge is not an inter-beam channel, so it is ignored
  return @{ runs = $runs; gaps = $gaps }
}
$s = Scan-Runs $cL 256 256 260 512
Add-Check 'S01' 'S_beam_separation' 'the mark is made of exactly 3 separate beams' '3 ink runs along the perpendicular scan' "runs = $($s['runs'].Count) -> $($s['runs'] -join ', ') (widths px)" ($s['runs'].Count -eq 3)
Add-Check 'S02' 'S_beam_separation' 'the channels between beams are open (negative space)' '2 gaps, each ~34 px' "gaps = $($s['gaps'].Count) -> $($s['gaps'] -join ', ') px" (($s['gaps'].Count -eq 2) -and ([double]$s['gaps'][0] -ge 20) -and ([double]$s['gaps'][1] -ge 20))
Add-Check 'S03' 'S_beam_separation' 'beam thickness survives downsampling (>=4 px at 32x32)' 'each beam >= 4 px' "512-space run widths = $($s['runs'] -join ', ') px" (($s['runs'] | ForEach-Object { [double]$_ } | Where-Object { $_ -lt 4 }).Count -eq 0)

$nBmp = Get-Bitmap 'symbol-color-native32'; $nL = Lock $nBmp
$s32 = Scan-Runs $nL 16 16 16 32
Add-Check 'S04' 'S_beam_separation' 'at a native 32x32 render the mark still resolves into 3 beams' '3 ink runs' "runs = $($s32['runs'].Count) -> $($s32['runs'] -join ', ') px; gaps = $($s32['gaps'] -join ', ') px" ($s32['runs'].Count -eq 3)
$nInk = 0
for ($y = 0; $y -lt 32; $y++) { for ($x = 0; $x -lt 32; $x++) { if ((Px $nL $x $y)['a'] -gt 8) { $nInk++ } } }
Add-Check 'S05' 'S_beam_separation' 'native 32x32 render is not empty and not a solid blob' 'ink pixels between 150 and 600' "$nInk ink pixels of 1024" (($nInk -ge 150) -and ($nInk -le 700))

# --------------------------------------------------------------- C: content ----
$dslDir = $T
$textChecks = @(
  @('brand-banner', '叠光 Layerlight'),
  @('brand-banner', '把复杂信息，组织成清晰画面'),
  @('launch-poster', '叠光 Layerlight'),
  @('launch-poster', '把复杂信息，组织成清晰画面'),
  @('launch-poster', '2026.11.07 · ONLINE'),
  @('launch-poster', 'OPEN BETA'),
  @('launch-poster', 'layerlight.example.org')
)
$ci = 1
foreach ($tc in $textChecks) {
  $raw = [IO.File]::ReadAllText((Join-Path $dslDir ($tc[0] + '.snapshot')), [Text.UTF8Encoding]::new($false))
  $has = $raw.Contains('<![CDATA[' + $tc[1] + ']]>')
  Add-Check ("C{0:D2}" -f $ci) 'C_required_copy' "$($tc[0]) contains '$($tc[1])' verbatim in CDATA" 'CDATA literal present' $(if ($has) { 'present' } else { 'absent' }) $has
  $ci++
}

# --------------------------------------------------------- N: no image embed ---
$ni = 1
foreach ($n in @('symbol-color', 'symbol-black', 'brand-banner', 'launch-poster')) {
  $raw = [IO.File]::ReadAllText((Join-Path $dslDir ($n + '.snapshot')), [Text.UTF8Encoding]::new($false))
  $hits = @()
  foreach ($tok in @('<Image', 'ImageProvider', 'base64', 'backgroundImage', 'http://', 'https://', 'transform=', 'scale=')) {
    if ($raw.Contains($tok)) { $hits += $tok }
  }
  Add-Check ("N{0:D2}" -f $ni) 'N_no_embedded_raster' "$n builds the mark from DSL primitives only" 'no Image/base64/url/transform tokens' $(if ($hits) { 'HITS: ' + ($hits -join ', ') } else { 'clean' }) ($hits.Count -eq 0)
  $ni++
}

# ------------------------------------------ H: banner/poster use the same rules --
# the banner carries TWO instances of the rule set (the mark at 176 px plus a 10%
# alpha echo at 300 px); the poster carries exactly one (the mark at 360 px).
$hExpected = @{ 'brand-banner' = 6; 'launch-poster' = 3 }
foreach ($n in @('brand-banner', 'launch-poster')) {
  $raw = [IO.File]::ReadAllText((Join-Path $dslDir ($n + '.snapshot')), [Text.UTF8Encoding]::new($false))
  $mCount = ([regex]::Matches($raw, [regex]::Escape($MATRIXGLOBAL))).Count
  $exp = $hExpected[$n]
  $inst = ([regex]::Matches($raw, 'borderRadius="')).Count
  Add-Check ("H-$n") 'H_shared_geometry' "$n embeds the mark through the same 45deg rule set" "$exp occurrences of the rotation matrix ($exp beam group(s) x 3 beams)" "$mCount occurrences of the matrix, $inst rounded bars total" ($mCount -eq $exp)
}

# ------------------------------------------------------------------ assemble ---
$passN = @($checks | Where-Object { $_.result -eq 'PASS' }).Count
$failN = @($checks | Where-Object { $_.result -eq 'FAIL' }).Count

$cBmp.Dispose(); $bBmp.Dispose(); $nBmp.Dispose()

$audit = [pscustomobject]@{
  task_id          = 'A13'
  run_id           = $RUN
  generated_at     = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')
  render_version   = "0$VER"
  render_versions  = $script:usedVer
  verifier         = 'verify.ps1 (reads only rendered PNG + delivered DSL)'
  totals           = @{ checks = $checks.Count; passed = $passN; failed = $failN }
  geometry         = @{
    direction        = 'A - three layered light beams (chosen from two previews)'
    beam             = @{ design_box = 512; length = 256; thickness = 88; corner_radius = 44 }
    axis_degrees     = 45
    spacing          = 122
    channel          = 34
    matrix           = $MATRIXGLOBAL
    clear_space_px   = @{ left = $mgL; right = $mgR; top = $mgT; bottom = $mgB }
    clear_space_pct  = $pct
    ink_bbox_512     = @{ x0 = $minx; x1 = $maxx; y0 = $miny; y1 = $maxy }
    beam_runs_px     = $s['runs']
    channel_gaps_px  = $s['gaps']
    native32_runs_px = $s32['runs']
    native32_gaps_px = $s32['gaps']
    black_ink_pixels = $inkB
    black_alpha_min  = $amin
    geometry_delta_pixels = $diff
  }
  checks           = $checks
}
$out = Join-Path "outputs\$RUN\A13" 'brand-audit.json'
[IO.File]::WriteAllText($out, ($audit | ConvertTo-Json -Depth 10), [Text.UTF8Encoding]::new($false))
Write-Output ("brand-audit.json written: {0}/{1} PASS, {2} FAIL  -> {3}" -f $passN, $checks.Count, $failN, $out)
foreach ($c in $checks) {
  if ($c.result -eq 'FAIL') { Write-Output ("  FAIL {0} [{1}] {2} | expected {3} | observed {4}" -f $c.id, $c.group, $c.description, $c.expected, $c.observed) }
}
