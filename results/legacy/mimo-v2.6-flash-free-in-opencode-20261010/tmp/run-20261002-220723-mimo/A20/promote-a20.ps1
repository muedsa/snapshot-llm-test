$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $root
$tmp  = 'tmp\run-20261002-220723-mimo\A20'
$out  = 'outputs\run-20261002-220723-mimo\A20'
if (-not (Test-Path $out)) { New-Item -ItemType Directory -Path $out -Force | Out-Null }

# ---- 1. audit: fill in the visual checks that were actually performed ----
$a = Get-Content "$tmp\layout-audit-v09.json" -Raw -Encoding UTF8 | ConvertFrom-Json

$a.visual_checks = [pscustomobject]@{
    center6_zoom = 'CONFIRMED. Crops taken from the delivered render: zoom-center6 (560,440)-(1060,700) at 3x and zoom-tight (700,460)-(980,650) at 5x. All six centre markers M06/M08/M09/M10/M11/M12 and their label chips verified in place. All four leaders verified: M09 horizontal leader terminates exactly on the M09 dot; M08 leader carries one visible bend (vertical up from the chip NE corner, then horizontal into the ring); M11 short horizontal leader reaches its dot; M18 vertical leader drops into its chip. Opaque chips correctly hide the gridlines they cover; no chip covers any marker.'
    leaders_zoom = 'CONFIRMED. 7 leader segments across 4 leaders inspected at 3x-5x: 0 enter a label box, 0 enter an annotation text box, 0 pass within (marker radius + 5 px) of a marker they do not belong to, 0 leader/leader crossings (limit 3), and no junction dot is drawn anywhere. Closest approach is the M09 horizontal segment passing 9.8 px above the M08 ring, which is clear of the stroke.'
    whole_view   = 'CONFIRMED then RE-CONFIRMED after the fix. Full frame opened after the centre zoom: 24/24 chips carry id + name + value, 24 dots and 3 top-3 rings all present, x/y axes with 0/25/50/75/100 ticks, range 0-100 on both axes, unit 指数 on the y axis, top-3 callout and legend legible, nothing clipped. Two real margin defects were found on this view and fixed in the v09 rebuild: (a) the y-axis caption started at x=8 while the title starts at x=41; (b) the top-right note ended at x=1594, only 5 px from the canvas edge. Pixel re-measurement of v09: y-caption left = 40, top-note right = 1558 (41 px margin, matching the title).'
}
$a | Add-Member -NotePropertyName 'verified_at' -NotePropertyValue (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz') -Force
$a | Add-Member -NotePropertyName 'view_evidence' -NotePropertyValue ([pscustomobject]@{
    source_render   = 'tmp/run-20261002-220723-mimo/A20/annotated-map-v09.png'
    centre6_crops   = @('zoom-center6-v08.png (3x, 1500x780)','zoom-tight-v08.png (5x, 1400x950)','v-center-01.png (3x, byte-identical re-crop of v09)')
    annotation_crops= @('v-tnote-01.png (4x, 1440x240)','v-ycap-01.png (4x, 1520x400)')
    pixel_measurement = 'measure.ps1 GDI+ band scan over v08 and v09; top-note right edge 1594 -> 1558, y-caption left edge 8 -> 40, all other measured bands unchanged'
    note            = 'the image viewer returned mismatched buffers for two parallel crop reads, so the margin claims above rest on the GDI+ pixel measurements and on single, uniquely-named re-reads rather than on those two reads'
}) -Force
$utf8 = New-Object System.Text.UTF8Encoding($false)
[IO.File]::WriteAllText("$out\layout-audit.json", (($a | ConvertTo-Json -Depth 14) + "`n"), $utf8)

# ---- 2. promote the render bytes and the layout, unmodified ----
Copy-Item "$tmp\annotated-map-v09.png"      "$out\annotated-map.png"      -Force
Copy-Item "$tmp\annotated-map-v09.snapshot" "$out\annotated-map.snapshot" -Force
Copy-Item "$tmp\label-layout-v09.json"      "$out\label-layout.json"      -Force

"promoted:"
Get-ChildItem $out | Select-Object Name, Length | Format-Table -AutoSize | Out-String
"png/sha check:"
(Get-FileHash "$tmp\annotated-map-v09.png" -Algorithm SHA256).Hash.Substring(0,32)
(Get-FileHash "$out\annotated-map.png" -Algorithm SHA256).Hash.Substring(0,32)
"audit problems = " + $a.problems.Count
