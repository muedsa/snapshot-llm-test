$colorHex = [ordered]@{ blue = '#3B82F6'; orange = '#F59E0B'; green = '#22C55E'; purple = '#A855F7' }
$byColor = @{ blue = 16; orange = 16; green = 16; purple = 16 }
$bySize  = @{ 48 = 21; 64 = 21; 80 = 22 }
$shapeList = @('circle','square','ring','rounded-square')
$sizeList  = @(48,64,80)
$N = 8; $ORIGIN = 40; $CELL = 190; $CANVAS = 1600
$problems = New-Object System.Collections.Generic.List[string]
$notes    = New-Object System.Collections.Generic.List[string]
$notes.Add('x')
$objs = New-Object System.Collections.Generic.List[object]
$objs.Add([pscustomobject]@{ row = 0; color='blue'; shape='circle' })
$rowChecks = @([pscustomobject]@{ row = 0; colors=@('blue'); shapes=@('circle'); n_colors=1; n_shapes=1 })

function CheckTry([string]$name, [scriptblock]$b) {
  try { & $b | Out-Null; "OK   $name" } catch { "FAIL $name -> " + $_.Exception.Message }
}

CheckTry 'canvas'      { [pscustomobject]@{ canvas = [pscustomobject]@{ width = $CANVAS; height = $CANVAS } } }
CheckTry 'grid'        { [pscustomobject]@{ grid = [pscustomobject]@{ rows = $N; cols = $N; frame_x = $ORIGIN; frame_y = $ORIGIN; cell = $CELL; frame_right = $ORIGIN + $CELL * $N; frame_bottom = $ORIGIN + $CELL * $N } } }
CheckTry 'palettes'    { [pscustomobject]@{ palettes = [pscustomobject]@{ colors = $colorHex; shapes = $shapeList; sizes = $sizeList } } }
CheckTry 'counts'      { [pscustomobject]@{ counts = [pscustomobject]@{ by_color = $byColor; by_shape = $byColor; by_size = $bySize } } }
CheckTry 'rowchecks'   { [pscustomobject]@{ row_checks = $rowChecks } }
CheckTry 'objects'     { [pscustomobject]@{ objects = @($objs) } }
CheckTry 'checks'      { [pscustomobject]@{ checks = [pscustomobject]@{ problems = @($problems); notes = @($notes) } } }

$geom = [ordered]@{
  schema = 'x'
  palettes = [pscustomobject]@{ colors = $colorHex; shapes = $shapeList; sizes = $sizeList }
  counts   = [pscustomobject]@{ by_color = $byColor; by_shape = $byColor; by_size = $bySize }
}
CheckTry 'ordered+json' { $geom | ConvertTo-Json -Depth 8 }
$geom2 = [ordered]@{ palettes = [pscustomobject]@{ colors = $colorHex } }
CheckTry 'orderedcolor+json' { $geom2 | ConvertTo-Json -Depth 8 }
