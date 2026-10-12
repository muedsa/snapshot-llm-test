$rgb = @(91, 79, 232)
$out = @(244, 245, 251)
$a   = 1.0
"types: rgb=" + $rgb.GetType().FullName + " out=" + $out.GetType().FullName + " a=" + $a.GetType().FullName
"rgb[1] type=" + $rgb[1].GetType().FullName + "  out[1] type=" + $out[1].GetType().FullName
try {
  $x = @($rgb[0] * $a + $out[0] * (1 - $a),
          $rgb[1] * $a + $out[1] * (1 - $a),
          $rgb[2] * $a + $out[2] * (1 - $a))
  "whole statement OK -> " + ($x -join ',')
} catch { "whole statement FAILED: " + $_.Exception.Message }

foreach ($i in 0, 1, 2) {
  try { $t = $rgb[$i] * $a; "term $i rgb*a OK  = $t" } catch { "term $i rgb*a FAILED: " + $_.Exception.Message }
  try { $u = $out[$i] * (1 - $a); "term $i out*(1-a) OK = $u" } catch { "term $i out*(1-a) FAILED: " + $_.Exception.Message }
}
