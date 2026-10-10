param(
  [Parameter(Mandatory=$true)][string]$GeomPath,
  [Parameter(Mandatory=$true)][string]$DslPath,
  [Parameter(Mandatory=$true)][string]$OutPath
)
$ErrorActionPreference = 'Stop'
[Threading.Thread]::CurrentThread.CurrentCulture   = [cultureinfo]::InvariantCulture
[Threading.Thread]::CurrentThread.CurrentUICulture = [cultureinfo]::InvariantCulture
$utf8 = New-Object System.Text.UTF8Encoding($false)

$g   = Get-Content $GeomPath -Raw | ConvertFrom-Json
$dsl = [IO.File]::ReadAllText($DslPath)

$problems = New-Object System.Collections.Generic.List[string]
$notes    = New-Object System.Collections.Generic.List[string]

$UNIT_D = 36; $NODE_S = 64
$CORNER = 14 * [Math]::Sqrt(2) + 18       # rounded-square reach = 37.8

$acts = @()
foreach ($act in $g.acts) {
  $ai    = [int]$act.act
  $panel = $g.panels | Where-Object { $_.act -eq $ai }
  $units = @($act.units)
  $nodes = @($act.nodes)

  # ---- inventory -----------------------------------------------------------
  $byColor = @{ blue = 0; orange = 0; gray = 0 }
  foreach ($u in $units) { $byColor[[string]$u.color] = 1 + $byColor[[string]$u.color] }
  $blue = [int]$byColor['blue']; $orange = [int]$byColor['orange']; $gray = [int]$byColor['gray']
  if ($units.Count -ne 15) { $problems.Add("act ${ai}: $($units.Count) units, expected 15") }
  if ($blue -ne 5 -or $orange -ne 5 -or $gray -ne 5) {
    $problems.Add("act ${ai}: colour counts blue=$blue orange=$orange gray=$gray, expected 5/5/5")
  }

  # ---- no unit-unit overlap ------------------------------------------------
  $minPair = [double]::MaxValue
  for ($i = 0; $i -lt $units.Count; $i++) {
    for ($j = $i + 1; $j -lt $units.Count; $j++) {
      $dx = [double]$units[$i].x - [double]$units[$j].x
      $dy = [double]$units[$i].y - [double]$units[$j].y
      $d  = [Math]::Sqrt($dx*$dx + $dy*$dy)
      if ($d -lt $minPair) { $minPair = $d }
    }
  }
  if ($minPair -lt 36.0) { $problems.Add("act ${ai}: units overlap, min centre distance $([Math]::Round($minPair,2)) < 36") }

  # ---- no unit-node overlap, fully inside panel ----------------------------
  $minGap = [double]::MaxValue
  foreach ($u in $units) {
    foreach ($n in $nodes) {
      $dx  = [double]$u.x - [double]$n.x
      $dy  = [double]$u.y - [double]$n.y
      $gap = [Math]::Sqrt($dx*$dx + $dy*$dy) - ($UNIT_D/2) - $CORNER
      if ($gap -lt $minGap) { $minGap = $gap }
    }
    $lx = [double]$u.x - [double]$panel.x
    $ly = [double]$u.y - [double]$panel.y
    if ($lx - 18 -lt 0 -or $lx + 18 -gt [double]$panel.width -or $ly - 18 -lt 0 -or $ly + 18 -gt [double]$panel.height) {
      $problems.Add("act ${ai}: unit $($u.id) not fully inside its panel")
    }
  }
  if ($minGap -lt -0.4) { $problems.Add("act ${ai}: a unit overlaps a node by $([Math]::Round(-$minGap,2)) px") }

  # ---- three equal geometric nodes ----------------------------------------
  if ($nodes.Count -ne 3) { $problems.Add("act ${ai}: $($nodes.Count) nodes, expected 3") }
  foreach ($n in $nodes) {
    if ([int]$n.size -ne $NODE_S) { $problems.Add("act ${ai}: node $($n.id) size $($n.size), expected 64") }
  }

  # ---- receiving node per unit --------------------------------------------
  $recv = @{ N1 = @(); N2 = @(); N3 = @() }
  foreach ($u in $units) {
    $k = [string]$u.receiving_node
    if ($recv.ContainsKey($k)) { $recv[$k] = @($recv[$k]) + @([string]$u.id) }
    else { $problems.Add("act ${ai}: unit $($u.id) targets unknown node '$k'") }
  }
  $recvRows = @()
  foreach ($k in @('N1','N2','N3')) {
    $ids  = @($recv[$k])
    $cols = @()
    foreach ($id in $ids) {
      $uu = $units | Where-Object { $_.id -eq $id }
      if ($cols -notcontains [string]$uu.color) { $cols += [string]$uu.color }
    }
    $recvRows += [pscustomobject]@{ node = $k; unit_count = $ids.Count; color_kinds = $cols.Count; colors = $cols; units = $ids }
    if ($ai -eq 3) {
      if ($ids.Count -ne 5) { $problems.Add("act 3: node $k receives $($ids.Count) units, expected 5") }
      if ($cols.Count -lt 2) { $problems.Add("act 3: node $k carries $($cols.Count) colour, expected >= 2") }
    } else {
      if ($k -eq 'N2') { if ($ids.Count -ne 15) { $problems.Add("act ${ai}: centre node receives $($ids.Count), expected 15") } }
      else             { if ($ids.Count -ne 0)  { $problems.Add("act ${ai}: idle node $k receives $($ids.Count), expected 0") } }
    }
  }

  $arrowNote = "chevron on the node end of every link"
  if ($ai -eq 2) { $arrowNote = "omitted by construction: at minimum spacing there is no room between unit edge and node edge" }

  $acts += [pscustomobject]@{
    act            = $ai
    act_name       = [string]$act.name
    hero_node      = [string]$act.hero
    panel          = [pscustomobject]@{ x = $panel.x; y = $panel.y; width = $panel.width; height = $panel.height }
    unit_diameter  = $UNIT_D
    node_size      = $NODE_S
    unit_counts    = [pscustomobject]@{ blue = $blue; orange = $orange; gray = $gray; total = $units.Count }
    min_unit_to_unit_centre_distance = [Math]::Round($minPair,2)
    min_unit_to_node_gap_px          = [Math]::Round($minGap,2)
    nodes          = @($nodes)
    units          = @($units | ForEach-Object {
      [pscustomobject]@{
        id             = [string]$_.id
        color          = [string]$_.color
        hex            = [string]$_.hex
        x              = [double]$_.x
        y              = [double]$_.y
        receiving_node = [string]$_.receiving_node
      }
    })
    receiving      = $recvRows
    link_count     = [int]$act.link_count
    arrowheads     = [bool]$act.arrowed
    arrow_note     = $arrowNote
  }
}

# ---- text inventory: title + three act names only ---------------------------
$textMatches = [regex]::Matches($dsl, '<Text\b[^>]*>([^<]*)</Text>')
$texts = @()
foreach ($m in $textMatches) { $texts += $m.Groups[1].Value }
if ($texts.Count -ne 4) { $problems.Add("DSL carries $($texts.Count) <Text> elements, expected 4 (title + 3 act names)") }

# ---- z-order: every stroke must precede every node and every unit -----------
$lastStroke = $dsl.LastIndexOf('<Transform')
$firstNode  = $dsl.IndexOf('width="64" height="64"')
$firstUnit  = $dsl.IndexOf('width="36" height="36"')
if ($lastStroke -lt 0 -or $firstNode -lt 0 -or $firstUnit -lt 0) {
  $problems.Add("could not locate draw-order markers (stroke=$lastStroke node=$firstNode unit=$firstUnit)")
} elseif (-not ($lastStroke -lt $firstNode -and $firstNode -lt $firstUnit)) {
  $problems.Add("draw order wrong: strokes=$lastStroke nodes=$firstNode units=$firstUnit")
}
if ($textMatches.Count -gt 0) {
  $firstText = $dsl.IndexOf('<Text')
  if ($firstText -lt $firstUnit) { $problems.Add("text is emitted before the units and could be covered") }
}

$notes.Add("links and chevrons are emitted before nodes, and nodes before units, so no stroke can paint over a circle")
$notes.Add("acts 1 and 2 route all 15 units to the single centre node N2 and leave N1/N3 idle; act 3 routes exactly 5 units to each node")
$notes.Add("the receiver of every unit is carried by its link and by its position, never by its colour")

$audit = [ordered]@{
  schema             = 'snapshot-suite/story-audit/v1'
  task               = 'A18'
  source_dsl         = ($DslPath -replace '\\','/')
  variant_chosen     = 'A'
  variant_choice     = 'horizontal three-band storyboard: nodes laid out in a row, narrative read top to bottom'
  variants_previewed = @('A','B')
  canvas             = $g.canvas
  text_elements      = $texts
  text_rule          = 'total title plus three act names only; no text on any node or unit'
  relation_rule      = 'distance, links, composition, direction and limited node deformation; never colour alone'
  draw_order         = [pscustomobject]@{ links = 'first'; chevrons = 'second'; nodes = 'third'; units = 'fourth'; text = 'last' }
  acts               = $acts
  checks             = [pscustomobject]@{ problems = @($problems); notes = @($notes) }
}
[IO.File]::WriteAllText($OutPath, (($audit | ConvertTo-Json -Depth 9) + "`n"), $utf8)

Write-Output ("problems = {0}   notes = {1}   text elements = {2}" -f $problems.Count, $notes.Count, $texts.Count)
foreach ($p in $problems) { Write-Output "  PROBLEM: $p" }
foreach ($t in $texts)    { Write-Output "  text: $t" }
