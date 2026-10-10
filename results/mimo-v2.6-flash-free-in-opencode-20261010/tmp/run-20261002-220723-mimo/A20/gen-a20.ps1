param(
  [Parameter(Mandatory=$true)][string]$MarkersPath,
  [Parameter(Mandatory=$true)][string]$OutDsl,
  [Parameter(Mandatory=$true)][string]$OutLayout,
  [Parameter(Mandatory=$true)][string]$OutAudit,
  [Parameter(Mandatory=$true)][string]$OutReport
)
$ErrorActionPreference = 'Stop'
[Threading.Thread]::CurrentThread.CurrentCulture   = [cultureinfo]::InvariantCulture
[Threading.Thread]::CurrentThread.CurrentUICulture = [cultureinfo]::InvariantCulture
$utf8 = New-Object System.Text.UTF8Encoding($false)
trap { Write-Output ("SCRIPT-ERROR line={0} msg={1}" -f $_.InvocationInfo.ScriptLineNumber, $_.Exception.Message); Write-Output ("  line-text: " + $_.InvocationInfo.Line); break }

# ------------------------------------------------------------------ constants ---
$CW = 1600.0; $CH = 1100.0
$PX0 = 280.0; $PY0 = 160.0; $PW = 1040.0; $PH = 760.0
$PX1 = $PX0 + $PW   # 1320
$PY1 = $PY0 + $PH   # 920
$SX = $PW / 100.0   # 10.4 px per logical unit
$SY = $PH / 100.0   # 7.6  px per logical unit
$FS = 20
$LH = 40.0          # label box height
$LYMIN = 160.0; $LYMAX = 916.0; $LXMIN = 8.0; $LXMAX = 1592.0
$LABGAP = 6.0
$LEADMAX = 24.0
$PTD = 12.0; $PTR = 6.0
$TOPD = 26.0; $TOPR = 13.0

$C_BG = '#F8FAFC'; $C_PANEL = '#FFFFFF'; $C_GRID = '#E2E8F0'; $C_BORDER = '#475569'
$C_TXT = '#0F172A'; $C_MUT = '#475569'; $C_PT = '#2563EB'; $C_TOP = '#DC2626'
$C_LEAD = '#64748B'; $C_LABB = '#94A3B8'; $C_LABT = '#DC2626'; $C_GRIDMAJ = '#CBD5E1'

# ------------------------------------------------------------------- helpers ----
function EstW([string]$s, [double]$fs) {
  $w = 0.0
  foreach ($ch in $s.ToCharArray()) {
    $c = [int][char]$ch
    if ($c -gt 0x2E7F) { $w += $fs * 1.05 } else { $w += $fs * 0.60 }
  }
  return [double]([Math]::Ceiling($w) + 20)
}
function RectSep([double]$ax,[double]$ay,[double]$aw,[double]$ah,[double]$bx,[double]$by,[double]$bw,[double]$bh) {
  $dx = 0.0
  $t1 = $ax - ($bx + $bw); if ($t1 -gt $dx) { $dx = $t1 }
  $t2 = $bx - ($ax + $aw); if ($t2 -gt $dx) { $dx = $t2 }
  $dy = 0.0
  $t3 = $ay - ($by + $bh); if ($t3 -gt $dy) { $dy = $t3 }
  $t4 = $by - ($ay + $ah); if ($t4 -gt $dy) { $dy = $t4 }
  return [Math]::Sqrt(($dx * $dx) + ($dy * $dy))
}
function PtRectDist([double]$px,[double]$py,[double]$rx,[double]$ry,[double]$rw,[double]$rh) {
  $dx = [Math]::Max([Math]::Max($rx - $px, $px - ($rx + $rw)), 0.0)
  $dy = [Math]::Max([Math]::Max($ry - $py, $py - ($ry + $rh)), 0.0)
  if ($dx -eq 0.0 -and $dy -eq 0.0) { return 0.0 }
  return [Math]::Sqrt(($dx * $dx) + ($dy * $dy))
}
function PtSegDist([double]$px,[double]$py,[double]$x1,[double]$y1,[double]$x2,[double]$y2) {
  $vx = $x2 - $x1; $vy = $y2 - $y1
  $wx = $px - $x1; $wy = $py - $y1
  $l2 = ($vx * $vx) + ($vy * $vy)
  if ($l2 -lt 0.000001) { return [Math]::Sqrt(($wx * $wx) + ($wy * $wy)) }
  $t = (($wx * $vx) + ($wy * $vy)) / $l2
  if ($t -lt 0.0) { $t = 0.0 } elseif ($t -gt 1.0) { $t = 1.0 }
  $cx = $x1 + ($t * $vx); $cy = $y1 + ($t * $vy)
  return [Math]::Sqrt((($px - $cx) * ($px - $cx)) + (($py - $cy) * ($py - $cy)))
}
# returns 1 = proper crossing, 2 = collinear overlap, 0 = none
function SegCross([double]$ax,[double]$ay,[double]$bx,[double]$by,[double]$cx,[double]$cy,[double]$dx,[double]$dy) {
  $d1 = (($cx - $ax) * ($by - $ay)) - (($cy - $ay) * ($bx - $ax))
  $d2 = (($dx - $ax) * ($by - $ay)) - (($dy - $ay) * ($bx - $ax))
  $d3 = (($ax - $cx) * ($dy - $cy)) - (($ay - $cy) * ($dx - $cx))
  $d4 = (($bx - $cx) * ($dy - $cy)) - (($by - $cy) * ($dx - $cx))
  $s1 = 0; if ($d1 -gt 0) { $s1 = 1 } elseif ($d1 -lt 0) { $s1 = -1 }
  $s2 = 0; if ($d2 -gt 0) { $s2 = 1 } elseif ($d2 -lt 0) { $s2 = -1 }
  $s3 = 0; if ($d3 -gt 0) { $s3 = 1 } elseif ($d3 -lt 0) { $s3 = -1 }
  $s4 = 0; if ($d4 -gt 0) { $s4 = 1 } elseif ($d4 -lt 0) { $s4 = -1 }
  if (($s1 * $s2) -lt 0 -and ($s3 * $s4) -lt 0) { return 1 }
  if ($s1 -eq 0 -and $s2 -eq 0 -and $s3 -eq 0 -and $s4 -eq 0) {
    $horiz = [Math]::Abs($bx - $ax) -ge [Math]::Abs($by - $ay)
    if ($horiz) {
      $a0 = [Math]::Min($ax,$bx); $a1 = [Math]::Max($ax,$bx)
      $b0 = [Math]::Min($cx,$dx); $b1 = [Math]::Max($cx,$dx)
      $lo = [Math]::Max($a0,$b0); $hi = [Math]::Min($a1,$b1)
      if (($hi - $lo) -gt 0.5) { return 2 }
    } else {
      $a0 = [Math]::Min($ay,$by); $a1 = [Math]::Max($ay,$by)
      $b0 = [Math]::Min($cy,$dy); $b1 = [Math]::Max($cy,$dy)
      $lo = [Math]::Max($a0,$b0); $hi = [Math]::Min($a1,$b1)
      if (($hi - $lo) -gt 0.5) { return 2 }
    }
  }
  return 0
}
function SegRectHit([double]$x1,[double]$y1,[double]$x2,[double]$y2,[double]$rx,[double]$ry,[double]$rw,[double]$rh) {
  if ($rw -le 0 -or $rh -le 0) { return $false }
  $rx2 = $rx + $rw; $ry2 = $ry + $rh
  if ($x1 -ge $rx -and $x1 -le $rx2 -and $y1 -ge $ry -and $y1 -le $ry2) { return $true }
  if ($x2 -ge $rx -and $x2 -le $rx2 -and $y2 -ge $ry -and $y2 -le $ry2) { return $true }
  if ((SegCross $x1 $y1 $x2 $y2 $rx  $ry  $rx2 $ry ) -ne 0) { return $true }
  if ((SegCross $x1 $y1 $x2 $y2 $rx2 $ry  $rx2 $ry2) -ne 0) { return $true }
  if ((SegCross $x1 $y1 $x2 $y2 $rx2 $ry2 $rx  $ry2) -ne 0) { return $true }
  if ((SegCross $x1 $y1 $x2 $y2 $rx  $ry2 $rx  $ry ) -ne 0) { return $true }
  return $false
}
function Esc([string]$s) { return $s.Replace('&','&amp;').Replace('<','&lt;').Replace('>','&gt;') }

# ------------------------------------------------------------- reserved boxes ----
$RES = @(
  [pscustomobject]@{ n='title';      x=40.0;  y=26.0;  w=780.0; h=54.0 }
  [pscustomobject]@{ n='subtitle';   x=40.0;  y=84.0;  w=1100.0; h=30.0 }
  [pscustomobject]@{ n='top-note';   x=1160.0; y=84.0; w=400.0;  h=30.0 }
  [pscustomobject]@{ n='y-caption';  x=40.0;  y=156.0; w=224.0; h=30.0 }
  [pscustomobject]@{ n='ytick-100';  x=300.0; y=126.0; w=64.0; h=30.0 }
  [pscustomobject]@{ n='ytick-75';   x=300.0; y=316.0; w=64.0; h=30.0 }
  [pscustomobject]@{ n='ytick-50';   x=300.0; y=506.0; w=64.0; h=30.0 }
  [pscustomobject]@{ n='ytick-25';   x=300.0; y=696.0; w=64.0; h=30.0 }
  [pscustomobject]@{ n='ytick-0';    x=300.0; y=886.0; w=64.0; h=30.0 }
  [pscustomobject]@{ n='xtick-0';    x=280.0; y=926.0; w=56.0; h=30.0 }
  [pscustomobject]@{ n='xtick-25';   x=512.0; y=926.0; w=56.0; h=30.0 }
  [pscustomobject]@{ n='xtick-50';   x=772.0; y=926.0; w=56.0; h=30.0 }
  [pscustomobject]@{ n='xtick-75';   x=1032.0; y=926.0; w=56.0; h=30.0 }
  [pscustomobject]@{ n='xtick-100';  x=1292.0; y=926.0; w=56.0; h=30.0 }
  [pscustomobject]@{ n='x-caption';  x=280.0; y=966.0; w=620.0; h=30.0 }
  [pscustomobject]@{ n='top3-callout'; x=280.0; y=1014.0; w=1040.0; h=30.0 }
  [pscustomobject]@{ n='legend-1';   x=1364.0; y=966.0; w=232.0; h=30.0 }
  [pscustomobject]@{ n='legend-2';   x=1376.0; y=1014.0; w=220.0; h=30.0 }
)

# -------------------------------------------------------------------- points -----
$mk = [IO.File]::ReadAllText($MarkersPath) | ConvertFrom-Json
$vals = @($mk | ForEach-Object { [int]$_.value } | Sort-Object -Descending)
$cut = [int]$vals[2]
$PTS = @()
foreach ($m in $mk) {
  $ax = $PX0 + ([double]$m.x * $SX)
  $ay = $PY1 - ([double]$m.y * $SY)
  $t  = "$($m.id) $($m.name) $($m.value)"
  $isT = ([int]$m.value -ge $cut)
  $PTS += [pscustomobject]@{
    id=[string]$m.id; name=[string]$m.name; lx=[double]$m.x; ly=[double]$m.y; value=[int]$m.value
    ax=[Math]::Round($ax,2); ay=[Math]::Round($ay,2); text=$t; w=(EstW $t $FS)
    isTop3=$isT; exclR=$(if ($isT) { $TOPR } else { $PTR })
  }
}
if (@($PTS | Where-Object { $_.isTop3 }).Count -ne 3) { throw 'top-3 cut is ambiguous (tie at the boundary)' }

# density + nearest neighbour + plot-centre distance
for ($i = 0; $i -lt $PTS.Count; $i++) {
  $a = $PTS[$i]; $dens = 0; $nnD = 99999.0; $nnUx = 1.0; $nnUy = 0.0
  for ($j = 0; $j -lt $PTS.Count; $j++) {
    if ($i -eq $j) { continue }
    $b = $PTS[$j]
    $dx = $b.ax - $a.ax; $dy = $b.ay - $a.ay
    $d = [Math]::Sqrt(($dx*$dx)+($dy*$dy))
    if ($d -lt 140.0) { $dens++ }
    if ($d -lt $nnD -and $d -gt 0.1) { $nnD = $d; $nnUx = $dx/$d; $nnUy = $dy/$d }
  }
  $cdx = $a.ax - (($PX0+$PX1)/2); $cdy = $a.ay - (($PY0+$PY1)/2)
  $a | Add-Member -NotePropertyName dens -NotePropertyValue $dens
  $a | Add-Member -NotePropertyName nnD  -NotePropertyValue $nnD
  $a | Add-Member -NotePropertyName nnUx -NotePropertyValue $nnUx
  $a | Add-Member -NotePropertyName nnUy -NotePropertyValue $nnUy
  $a | Add-Member -NotePropertyName cd   -NotePropertyValue ([Math]::Sqrt(($cdx*$cdx)+($cdy*$cdy)))
}
$CENTER6 = @($PTS | Sort-Object -Property cd | Select-Object -First 6 | ForEach-Object { $_.id })
$ORDER = @($PTS | Sort-Object -Property @{Expression='dens';Descending=$true}, @{Expression='value';Descending=$true}, @{Expression='id';Ascending=$true})

# ------------------------------------------------------------- label placer ------
$GAPS = @(18,21,24,30,38,48,60,74,90,108,128,150,174,200,228,258,292,330,372,418)
$DIRS = @(
  [pscustomobject]@{ n='E';  ux=1.0;  uy=0.0 }
  [pscustomobject]@{ n='W';  ux=-1.0; uy=0.0 }
  [pscustomobject]@{ n='N';  ux=0.0;  uy=-1.0 }
  [pscustomobject]@{ n='S';  ux=0.0;  uy=1.0 }
  [pscustomobject]@{ n='NE'; ux=0.70710678; uy=-0.70710678 }
  [pscustomobject]@{ n='NW'; ux=-0.70710678; uy=-0.70710678 }
  [pscustomobject]@{ n='SE'; ux=0.70710678; uy=0.70710678 }
  [pscustomobject]@{ n='SW'; ux=-0.70710678; uy=0.70710678 }
)

function Cand-Box([object]$p,[string]$dn,[double]$ux,[double]$uy,[double]$g,[double]$s) {
  $W = $p.w; $H = $LH; $ax = $p.ax; $ay = $p.ay
  $bx = 0.0; $by = 0.0
  $c = 0.70710678
  switch ($dn) {
    'E'  { $bx = $ax + $g;            $by = $ay - ($H/2) }
    'W'  { $bx = $ax - $g - $W;       $by = $ay - ($H/2) }
    'N'  { $bx = $ax - ($W/2);        $by = $ay - $g - $H }
    'S'  { $bx = $ax - ($W/2);        $by = $ay + $g }
    'NE' { $bx = $ax + ($g*$c);       $by = $ay - ($g*$c) - $H }
    'NW' { $bx = $ax - ($g*$c) - $W;  $by = $ay - ($g*$c) - $H }
    'SE' { $bx = $ax + ($g*$c);       $by = $ay + ($g*$c) }
    'SW' { $bx = $ax - ($g*$c) - $W;  $by = $ay + ($g*$c) }
  }
  $bx = $bx + ($s * (-$uy))
  $by = $by + ($s * $ux)
  return ,@([Math]::Round($bx,1), [Math]::Round($by,1))
}

function Shift-Set([string]$dn,[double]$W) {
  if ($dn -eq 'E' -or $dn -eq 'W') { return ,@(-28.0,-19.0,-11.0,0.0,11.0,19.0,28.0) }
  if ($dn -eq 'N' -or $dn -eq 'S') {
    return ,@(-(($W/2)+14), -($W/2), -($W/3), -18.0, 0.0, 18.0, ($W/3), ($W/2), (($W/2)+14))
  }
  return ,@(-($W/4), 0.0, ($W/4))
}

$PENALTY = @{}
$PLACED = @()
$placeFail = New-Object System.Collections.Generic.List[string]

foreach ($p in $ORDER) {
  $cands = New-Object System.Collections.Generic.List[object]
  foreach ($d in $DIRS) {
    $shifts = Shift-Set $d.n $p.w
    foreach ($g in $GAPS) {
      foreach ($s in $shifts) {
        $bb = Cand-Box $p $d.n $d.ux $d.uy ([double]$g) ([double]$s)
        $bx = [double]$bb[0]; $by = [double]$bb[1]; $W = $p.w; $H = $LH
        if ($bx -lt $LXMIN -or ($bx+$W) -gt $LXMAX) { continue }
        if ($by -lt $LYMIN -or ($by+$H) -gt $LYMAX) { continue }
        $dist = PtRectDist $p.ax $p.ay $bx $by $W $H
        if ($dist -lt ($p.exclR + 3)) { continue }
        $bad = $false
        foreach ($q in $PTS) {
          if ($q.id -eq $p.id) { continue }
          if ((PtRectDist $q.ax $q.ay $bx $by $W $H) -lt ($q.exclR + 6)) { $bad = $true; break }
        }
        if ($bad) { continue }
        foreach ($r in $RES) { if ((RectSep $bx $by $W $H $r.x $r.y $r.w $r.h) -lt 3.0) { $bad = $true; break } }
        if ($bad) { continue }
        $dmin = 99999.0
        foreach ($q in $PTS) {
          if ($q.id -eq $p.id) { continue }
          $dd = PtRectDist $q.ax $q.ay $bx $by $W $H
          if ($dd -lt $dmin) { $dmin = $dd }
        }
        $ambig = $false
        if ($dist -le $LEADMAX -and ($dist + 5.0) -gt $dmin) { $ambig = $true }
        if ($ambig) { continue }
        $okGap = $true
        foreach ($pl in $PLACED) { if ((RectSep $bx $by $W $H $pl.bx $pl.by $W $pl.bh) -lt $LABGAP) { $okGap = $false; break } }
        if (-not $okGap) { continue }

        $cost = 0.0
        if ($dist -le $LEADMAX) { $cost = $dist } else { $cost = 85.0 + ($dist * 0.45) }
        if ($d.n -eq 'N' -or $d.n -eq 'S') { $cost += 3.0 }
        elseif ($d.n -ne 'E' -and $d.n -ne 'W') { $cost += 1.5 }
        $cost += [Math]::Abs($s) * 0.10
        if ($bx -lt $PX0 -or ($bx+$W) -gt $PX1 -or $by -lt $PY0 -or ($by+$H) -gt $PY1) { $cost += 26.0 }
        if ($p.nnD -lt 150.0) { if ((($d.ux*$p.nnUx)+($d.uy*$p.nnUy)) -gt 0.55) { $cost += 14.0 } }
        $key = "$($p.id)|$($d.n)|$g|$s"
        if ($PENALTY.ContainsKey($key)) { $cost += $PENALTY[$key] }
        $cands.Add([pscustomobject]@{ bx=$bx; by=$by; bw=$W; bh=$H; dist=$dist; dir=$d.n; gap=[double]$g; shift=[double]$s; cost=$cost })
      }
    }
  }
  if ($cands.Count -eq 0) { $placeFail.Add($p.id); continue }
  $pick = $cands | Sort-Object -Property cost | Select-Object -First 1
  $PLACED += [pscustomobject]@{ id=$p.id; bx=$pick.bx; by=$pick.by; bw=$pick.bw; bh=$pick.bh; dist=$pick.dist; dir=$pick.dir; gap=$pick.gap; shift=$pick.shift; cost=$pick.cost }
}

$placedById = @{}
foreach ($pl in $PLACED) { $placedById[$pl.id] = $pl }

# ------------------------------------------------------------------- routing ----
function Get-Anchor([double]$bx,[double]$by,[double]$bw,[double]$bh,[double]$ax,[double]$ay) {
  $cx = [Math]::Max($bx, [Math]::Min($bx+$bw, $ax))
  $cy = [Math]::Max($by, [Math]::Min($by+$bh, $ay))
  return ,@([Math]::Round($cx,1), [Math]::Round($cy,1))
}
function Build-Routes([double]$cx,[double]$cy,[double]$ax,[double]$ay) {
  $rs = New-Object System.Collections.Generic.List[object]
  if ([Math]::Abs($cy - $ay) -lt 0.6) { $rs.Add(@($cx,$cy,$ax,$ay)) }
  if ([Math]::Abs($cx - $ax) -lt 0.6) { $rs.Add(@($cx,$cy,$ax,$ay)) }
  $rs.Add(@($cx,$cy,$ax,$cy,$ax,$ay))
  $rs.Add(@($cx,$cy,$cx,$ay,$ax,$ay))
  $mid = $cx + (($ax - $cx) / 2.0)
  foreach ($off in @(-48.0,-28.0,-14.0,0.0,14.0,28.0,48.0)) {
    $gx = [Math]::Round($mid + $off,1)
    $rs.Add(@($cx,$cy,$gx,$cy,$gx,$ay,$ax,$ay))
  }
  $midy = $cy + (($ay - $cy) / 2.0)
  foreach ($off in @(-40.0,-22.0,0.0,22.0,40.0)) {
    $gy = [Math]::Round($midy + $off,1)
    $rs.Add(@($cx,$cy,$cx,$gy,$ax,$gy,$ax,$ay))
  }
  return $rs
}
function Route-Ok([object]$rt,[string]$ownId,[array]$segs) {
  foreach ($sg in $segs) {
    foreach ($lb in $LABELBOX) {
      if ($lb.id -eq $ownId) {
        if ((SegRectHit $sg[0] $sg[1] $sg[2] $sg[3] ($lb.bx+1.2) ($lb.by+1.2) ($lb.bw-2.4) ($lb.bh-2.4))) { return $false }
      } else {
        if ((SegRectHit $sg[0] $sg[1] $sg[2] $sg[3] ($lb.bx-1.5) ($lb.by-1.5) ($lb.bw+3.0) ($lb.bh+3.0))) { return $false }
      }
    }
    foreach ($r in $RES) {
      if ((SegRectHit $sg[0] $sg[1] $sg[2] $sg[3] ($r.x-1.5) ($r.y-1.5) ($r.w+3.0) ($r.h+3.0))) { return $false }
    }
    foreach ($q in $PTS) {
      if ($q.id -eq $ownId) { continue }
      $dd = PtSegDist $q.ax $q.ay $sg[0] $sg[1] $sg[2] $sg[3]
      if ($dd -lt ($q.exclR + 5.0)) { return $false }
    }
  }
  return $true
}
function Segs-Of([array]$flat) {
  $out = @()
  for ($k = 0; $k -lt ($flat.Count - 2); $k += 2) {
    $out += ,@([double]$flat[$k], [double]$flat[$k+1], [double]$flat[$k+2], [double]$flat[$k+3])
  }
  return $out
}
function Route-Len([array]$flat) {
  $L = 0.0
  for ($k = 0; $k -lt ($flat.Count - 2); $k += 2) {
    $dx = [double]$flat[$k+2] - [double]$flat[$k]
    $dy = [double]$flat[$k+3] - [double]$flat[$k+1]
    $L += [Math]::Sqrt(($dx*$dx)+($dy*$dy))
  }
  return $L
}
function Count-Cross([array]$segsA,[array]$segsB) {
  $c = 0
  foreach ($sa in $segsA) { foreach ($sb in $segsB) { if ((SegCross $sa[0] $sa[1] $sa[2] $sa[3] $sb[0] $sb[1] $sb[2] $sb[3]) -ne 0) { $c++ } } }
  return $c
}

$LABELBOX = @()
foreach ($pl in $PLACED) { $LABELBOX += [pscustomobject]@{ id=$pl.id; bx=$pl.bx; by=$pl.by; bw=$pl.bw; bh=$pl.bh } }

$LEADERS = @()
$noRoute = New-Object System.Collections.Generic.List[string]
$needLead = New-Object System.Collections.Generic.List[string]
$OPTS = @()
foreach ($pl in $PLACED) {
  if ($pl.dist -le $LEADMAX) { continue }
  $needLead.Add($pl.id)
  $p = $PTS | Where-Object { $_.id -eq $pl.id } | Select-Object -First 1
  $an = Get-Anchor $pl.bx $pl.by $pl.bw $pl.bh $p.ax $p.ay
  $routes = Build-Routes ([double]$an[0]) ([double]$an[1]) $p.ax $p.ay
  $good = @()
  foreach ($rt in $routes) {
    $sgs = Segs-Of $rt
    if (Route-Ok $rt $pl.id $sgs) {
      $bends = ($rt.Count/2) - 1
      $good += [pscustomobject]@{ flat=$rt; len=(Route-Len $rt); bends=$bends }
    }
  }
  if ($good.Count -eq 0) { $noRoute.Add($pl.id); continue }
  $good = @($good | Sort-Object -Property @{Expression='bends';Ascending=$true}, @{Expression='len';Ascending=$true})
  $OPTS += [pscustomobject]@{ id=$pl.id; opts=$good }
}

# pick routes minimising crossings
$CHOSEN = @{}
$assigned = @()
foreach ($o in ($OPTS | Sort-Object -Property @{Expression={ $_.opts.Count };Ascending=$true})) {
  $best = $null; $bestScore = 1000000.0
  foreach ($cand in $o.opts) {
    $sgs = Segs-Of $cand.flat
    $cross = 0
    foreach ($a in $assigned) { $cross += Count-Cross (Segs-Of $CHOSEN[$a]) $sgs }
    $score = ($cross * 1000.0) + $cand.len + ($cand.bends * 4.0)
    if ($score -lt $bestScore) { $bestScore = $score; $best = $cand }
  }
  $CHOSEN[$o.id] = $best.flat
  $assigned += $o.id
}

$totalCross = 0
$crossPairs = @()
for ($i = 0; $i -lt $assigned.Count; $i++) {
  for ($j = $i+1; $j -lt $assigned.Count; $j++) {
    $sa = Segs-Of $CHOSEN[$assigned[$i]]
    $sb = Segs-Of $CHOSEN[$assigned[$j]]
    $c = Count-Cross $sa $sb
    if ($c -gt 0) { $totalCross += $c; $crossPairs += "$($assigned[$i]) x $($assigned[$assigned.IndexOf($assigned[$j])]) = $c" }
  }
}
foreach ($id in $assigned) { $LEADERS += [pscustomobject]@{ id=$id; flat=$CHOSEN[$id] } }

# -------------------------------------------------------------- final audit ------
$probs = New-Object System.Collections.Generic.List[string]
foreach ($f in $placeFail) { $probs.Add("no candidate placement for $f") }
foreach ($f in $noRoute)   { $probs.Add("no valid leader route for $f") }

$minGap = 99999.0; $gapPair = ''
for ($i = 0; $i -lt $PLACED.Count; $i++) {
  for ($j = $i+1; $j -lt $PLACED.Count; $j++) {
    $a = $PLACED[$i]; $b = $PLACED[$j]
    $g = RectSep $a.bx $a.by $a.bw $a.bh $b.bx $b.by $b.bw $b.bh
    if ($g -lt $minGap) { $minGap = $g; $gapPair = "$($a.id)-$($b.id)" }
  }
}
if ($minGap -lt $LABGAP) { $probs.Add("label-label gap $minGap px ($gapPair) < $LABGAP") }

$minPt = 99999.0; $ptPair = ''
$ptOverlap = 0
foreach ($pl in $PLACED) {
  foreach ($q in $PTS) {
    if ($q.id -eq $pl.id) { continue }
    $d = PtRectDist $q.ax $q.ay $pl.bx $pl.by $pl.bw $pl.bh
    if ($d -lt $minPt) { $minPt = $d; $ptPair = "$($pl.id) vs $($q.id)" }
    if ($d -lt ($q.exclR + 6)) { $ptOverlap++ }
  }
}
if ($ptOverlap -gt 0) { $probs.Add("$ptOverlap label/point covers") }

$resHit = 0
foreach ($pl in $PLACED) {
  foreach ($r in $RES) { if ((RectSep $pl.bx $pl.by $pl.bw $pl.bh $r.x $r.y $r.w $r.h) -lt 3.0) { $resHit++ } }
}
if ($resHit -gt 0) { $probs.Add("$resHit labels sit on annotation text") }

$boundsOk = $true
foreach ($pl in $PLACED) {
  if ($pl.bx -lt $LXMIN -or ($pl.bx+$pl.bw) -gt $LXMAX -or $pl.by -lt $LYMIN -or ($pl.by+$pl.bh) -gt $LYMAX) { $boundsOk = $false }
}
if (-not $boundsOk) { $probs.Add('label outside canvas/annotation-safe band') }

$lineHits = 0
foreach ($ld in $LEADERS) {
  $sgs = Segs-Of $ld.flat
  foreach ($sg in $sgs) {
    foreach ($lb in $LABELBOX) {
      if ($lb.id -eq $ld.id) { if (SegRectHit $sg[0] $sg[1] $sg[2] $sg[3] ($lb.bx+1.2) ($lb.by+1.2) ($lb.bw-2.4) ($lb.bh-2.4)) { $lineHits++ } }
      else { if (SegRectHit $sg[0] $sg[1] $sg[2] $sg[3] ($lb.bx-1.5) ($lb.by-1.5) ($lb.bw+3.0) ($lb.bh+3.0)) { $lineHits++ } }
    }
    foreach ($r in $RES) { if (SegRectHit $sg[0] $sg[1] $sg[2] $sg[3] ($r.x-1.5) ($r.y-1.5) ($r.w+3.0) ($r.h+3.0)) { $lineHits++ } }
  }
}
if ($lineHits -gt 0) { $probs.Add("$lineHits leader segments pass through text") }

$wrongPt = 0
foreach ($ld in $LEADERS) {
  $sgs = Segs-Of $ld.flat
  foreach ($sg in $sgs) {
    foreach ($q in $PTS) {
      if ($q.id -eq $ld.id) { continue }
      if ((PtSegDist $q.ax $q.ay $sg[0] $sg[1] $sg[2] $sg[3]) -lt ($q.exclR + 5.0)) { $wrongPt++ }
    }
  }
}
if ($wrongPt -gt 0) { $probs.Add("$wrongPt leader segments pass too close to a non-target point") }

if ($totalCross -gt 3) { $probs.Add("line-line crossings $totalCross > 3") }

$minSegGap = 99999.0
foreach ($pl in $PLACED) {
  if ($pl.dist -le $LEADMAX) {
    $dmin = 99999.0
    foreach ($q in $PTS) { if ($q.id -ne $pl.id) { $d = PtRectDist $q.ax $q.ay $pl.bx $pl.by $pl.bw $pl.bh; if ($d -lt $dmin) { $dmin = $d } } }
    $margin = $dmin - $pl.dist
    if ($margin -lt $minSegGap) { $minSegGap = $margin }
    if ($margin -le 0) { $probs.Add("ambiguous association for $($pl.id)") }
  }
}

$leadCovered = 0
foreach ($pl in $PLACED) { if ($pl.dist -gt $LEADMAX -and (@($LEADERS | Where-Object { $_.id -eq $pl.id }).Count -gt 0)) { $leadCovered++ } }
$needCount = @($PLACED | Where-Object { $_.dist -gt $LEADMAX }).Count
if ($leadCovered -ne $needCount) { $probs.Add("leader coverage $leadCovered/$needCount") }

# point-circle occlusion among markers
$minPtGap = 99999.0; $occl = 0
for ($i = 0; $i -lt $PTS.Count; $i++) {
  for ($j = $i+1; $j -lt $PTS.Count; $j++) {
    $a = $PTS[$i]; $b = $PTS[$j]
    $dx = $b.ax - $a.ax; $dy = $b.ay - $a.ay
    $d = [Math]::Sqrt(($dx*$dx)+($dy*$dy)) - $a.exclR - $b.exclR
    if ($d -lt $minPtGap) { $minPtGap = $d; $minPtPair = "$($a.id)-$($b.id)" }
    if ($d -lt 0) { $occl++ }
  }
}
if ($occl -gt 0) { $probs.Add("$occl marker pairs occlude each other") }

Write-Output ("markers={0} placed={1} needLeader={2} leaders={3} crossings={4}" -f $PTS.Count, $PLACED.Count, $needCount, $LEADERS.Count, $totalCross)
Write-Output ("min label gap={0} ({1})  min label->other point={2} ({3})  min marker gap={4} ({5})" -f [Math]::Round($minGap,1), $gapPair, [Math]::Round($minPt,1), $ptPair, [Math]::Round($minPtGap,1), $minPtPair)
Write-Output ("center6: " + ($CENTER6 -join ','))
Write-Output ("problems = {0}" -f $probs.Count)
foreach ($pr in $probs) { Write-Output ("  PROBLEM: " + $pr) }

$STATE = [pscustomobject]@{
  pts = $PTS; placed = $PLACED; leaders = $LEADERS; res = $RES
  center6 = $CENTER6; cross = $totalCross; probs = $probs.ToArray()
  minGap = $minGap; minPt = $minPt; minPtGap = $minPtGap; minPtPair = $minPtPair
  needCount = $needCount; leadCovered = $leadCovered; lineHits = $lineHits
  wrongPt = $wrongPt; boundsOk = $boundsOk; resHit = $resHit; ptOverlap = $ptOverlap
  cut = $cut; order = @($ORDER | ForEach-Object { $_.id })
}
[IO.File]::WriteAllText(($OutReport), (($state | ConvertTo-Json -Depth 8) + "`n"), $utf8)
Write-Output ("-> {0}" -f $OutReport)

# ============================================================== emission =========
function Fmt([double]$v) { return ([Math]::Round($v,1)).ToString([cultureinfo]::InvariantCulture) }
function EmitBox([double]$x,[double]$y,[double]$w,[double]$h,[string]$bg,[string]$border,[int]$rad) {
  $a = '<Positioned left="' + (Fmt $x) + '" top="' + (Fmt $y) + '" width="' + (Fmt $w) + '" height="' + (Fmt $h) + '">'
  $a += '<Container width="' + (Fmt $w) + '" height="' + (Fmt $h) + '"'
  if ($bg -ne '') { $a += ' color="' + $bg + '"' }
  if ($border -ne '') { $a += ' border="' + $border + '"' }
  if ($rad -gt 0) { $a += ' borderRadius="' + $rad + '"' }
  $a += '/></Positioned>'
  return $a
}
function EmitText([double]$x,[double]$y,[double]$w,[double]$h,[int]$fs,[string]$col,[string]$al,[bool]$bold,[string]$txt) {
  $a = ''
  if ($al -ne 'LEFT') { $a += ' textAlign="' + $al + '"' }
  if ($bold) { $a += ' fontStyle="BOLD"' }
  return ('<Positioned left="' + (Fmt $x) + '" top="' + (Fmt $y) + '" width="' + (Fmt $w) + '" height="' + (Fmt $h) + '">' +
          '<Text fontSize="' + $fs + '" fontFamily="Noto Sans CJK SC" color="' + $col + '"' + $a + '>' +
          (Esc $txt) + '</Text></Positioned>')
}
function SEG([double]$x1,[double]$y1,[double]$x2,[double]$y2) {
  $dx = [Math]::Abs($x2-$x1); $dy = [Math]::Abs($y2-$y1)
  if ($dx -lt 0.5 -and $dy -lt 0.5) { return '' }
  if ($dy -lt 0.5) { return (EmitBox ([Math]::Min($x1,$x2)) ($y1-1.0) $dx 2.0 $C_LEAD '' 0) }
  if ($dx -lt 0.5) { return (EmitBox ($x1-1.0) ([Math]::Min($y1,$y2)) 2.0 $dy $C_LEAD '' 0) }
  return ''   # diagonal segments are never emitted (orthogonal routing only)
}

$NOW = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')
$YT = @(
  [pscustomobject]@{ v=100; py=160.0 }; [pscustomobject]@{ v=75; py=350.0 }
  [pscustomobject]@{ v=50;  py=540.0 }; [pscustomobject]@{ v=25; py=730.0 }
  [pscustomobject]@{ v=0;   py=920.0 }
)
$XT = @(
  [pscustomobject]@{ v=0; px=280.0 }; [pscustomobject]@{ v=25; px=540.0 }
  [pscustomobject]@{ v=50; px=800.0 }; [pscustomobject]@{ v=75; px=1060.0 }
  [pscustomobject]@{ v=100; px=1320.0 }
)
$top3List = @($PTS | Where-Object { $_.isTop3 } | Sort-Object -Property @{Expression='value';Descending=$true})
$leadById = @{}
foreach ($ld in $LEADERS) { $leadById[$ld.id] = $ld }
$placedById = @{}
foreach ($pl in $PLACED) { $placedById[$pl.id] = $pl }

$L = New-Object System.Collections.Generic.List[string]
[void]$L.Add('<Snapshot type="png" background="' + $C_BG + '"><Container width="1600" height="1100" color="' + $C_BG + '"><Stack>')
# 1. plot panel
[void]$L.Add((EmitBox $PX0 $PY0 $PW $PH $C_PANEL ('2 SOLID ' + $C_BORDER) 0))
# 2. gridlines (interior quarter lines only)
foreach ($gy in @(350.0,540.0,730.0)) { [void]$L.Add((EmitBox ($PX0+1) $gy ($PW-2) 1.0 $C_GRID '' 0)) }
foreach ($gx in @(540.0,800.0,1060.0)) { [void]$L.Add((EmitBox $gx ($PY0+1) 1.0 ($PH-2) $C_GRID '' 0)) }
# 3. tick marks (inside)
foreach ($t in $YT) { [void]$L.Add((EmitBox 282.0 ($t.py - 1.0) 12.0 2.0 $C_BORDER '' 0)) }
foreach ($t in $XT) { [void]$L.Add((EmitBox ($t.px - 1.0) 906.0 2.0 12.0 $C_BORDER '' 0)) }
# 4. leader lines (under points and labels = layering)
foreach ($ld in $LEADERS) {
  $fl = $ld.flat
  for ($k = 0; $k -lt ($fl.Count - 2); $k += 2) {
    $seg = SEG ([double]$fl[$k]) ([double]$fl[$k+1]) ([double]$fl[$k+2]) ([double]$fl[$k+3])
    if ($seg -ne '') { [void]$L.Add($seg) }
  }
}
# 5. markers
foreach ($p in $PTS) {
  if ($p.isTop3) { [void]$L.Add((EmitBox ($p.ax-13.0) ($p.ay-13.0) 26.0 26.0 '#00000000' ('2 SOLID ' + $C_TOP) 13)) }
}
foreach ($p in $PTS) {
  $dotCol = $C_PT; if ($p.isTop3) { $dotCol = $C_TOP }
  [void]$L.Add((EmitBox ($p.ax-6.0) ($p.ay-6.0) 12.0 12.0 $dotCol '' 6))
}
# 6. label chips + label text
foreach ($pl in $PLACED) {
  $bg = '#FFFFFF'; $bd = '1 SOLID ' + $C_LABB; $tc = $C_TXT; $bold = $false
  $p0 = $PTS | Where-Object { $_.id -eq $pl.id } | Select-Object -First 1
  if ($p0.isTop3) { $bg = '#FFF7ED'; $bd = '1 SOLID ' + $C_LABT; $tc = '#9A3412'; $bold = $true }
  [void]$L.Add((EmitBox $pl.bx $pl.by $pl.bw $pl.bh $bg $bd 6))
  [void]$L.Add((EmitText $pl.bx ($pl.by + 6.0) $pl.bw 30.0 $FS $tc 'CENTER' $bold $p0.text))
}
# 7. annotations
[void]$L.Add((EmitText 40.0 26.0 520.0 54.0 34 $C_TXT 'LEFT' $true  '示意地图 · 24 点指数标注'))
[void]$L.Add((EmitText 40.0 84.0 1100.0 30.0 $FS $C_MUT 'LEFT' $false '原点左下 · x 向右 · y 向上 · 逻辑坐标 0-100 映射到主图区 (280,160) 1040×760'))
[void]$L.Add((EmitText 1160.0 84.0 400.0 30.0 $FS $C_MUT 'RIGHT' $false '点圆直径 12 · Top 3 加环'))
[void]$L.Add((EmitText 40.0 156.0 224.0 30.0 $FS $C_TXT 'LEFT' $true  'y 轴 · 指数 0-100'))
foreach ($t in $YT) { [void]$L.Add((EmitText 300.0 ($t.py - 34.0) 64.0 30.0 $FS $C_MUT 'RIGHT' $false ([string]$t.v))) }
foreach ($t in $XT) { [void]$L.Add((EmitText ($t.px - 28.0) 926.0 56.0 30.0 $FS $C_MUT 'CENTER' $false ([string]$t.v))) }
[void]$L.Add((EmitText 280.0 966.0 620.0 30.0 $FS $C_TXT 'LEFT' $false 'x 轴 · 逻辑坐标 0-100（原点左下，向右增大）'))
$t3txt = '最高 3 点（按 value 排序）：'
for ($i = 0; $i -lt $top3List.Count; $i++) {
  $tp = $top3List[$i]
  if ($i -gt 0) { $t3txt += ' · ' }
  $t3txt += ('{0} {1} {2}' -f $tp.id, $tp.name, $tp.value)
}
[void]$L.Add((EmitText 280.0 1014.0 1040.0 30.0 $FS '#9A3412' 'LEFT' $true $t3txt))
[void]$L.Add((EmitBox 1344.0 975.0 12.0 12.0 $C_PT '' 6))
[void]$L.Add((EmitText 1364.0 966.0 232.0 30.0 $FS $C_MUT 'LEFT' $false '圆点＝观测点'))
[void]$L.Add((EmitBox 1344.0 1019.0 20.0 20.0 '#00000000' ('2 SOLID ' + $C_TOP) 10))
[void]$L.Add((EmitText 1376.0 1014.0 220.0 30.0 $FS $C_MUT 'LEFT' $false '环＝最高 3 点'))
[void]$L.Add('</Stack></Container></Snapshot>')
[IO.File]::WriteAllText($OutDsl, (-join $L), $utf8)

# ---- label-layout.json ----
$lm = @()
foreach ($pl in $PLACED) {
  $p0 = $PTS | Where-Object { $_.id -eq $pl.id } | Select-Object -First 1
  $poly = $null
  if ($leadById.ContainsKey($pl.id)) {
    $fl = $leadById[$pl.id].flat
    $poly = @()
    for ($k = 0; $k -lt $fl.Count; $k += 2) { $poly += [pscustomobject]@{ x=[double]$fl[$k]; y=[double]$fl[$k+1] } }
  }
  $lm += [pscustomobject]@{
    id = $p0.id; name = $p0.name; value = $p0.value
    logical = [pscustomobject]@{ x = $p0.lx; y = $p0.ly }
    anchor  = [pscustomobject]@{ x = $p0.ax; y = $p0.ay }
    marker  = [pscustomobject]@{ diameter = 12; isTop3 = [bool]$p0.isTop3; ringDiameter = $(if ($p0.isTop3) { 26 } else { 0 }) }
    label   = [pscustomobject]@{
      text = $p0.text
      box  = [pscustomobject]@{ x = $pl.bx; y = $pl.by; width = $pl.bw; height = $pl.bh }
      fontFamily = 'Noto Sans CJK SC'; fontSize = 20
      direction = $pl.dir; distance = [Math]::Round($pl.dist,2)
      needsLeader = ($pl.dist -gt 24.0); paramGap = $pl.gap
    }
    leader = $(if ($null -ne $poly) { [pscustomobject]@{ polyline = $poly; segmentCount = ($poly.Count - 1) } } else { $null })
  }
}
# The spec says "映射到像素时不要反转错误" - so prove the inversion is CORRECT rather
# than asserting a bare boolean that could be read as "we flipped the data".
# Corners are computed with the exact same expressions the marker loader uses (line 136).
$cornerChecks = @()
foreach ($c in @(
    [pscustomobject]@{ lx = 0.0;   ly = 0.0;   want = 'bottom-left'  },
    [pscustomobject]@{ lx = 100.0; ly = 0.0;   want = 'bottom-right' },
    [pscustomobject]@{ lx = 0.0;   ly = 100.0; want = 'top-left'     },
    [pscustomobject]@{ lx = 100.0; ly = 100.0; want = 'top-right'    }
  )) {
  $cx = $PX0 + ($c.lx * $SX)
  $cy = $PY1 - ($c.ly * $SY)
  $ex = $PX0; $ey = $PY1
  if ($c.want -eq 'bottom-right') { $ex = $PX1; $ey = $PY1 }
  if ($c.want -eq 'top-left')     { $ex = $PX0; $ey = $PY0 }
  if ($c.want -eq 'top-right')    { $ex = $PX1; $ey = $PY0 }
  if ([Math]::Abs($cx - $ex) -gt 1e-6 -or [Math]::Abs($cy - $ey) -gt 1e-6) {
    throw "mapping corner check FAILED: logical ($($c.lx),$($c.ly)) -> pixel ($cx,$cy), expected $c.want = ($ex,$ey)"
  }
  $cornerChecks += [pscustomobject]@{
    logical_x = $c.lx; logical_y = $c.ly
    pixel_x = $cx; pixel_y = $cy
    expected_plot_corner = $c.want
    expected_pixel_x = $ex; expected_pixel_y = $ey
    pass = $true
  }
}
if ($cornerChecks.Count -ne 4) { throw 'corner checks did not run 4 times' }

$layout = [pscustomobject]@{
  generated_at = $NOW; task = 'A20'; canvas = [pscustomobject]@{ width = 1600; height = 1100 }
  mapping = [pscustomobject]@{
    logical_origin = 'bottom-left'; logical_x_direction = 'right'; logical_y_direction = 'up'
    logical_range = [pscustomobject]@{ x = @(0,100); y = @(0,100) }
    plot_rect = [pscustomobject]@{ left = $PX0; top = $PY0; width = $PW; height = $PH; right = $PX1; bottom = $PY1 }
    formula = 'px = 280 + x * 10.4 ; py = 920 - y * 7.6'
    x_scale_px_per_unit = $SX; y_scale_px_per_unit = $SY
    pixel_y_inversion_applied = $true
    pixel_y_inversion_correct = $true
    data_mirrored = $false
    inversion_note = '屏幕像素 y 向下、逻辑 y 向上，所以 py = 920 - y * 7.6 施加了一次上下反转；该反转施加正确（下方 corner_checks 逐角实测通过）：逻辑原点 (0,0) 落在主图区左下角，x 向右增大、y 向上增大，没有左右镜像，也没有把任何一条轴的方向写反。'
    corner_checks = $cornerChecks
  }
  label_style = [pscustomobject]@{ fontSize = 20; fontFamily = 'Noto Sans CJK SC'; box_height = $LH; min_gap_px = $LABGAP; leader_threshold_px = 24 }
  leader_rule = [pscustomobject]@{ required_when_distance_gt = 24; geometry = 'orthogonal (horizontal / vertical segments only, one bend where the anchor is not axis-aligned with the marker)'; crossing_limit = 3; junction_dots = $false }
  center6 = $CENTER6; top3 = @($top3List | ForEach-Object { $_.id })
  markers = $lm
}
[IO.File]::WriteAllText($OutLayout, (($layout | ConvertTo-Json -Depth 12) + "`n"), $utf8)

# ---- layout-audit.json ----
$minMargin = 99999.0
foreach ($pl in $PLACED) {
  $m = [Math]::Min([Math]::Min($pl.bx, $CW - ($pl.bx + $pl.bw)), [Math]::Min($pl.by, $CH - ($pl.by + $pl.bh)))
  if ($m -lt $minMargin) { $minMargin = $m }
}
$crossList = @()
for ($i = 0; $i -lt $assigned.Count; $i++) {
  for ($j = $i + 1; $j -lt $assigned.Count; $j++) {
    $c = Count-Cross (Segs-Of $CHOSEN[$assigned[$i]]) (Segs-Of $CHOSEN[$assigned[$j]])
    if ($c -gt 0) { $crossList += [pscustomobject]@{ a = $assigned[$i]; b = $assigned[$j]; crossings = $c } }
  }
}
$needIds = @($PLACED | Where-Object { $_.dist -gt 24.0 } | ForEach-Object { $_.id })
$haveIds = @($LEADERS | ForEach-Object { $_.id })
$missing = @($needIds | Where-Object { $haveIds -notcontains $_ })
$assocMargin = 99999.0
foreach ($pl in $PLACED) {
  if ($pl.dist -le 24.0) {
    $dm = 99999.0
    foreach ($q in $PTS) { if ($q.id -ne $pl.id) { $d = PtRectDist $q.ax $q.ay $pl.bx $pl.by $pl.bw $pl.bh; if ($d -lt $dm) { $dm = $d } } }
    if (($dm - $pl.dist) -lt $assocMargin) { $assocMargin = $dm - $pl.dist }
  }
}
$segChecked = 0
foreach ($ld in $LEADERS) { $segChecked += (($ld.flat.Count / 2) - 1) }
$assocViol = 0
foreach ($pl in $PLACED) {
  if ($pl.dist -le 24.0) {
    $dm = 99999.0
    foreach ($q in $PTS) { if ($q.id -ne $pl.id) { $d = PtRectDist $q.ax $q.ay $pl.bx $pl.by $pl.bw $pl.bh; if ($d -lt $dm) { $dm = $d } } }
    if (($dm - $pl.dist) -le 0) { $assocViol++ }
  }
}
$audit = [pscustomobject]@{
  generated_at = $NOW; task = 'A20'; canvas = [pscustomobject]@{ width = 1600; height = 1100 }
  counts = [pscustomobject]@{ markers = $PTS.Count; labels = $PLACED.Count; leaders = $LEADERS.Count; labels_over_24px = $needIds.Count }
  label_intersections = [pscustomobject]@{
    rule = 'every pair of label boxes separated by >= 4 px'; threshold_px = 4
    min_gap_px = [Math]::Round($minGap,2); min_gap_pair = $gapPair
    violations = $(if ($minGap -lt 4.0) { 1 } else { 0 }); detail = @()
  }
  label_point_coverage = [pscustomobject]@{
    rule = 'no label box may cover a marker other than its own (clearance >= marker radius + 6 px)'
    min_clearance_px = [Math]::Round($minPt,2); min_clearance_pair = $ptPair
    violations = $ptOverlap
  }
  leader_required = [pscustomobject]@{
    rule = 'labels farther than 24 px from their marker must carry a leader line'
    labels_over_24px = $needIds; labels_with_leader = $haveIds; missing = $missing
    violations = $missing.Count
  }
  line_through_label = [pscustomobject]@{
    rule = 'no leader segment may enter any label box or any annotation text box'
    segments_checked = [int]$segChecked
    violations = $lineHits
  }
  line_wrong_point = [pscustomobject]@{
    rule = 'a leader must not pass within (marker radius + 5 px) of a marker it does not belong to'
    violations = $wrongPt
  }
  line_crossings = [pscustomobject]@{
    rule = 'at most 3 leader/leader crossings; no junction dot is drawn where lines cross'
    limit = 3; count = $totalCross; pairs = $crossList; junction_dots_drawn = 0
    violations = $(if ($totalCross -gt 3) { 1 } else { 0 })
  }
  boundary_check = [pscustomobject]@{
    rule = 'label boxes inside 1600x1100 with >= 8 px margin, and outside the title band (y<160) and the axis band (y>916)'
    min_margin_px = [Math]::Round($minMargin,2); violations = $(if ($boundsOk) { 0 } else { 1 })
    all_inside = [bool]$boundsOk
  }
  annotation_text_check = [pscustomobject]@{
    rule = 'label boxes must not sit on axis ticks, captions, title or legend'
    reserved_boxes = @($RES | ForEach-Object { $_.n }); violations = $resHit
  }
  association_check = [pscustomobject]@{
    rule = 'a label placed within 24 px (no leader) must be nearest to its own marker'
    min_margin_px = [Math]::Round($assocMargin,2)
    violations = $assocViol
  }
  text_size = [pscustomobject]@{ label_font_size = 20; rule = 'label body text >= 20 px'; violations = 0 }
  marker_geometry = [pscustomobject]@{
    diameter = 12; shrink_applied = $false; shrink_to = 0
    min_edge_gap_px = [Math]::Round($minPtGap,2); min_edge_gap_pair = $minPtPair; occluding_pairs = $occl
    center6 = $CENTER6
    note = 'no marker pair occludes another at the specified 12 px diameter, so the permitted shrink to 8 px was not needed; the edge gap is recorded above'
  }
  annotations_present = @('x axis + ticks 0/25/50/75/100', 'y axis + ticks 0/25/50/75/100', 'axis range 0-100 on both axes', 'unit 指数 on the y axis', 'top-3 markers ringed and listed by value')
  visual_checks = [pscustomobject]@{
    center6_zoom = 'pending'; leaders_zoom = 'pending'; whole_view = 'pending'
  }
  problems = $probs
}
[IO.File]::WriteAllText($OutAudit, (($audit | ConvertTo-Json -Depth 12) + "`n"), $utf8)
Write-Output ("-> {0}" -f $OutDsl)
Write-Output ("-> {0}" -f $OutLayout)
Write-Output ("-> {0}" -f $OutAudit)
