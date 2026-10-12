function N([double]$v) {
  if ([double]::IsNaN($v)) { return '0' }
  if ($v -eq [Math]::Truncate($v)) { return ([long]$v).ToString([cultureinfo]::InvariantCulture) }
  return $v.ToString('0.##', [cultureinfo]::InvariantCulture)
}
function Hex2Rgb([string]$h) {
  return @([Convert]::ToInt32($h.Substring(0, 2), 16), [Convert]::ToInt32($h.Substring(2, 2), 16), [Convert]::ToInt32($h.Substring(4, 2), 16))
}
function Rgb2Hex($r, $g, $b) { return ('{0:X2}{1:X2}{2:X2}' -f [int][Math]::Round($r), [int][Math]::Round($g), [int][Math]::Round($b)) }

function Composite([string[]]$layers) {
  $out = $null
  foreach ($spec in $layers) {
    $parts = $spec.Split(':')
    $rgb = Hex2Rgb $parts[0]
    Write-Host ("    spec='{0}' parts.Count={1} rgb type={2} count={3} rgb[0] type={4}" -f $spec, $parts.Count, $rgb.GetType().FullName, @($rgb).Count, $rgb[0].GetType().FullName)
    $a = 1.0
    if ($parts.Count -gt 1) { $a = [Convert]::ToInt32($parts[1], 16) / 255.0 }
    Write-Host ("    a type={0} value={1}" -f $a.GetType().FullName, $a)
    if ($null -eq $out) { $out = $rgb }
    else {
      Write-Host ("    out type={0} count={1}" -f $out.GetType().FullName, @($out).Count)
      Write-Host ("    out[0] type={0} val={1}" -f $out[0].GetType().FullName, $out[0])
      Write-Host ("    is out[0] array? {0}" -f ($out[0] -is [array]))
      $out = @($rgb[0] * $a + $out[0] * (1 - $a),
                $rgb[1] * $a + $out[1] * (1 - $a),
                $rgb[2] * $a + $out[2] * (1 - $a))
    }
  }
  return Rgb2Hex $out[0] $out[1] $out[2]
}

Write-Host "--- single layer (what rounds 1 and 2 did) ---"
Write-Host ("  result = " + (Composite @('0E1026')))
Write-Host "--- two layers, second opaque (round-03 band without alpha) ---"
try { Write-Host ("  result = " + (Composite @('F4F5FB', '5B4FE81F'))) } catch { Write-Host ("  FAILED: " + $_.Exception.Message) }
Write-Host "--- two layers, second with :AA (correct form) ---"
try { Write-Host ("  result = " + (Composite @('F4F5FB', '5B4FE8:1F'))) } catch { Write-Host ("  FAILED: " + $_.Exception.Message) }
