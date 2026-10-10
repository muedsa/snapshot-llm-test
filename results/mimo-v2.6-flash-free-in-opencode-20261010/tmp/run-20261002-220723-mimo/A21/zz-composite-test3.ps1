$rgb = @(91, 79, 232)
$out = @(244, 245, 251)
$a   = 1.0

"A  single element, no commas:"
try { $x = @($rgb[0] * $a + $out[0] * (1 - $a)); "   OK -> " + ($x -join ',') } catch { "   FAILED: " + $_.Exception.Message }

"B  three elements each parenthesised (single line):"
try { $x = @(($rgb[0] * $a + $out[0] * (1 - $a)), ($rgb[1] * $a + $out[1] * (1 - $a)), ($rgb[2] * $a + $out[2] * (1 - $a))); "   OK -> " + ($x -join ',') } catch { "   FAILED: " + $_.Exception.Message }

"C  three elements, multi-line, parenthesised:"
try {
  $x = @(($rgb[0] * $a + $out[0] * (1 - $a)),
          ($rgb[1] * $a + $out[1] * (1 - $a)),
          ($rgb[2] * $a + $out[2] * (1 - $a)))
  "   OK -> " + ($x -join ',')
} catch { "   FAILED: " + $_.Exception.Message }

"D  temps, no nested arithmetic inside @():"
try {
  $t0 = $rgb[0] * $a + $out[0] * (1 - $a)
  $t1 = $rgb[1] * $a + $out[1] * (1 - $a)
  $t2 = $rgb[2] * $a + $out[2] * (1 - $a)
  $x = @($t0, $t1, $t2)
  "   OK -> " + ($x -join ',')
} catch { "   FAILED: " + $_.Exception.Message }

"E  probe: what does '1 * 2, 3' evaluate to?"
try { $p = (1 * 2, 3); "   1 * 2, 3  -> " + ($p -join ' | ') + "  count=" + @($p).Count } catch { "   FAILED: " + $_.Exception.Message }

"F  probe: does ',' bind tighter than '*' inside @()?"
try { $p = @(1 * 2, 3); "   @(1 * 2, 3) -> count=" + @($p).Count + " vals=" + ($p -join ' | ') } catch { "   FAILED: " + $_.Exception.Message }
try { $p = @(1 * (2, 3)); "   @(1 * (2,3)) -> " + ($p -join ' | ') } catch { "   FAILED: " + $_.Exception.Message }
