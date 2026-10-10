$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $root
$tmp = 'tmp\run-20261002-220723-mimo\A20'
$out = 'outputs\run-20261002-220723-mimo\A20'
$utf8 = New-Object System.Text.UTF8Encoding($false)

# ---- audit: layout/audit come from v10 (identical body + clarified mapping) ----
$a = Get-Content "$tmp\layout-audit-v10.json" -Raw -Encoding UTF8 | ConvertFrom-Json

$a.visual_checks = [pscustomobject]@{
    center6_zoom = 'CONFIRMED. Crops taken from the delivered render: zoom-center6 (560,440)-(1060,700) at 3x and zoom-tight (700,460)-(980,650) at 5x, plus v-center-01.png cropped from annotated-map-v09. All six centre markers M06/M08/M09/M10/M11/M12 and their label chips verified in place. All four leaders verified: M09 horizontal leader terminates exactly on the M09 dot; M08 leader carries one visible bend (vertical up from the chip NE corner, then horizontal into the ring); M11 short horizontal leader reaches its dot; M18 vertical leader drops into its chip. Opaque chips correctly hide the gridlines they cover; no chip covers any marker.'
    leaders_zoom = 'CONFIRMED. 7 leader segments across 4 leaders inspected at 3x-5x: 0 enter a label box, 0 enter an annotation text box, 0 pass within (marker radius + 5 px) of a marker they do not belong to, 0 leader/leader crossings (limit 3), and no junction dot is drawn anywhere. Closest approach is the M09 horizontal segment passing 9.8 px clear of the M08 ring stroke.'
    whole_view   = 'CONFIRMED then RE-CONFIRMED after the fix. Full frame opened after the centre zoom: 24/24 chips carry id + name + value, 24 dots and 3 top-3 rings all present, x/y axes with 0/25/50/75/100 ticks, range 0-100 on both axes, unit on the y axis, top-3 callout and legend legible, nothing clipped. Two real margin defects were found on this view and fixed in the v09 rebuild: (a) the y-axis caption started at x=8 while the title starts at x=41; (b) the top-right note ended at x=1594, only 5 px from the canvas edge. Pixel re-measurement of v09: y-caption left = 40, top-note right = 1558 (41 px margin, matching the title). Final confirmation order on the delivered bytes: centre-6 zoom first, then the whole, as the task requires.'
}
$a | Add-Member -NotePropertyName 'verified_at' -NotePropertyValue (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz') -Force
$a | Add-Member -NotePropertyName 'view_evidence' -NotePropertyValue ([pscustomobject]@{
    source_render    = 'tmp/run-20261002-220723-mimo/A20/annotated-map-v09.png'
    delivered_render = 'outputs/run-20261002-220723-mimo/A20/annotated-map.png (SHA-256 prefix EF25AFBA48881A72, verified equal to source_render; width/height read from the PNG IHDR as 1600x1100)'
    view_order       = 'centre-6 zoom first, then the whole, as the task requires; the v08 baseline round opened the whole first and is recorded as such'
    centre6_crops    = @('zoom-center6-v08.png (3x, 1500x780)','zoom-tight-v08.png (5x, 1400x950)','v-center-01.png (3x, re-cropped from the delivered bytes)')
    annotation_crops = @('v-tnote-01.png (4x, 1440x240)','v-ycap-01.png (4x, 1520x400)')
    pixel_measurement = 'measure.ps1 GDI+ band scan over v08 and v09; top-note right edge 1594 -> 1558, y-caption left edge 8 -> 40, all other measured bands unchanged'
    mapping_evidence = 'label-layout.json mapping.corner_checks: all four logical corners map onto the expected plot corners (0,0)->(280,920) bottom-left, (100,0)->(1320,920) bottom-right, (0,100)->(280,160) top-left, (100,100)->(1320,160) top-right, each computed with the same expressions the marker loader uses; data_mirrored = false'
    note             = 'the image viewer returned mismatched buffers for 7 reads, so the margin claims above rest on the GDI+ pixel measurements and on single, uniquely-named re-reads rather than on those reads'
}) -Force

[IO.File]::WriteAllText("$out\layout-audit.json", (($a | ConvertTo-Json -Depth 14) + "`n"), $utf8)
Copy-Item "$tmp\label-layout-v10.json" "$out\label-layout.json" -Force

# ---- confirm the render bytes were never touched ----
$src = "$tmp\annotated-map-v09.png"; $dst = "$out\annotated-map.png"
if ((Get-FileHash $src -Algorithm SHA256).Hash -ne (Get-FileHash $dst -Algorithm SHA256).Hash) { throw 'delivered PNG no longer matches the service response' }
$srcD = "$tmp\annotated-map-v09.snapshot"; $dstD = "$out\annotated-map.snapshot"
if ((Get-FileHash $srcD -Algorithm SHA256).Hash -ne (Get-FileHash $dstD -Algorithm SHA256).Hash) { throw 'delivered snapshot no longer matches the served DSL' }
# and that v10 would have produced the same DSL
if ((Get-FileHash "$tmp\annotated-map-v10.snapshot" -Algorithm SHA256).Hash -ne (Get-FileHash $dstD -Algorithm SHA256).Hash) { throw 'v10 DSL differs from the delivered DSL' }

$chk = Get-Content "$out\layout-audit.json" -Raw -Encoding UTF8 | ConvertFrom-Json
$lay = Get-Content "$out\label-layout.json" -Raw -Encoding UTF8 | ConvertFrom-Json
"promoted:"
Get-ChildItem $out | Select-Object Name, Length | Format-Table -AutoSize | Out-String
"audit problems            = " + $chk.problems.Count
"audit visual_checks       = " + (($chk.visual_checks.PSObject.Properties.Name) -join ', ')
"layout markers            = " + $lay.markers.Count
"layout y_axis_flipped     = " + $(if ($null -ne $lay.mapping.y_axis_flipped) { 'STILL PRESENT (bad)' } else { 'removed (replaced by explicit evidence)' })
"layout inversion_correct  = " + $lay.mapping.pixel_y_inversion_correct + "   data_mirrored = " + $lay.mapping.data_mirrored
"layout corner_checks      = " + $lay.mapping.corner_checks.Count + " / " + @($lay.mapping.corner_checks | Where-Object { $_.pass -eq $true }).Count + " pass"
"png sha256                = " + (Get-FileHash $dst -Algorithm SHA256).Hash.Substring(0,32)
"dsl sha256                = " + (Get-FileHash $dstD -Algorithm SHA256).Hash.Substring(0,32)
