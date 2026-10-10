# design-a23.ps1 - search for frame-01 start positions that are (a) genuinely dispersed
# and (b) never let two 60x60 unit boxes overlap at ANY point of the 6-frame path.
#
# Construction: each unit moves radially along its own ray from the frame centre,
#   p_i(t) = centre + rho_i(t) * unitvector(final_i - centre),  rho_i(t) = s_i + t*(r_i - s_i)
# Different rays only meet at the centre (which no unit reaches), so the only real
# risk is nearby rays / same ray.  Feasibility is verified exhaustively, not assumed.
param(
  [string]$DataPath = 'outputs\run-20261002-220723-mimo\A23\frame-data.json',
  [string]$OutPath  = 'tmp\run-20261002-220723-mimo\A23\start-design.json',
  [int]$Trials = 400000,
  [int]$Seed = 20261005
)
$ErrorActionPreference = 'Stop'
[Threading.Thread]::CurrentThread.CurrentCulture   = [cultureinfo]::InvariantCulture
[Threading.Thread]::CurrentThread.CurrentUICulture = [cultureinfo]::InvariantCulture
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $root
$utf8 = New-Object System.Text.UTF8Encoding($false)

$fd = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText($DataPath, $utf8))
$U = 60.0; $H = $U / 2.0
$CX = 300.0; $CY = 300.0
$N = $fd.units.Count
if ($N -ne 12) { throw "expected 12 units, got $N" }

# ---------------------------------------------------------------- units + rays ----
$ids = @(); $fx = @(); $fy = @(); $ang = @(); $rad = @(); $ux = @(); $uy = @()
# NB: never name the loop variable $u - PowerShell variables are case-insensitive and
#     it would clobber the $U edge-length constant (that is exactly what happened once).
foreach ($un in $fd.units) {
  $x = [double]$un.frame_06_final.x; $y = [double]$un.frame_06_final.y
  $ids += $un.id; $fx += $x; $fy += $y
  $dx = ($x + $H) - $CX; $dy = ($y + $H) - $CY
  $r  = [Math]::Sqrt($dx * $dx + $dy * $dy)
  $rad += $r
  $ang += [Math]::Atan2($dy, $dx)
  $ux  += $dx / $r; $uy += $dy / $r
}

# ------------------------------------------------------------- feasibility fn -----
function Test-Layout([double[]]$s) {
  # returns @{ ok; minDistT0 (frame-01 dispersion); minDistAny (whole trajectory) }
  $minD = 1e9; $minD0 = 1e9
  # bounds
  for ($i = 0; $i -lt $N; $i++) {
    $x0 = $CX + $s[$i] * $ux[$i]; $y0 = $CY + $s[$i] * $uy[$i]
    if ($x0 - $H -lt 0 -or $x0 + $H -gt 600 -or $y0 - $H -lt 0 -or $y0 + $H -gt 600) {
      return @{ ok = $false; reason = "bounds:$($ids[$i])" }
    }
  }
  # overlap over a fine t grid
  $steps = 101
  for ($k = 0; $k -lt $steps; $k++) {
    $t = $k / ([double]($steps - 1))
    $px = New-Object double[] $N; $py = New-Object double[] $N
    for ($i = 0; $i -lt $N; $i++) {
      $rho = $s[$i] + $t * ($rad[$i] - $s[$i])
      $px[$i] = $CX + $rho * $ux[$i]
      $py[$i] = $CY + $rho * $uy[$i]
    }
    for ($a = 0; $a -lt ($N - 1); $a++) {
      for ($b = $a + 1; $b -lt $N; $b++) {
        $dx = [Math]::Abs($px[$a] - $px[$b])
        $dy = [Math]::Abs($py[$a] - $py[$b])
        $d  = [Math]::Sqrt($dx * $dx + $dy * $dy)
        if ($d -lt $minD) { $minD = $d }
        if ($k -eq 0 -and $d -lt $minD0) { $minD0 = $d }
        if ($dx -lt $U -and $dy -lt $U) { return @{ ok = $false; reason = "$($ids[$a])/$($ids[$b])@t=$([Math]::Round($t,3))" } }
      }
    }
  }
  return @{ ok = $true; minDistT0 = [Math]::Round($minD0, 2); minDistAny = [Math]::Round($minD, 2) }
}

# ------------------------------------------------------------ seeded sampling -----
$rng = New-Object System.Random($Seed)
$best = $null; $bestScore = -1.0; $feasible = 0
$LO = 75.0; $HI = 265.0
# unit order in frame-data.json is u01..u12 -> index 0..11
# same-ray pairs (inner, outer): u03(2)/u06(5) both point up, u08(7)/u11(10) both point down
$sameRay = @(2, 5, 7, 10)

for ($trial = 0; $trial -lt $Trials; $trial++) {
  # radius proposal: uniform, but same-ray pairs are forced apart by construction
  $s = New-Object double[] $N
  for ($i = 0; $i -lt $N; $i++) { $s[$i] = $LO + ($HI - $LO) * $rng.NextDouble() }
  for ($q = 0; $q -lt $sameRay.Count; $q += 2) {
    $a = $sameRay[$q]; $b = $sameRay[$q + 1]
    # rad[$b] > rad[$a] (u06/u11 are the outer ones) so s must obey the same order
    if ($s[$b] -lt $s[$a] + 65) { $s[$b] = $s[$a] + 65 }
    if ($s[$b] -gt $HI) { $s[$a] = $s[$b] - 65; if ($s[$a] -lt $LO) { $s[$b] = $LO + 65; $s[$a] = $LO } }
  }
  $r = Test-Layout $s
  if (-not $r.ok) { continue }
  $feasible++
  # score: dispersion of frame-01 itself (bigger = more scattered start state)
  if ($r.minDistT0 -gt $bestScore) { $bestScore = $r.minDistT0; $best = $s }
}
Write-Output ("trials={0}  feasible={1}  best frame-01 min pair distance = {2}px" -f $Trials, $feasible, $bestScore)
if ($null -eq $best) { throw 'no feasible start layout found - increase Trials or widen LO/HI' }

# ------------------------------------------------------------------ emit result ---
$entries = @()
for ($i = 0; $i -lt $N; $i++) {
  $sx = [Math]::Round($CX + $best[$i] * $ux[$i], 2)
  $sy = [Math]::Round($CY + $best[$i] * $uy[$i], 2)
  $entries += [pscustomobject][ordered]@{
    id = $ids[$i]
    ray_deg   = [Math]::Round([double]$ang[$i] * 180.0 / [Math]::PI, 2)
    final_r   = [Math]::Round($rad[$i], 2)
    start_r   = [Math]::Round($best[$i], 2)
    start_box_x = [Math]::Round($sx - $H, 2)
    start_box_y = [Math]::Round($sy - $H, 2)
    start_cx  = $sx; start_cy = $sy
    path_px   = [Math]::Round([Math]::Sqrt([Math]::Pow(($fx[$i] + $H) - $sx, 2) + [Math]::Pow(($fy[$i] + $H) - $sy, 2)), 2)
  }
}
$check = Test-Layout $best
$result = [pscustomobject][ordered]@{
  schema = 'snapshot-suite/a23-start-design/v1'
  method = 'radial dispersal: start_i = centre + s_i * unitvector(final_i - centre); each unit flies straight inward along its own ray'
  seed = $Seed; trials = $Trials; feasible_layouts = $feasible
  radius_range_px = @($LO, $HI)
  verified = [pscustomobject]@{
    t_samples = 101
    t_step = 0.01
    overlap_at_any_t = (-not $check.ok)
    min_pair_centre_distance_frame01_px = $check.minDistT0
    min_pair_centre_distance_whole_path_px = $check.minDistAny
    boxes_inside_canvas = $true
    same_ray_pairs = @(
      [pscustomobject]@{ pair = 'u03/u06'; note = 'both point up; start radii differ by >= 65px and keep the outer unit outer' },
      [pscustomobject]@{ pair = 'u08/u11'; note = 'both point down; same rule' }
    )
  }
  scatter_note = 'start radii are deliberately NOT proportional to final radii, so frame-01 reads as 12 scattered squares rather than a pre-formed figure'
  units = $entries
}
[IO.File]::WriteAllText($OutPath, (($result | ConvertTo-Json -Depth 8) + "`n"), $utf8)
Write-Output ("wrote {0}  ({1} bytes)" -f $OutPath, (Get-Item $OutPath).Length)
Write-Output ''
Write-Output ('{0,-5} {1,9} {2,9} {3,9} {4,9} {5,9} {6,9}' -f 'id', 'ray', 'final_r', 'start_r', 'box.x', 'box.y', 'path')
foreach ($e in $entries) {
  Write-Output ('{0,-5} {1,9} {2,9} {3,9} {4,9} {5,9} {6,9}' -f $e.id, $e.ray_deg, $e.final_r, $e.start_r, $e.start_box_x, $e.start_box_y, $e.path_px)
}
