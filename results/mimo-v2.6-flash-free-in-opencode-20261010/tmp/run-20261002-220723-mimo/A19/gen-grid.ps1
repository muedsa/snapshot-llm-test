param(
  [int]$Seed = 20261004,
  [Parameter(Mandatory=$true)][string]$OutDsl,
  [Parameter(Mandatory=$true)][string]$OutGeom,
  [switch]$Quiet
)
$ErrorActionPreference = 'Stop'
[Threading.Thread]::CurrentThread.CurrentCulture   = [cultureinfo]::InvariantCulture
[Threading.Thread]::CurrentThread.CurrentUICulture = [cultureinfo]::InvariantCulture
$utf8 = New-Object System.Text.UTF8Encoding($false)

# ---------------------------------------------------------------- constants ----
$CANVAS = 1600
$ORIGIN = 40          # grid frame top-left
$CELL   = 190         # 40 + 8*190 = 1560, 40px frame margin
$N      = 8

$BG      = '#F8FAFC'
$ROWALT  = '#EEF2F7'
$LINE    = '#94A3B8'
$IDCOL   = '#475569'
$FONTID  = 'Noto Sans Mono CJK SC'

$colorHex = [ordered]@{ blue = '#3B82F6'; orange = '#F59E0B'; green = '#22C55E'; purple = '#A855F7' }
$shapeList = @('circle','square','ring','rounded-square')
$sizeList  = @(48, 64, 80)

function F([double]$v) { if ($v -eq [Math]::Floor($v)) { return [string][int]$v } return $v.ToString([cultureinfo]::InvariantCulture) }

# --------------------------------------------------------------- assignment ----
# Deterministic and seeded. Colour and shape are two independent 64-cell bags
# (16 of each value) shuffled separately and then checked against the hard rules;
# sizes are a third independent shuffle. Attributes therefore cross rather than
# repeat: an earlier draft derived colour and shape from the same column index,
# which locked them into period-4 pairs inside every row - visible on the render
# and confirmed by the colour x shape matrix, so it was replaced by this.
$rng = New-Object System.Random($Seed)
function Shuffled($bag) {
  $w = @(); foreach ($x in $bag) { $w += $x }
  for ($i = $w.Count - 1; $i -gt 0; $i--) { $j = $rng.Next($i + 1); $t = $w[$i]; $w[$i] = $w[$j]; $w[$j] = $t }
  return ,$w
}
$colorNames = @($colorHex.Keys)

# Colours and shapes are shuffled INDEPENDENTLY as two separate 64-cell bags, so
# the two attributes are genuinely crossed instead of being locked in period-4
# pairs (a first draft built both from the same column index, which made every
# row a repeating colour<->shape pairing - that was seen by looking at the render
# and reading the resulting matrix, and is why this is a shuffle now).
# Acceptance test: >= 3 distinct colours AND >= 3 distinct shapes in every row,
# AND all 16 colour x shape combinations present at least once.
function Assign($bag, [int]$minDistinct, [string]$what, [int]$mustCover) {
  for ($try = 1; $try -le 400; $try++) {
    $arr = Shuffled $bag
    $ok = $true
    for ($r = 0; $r -lt $N -and $ok; $r++) {
      $seen = @{}
      for ($c = 0; $c -lt $N; $c++) { $seen[$arr[$r * $N + $c]] = 1 }
      if ($seen.Count -lt $minDistinct) { $ok = $false }
    }
    if ($ok -and $mustCover -gt 0) {
      $cov = @{}
      for ($i = 0; $i -lt $arr.Count; $i++) { $cov[$arr[$i]] = 1 + $cov[$arr[$i]] }
      if ($cov.Count -lt $mustCover) { $ok = $false }
    }
    if ($ok) { return ,@($arr, $try) }
  }
  throw "could not satisfy the $what constraints in 400 shuffles (seed $Seed)"
}

$colorBag = @()
$shapeBag = @()
foreach ($cn in $colorNames) { for ($i = 0; $i -lt 16; $i++) { $colorBag += $cn } }
foreach ($sn in $shapeList)  { for ($i = 0; $i -lt 16; $i++) { $shapeBag += $sn } }

# accept / reject whole candidate pairs until colour x shape covers all 16 combos
$pairTries = 0
$pairCover = 0
$colorTries = 0
$shapeTries = 0
while ($pairCover -lt 16 -and $pairTries -lt 400) {
  $pairTries++
  $colorRes = Assign $colorBag 3 'row colour' 0
  $shapeRes = Assign $shapeBag 3 'row shape'  0
  $colorArr = $colorRes[0]; $colorTries = $colorRes[1]
  $shapeArr = $shapeRes[0]; $shapeTries = $shapeRes[1]
  $pairs = @{}
  for ($i = 0; $i -lt 64; $i++) { $pairs["$($colorArr[$i])/$($shapeArr[$i])"] = 1 }
  $pairCover = $pairs.Count
}

$colorAt = @{}   # "$r,$c" -> colour name
$shapeAt = @{}
for ($i = 0; $i -lt 64; $i++) {
  $rr = [int][Math]::Floor($i / $N); $cc = $i % $N
  $colorAt["$rr,$cc"] = $colorArr[$i]
  $shapeAt["$rr,$cc"] = $shapeArr[$i]
}
# sizes: 22/21/21 across 64 cells, spread by a seeded shuffle
$sizeBag = @()
for ($i = 0; $i -lt 22; $i++) { $sizeBag += 80 }
for ($i = 0; $i -lt 21; $i++) { $sizeBag += 64 }
for ($i = 0; $i -lt 21; $i++) { $sizeBag += 48 }
$sizeBag = Shuffled $sizeBag

# ---------------------------------------------------------------- geometry -----
$objs = New-Object System.Collections.Generic.List[object]
$k = 0
for ($r = 0; $r -lt $N; $r++) {
  for ($c = 0; $c -lt $N; $c++) {
    $id    = 'G' + ('{0:d2}' -f ($r * $N + $c + 1))
    $cx    = $ORIGIN + $CELL * $c + ($CELL / 2)
    $cy    = $ORIGIN + $CELL * $r + ($CELL / 2)
    $sz    = [int]$sizeBag[$k]
    $col   = $colorAt["$r,$c"]
    $shp   = $shapeAt["$r,$c"]
    $half  = $sz / 2
    $objs.Add([pscustomobject]@{
      id = $id; row = $r; col = $c
      cx = $cx; cy = $cy
      color = $col; hex = $colorHex[$col]; shape = $shp; size = $sz
      bbox_x0 = $cx - $half; bbox_y0 = $cy - $half
      bbox_x1 = $cx + $half; bbox_y1 = $cy + $half
      ring_inner = $(if ($shp -eq 'ring') { $sz / 2 } else { 0 })
      cell_x0 = $ORIGIN + $CELL * $c; cell_y0 = $ORIGIN + $CELL * $r
      cell_x1 = $ORIGIN + $CELL * ($c + 1); cell_y1 = $ORIGIN + $CELL * ($r + 1)
      id_label_x = $ORIGIN + $CELL * $c + 8
      id_label_y = $ORIGIN + $CELL * $r + 6
    })
    $k++
  }
}

# ------------------------------------------------------------- self-checks ------
$problems = New-Object System.Collections.Generic.List[string]
$notes    = New-Object System.Collections.Generic.List[string]

$byColor = @{}; foreach ($o in $objs) { $byColor[$o.color] = 1 + $byColor[$o.color] }
$byShape = @{}; foreach ($o in $objs) { $byShape[$o.shape] = 1 + $byShape[$o.shape] }
foreach ($cn in $colorNames) { if ($byColor[$cn] -ne 16) { $problems.Add("colour $cn has $($byColor[$cn]), expected 16") } }
foreach ($sn in $shapeList)  { if ($byShape[$sn] -ne 16) { $problems.Add("shape $sn has $($byShape[$sn]), expected 16") } }
if ($objs.Count -ne 64) { $problems.Add("object count $($objs.Count), expected 64") }

for ($r = 0; $r -lt $N; $r++) {
  $rowObjs = @($objs | Where-Object { $_.row -eq $r })
  $rc = @($rowObjs | ForEach-Object { $_.color } | Sort-Object -Unique)
  $rs = @($rowObjs | ForEach-Object { $_.shape } | Sort-Object -Unique)
  if ($rc.Count -lt 3) { $problems.Add("row $r has only $($rc.Count) colours, need >= 3") }
  if ($rs.Count -lt 3) { $problems.Add("row $r has only $($rs.Count) shapes, need >= 3") }
  if ($rowObjs.Count -ne 8) { $problems.Add("row $r has $($rowObjs.Count) objects, expected 8") }
}
$notes.Add("row colour spread: min " + (@($objs | Group-Object row | ForEach-Object { @($_.Group | ForEach-Object { $_.color } | Sort-Object -Unique).Count }) | Measure-Object -Minimum).Minimum + " distinct colours per row")
$notes.Add("row shape spread: min " + (@($objs | Group-Object row | ForEach-Object { @($_.Group | ForEach-Object { $_.shape } | Sort-Object -Unique).Count }) | Measure-Object -Minimum).Minimum + " distinct shapes per row")
$bySize = @{}; foreach ($o in $objs) { $bySize[$o.size] = 1 + $bySize[$o.size] }
$notes.Add("size spread 48/64/80 = " + $bySize[48] + '/' + $bySize[64] + '/' + $bySize[80])

foreach ($o in $objs) {
  if ($o.bbox_x0 -le $o.cell_x0 -or $o.bbox_x1 -ge $o.cell_x1 -or $o.bbox_y0 -le $o.cell_y0 -or $o.bbox_y1 -ge $o.cell_y1) {
    $problems.Add("$($o.id) bbox touches a cell border")
  }
  # id label must sit outside the subject bbox
  if ($o.id_label_x + 64 -gt $o.bbox_x0 -and $o.id_label_y + 24 -gt $o.bbox_y0 -and $o.id_label_x -lt $o.bbox_x1 -and $o.id_label_y -lt $o.bbox_y1) {
    $problems.Add("$($o.id) id label overlaps its subject")
  }
  if ($o.size -notin $sizeList) { $problems.Add("$($o.id) size $($o.size) not in 48/64/80") }
}

# ----------------------------------------------------------------- DSL ----------
$L = New-Object System.Collections.Generic.List[string]
$L.Add('<Snapshot type="png" background="' + $BG + '">')
$L.Add('  <Container width="' + $CANVAS + '" height="' + $CANVAS + '" color="' + $BG + '">')
$L.Add('    <Stack>')
$L.Add('      <!--ROWBG-->')
for ($r = 0; $r -lt $N; $r++) {
  if ($r % 2 -eq 1) {
    $L.Add('      <Positioned left="' + $ORIGIN + '" top="' + ($ORIGIN + $CELL * $r) + '" width="' + ($CELL * $N) + '" height="' + $CELL + '">')
    $L.Add('        <Container width="' + ($CELL * $N) + '" height="' + $CELL + '" color="' + $ROWALT + '"/>')
    $L.Add('      </Positioned>')
  }
}
$L.Add('      <!--GRID-->')
# interior + frame lines (2px so they survive downscaling)
for ($i = 1; $i -lt $N; $i++) {
  $x = $ORIGIN + $CELL * $i
  $L.Add('      <Positioned left="' + $x + '" top="' + $ORIGIN + '" width="2" height="' + ($CELL * $N) + '"><Container width="2" height="' + ($CELL * $N) + '" color="' + $LINE + '"/></Positioned>')
  $y = $ORIGIN + $CELL * $i
  $L.Add('      <Positioned left="' + $ORIGIN + '" top="' + $y + '" width="' + ($CELL * $N) + '" height="2"><Container width="' + ($CELL * $N) + '" height="2" color="' + $LINE + '"/></Positioned>')
}
$fw = $CELL * $N
$L.Add('      <Positioned left="' + $ORIGIN + '" top="' + $ORIGIN + '" width="' + $fw + '" height="2"><Container width="' + $fw + '" height="2" color="' + $IDCOL + '"/></Positioned>')
$L.Add('      <Positioned left="' + $ORIGIN + '" top="' + ($ORIGIN + $fw - 2) + '" width="' + $fw + '" height="2"><Container width="' + $fw + '" height="2" color="' + $IDCOL + '"/></Positioned>')
$L.Add('      <Positioned left="' + $ORIGIN + '" top="' + $ORIGIN + '" width="2" height="' + $fw + '"><Container width="2" height="' + $fw + '" color="' + $IDCOL + '"/></Positioned>')
$L.Add('      <Positioned left="' + ($ORIGIN + $fw - 2) + '" top="' + $ORIGIN + '" width="2" height="' + $fw + '"><Container width="2" height="' + $fw + '" color="' + $IDCOL + '"/></Positioned>')
$L.Add('      <!--SUBJECTS-->')
foreach ($o in $objs) {
  $rowBg = $BG; if ($o.row % 2 -eq 1) { $rowBg = $ROWALT }
  $x0 = [double]$o.bbox_x0; $y0 = [double]$o.bbox_y0
  $L.Add('      <Positioned left="' + (F $x0) + '" top="' + (F $y0) + '" width="' + $o.size + '" height="' + $o.size + '">')
  if ($o.shape -eq 'circle' -or $o.shape -eq 'ring') {
    $rad = $o.size / 2
  } elseif ($o.shape -eq 'rounded-square') {
    $rad = $o.size / 4
  } else {
    $rad = 0
  }
  $L.Add('        <Container width="' + $o.size + '" height="' + $o.size + '" color="' + $o.hex + '" borderRadius="' + (F $rad) + '"/>')
  $L.Add('      </Positioned>')
  if ($o.shape -eq 'ring') {
    $in = $o.ring_inner
    $L.Add('      <Positioned left="' + (F ($o.cx - $in / 2)) + '" top="' + (F ($o.cy - $in / 2)) + '" width="' + (F $in) + '" height="' + (F $in) + '">')
    $L.Add('        <Container width="' + (F $in) + '" height="' + (F $in) + '" color="' + $rowBg + '" borderRadius="' + (F ($in / 2)) + '"/>')
    $L.Add('      </Positioned>')
  }
}
$L.Add('      <!--IDS-->')
foreach ($o in $objs) {
  $L.Add('      <Positioned left="' + $o.id_label_x + '" top="' + $o.id_label_y + '" width="64" height="24">')
  $L.Add('        <Text fontSize="16" fontFamily="' + $FONTID + '" color="' + $IDCOL + '">' + $o.id + '</Text>')
  $L.Add('      </Positioned>')
}
$L.Add('    </Stack>')
$L.Add('  </Container>')
$L.Add('</Snapshot>')

[IO.File]::WriteAllText($OutDsl, (($L -join "`r`n") + "`r`n"), $utf8)

# --------------------------------------------------------------- geometry json --
$rowChecks = @(0..7 | ForEach-Object {
    $rr = $_
    $ro = @($objs | Where-Object { $_.row -eq $rr })
    [pscustomobject]@{
      row      = $rr
      colors   = @($ro | ForEach-Object { $_.color } | Sort-Object -Unique)
      shapes   = @($ro | ForEach-Object { $_.shape } | Sort-Object -Unique)
      n_colors = @($ro | ForEach-Object { $_.color } | Sort-Object -Unique).Count
      n_shapes = @($ro | ForEach-Object { $_.shape } | Sort-Object -Unique).Count
    }
  })
$countsObj = [pscustomobject]@{
  by_color = [pscustomobject]@{ blue = $byColor['blue']; orange = $byColor['orange']; green = $byColor['green']; purple = $byColor['purple'] }
  by_shape = [pscustomobject]@{ circle = $byShape['circle']; square = $byShape['square']; ring = $byShape['ring']; 'rounded-square' = $byShape['rounded-square'] }
  by_size  = [pscustomobject]@{ '48' = $bySize[48]; '64' = $bySize[64]; '80' = $bySize[80] }
}
$matrix = [ordered]@{}
foreach ($cn in $colorNames) {
  $rowm = [ordered]@{}
  foreach ($sn in $shapeList) { $rowm[$sn] = 0 }
  $matrix[$cn] = $rowm
}
for ($i = 0; $i -lt 64; $i++) {
  $mc = $colorArr[$i]; $ms = $shapeArr[$i]
  $matrix[$mc][$ms] = 1 + $matrix[$mc][$ms]
}
$notes.Add(("colour x shape crossing: " + (($matrix.GetEnumerator() | ForEach-Object { $_.Name + '[' + (($_.Value.GetEnumerator() | ForEach-Object { $_.Value }) -join '/') + ']' }) -join ' ')))
$notes.Add("shuffles needed - colour $colorTries, shape $shapeTries, pair $pairTries; all 16 colour x shape combinations present = " + ($pairCover -eq 16))
$geom = [ordered]@{
  schema     = 'snapshot-suite/scene-data/v1'
  task       = 'A19'
  kind       = 'grid-scene'
  seed       = $Seed
  seed_note  = 'System.Random(Seed) drives three independent shuffles: the 64-cell colour bag, the 64-cell shape bag and the size bag. A candidate pair of shuffles is accepted only when every row holds >= 3 distinct colours and >= 3 distinct shapes; scene-data.json stores the realised geometry, which is authoritative.'
  canvas     = [pscustomobject]@{ width = $CANVAS; height = $CANVAS }
  origin     = 'top-left (0,0); x grows right, y grows down; unit = pixel'
  grid       = [pscustomobject]@{ rows = $N; cols = $N; frame_x = $ORIGIN; frame_y = $ORIGIN; cell = $CELL; frame_right = $ORIGIN + $CELL * $N; frame_bottom = $ORIGIN + $CELL * $N }
  palettes   = [pscustomobject]@{ colors = $colorHex; shapes = $shapeList; sizes = $sizeList }
  counts     = $countsObj
  assignment = [pscustomobject]@{
    method                  = 'independent Fisher-Yates shuffle of a 64-cell colour bag, a 64-cell shape bag and a size bag, with a seeded System.Random and a rejection test'
    colour_bag              = '16 blue + 16 orange + 16 green + 16 purple'
    shape_bag               = '16 circle + 16 square + 16 ring + 16 rounded-square'
    acceptance_rule         = 'every row has >= 3 distinct colours AND >= 3 distinct shapes; additionally the colour x shape matrix must cover all 16 combinations'
    colour_shuffle_attempts = $colorTries
    shape_shuffle_attempts  = $shapeTries
    pair_attempts           = $pairTries
    colour_x_shape_matrix   = $matrix
  }
  row_checks = $rowChecks
  objects    = $objs.ToArray()
  checks     = [pscustomobject]@{ problems = $problems.ToArray(); notes = $notes.ToArray() }
}
[IO.File]::WriteAllText($OutGeom, (($geom | ConvertTo-Json -Depth 8) + "`n"), $utf8)

if (-not $Quiet) {
  Write-Output ("objects={0}  colours={1}  shapes={2}  sizes=48:{3} 64:{4} 80:{5}" -f $objs.Count, (($byColor.GetEnumerator() | ForEach-Object { "$($_.Name)=$($_.Value)" }) -join ' '), (($byShape.GetEnumerator() | ForEach-Object { "$($_.Name)=$($_.Value)" }) -join ' '), $bySize[48], $bySize[64], $bySize[80])
  foreach ($n in $notes) { Write-Output ("  note: " + $n) }
  Write-Output ("problems = {0}" -f $problems.Count)
  foreach ($p in $problems) { Write-Output ("  PROBLEM: " + $p) }
  Write-Output ("-> {0} ({1} lines), {2}" -f $OutDsl, $L.Count, $OutGeom)
}
