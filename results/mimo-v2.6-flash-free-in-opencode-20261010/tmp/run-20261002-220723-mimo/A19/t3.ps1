$objs = New-Object System.Collections.Generic.List[object]
$objs.Add([pscustomobject]@{ a = 1 })
function T1 { $objs2 = $args[0]; try { $r = @($objs2); "A ok type=" + $r.GetType().Name + " len=" + $r.Count } catch { "A FAIL " + $_.Exception.Message } }
T1 $objs

$list = New-Object System.Collections.Generic.List[object]
$list.Add([pscustomobject]@{ a = 1 })
try { $x = [pscustomobject]@{ objects = @($list) }; "B ok " + ($x | ConvertTo-Json -Compress) } catch { "B FAIL " + $_.Exception.Message }
try { $y = @($list); "C ok " + $y.GetType().Name + " " + $y.Count } catch { "C FAIL " + $_.Exception.Message }
try { $z = [pscustomobject]@{ objects = @($list.ToArray()) }; "D ok " + ($z | ConvertTo-Json -Compress) } catch { "D FAIL " + $_.Exception.Message }
try { $w = @(); foreach ($e in $list) { $w += $e }; $v = [pscustomobject]@{ objects = $w }; "E ok " + ($v | ConvertTo-Json -Compress) } catch { "E FAIL " + $_.Exception.Message }
