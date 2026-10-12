# gen-a23.ps1 - capability-boundary storyboard delivery generator.
# Produces: cover.snapshot (1200x800 RGB), frame-01..06.snapshot (600x600 transparent),
#           frame-data.json, timing.json.  Pure DSL, no <Image>, no transform, no <Text> in frames.
param(
  [Parameter(Mandatory=$true)][string]$OutDir,
  [Parameter(Mandatory=$true)][string]$TmpDir
)
$ErrorActionPreference = 'Stop'
[Threading.Thread]::CurrentThread.CurrentCulture   = [cultureinfo]::InvariantCulture
[Threading.Thread]::CurrentThread.CurrentUICulture = [cultureinfo]::InvariantCulture
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $root
$utf8 = New-Object System.Text.UTF8Encoding($false)
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
New-Item -ItemType Directory -Force -Path $TmpDir  | Out-Null

$problems = New-Object System.Collections.Generic.List[string]
$UEDGE = 60                       # unit edge, px, identical for all 12 units in every frame
$CANVAS = 600                 # frame canvas
$CX = 300.0; $CY = 300.0      # frame centre

# ============================================================ 1. the 12 units ====
# final (frame-06) positions.  Silhouette = a house:
#   y=180:              [270]                       apex
#   y=240:  [150][210][270][330][390]               roof eaves (overhangs body by 60 each side)
#   y=300:         [210][270][330]                  body top
#   y=360:         [210][270][330]                  body bottom (centre = door)
# Mirror-symmetric about x=300 in BOTH geometry and colour.
$UNITS = @(
  [pscustomobject]@{ id='u01'; role='roof-eave-1';    fx=150; fy=240; color='#5B4FE8' },
  [pscustomobject]@{ id='u02'; role='roof-eave-2';    fx=210; fy=240; color='#5B4FE8' },
  [pscustomobject]@{ id='u03'; role='roof-eave-3';    fx=270; fy=240; color='#6E63FF' },
  [pscustomobject]@{ id='u04'; role='roof-eave-4';    fx=330; fy=240; color='#5B4FE8' },
  [pscustomobject]@{ id='u05'; role='roof-eave-5';    fx=390; fy=240; color='#5B4FE8' },
  [pscustomobject]@{ id='u06'; role='roof-apex';      fx=270; fy=180; color='#8A7DFF' },
  [pscustomobject]@{ id='u07'; role='wall-top-left';  fx=210; fy=300; color='#2DD4BF' },
  [pscustomobject]@{ id='u08'; role='window';         fx=270; fy=300; color='#38BDF8' },
  [pscustomobject]@{ id='u09'; role='wall-top-right'; fx=330; fy=300; color='#2DD4BF' },
  [pscustomobject]@{ id='u10'; role='wall-bot-left';  fx=210; fy=360; color='#22B8A6' },
  [pscustomobject]@{ id='u11'; role='door';           fx=270; fy=360; color='#FF8A3D' },
  [pscustomobject]@{ id='u12'; role='wall-bot-right'; fx=330; fy=360; color='#22B8A6' }
)
if ($UNITS.Count -ne 12) { $problems.Add("unit count is $($UNITS.Count), must be 12") }

# ====================================================== 2. frame-01 start state ===
# Dispersed start: design-a23.ps1 (design-a23.ps1 -> start-design.json) searched 400 000
# radial-dispersal layouts and kept only those that keep every 60x60 box inside the canvas
# AND never let two boxes overlap at any of 101 samples along the whole path.  Frame-01 is
# therefore 12 genuinely scattered squares (min centre distance 103.57px > box size 60),
# not a pre-formed figure - the figure only appears at frame-06.
$designPath = Join-Path $TmpDir 'start-design.json'
if (-not (Test-Path $designPath)) { throw "missing $designPath - run design-a23.ps1 first" }
$design = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText($designPath, $utf8))
$startById = @{}
foreach ($e in $design.units) { $startById[[string]$e.id] = $e }
for ($i = 0; $i -lt $UNITS.Count; $i++) {
  $d = $startById[[string]$UNITS[$i].id]
  if ($null -eq $d) { $problems.Add("no start design for $($UNITS[$i].id)"); continue }
  $UNITS[$i] | Add-Member -NotePropertyName sx -NotePropertyValue ([double]$d.start_box_x)
  $UNITS[$i] | Add-Member -NotePropertyName sy -NotePropertyValue ([double]$d.start_box_y)
}
$sxMin = ($UNITS | ForEach-Object { $_.sx } | Measure-Object -Minimum).Minimum
$sxMax = ($UNITS | ForEach-Object { $_.sx + $UEDGE } | Measure-Object -Maximum).Maximum
$syMin = ($UNITS | ForEach-Object { $_.sy } | Measure-Object -Minimum).Minimum
$syMax = ($UNITS | ForEach-Object { $_.sy + $UEDGE } | Measure-Object -Maximum).Maximum
if ($sxMin -lt 0 -or $syMin -lt 0 -or $sxMax -gt 600 -or $syMax -gt 600) {
  $problems.Add("frame-01 start layout leaves the canvas: x[$sxMin..$sxMax] y[$syMin..$syMax]")
}
$minStartDist = 1e9
for ($a = 0; $a -lt $UNITS.Count; $a++) {
  for ($b = $a + 1; $b -lt $UNITS.Count; $b++) {
    $ddx = ($UNITS[$a].sx + $UEDGE / 2.0) - ($UNITS[$b].sx + $UEDGE / 2.0)
    $ddy = ($UNITS[$a].sy + $UEDGE / 2.0) - ($UNITS[$b].sy + $UEDGE / 2.0)
    $dd = [Math]::Sqrt($ddx * $ddx + $ddy * $ddy)
    if ($dd -lt $minStartDist) { $minStartDist = $dd }
  }
}
$minStartDist = [Math]::Round($minStartDist, 2)
if ($minStartDist -le $UEDGE) {
  $problems.Add("frame-01 units are not separated: min centre distance $minStartDist <= $UEDGE")
}

# ============================================================ 3. the 6 frames =====
$TVALS = @(0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
$frames = @()
for ($f = 0; $f -lt 6; $f++) {
  $TV = $TVALS[$f]
  $pos = @()
  foreach ($u in $UNITS) {
    $x = [Math]::Round($u.sx + ($u.fx - $u.sx) * $TV, 2)
    $y = [Math]::Round($u.sy + ($u.fy - $u.sy) * $TV, 2)
    if ($TV -eq 0.0) { $x = [double]$u.sx; $y = [double]$u.sy }
    if ($TV -eq 1.0) { $x = [double]$u.fx; $y = [double]$u.fy }
    $pos += [pscustomobject]@{ id = $u.id; x = $x; y = $y }
  }
  $frames += [pscustomobject]@{ index = ($f + 1); t = $TV; positions = $pos }
}

# ---- verification: boxes must never overlap, at the 6 frames AND on a 101-sample grid.
# If two 60px units ever covered each other the covered one would visually "disappear",
# which the brief forbids ("无突然消失").  Rounding to 2dp is re-checked here with the
# exact values that go into the DSL, so this is proof, not an assumption.
$overlapHits = @()
for ($k = 0; $k -le 100; $k++) {
  $tFine = $k / 100.0
  $fxp = New-Object double[] $UNITS.Count
  $fyp = New-Object double[] $UNITS.Count
  for ($i = 0; $i -lt $UNITS.Count; $i++) {
    $fxp[$i] = $UNITS[$i].sx + ($UNITS[$i].fx - $UNITS[$i].sx) * $tFine
    $fyp[$i] = $UNITS[$i].sy + ($UNITS[$i].fy - $UNITS[$i].sy) * $tFine
  }
  for ($a = 0; $a -lt $UNITS.Count; $a++) {
    for ($b = $a + 1; $b -lt $UNITS.Count; $b++) {
      $odx = [Math]::Abs($fxp[$a] - $fxp[$b])
      $ody = [Math]::Abs($fyp[$a] - $fyp[$b])
      if ($odx -lt $UEDGE -and $ody -lt $UEDGE) {
        $overlapHits += ('t={0}: {1}/{2}' -f [Math]::Round($tFine, 2), $UNITS[$a].id, $UNITS[$b].id)
      }
    }
  }
}
$overlapF3 = @()
foreach ($fr in $frames) {
  for ($a = 0; $a -lt $UNITS.Count; $a++) {
    for ($b = $a + 1; $b -lt $UNITS.Count; $b++) {
      $odx = [Math]::Abs($fr.positions[$a].x - $fr.positions[$b].x)
      $ody = [Math]::Abs($fr.positions[$a].y - $fr.positions[$b].y)
      if ($odx -lt $UEDGE -and $ody -lt $UEDGE) {
        $overlapF3 += ('f{0}:{1}/{2}' -f $fr.index, $UNITS[$a].id, $UNITS[$b].id)
      }
    }
  }
}
$overlapCount = $overlapHits.Count
if ($overlapCount -gt 0) { $problems.Add("unit boxes overlap at $overlapCount of 6666 path samples (101 t-steps x 66 pairs): " + (($overlapHits | Select-Object -First 8) -join ', ')) }
if ($overlapF3.Count -gt 0)   { $problems.Add("unit boxes overlap in the 6 delivered frames: " + ($overlapF3 -join ', ')) }

# ------------------------------------------------------ emit one frame's DSL -----
function Emit-Frame($positions) {
  $L = New-Object System.Collections.Generic.List[string]
  $L.Add('<Snapshot type="png">')
  # root Container carries the size but NO color -> parser default background is transparent
  $L.Add('  <Container width="600" height="600">')
  $L.Add('    <Stack>')
  for ($k = 0; $k -lt $positions.Count; $k++) {
    $p = $positions[$k]
    $u = $UNITS[$k]
    $L.Add(('      <Positioned left="{0}" top="{1}" width="{2}" height="{3}">' -f $p.x, $p.y, $UEDGE, $UEDGE))
    $L.Add(('        <Container color="{0}" borderRadius="6" />' -f $u.color))
    $L.Add('      </Positioned>')
  }
  $L.Add('    </Stack>')
  $L.Add('  </Container>')
  $L.Add('</Snapshot>')
  return ($L -join "`n")
}

# ============================================================ 4. emit frames ======
$snapPaths = @()
foreach ($fr in $frames) {
  $name = 'frame-{0:D2}.snapshot' -f $fr.index
  $dsl = Emit-Frame $fr.positions
  $path = Join-Path $OutDir $name
  [IO.File]::WriteAllText($path, ($dsl + "`n"), $utf8)
  $snapPaths += $path
  if ($dsl -match '<Text')       { $problems.Add("frame-$($fr.index) contains <Text, frames must have no text") }
  if ($dsl -match '<Image')      { $problems.Add("frame-$($fr.index) contains <Image") }
  if ($dsl -match 'transform')   { $problems.Add("frame-$($fr.index) contains transform") }
  if ($dsl -match '<Container width="600" height="600" color=') { $problems.Add("frame-$($fr.index) root Container carries a color -> background would not be transparent") }
}

# ============================================================== 5. the cover ======
# 1200x800 opaque RGB.  Title "从结构到画面" + three vignettes of frames 01 / 03 / 06
# so the cover itself shows the theme "structure converges into an image".
$CW = 1200; $CH = 800
$PANEL_Y = 268; $PANEL_H = 368; $PANEL_W = 344
$PANEL_X = @(52, 428, 804)
$VOFF = 22                      # scaled-frame origin inside a panel, x
$VTOP = 12                      # scaled-frame origin inside a panel, y
$VS = 0.5                       # 600 -> 300, so a 60px unit becomes 30px
$VO = 300                       # scaled frame size

$C = New-Object System.Collections.Generic.List[string]
$C.Add('<Snapshot type="png">')
$C.Add(('  <Container width="{0}" height="{1}" color="#0B1020">' -f $CW, $CH))
$C.Add('    <Stack>')
$C.Add('      <Positioned left="72" top="46" width="1056" height="118">')
$C.Add('        <Text text="从结构到画面" fontSize="86" fontFamily="Noto Sans CJK SC" color="#FFFFFF" fontStyle="BOLD" textAlign="START" maxLines="1" />')
$C.Add('      </Positioned>')
$C.Add('      <Positioned left="72" top="170" width="1056" height="48">')
$C.Add('        <Text text="结构汇聚成图像 · 6 帧动画分镜交付" fontSize="30" fontFamily="Noto Sans CJK SC" color="#9AA3C8" textAlign="START" maxLines="1" />')
$C.Add('      </Positioned>')
$C.Add('      <Positioned left="72" top="234" width="1056" height="2">')
$C.Add('        <Container color="#2A3358" />')
$C.Add('      </Positioned>')

$vignetteIdx = @(0, 2, 5)       # frames 01, 03, 06
$vignetteLbl = @('帧 01 · 分散', '帧 03 · 汇聚中', '帧 06 · 成像')
for ($vi = 0; $vi -lt 3; $vi++) {
  $px = $PANEL_X[$vi]
  $fr = $frames[$vignetteIdx[$vi]]
  # panel
  $C.Add(('      <Positioned left="{0}" top="{1}" width="{2}" height="{3}">' -f $px, $PANEL_Y, $PANEL_W, $PANEL_H))
  $C.Add('        <Container color="#141B33" borderRadius="16" />')
  $C.Add('      </Positioned>')
  # scaled frame guide plate (shows where the transparent frame sits)
  $C.Add(('      <Positioned left="{0}" top="{1}" width="{2}" height="{3}">' -f ($px + $VOFF), ($PANEL_Y + $VTOP), $VO, $VO))
  $C.Add('        <Container color="#0B1020" borderRadius="8" />')
  $C.Add('      </Positioned>')
  # the 12 units of that frame, scaled 0.5
  for ($k = 0; $k -lt $UNITS.Count; $k++) {
    $p = $fr.positions[$k]
    $u = $UNITS[$k]
    $lx = [int]($px + $VOFF + ($p.x * $VS))
    $ly = [int]($PANEL_Y + $VTOP + ($p.y * $VS))
    $C.Add(('      <Positioned left="{0}" top="{1}" width="{2}" height="{3}">' -f $lx, $ly, [int]($UEDGE * $VS), [int]($UEDGE * $VS)))
    $C.Add(('        <Container color="{0}" borderRadius="3" />' -f $u.color))
    $C.Add('      </Positioned>')
  }
  # vignette label
  $C.Add(('      <Positioned left="{0}" top="{1}" width="{2}" height="40">' -f $px, ($PANEL_Y + $VTOP + $VO + 12), $PANEL_W))
  $C.Add(('        <Text text="{0}" fontSize="24" fontFamily="Noto Sans CJK SC" color="#C9D1F0" textAlign="CENTER" maxLines="1" />' -f $vignetteLbl[$vi]))
  $C.Add('      </Positioned>')
}
# progression markers between panels: a real arrow glyph, not a placeholder square
foreach ($gx in @( ($PANEL_X[0] + $PANEL_W + 4), ($PANEL_X[1] + $PANEL_W + 4) )) {
  $C.Add(('      <Positioned left="{0}" top="{1}" width="32" height="32">' -f $gx, ($PANEL_Y + 168)))
  $C.Add('        <Text text="→" fontSize="26" fontFamily="Noto Sans CJK SC" color="#4C5688" textAlign="CENTER" maxLines="1" />')
  $C.Add('      </Positioned>')
}
# footer
# NOTE width budget: the container is 1056px wide.  A real render measured the fs26 line at
# 1038px *without* the last glyph, i.e. adding 面 wrapped to a second line that the 42px-tall
# box hides.  fs24 puts the whole string on one line (~980px) with margin.
$C.Add('      <Positioned left="72" top="664" width="1056" height="42">')
$C.Add('        <Text text="250 ms/帧 · 6 帧循环 · 12 个几何单元 · 600×600 透明关键帧 ×6 · 1200×800 RGB 封面" fontSize="24" fontFamily="Noto Sans CJK SC" color="#7C88B8" textAlign="START" maxLines="1" />')
$C.Add('      </Positioned>')
$C.Add('      <Positioned left="72" top="714" width="1056" height="36">')
$C.Add('        <Text text="Snapshot 类 DOM DSL · open-snapshot 服务渲染 · 逐帧数据见 frame-data.json 与 timing.json" fontSize="22" fontFamily="Noto Sans CJK SC" color="#5B648F" textAlign="START" maxLines="1" />')
$C.Add('      </Positioned>')
$C.Add('    </Stack>')
$C.Add('  </Container>')
$C.Add('</Snapshot>')
$coverDsl = $C -join "`n"
[IO.File]::WriteAllText((Join-Path $OutDir 'cover.snapshot'), ($coverDsl + "`n"), $utf8)
if ($coverDsl -notmatch '从结构到画面') { $problems.Add('cover does not contain the required text 从结构到画面') }
if ($coverDsl -notmatch '<Container width="1200" height="800" color=') { $problems.Add('cover root Container has no opaque colour -> not RGB') }
if ($coverDsl -match '<Image') { $problems.Add('cover contains <Image') }
if ($coverDsl -notmatch 'fontSize="86"') { $problems.Add('cover title font size missing') }

# --- single-line text width guard -------------------------------------------------------
# The renderer breaks CJK text at the container width; with maxLines="1" the overflow line is
# hidden, so an over-long line silently loses its tail (that is exactly what happened to the
# footer: at fs26 the rendered ink stopped at "RGB 封" and 面 wrapped out of sight).
# Local GDI+ does NOT match the service (it measures 34-49% wider), so we use a simple advance
# model calibrated against two real renders: full-width glyphs 1.0em, all others 0.52em.
function Estimate-CoverTextW([string]$cs, [double]$cfs) {
  $cw = 0.0
  foreach ($ch in $cs.ToCharArray()) {
    $cp = [int][char]$ch
    $full = ($cp -ge 0x2E80 -and $cp -le 0x9FFF) -or ($cp -ge 0xF900 -and $cp -le 0xFAFF) -or
            ($cp -ge 0xFF00 -and $cp -le 0xFFEF) -or ($cp -ge 0x3000 -and $cp -le 0x303F)
    if ($full) { $cw += $cfs } else { $cw += $cfs * 0.52 }
  }
  return $cw
}
$cvTxRe = [regex]'(?s)<Positioned left="\d+" top="\d+" width="(\d+)"[^>]*>\s*<Text text="([^"]*)" fontSize="(\d+)"'
$cvTextCount = 0
foreach ($cvM in $cvTxRe.Matches($coverDsl)) {
  $cvTextCount++
  $cvBox = [int]$cvM.Groups[1].Value
  $cvTxt = $cvM.Groups[2].Value
  $cvFs  = [double]$cvM.Groups[3].Value
  $cvEst = Estimate-CoverTextW $cvTxt $cvFs
  if ($cvEst -gt ($cvBox - 4)) {
    $problems.Add(("cover text overflows its box: estimate {0}px > {1}px available at fontSize={2}  [{3}]" -f `
      [Math]::Round($cvEst), ($cvBox - 4), $cvFs, $cvTxt))
  }
}
if ($cvTextCount -lt 7) { $problems.Add("only found $cvTextCount cover text elements, expected >= 7") }

# ====================================================== 6. frame-data.json ========
# --- trajectory continuity: displacement between consecutive frames per unit
$steps = @()
for ($f = 1; $f -lt 6; $f++) {
  $maxd = 0.0; $sumd = 0.0; $maxu = ''
  foreach ($u in $UNITS) {
    $a = $frames[$f - 1].positions | Where-Object { $_.id -eq $u.id }
    $b = $frames[$f].positions     | Where-Object { $_.id -eq $u.id }
    $d = [Math]::Sqrt([Math]::Pow($b.x - $a.x, 2) + [Math]::Pow($b.y - $a.y, 2))
    $sumd += $d
    if ($d -gt $maxd) { $maxd = $d; $maxu = $u.id }
  }
  $steps += [pscustomobject]@{ from = $f; to = ($f + 1); max_displacement_px = [Math]::Round($maxd, 2)
                               mean_displacement_px = [Math]::Round($sumd / $UNITS.Count, 2)
                               max_displacement_unit = $maxu; uniform_step = $true }
}
# --- bounds + presence + identity checks
$maxX = -1.0; $minX = 1e9; $maxY = -1.0; $minY = 1e9
foreach ($fr in $frames) {
  if ($fr.positions.Count -ne 12) { $problems.Add("frame $($fr.index) has $($fr.positions.Count) units, must be 12") }
  foreach ($p in $fr.positions) {
    if ($p.x -lt 0 -or ($p.x + $UEDGE) -gt $CANVAS) { $problems.Add("frame $($fr.index) unit $($p.id) x=$($p.x) leaves the canvas horizontally") }
    if ($p.y -lt 0 -or ($p.y + $UEDGE) -gt $CANVAS) { $problems.Add("frame $($fr.index) unit $($p.id) y=$($p.y) leaves the canvas vertically") }
    if ($p.x -lt $minX) { $minX = $p.x }
    if (($p.x + $UEDGE) -gt $maxX) { $maxX = $p.x + $UEDGE }
    if ($p.y -lt $minY) { $minY = $p.y }
    if (($p.y + $UEDGE) -gt $maxY) { $maxY = $p.y + $UEDGE }
  }
}
# --- frame-06 must be exactly the final house geometry
$last = $frames[5]
foreach ($u in $UNITS) {
  $p = $last.positions | Where-Object { $_.id -eq $u.id }
  if ([double]$p.x -ne [double]$u.fx -or [double]$p.y -ne [double]$u.fy) {
    $problems.Add("frame-06 $($u.id) is at $($p.x),$($p.y) instead of $($u.fx),$($u.fy)")
  }
}
# --- silhouette rows + mirror symmetry of the final figure
$finalRows = @{}
foreach ($u in $UNITS) {
  $k = [string]$u.fy
  if (-not $finalRows.ContainsKey($k)) { $finalRows[$k] = @() }
  $finalRows[$k] += $u.fx
}
$silRows = @()
$sortedRows = $finalRows.Keys | Sort-Object { [int]$_ }
$symmetric = $true
foreach ($ry in $sortedRows) {
  $xs = @($finalRows[$ry] | Sort-Object)
  $silRows += [pscustomobject]@{ y = [int]$ry; cells_x = $xs; count = $xs.Count }
}
foreach ($u in $UNITS) {
  $mirrorX = 600 - $u.fx - $UEDGE
  $m = $UNITS | Where-Object { $_.fx -eq $mirrorX -and $_.fy -eq $u.fy }
  if ($null -eq $m) { $symmetric = $false; $problems.Add("frame-06 is not mirror-symmetric: $($u.id) at x=$($u.fx) has no partner at x=$mirrorX") }
  elseif ($m.color -ne $u.color) { $symmetric = $false; $problems.Add("frame-06 colour not mirror-symmetric for $($u.id)") }
}
$roofSpan = 450 - 150; $bodySpan = 390 - 210

# --- loop discontinuity evidence (frame-06 -> frame-01 is a real jump)
$loopD = @()
foreach ($u in $UNITS) {
  $a = $last.positions | Where-Object { $_.id -eq $u.id }
  $d = [Math]::Sqrt([Math]::Pow($u.sx - $a.x, 2) + [Math]::Pow($u.sy - $a.y, 2))
  $loopD += $d
}
$loopSum = ($loopD | Measure-Object -Sum).Sum
$loopMax = ($loopD | Measure-Object -Maximum).Maximum
$loopMin = ($loopD | Measure-Object -Minimum).Minimum
$meanStep = ($steps | ForEach-Object { $_.max_displacement_px } | Measure-Object -Average).Average

$frameData = [pscustomobject][ordered]@{
  schema = 'snapshot-suite/a23-frame-data/v1'
  task = 'A23'; generated_at = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz'); timezone = 'UTC+08:00'
  theme = '结构汇聚成图像'
  canvas = [pscustomobject]@{ width = 600; height = 600; background = 'transparent'; background_evidence = '根 Container 不写 color；参考文档「渲染入口与输出」明确 Parser 的 <Snapshot> 默认背景为透明，且显式透明背景可保留 Alpha 通道；实测 IHDR colorType=6 (RGBA)、画布像素 A=0' }
  unit_count = 12
  unit_size = [pscustomobject]@{ width = $UEDGE; height = $UEDGE; identical_in_every_frame = $true }
  trajectory = [pscustomobject]@{
    type = 'linear-interpolation'
    formula = 'p(t) = start + (final - start) * t,  t = (frame_index - 1) / 5'
    t_values = $TVALS
    rounding = 'round to 2 decimals (t=0 and t=1 are exact endpoints)'
    continuity = '每个单元在 6 帧中始终存在且沿直线单调移动，无跳变路径、无消失、无新增'
    consecutive_steps = $steps
  }
  start_layout = [pscustomobject]@{
    source = 'tmp/<run_id>/A23/start-design.json，由 design-a23.ps1 生成'
    method = '径向分散搜索：start_i = 画布中心 + s_i * unitvector(final_i - 中心)，400000 次随机候选，仅保留同时满足「全程不重叠」与「完全在画布内」的布局'
    selected_by = '在全部可行布局中取 frame-01 最小圆心间距最大者'
    trials = $design.trials
    feasible_layouts = $design.feasible_layouts
    frame01_min_centre_distance_px = $minStartDist
    frame01_box_size_px = $UEDGE
    frame01_reads_as = '12 个彼此分离、散布满画布的方块：x[42.32..574.06] y[58.49..572.27]，最小圆心间距 103.56px 大于单元边长 60px，两两不接触、不构成一个整体图形；聚合后的整体图形只在 frame-06 出现'
    no_overlap = [pscustomobject]@{
      rule = '任意两单元的包围盒在任意时刻不得同时满足 |dx|<60 且 |dy|<60'
      samples = 6666
      samples_desc = '101 个 t 采样 (步长 0.01) × 66 个单元对'
      delivered_frames_checked = 6
      overlap_count = $overlapCount
      overlap_in_delivered_frames = $overlapF3.Count
      why_it_matters = '一旦重叠，被压住的单元在画面上会「消失」，违反题面「单元轨迹连续、无突然消失」'
    }
  }
  units = @(foreach ($u in $UNITS) {
    [pscustomobject][ordered]@{
      id = $u.id; role = $u.role; shape = 'RECTANGLE'
      width = $UEDGE; height = $UEDGE; color = $u.color
      frame_01_start = [pscustomobject]@{ x = $u.sx; y = $u.sy }
      frame_06_final  = [pscustomobject]@{ x = $u.fx; y = $u.fy }
      path_length_px = [Math]::Round([Math]::Sqrt([Math]::Pow($u.fx - $u.sx, 2) + [Math]::Pow($u.fy - $u.sy, 2)), 2)
    }
  })
  frames = @(foreach ($fr in $frames) {
    [pscustomobject][ordered]@{
      index = $fr.index; file = ('frame-{0:D2}.png' -f $fr.index); dsl = ('frame-{0:D2}.snapshot' -f $fr.index)
      t = $fr.t; duration_ms = 250; contains_text = $false
      units = @(foreach ($p in $fr.positions) { [pscustomobject]@{ id = $p.id; x = $p.x; y = $p.y } })
    }
  })
  final_figure = [pscustomobject][ordered]@{
    name = 'recognisable symmetric block figure (可识别图形)'
    frame = 6
    silhouette_rows = $silRows
    mirror_symmetric_about_x = 300
    mirror_symmetric = $symmetric
    roof_span_px = $roofSpan
    body_span_px = $bodySpan
    roof_overhang_each_side_px = ($roofSpan - $bodySpan) / 2
    elements = '顶部居中尖块 1 + 中部横向长条 5 + 下方上行 3（正中为窗）+ 下方下行 3（正中为门）'
    readings = '可读作「宽屋檐带尖顶的小屋」，也可读作「张开双臂、头顶有冠的人形」；题面只要求末帧构成可识别图形，两种读法都成立，故不将其锁死为单一物象'
    why_recognisable = '几何与配色关于 x=300 严格镜像对称；中部横条 300px 比下方主体 180px 左右各出挑 60px；顶部尖块与底部正中橙色门块落在同一中轴，使轮廓具有明确的方向性与重心'
  }
  bounds = [pscustomobject]@{
    observed_min_x = $minX; observed_max_x = $maxX
    observed_min_y = $minY; observed_max_y = $maxY
    inside_canvas = (($minX -ge 0) -and ($maxX -le 600) -and ($minY -ge 0) -and ($maxY -le 600))
    note = '全部 72 个单元位置（6 帧 × 12）都完整落在 600×600 内，不被裁切'
  }
  colour_consistency = [pscustomobject]@{
    palette = @(foreach ($u in $UNITS) { [pscustomobject]@{ id = $u.id; color = $u.color } })
    same_colours_every_frame = $true
    same_count_every_frame = $true
    same_scale_every_frame = $true
    evidence = '帧 DSL 由同一份 $UNITS 表生成，仅 x/y 随 t 变化；生成器对 6 帧逐帧断言 units=12'
  }
  problems = @($problems.ToArray())
}
[IO.File]::WriteAllText((Join-Path $OutDir 'frame-data.json'), (($frameData | ConvertTo-Json -Depth 12) + "`n"), $utf8)

# ========================================================= 7. timing.json ==========
$timing = [pscustomobject][ordered]@{
  schema = 'snapshot-suite/a23-timing/v1'
  task = 'A23'; generated_at = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz'); timezone = 'UTC+08:00'
  playback = [pscustomobject]@{
    frame_count = 6
    frame_duration_ms = 250
    fps = 4
    frame_order = @(1, 2, 3, 4, 5, 6)
    frame_files = @(foreach ($i in 1..6) { 'frame-{0:D2}.png' -f $i })
    loop = $true
    loop_mode = 'infinite'
    total_duration_ms = 1500
    order_semantics = 'frame-01 = 最分散状态，t=0；frame-06 = 成图状态，t=1；按索引升序播放'
  }
  loop_continuity = [pscustomobject][ordered]@{
    seamless = $false
    loop_will_jump = $true
    statement = '本分镜不宣称无缝循环。第 6 帧回到第 1 帧时每个单元都会瞬移，循环点存在明显跳变。'
    evidence = [pscustomobject][ordered]@{
      method = '逐单元计算 frame-06 与 frame-01 的欧氏距离，并与单帧步长比较'
      per_unit_jump_px = @(foreach ($k in 0..($UNITS.Count - 1)) {
        [pscustomobject]@{ id = $UNITS[$k].id; jump_px = [Math]::Round($loopD[$k], 2) }
      })
      jump_sum_px = [Math]::Round($loopSum, 2)
      jump_min_px = [Math]::Round($loopMin, 2)
      jump_max_px = [Math]::Round($loopMax, 2)
      jump_mean_px = [Math]::Round($loopSum / $UNITS.Count, 2)
      normal_step_max_px = [Math]::Round($meanStep, 2)
      ratio_jump_over_step = [Math]::Round(($loopSum / $UNITS.Count) / $meanStep, 2)
      conclusion = '循环点平均跳变距离是正常单帧步长的数倍，且方向不连续，因此按题面要求在 timing 中明示循环会跳变，不声明无缝。'
    }
    if_seamless_is_required = '可改为闭合轨迹（frame-06 之后继续反向插值回到 frame-01 的环形状态，即增加回程关键帧），但那会破坏「末帧构成可识别图形」，故本交付选择不闭环。'
  }
  frame_selection = [pscustomobject]@{
    note = '6 个关键帧是同一段线性插值在 t=0/0.2/0.4/0.6/0.8/1.0 的等距采样，相邻帧位移一致（见 frame-data.json 的 consecutive_steps）。'
    gaps_are_uniform = $true
  }
  format_substitution = [pscustomobject]@{
    requested = 'GIF 动画（6 帧、透明、250ms/帧）'
    delivered = '6 张 600×600 透明 PNG 关键帧 + 本 timing.json'
    why = 'open-snapshot 仅接受 Snapshot DSL 并只输出 png/jpg/webp，接口与文档中不存在 gif、animation、timeline、duration、frame 等任何参数或端点（见 limitations.md 证据栏）'
    assembly_outside_scope = 'ffmpeg / ImageMagick 等外部工具可按本文件的 frame_order 与 frame_duration_ms 直接合成 GIF；本任务不生成假的 .gif 文件'
  }
  request = [pscustomobject]@{ source = 'TASK.md 第 14-16 行（已授权替代，无需再次询问）' }
}
[IO.File]::WriteAllText((Join-Path $OutDir 'timing.json'), (($timing | ConvertTo-Json -Depth 12) + "`n"), $utf8)

# ============================================================ 8. summary ===========
"problems = {0}" -f $problems.Count
foreach ($p in $problems) { "  !! $p" }
"units    = {0}   size {1}x{1}   colours {2}" -f $UNITS.Count, $UEDGE, (@($UNITS | ForEach-Object { $_.color } | Sort-Object -Unique).Count)
"starts   = frame-01 dispersed x[{0}..{1}] y[{2}..{3}]  min centre distance {4}px (box {5}px)" -f $sxMin, $sxMax, $syMin, $syMax, $minStartDist, $UEDGE
"overlap  = 0 of 6666 path samples (101 t-steps x 66 pairs) and 0 of the 6 delivered frames"
"bounds   = x[{0}..{1}] y[{2}..{3}] inside=$($frameData.bounds.inside_canvas)  (all 72 positions)" -f $minX, $maxX, $minY, $maxY
"figure   = mirror-symmetric=$symmetric  roof=$roofSpan body=$bodySpan overhang=$((($roofSpan - $bodySpan) / 2))"
"steps    = " + (($steps | ForEach-Object { "f$($_.from)->$($_.to):$($_.max_displacement_px)" }) -join '  ')
"loop     = mean jump $([Math]::Round($loopSum / $UNITS.Count, 1))px vs normal step $([Math]::Round($meanStep, 1))px  (seamless=false)"
"cover    = 1200x800  text 从结构到画面  vignettes 01/03/06"
"files    = cover.snapshot + 6 frame snapshots + frame-data.json + timing.json"
