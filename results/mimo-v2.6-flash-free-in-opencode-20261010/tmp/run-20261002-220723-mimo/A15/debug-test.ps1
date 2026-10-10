$m = [ordered]@{}
$m['a'] = 1
$m['b'] = 2
$o = [pscustomobject]$m
if ($null -eq $o) { Write-Output 'cast: null' } else { Write-Output ('cast: ' + $o.GetType().FullName + ' json=' + ($o | ConvertTo-Json -Compress)) }

function T($x) {
  $z = [ordered]@{}
  $z['k'] = 'v'
  return [pscustomobject]$z
}
$r = T 5
if ($null -eq $r) { Write-Output 'fn: null' } else { Write-Output ('fn: json=' + ($r | ConvertTo-Json -Compress)) }
