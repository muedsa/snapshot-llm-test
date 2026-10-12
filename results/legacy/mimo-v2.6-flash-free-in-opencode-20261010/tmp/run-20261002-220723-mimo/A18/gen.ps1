param(
  [Parameter(Mandatory=$true)][ValidateSet("A","B")][string]$Variant,
  [Parameter(Mandatory=$true)][string]$OutDsl,
  [Parameter(Mandatory=$true)][string]$OutGeom
)
$ErrorActionPreference = 'Stop'
[Threading.Thread]::CurrentThread.CurrentCulture   = [cultureinfo]::InvariantCulture
[Threading.Thread]::CurrentThread.CurrentUICulture = [cultureinfo]::InvariantCulture
$utf8 = New-Object System.Text.UTF8Encoding($false)
$D2R  = [Math]::PI / 180.0

function F([double]$v) {
  $r = [Math]::Round($v, 2)
  if ([Math]::Abs($r) -lt 0.005) { $r = 0.0 }
  return $r.ToString("0.##", [cultureinfo]::InvariantCulture)
}
function MF([double]$v) {
  $r = [Math]::Round($v, 6)
  if ([Math]::Abs($r) -lt 0.0000005) { $r = 0.0 }
  return $r.ToString("0.######", [cultureinfo]::InvariantCulture)
}

# ---------------------------------------------------------------- design tokens --
$C_W = 1600; $C_H = 1000
$bg        = "#0B1220"
$panelFill = "#101B2E"
$panelBrd  = "#23324A"
$cBlue     = "#3B82F6"
$cOrange   = "#F59E0B"
$cGray     = "#94A3B8"
$cLine     = "#CBD5E1"
$cNode     = "#FFFFFF"
$cPort     = "#0B1220"
$cTitle    = "#F8FAFC"
$cAct      = "#E2E8F0"
$font      = "Noto Sans CJK SC"
$TITLE     = "同一系统的三幕演化"
$names     = @("第一幕 · 集中", "第二幕 · 过载", "第三幕 · 重新分配")

$NODE  = 64; $NODE_H = 32; $NODE_R = 18
$UNIT  = 36; $UNIT_R = 18
$TIP   = 46.0; $LEG = 9.0; $ATH = 3.0   # arrow tip radius, leg length, thickness
$LNH   = 4.0                             # link thickness
$CORNER_EXTENT = 37.8                    # rounded-square half-extreme (14*sqrt2 + 18)

# ---------------------------------------------------------------------- units ----
$units = @()
for ($i = 1; $i -le 15; $i++) {
  $id = "U{0:D2}" -f $i
  if     ($i -le 5)  { $cn = "blue";   $hex = $cBlue }
  elseif ($i -le 10) { $cn = "orange"; $hex = $cOrange }
  else               { $cn = "gray";   $hex = $cGray }
  $units += [pscustomobject]@{ idx = $i; id = $id; color = $cn; hex = $hex }
}
# act-3 assignment: 5 per node, every node sees >= 2 colours, colour totals preserved
$assign = @()
$assign += ,@("U01","U02","U06","U07","U11")
$assign += ,@("U03","U04","U08","U12","U13")
$assign += ,@("U05","U09","U10","U14","U15")
$nodeOf = @{}
for ($g = 0; $g -lt 3; $g++) { foreach ($u in $assign[$g]) { $nodeOf[$u] = "N$($g+1)" } }

# -------------------------------------------------------------------- geometry ---
function Ring([double]$cx, [double]$cy, [int]$n, [double]$r, [double]$a0) {
  $o = @()
  for ($k = 0; $k -lt $n; $k++) {
    $a = ($a0 + $k * 360.0 / $n) * $D2R
    $o += [pscustomobject]@{ x = $cx + $r * [Math]::Cos($a); y = $cy + $r * [Math]::Sin($a); a = $a0 + $k * 360.0 / $n }
  }
  return $o
}
function EllipseRing([double]$cx, [double]$cy, [int]$n, [double]$rx, [double]$ry, [double]$a0) {
  $o = @()
  for ($k = 0; $k -lt $n; $k++) {
    $deg = $a0 + $k * 360.0 / $n
    $a = $deg * $D2R
    $o += [pscustomobject]@{ x = $cx + $rx * [Math]::Cos($a); y = $cy + $ry * [Math]::Sin($a); a = $deg }
  }
  return $o
}

# ------------------------------------------------------------------- emitters ----
function Bar([double]$x1, [double]$y1, [double]$x2, [double]$y2, [string]$col, [double]$th) {
  $dx = $x2 - $x1; $dy = $y2 - $y1
  $len = [Math]::Sqrt($dx * $dx + $dy * $dy)
  $o = New-Object System.Collections.Generic.List[string]
  if ($len -lt 1.0) { return $o }
  $mx = ($x1 + $x2) / 2.0; $my = ($y1 + $y2) / 2.0
  $ang = [Math]::Atan2($dy, $dx)
  $c = [Math]::Cos($ang); $s = [Math]::Sin($ang)
  $m = "(" + (MF $c) + "," + (MF $s) + ",0,0," + (MF (-$s)) + "," + (MF $c) + ",0,0,0,0,1,0,0,0,0,1)"
  $L = F ($mx - $len / 2.0); $T = F ($my - $th / 2.0); $W = F $len; $H = F $th
  $o.Add('      <Positioned left="' + $L + '" top="' + $T + '" width="' + $W + '" height="' + $H + '">')
  $o.Add('        <Transform matrix="' + $m + '" alignment="(0,0)">')
  $o.Add('          <Container width="' + $W + '" height="' + $H + '" color="' + $col + '"/>')
  $o.Add('        </Transform>')
  $o.Add('      </Positioned>')
  return $o
}

# chevron pointing along (ux,uy) [node -> unit]; tip sits at the node boundary
function Arrow([double]$tipx, [double]$tipy, [double]$ux, [double]$uy, [string]$col) {
  $o = New-Object System.Collections.Generic.List[string]
  $base = [Math]::Atan2($uy, $ux)
  foreach ($sg in @(1.0, -1.0)) {
    $a = $base + $sg * 30.0 * $D2R
    $ex = $tipx + $LEG * [Math]::Cos($a)
    $ey = $tipy + $LEG * [Math]::Sin($a)
    $b = Bar $tipx $tipy $ex $ey $col $ATH
    foreach ($l in $b) { $o.Add($l) }
  }
  return $o
}

function NodeBox([double]$cx, [double]$cy, [bool]$dilated) {
  $o = New-Object System.Collections.Generic.List[string]
  $o.Add('      <Positioned left="' + (F ($cx - 32)) + '" top="' + (F ($cy - 32)) + '" width="64" height="64">')
  $o.Add('        <Container width="64" height="64" color="' + $cNode + '" borderRadius="18"/>')
  $o.Add('      </Positioned>')
  if ($dilated) {
    $o.Add('      <Positioned left="' + (F ($cx - 26)) + '" top="' + (F ($cy - 11)) + '" width="52" height="22">')
    $o.Add('        <Container width="52" height="22" color="' + $cPort + '" borderRadius="11"/>')
  } else {
    $o.Add('      <Positioned left="' + (F ($cx - 13)) + '" top="' + (F ($cy - 13)) + '" width="26" height="26">')
    $o.Add('        <Container width="26" height="26" color="' + $cPort + '" borderRadius="13"/>')
  }
  $o.Add('      </Positioned>')
  return $o
}
function UnitDot([double]$cx, [double]$cy, [string]$hex) {
  $o = New-Object System.Collections.Generic.List[string]
  $o.Add('      <Positioned left="' + (F ($cx - 18)) + '" top="' + (F ($cy - 18)) + '" width="36" height="36">')
  $o.Add('        <Container width="36" height="36" color="' + $hex + '" borderRadius="18"/>')
  $o.Add('      </Positioned>')
  return $o
}

# --------------------------------------------------------------------- layout ----
if ($Variant -eq "A") {
  $bandX = 40; $bandW = 1520; $bandH = 294
  $bandY = @(88, 392, 696)
  $nodeXs = @(400.0, 800.0, 1200.0)
  $nodeYs = @(235.0, 539.0, 843.0)      # one row per act
} else {
  $panX = @(40, 560, 1080); $panW = 480; $panY = 130; $panH = 840
  $nameY = @(84, 84, 84)
  $nodeXs = @(280.0, 800.0, 1320.0)      # one column per act
  $nodeYs = @(270.0, 550.0, 830.0)       # node row (same in every act)
}

function PanelRect([int]$ai) {
  if ($Variant -eq "A") { return @{ x = $bandX; y = $bandY[$ai]; w = $bandW; h = $bandH } }
  return @{ x = [double]$panX[$ai]; y = [double]$panY; w = [double]$panW; h = [double]$panH }
}
function NodeAt([int]$ai, [int]$ni) {
  if ($Variant -eq "A") { return @{ x = $nodeXs[$ni]; y = $nodeYs[$ai] } }
  return @{ x = $nodeXs[$ai]; y = $nodeYs[$ni] }
}

# unit positions per act -----------------------------------------------------------
$actPos = @()   # array of 3 arrays of 15 {x,y}
if ($Variant -eq "A") {
  $c = NodeAt 0 1
  $p1 = @(EllipseRing $c.x $c.y 5 110 76 0) + @(EllipseRing $c.x $c.y 10 285 118 18)
  $c = NodeAt 1 1
  $p2 = @(Ring $c.x $c.y 5 64 -90) + @(Ring $c.x $c.y 10 94 -72)
  $p3 = @()
  for ($g = 0; $g -lt 3; $g++) { $nd = NodeAt 2 $g; $p3 += @(Ring $nd.x $nd.y 5 90 -90) }
  $actPos = @(); $actPos += ,$p1; $actPos += ,$p2; $actPos += ,$p3
} else {
  $c = NodeAt 0 1
  $p1 = @(Ring $c.x $c.y 4 105 -90) + @(Ring $c.x $c.y 5 155 -54) + @(Ring $c.x $c.y 6 205 -90)
  $c = NodeAt 1 1
  $p2 = @(Ring $c.x $c.y 5 64 -90) + @(Ring $c.x $c.y 10 94 -72)
  $p3 = @()
  for ($g = 0; $g -lt 3; $g++) { $nd = NodeAt 2 $g; $p3 += @(Ring $nd.x $nd.y 5 90 -90) }
  $actPos = @(); $actPos += ,$p1; $actPos += ,$p2; $actPos += ,$p3
}

# assign ids: act 1 and 2 keep id order; act 3 follows $assign groups
# Interleave colours into act-1/act-2 positions so that neither colour nor ID
# encodes position: any run of positions sees blue/orange/grey in turn.
$perm = @(0,5,10,1,6,11,2,7,12,3,8,13,4,9,14)
$actUnits = @()
for ($ai0 = 0; $ai0 -lt 2; $ai0++) {
  $rows = @()
  for ($k = 0; $k -lt 15; $k++) {
    $rows += [pscustomobject]@{ u = $units[$perm[$k]]; pos = $actPos[$ai0][$k]; node = "N2" }
  }
  $actUnits += ,$rows
}
$g3 = @()
for ($g = 0; $g -lt 3; $g++) {
  $slot = 0
  foreach ($uid in $assign[$g]) {
    $u = $units | Where-Object { $_.id -eq $uid }
    $g3 += [pscustomobject]@{ u = $u; pos = $actPos[2][($g * 5 + $slot)]; node = "N$($g+1)" }
    $slot++
  }
}
$actUnits += ,$g3
Write-Output ("diag: actPos={0}x{1}  actUnits={2}  a1={3} a2={4} a3={5}  a3[0].pos=({6},{7}) id={8}" -f `
  @($actPos).Count, @($actPos[0]).Count, @($actUnits).Count, @($actUnits[0]).Count, `
  @($actUnits[1]).Count, @($actUnits[2]).Count, @($actUnits[2])[0].pos.x, @($actUnits[2])[0].pos.y, @($actUnits[2])[0].u.id)

# ------------------------------------------------------------------- assembly ----
$lines = New-Object System.Collections.Generic.List[string]
$geomActs = @()
$problems = New-Object System.Collections.Generic.List[string]

# ---- root ---------------------------------------------------------------------
$lines.Add('<Snapshot type="png" background="' + $bg + '">')
$lines.Add('  <Container width="' + $C_W + '" height="' + $C_H + '" color="' + $bg + '">')
$lines.Add('    <Stack>')

# ---- panels / names -----------------------------------------------------------
for ($ai = 0; $ai -lt 3; $ai++) {
  $pr = PanelRect $ai
  $lines.Add('      <Positioned left="' + (F $pr.x) + '" top="' + (F $pr.y) + '" width="' + (F $pr.w) + '" height="' + (F $pr.h) + '">')
  $lines.Add('        <Container width="' + (F $pr.w) + '" height="' + (F $pr.h) + '" color="' + $panelFill + '" borderRadius="14" border="1 SOLID ' + $panelBrd + '"/>')
  $lines.Add('      </Positioned>')
}

# ---- links (behind everything else) ------------------------------------------
$linkRows = @()
for ($ai = 0; $ai -lt 3; $ai++) {
  if ($Variant -eq "A") { $hero = NodeAt $ai 1 } else { $hero = NodeAt $ai 1 }
  $list = $actUnits[$ai]
  foreach ($e in $list) {
    if ($ai -eq 2) {
      $gid = [int]($e.node.Substring(1)) - 1
      $tgt = NodeAt 2 $gid
    } else { $tgt = $hero }
    $px = $e.pos.x; $py = $e.pos.y
    $b = Bar $px $py $tgt.x $tgt.y $cLine $LNH
    foreach ($l in $b) { $lines.Add($l) }
    $linkRows += [pscustomobject]@{ act = ($ai + 1); unit = $e.u.id; node = $(if ($ai -eq 2) { $e.node } else { "N2" }); from = @($px, $py); to = @($tgt.x, $tgt.y) }
  }
}

# ---- arrows (act 1 and 3 only; act 2 has no room by construction) --------------
for ($ai = 0; $ai -lt 3; $ai++) {
  if ($ai -eq 1) { continue }
  $list = $actUnits[$ai]
  foreach ($e in $list) {
    if ($ai -eq 2) { $gid = [int]($e.node.Substring(1)) - 1; $tgt = NodeAt 2 $gid }
    else           { $tgt = NodeAt $ai 1 }
    $dx = $e.pos.x - $tgt.x; $dy = $e.pos.y - $tgt.y
    $d = [Math]::Sqrt($dx * $dx + $dy * $dy)
    if ($d -lt 1) { continue }
    $ux = $dx / $d; $uy = $dy / $d
    $tipx = $tgt.x + $TIP * $ux; $tipy = $tgt.y + $TIP * $uy
    $b = Arrow $tipx $tipy $ux $uy $cLine
    foreach ($l in $b) { $lines.Add($l) }
  }
}

# ---- nodes ---------------------------------------------------------------------
$geomNodes = @()
for ($ai = 0; $ai -lt 3; $ai++) {
  for ($ni = 0; $ni -lt 3; $ni++) {
    $p = NodeAt $ai $ni
    $dil = ($ai -eq 1 -and $ni -eq 1)
    $b = NodeBox $p.x $p.y $dil
    foreach ($l in $b) { $lines.Add($l) }
  }
}

# ---- units ---------------------------------------------------------------------
for ($ai = 0; $ai -lt 3; $ai++) {
  $list = $actUnits[$ai]
  foreach ($e in $list) {
    if ($ai -eq 2) { $px = $e.pos.x; $py = $e.pos.y; $hex = $e.u.hex }
    else           { $px = $e.pos.x; $py = $e.pos.y; $hex = $e.u.hex }
    $b = UnitDot $px $py $hex
    foreach ($l in $b) { $lines.Add($l) }
  }
}

# ---- title + act names ---------------------------------------------------------
$lines.Add('      <Positioned left="0" top="16" width="1600" height="60">')
$lines.Add('        <Text fontSize="40" fontFamily="' + $font + '" fontStyle="BOLD" textAlign="CENTER" color="' + $cTitle + '">' + $TITLE + '</Text>')
$lines.Add('      </Positioned>')
for ($ai = 0; $ai -lt 3; $ai++) {
  $pr = PanelRect $ai
  if ($Variant -eq "A") {
    $nx = $pr.x + 24; $ny = $pr.y + 16; $w = 500; $al = "START"
  } else {
    $nx = $pr.x; $ny = $nameY[$ai]; $w = $pr.w; $al = "CENTER"
  }
  $lines.Add('      <Positioned left="' + (F $nx) + '" top="' + (F $ny) + '" width="' + $w + '" height="56">')
  $lines.Add('        <Text fontSize="32" fontFamily="' + $font + '" fontStyle="BOLD" textAlign="' + $al + '" color="' + $cAct + '">' + $names[$ai] + '</Text>')
  $lines.Add('      </Positioned>')
}

$lines.Add('    </Stack>')
$lines.Add('  </Container>')
$lines.Add('</Snapshot>')

# ------------------------------------------------------------------ self checks --
for ($ai = 0; $ai -lt 3; $ai++) {
  $pr = PanelRect $ai
  $list = $actUnits[$ai]
  $minPair = 1e9; $minNode = 1e9
  for ($i = 0; $i -lt 15; $i++) {
    $a = $list[$i].pos
    for ($j = $i + 1; $j -lt 15; $j++) {
      $b2 = $list[$j].pos
      $d = [Math]::Sqrt(($a.x - $b2.x) * ($a.x - $b2.x) + ($a.y - $b2.y) * ($a.y - $b2.y))
      if ($d -lt $minPair) { $minPair = $d }
    }
    $dx = $a.x - $pr.x; $dy = $a.y - $pr.y
    if ($dx - 18 -lt -0.5 -or $dx + 18 -gt $pr.w + 0.5 -or $dy - 18 -lt -0.5 -or $dy + 18 -gt $pr.h + 0.5) {
      $problems.Add("act $($ai+1): unit $($list[$i].u.id) outside panel ($([Math]::Round($dx,1)),$([Math]::Round($dy,1)))")
    }
    for ($ni = 0; $ni -lt 3; $ni++) {
      $nd = NodeAt $ai $ni
      $d = [Math]::Sqrt(($a.x - $nd.x) * ($a.x - $nd.x) + ($a.y - $nd.y) * ($a.y - $nd.y))
      if ($d - 18 - $CORNER_EXTENT -lt $minNode) { $minNode = $d - 18 - $CORNER_EXTENT }
    }
  }
  if ($minPair -lt 36.0) { $problems.Add("act $($ai+1): units overlap, min centre distance = $([Math]::Round($minPair,2)) (< 36)") }
  if ($minNode -lt -0.4) { $problems.Add("act $($ai+1): unit overlaps a node by $([Math]::Round(-$minNode,2)) px") }
  Write-Output ("act {0}: min unit-unit centre distance = {1}  (need >= 36)   min unit-node gap = {2}" -f ($ai+1), [Math]::Round($minPair,2), [Math]::Round($minNode,2))
}

# ------------------------------------------------------------------ emit files ---
[IO.File]::WriteAllText($OutDsl, ([string]::Join("`n", $lines.ToArray()) + "`n"), $utf8)

$geom = [ordered]@{
  schema   = "snapshot-suite/story-geometry/v1"
  variant  = $Variant
  canvas   = @{ width = $C_W; height = $C_H; background = $bg }
  tokens   = @{ unit_diameter = 36; unit_radius = 18; node_size = 64; node_radius = 18; link_thickness = $LNH; arrow_tip_radius = $TIP }
  panels   = @()
  acts     = @()
}
for ($ai = 0; $ai -lt 3; $ai++) {
  $pr = PanelRect $ai
  $geom.panels += [pscustomobject]@{ act = ($ai+1); x = $pr.x; y = $pr.y; width = $pr.w; height = $pr.h; name = $names[$ai] }
}
for ($ai = 0; $ai -lt 3; $ai++) {
  $nodeRows = @()
  for ($ni = 0; $ni -lt 3; $ni++) { $p = NodeAt $ai $ni; $nodeRows += [pscustomobject]@{ id = "N$($ni+1)"; x = [Math]::Round($p.x,2); y = [Math]::Round($p.y,2); size = 64 } }
  $uRows = @()
  $list = $actUnits[$ai]
  foreach ($e in $list) {
    $recv = "N2"
    if ($ai -eq 2) { $recv = $e.node }
    $uRows += [pscustomobject]@{ id = $e.u.id; color = $e.u.color; hex = $e.u.hex; x = [Math]::Round($e.pos.x,2); y = [Math]::Round($e.pos.y,2); radius = $e.pos.a; receiving_node = $recv }
  }
  $geom.acts += [pscustomobject]@{
    act         = ($ai+1)
    name        = $names[$ai]
    hero        = "N2"
    nodes       = $nodeRows
    units       = $uRows
    link_count  = 15
    arrowed     = ($ai -ne 1)
  }
}
$geom.checks = [pscustomobject]@{ problems = @($problems); }
[IO.File]::WriteAllText($OutGeom, (($geom | ConvertTo-Json -Depth 8) + "`n"), $utf8)

Write-Output "variant $Variant -> $OutDsl ($($lines.Count) lines), $OutGeom"
if ($problems.Count -gt 0) { foreach ($p in $problems) { Write-Output "  PROBLEM: $p" } }
