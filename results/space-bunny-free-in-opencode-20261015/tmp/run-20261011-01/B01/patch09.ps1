$f='tmp/run-20261011-01/B01/cases_b01_b.py'
$c = Get-Content $f -Encoding UTF8 -Raw
$c = $c.Replace("r * 1.15)", "r * 1.00)")
$c = $c.Replace("(36, 430, ", "(36, 441, ").Replace("(48, 426, ", "(48, 438, ")
$c = $c.Replace("(12, 444, ", "(12, 448, ").Replace("(24, 436, ", "(24, 444, ")
$c = $c.Replace("(60, 434, ", "(60, 443, ").Replace("(72, 446, ", "(72, 449, ")
$c = $c.Replace("rect(hx(hr), 300, 1, 250,", "rect(hx(hr), 336, 1, 206,")
$c = $c.Replace("hx(hr) - 40, 272, 80, None, 19, DIM,", "hx(hr) - 40, 548, 80, None, 19, DIM,")
$c = $c.Replace("PY, PITCH = 566, 44", "PY, PITCH = 600, 42")
$c = $c.Replace("footer(b, 72, H - 46, W - 144,`r`n           `"数据为自拟示例；路径带取集合预报", "footer(b, 72, H - 40, W - 144,`r`n           `"数据为自拟示例；路径带取集合预报")
Set-Content $f $c -Encoding UTF8
python tmp/run-20261011-01/B01/build_b01.py 9 v1
foreach ($k=1; $k -le 3; $k++) {
  $r = python tmp/run-20261011-01/_suite/scripts/snapshot_render.py --task B01 --version "case-09-f$k" --dsl "tmp/run-20261011-01/B01/drafts/case-09-v1.snapshot" --out "tmp/run-20261011-01/B01/preview/case-09.png" --log tmp/run-20261011-01/B01/requests.jsonl --responses-dir tmp/run-20261011-01/B01/responses
  if ($r -match '"ok": true') { Write-Host OK; break } else { Start-Sleep -Seconds 4 }
}