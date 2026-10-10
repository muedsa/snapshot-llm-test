# A06 verifier: reconstructs every drawn edge from the DSL (not from my intentions) and checks the task's hard claims.
$ErrorActionPreference = 'Stop'
$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
$dsl  = Join-Path $ROOT ("tmp\$RUN\A06\v01.snapshot")
$png  = Join-Path $ROOT ("tmp\$RUN\A06\v01.png")

# ---------- 1. parse Transform segments straight out of the DSL ----------
$lines = [System.IO.File]::ReadAllLines($dsl)
$segs = New-Object System.Collections.ArrayList
for ($i = 0; $i -lt $lines.Count; $i++) {
  if ($lines[$i] -match '<Transform matrix="\(([-\d.,]+)\)"') {
    $m = $matches[1].Split(',')
    $c = [double]$m[0]; $s = [double]$m[1]
    $pm = [regex]::Match($lines[$i-1], '<Positioned left="([-\d.]+)" top="([-\d.]+)">')
    $cm = [regex]::Match($lines[$i+1], '<Container width="([-\d.]+)" height="([-\d.]+)"')
    $left = [double]$pm.Groups[1].Value; $top = [double]$pm.Groups[2].Value
    $len  = [double]$cm.Groups[1].Value; $th   = [double]$cm.Groups[2].Value
    $x1 = $left; $y1 = $top + $th / 2
    [void]$segs.Add([pscustomobject]@{
      idx = $segs.Count; x1 = $x1; y1 = $y1; x2 = $x1 + $len * $c; y2 = $y1 + $len * $s; th = $th
    })
  }
}
"DSL Transform segments parsed : " + $segs.Count

# ---------- 2. group them into semantic elements (emission order of gen.ps1) ----------
$groups = New-Object System.Collections.ArrayList
function G($name,$from,$to){ [void]$groups.Add([pscustomobject]@{ name=$name; from=$from; to=$to }) }
G 'legend-solid-1' 0 2
G 'legend-dashed'  3 7
G 'legend-solid-2' 8 10
G 'edge:N04->N13'  11 15
$short = @('N01->N02','N01->N03','N02->N04','N02->N05','N03->N06','N05->N06','N04->N07','N06->N08',
           'N07->N08','N08->N09','N09->N10','N10->N11','N11->N12','N12->N13','N13->N14')
for ($k = 0; $k -lt $short.Count; $k++) { G ("edge:" + $short[$k]) (16 + 3*$k) (18 + 3*$k) }
G 'feedback:N09->N08' 61 77
G 'feedback:N10->N08' 78 118
$covered = 0; foreach ($g in $groups) { $covered += ($g.to - $g.from + 1) }
"groups                              : " + $groups.Count + "  covering $covered segments (uncovered = " + ($segs.Count - $covered) + ")"

function InGroup($idx,$g){ return ($idx -ge $g.from -and $idx -le $g.to) }

# ---------- 3. transversal crossing test between DIFFERENT elements ----------
function Cross($ax1,$ay1,$ax2,$ay2,$bx1,$by1,$bx2,$by2) {
  $d1x = $ax2-$ax1; $d1y = $ay2-$ay1
  $d2x = $bx2-$bx1; $d2y = $by2-$by1
  $den = $d1x*$d2y - $d1y*$d2x
  if ([Math]::Abs($den) -lt 1e-9) { return $null }        # parallel / collinear
  $ex = $bx1-$ax1; $ey = $by1-$ay1
  $t = ($ex*$d2y - $ey*$d2x)/$den
  $u = ($ex*$d1y - $ey*$d1x)/$den
  if ($t -le 0.02 -or $t -ge 0.98 -or $u -le 0.02 -or $u -ge 0.98) { return $null }  # endpoint contact only
  return , @($ax1+$t*$d1x, $ay1+$t*$d1y)
}
$hits = @()
for ($a = 0; $a -lt $groups.Count; $a++) {
  for ($b = $a+1; $b -lt $groups.Count; $b++) {
    $ga = $groups[$a]; $gb = $groups[$b]
    for ($i = $ga.from; $i -le $ga.to; $i++) {
      for ($j = $gb.from; $j -le $gb.to; $j++) {
        $sa = $segs[$i]; $sb = $segs[$j]
        $p = Cross $sa.x1 $sa.y1 $sa.x2 $sa.y2 $sb.x1 $sb.y1 $sb.x2 $sb.y2
        if ($null -ne $p) { $hits += ("{0}[{1}] X {2}[{3}] at ({4},{5})" -f $ga.name,$i,$gb.name,$j,[Math]::Round($p[0],1),[Math]::Round($p[1],1)) }
      }
    }
  }
}
""
"=== CROSSING TEST (interior x interior, endpoints excluded) ==="
if ($hits.Count -eq 0) { "  PASS - zero crossings between distinct elements." }
else { "  FAIL - " + $hits.Count + " crossing(s):"; $hits | ForEach-Object { "    $_" } }

# ---------- 4. per-edge: does every solid prerequisite advance to a strictly later layer? ----------
""
"=== EDGE <-> LAYER DIRECTION (from graph-audit.json) ==="
$au = Get-Content (Join-Path $ROOT ("outputs\$RUN\A06\graph-audit.json")) -Raw | ConvertFrom-Json
$lay = @{}; foreach ($n in $au.nodes) { $lay[$n.id] = $n.layer }
$bad = @()
foreach ($n in $au.nodes) { foreach ($p in $n.out_neighbors) { if ($lay[$p] -le $lay[$n.id]) { $bad += ($n.id + "->" + $p) } } }
"  solid edges whose target layer <= source layer : " + $bad.Count + $(if($bad.Count){"  (" + ($bad -join ',') + ")"}else{"  -> every prerequisite points strictly forward"})
"  feedback edges excluded from that check        : " + (($au.feedback_edges | ForEach-Object { $_.edge -join '>' }) -join ', ')
"  feedback participates_in_dag_ordering           : " + (($au.feedback_edges | ForEach-Object { $_.participates_in_dag_ordering }) -join ', ')

# ---------- 5. pixels ----------
Add-Type -AssemblyName System.Drawing
$b = [System.Drawing.Bitmap]::FromFile($png)
""
"=== CANVAS ==="
"  size          : " + $b.Width + "x" + $b.Height
$bytes = [System.IO.File]::ReadAllBytes($png)
"  png signature  : " + (($bytes[0..7] | ForEach-Object { $_.ToString('X2') }) -join ' ')
$dslBytes = [System.IO.File]::ReadAllBytes($dsl)
"  dsl BOM       : " + $(if ($dslBytes[0] -eq 0xEF) { "PRESENT (bad)" } else { "absent" })

$bg = [System.Drawing.Color]::FromArgb(11,18,32)
function NonBg($x0,$x1,$y0,$y1){
  $n=0;$minx=99999;$maxx=-1;$miny=99999;$maxy=-1
  for($y=$y0;$y -le $y1;$y++){for($x=$x0;$x -le $x1;$x++){
    $p=$b.GetPixel($x,$y)
    $d=[Math]::Abs($p.R-$bg.R)+[Math]::Abs($p.G-$bg.G)+[Math]::Abs($p.B-$bg.B)
    if($d -gt 28){$n++;if($x -lt $minx){$minx=$x};if($x -gt $maxx){$maxx=$x};if($y -lt $miny){$miny=$y};if($y -gt $maxy){$maxy=$y}}
  }}
  if($n -eq 0){return "n=0"}; return "n=$n bbox=$minx,$miny..$maxx,$maxy"
}
""
"=== MARGINS (non-background pixels) ==="
"  top    y 0..30  : " + (NonBg 0 1599 0 30)
"  bottom y 953..999: " + (NonBg 0 1599 953 999)
"  left   x 0..31  : " + (NonBg 0 31 0 999)
"  right  x 1569..1599: " + (NonBg 1569 1599 0 999)

# ---------- 6. all 14 nodes: box present, id text present, label text present, text inside box ----------
$COLX = @(40.0,181.2,322.4,463.6,604.8,746.0,887.2,1028.4,1169.6,1310.8,1452.0)
$ROWY = @(220.0,480.0,700.0)
$nodeRows = @(
  @('N01','需求冻结',0,1),@('N02','输入检查',1,0),@('N03','字体查询',1,2),@('N04','数据计算',2,0),
  @('N05','内容规划',2,1),@('N06','版式系统',3,2),@('N07','图表生成',3,0),@('N08','DSL构建',4,1),
  @('N09','首轮渲染',5,1),@('N10','视觉检查',6,1),@('N11','问题修复',7,1),@('N12','回归渲染',8,1),
  @('N13','产物校验',9,1),@('N14','交付归档',10,1))
""
"=== NODES (id + label both drawn, text contained in the 108x72 box) ==="
$nodeFail = 0
foreach ($r in $nodeRows) {
  $x = [int]$COLX[$r[2]]; $y = [int]$ROWY[$r[3]]
  # border ring colour just outside the fill
  $borderHit = $false
  for ($dx = -2; $dx -le 109; $dx += 1) {
    $p = $b.GetPixel($x+$dx, $y+2)
    if ($p.R -gt 40 -and $p.R -lt 70 -and $p.B -gt 75) { $borderHit = $true; break }
  }
  # text pixels (bright) inside the box
  $tx0=9999;$tx1=-1;$ty0=9999;$ty1=-1; $nid=0; $nlab=0
  for ($yy = $y+4; $yy -le $y+67; $yy++) {
    for ($xx = $x+4; $xx -le $x+103; $xx++) {
      $p = $b.GetPixel($xx,$yy)
      if ($p.G -gt 150 -and $p.B -gt 170) {           # white label or blue id
        if ($xx -lt $tx0){$tx0=$xx}; if ($xx -gt $tx1){$tx1=$xx}
        if ($yy -lt $ty0){$ty0=$yy}; if ($yy -gt $ty1){$ty1=$yy}
        if ($yy -le $y+33) { $nid++ } else { $nlab++ }
      }
    }
  }
  $ok = ($borderHit -and $nid -gt 40 -and $nlab -gt 40 -and $tx0 -ge $x -and $tx1 -le ($x+107) -and $ty0 -ge $y -and $ty1 -le ($y+71))
  if (-not $ok) { $nodeFail++ }
  "  {0} {1}: border={2} id_px={3} label_px={4} textbox={5}..{6} x {7}..{8}  {9}" -f $r[0],$r[1],$borderHit,$nid,$nlab,$tx0,$tx1,$ty0,$ty1,$(if($ok){'OK'}else{'FAIL'})
}
""
"  nodes failing: $nodeFail / 14"

# ---------- 7. font sizes ----------
""
"=== FONT SIZES IN DSL ==="
$fs = [regex]::Matches((Get-Content $dsl -Raw), 'fontSize="([\d.]+)"') | ForEach-Object { [double]$_.Groups[1].Value }
"  distinct      : " + (($fs | Sort-Object -Unique) -join ', ')
"  min           : " + (($fs | Measure-Object -Minimum).Minimum)
"  element count : " + [regex]::Matches((Get-Content $dsl -Raw), '<(Positioned|Container|Transform|Text|Stack|Snapshot)\b').Count
$b.Dispose()
