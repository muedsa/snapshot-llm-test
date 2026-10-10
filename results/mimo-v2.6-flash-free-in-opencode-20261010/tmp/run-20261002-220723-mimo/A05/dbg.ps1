$PX0 = 124.0; $PX1 = 1372.0; $PW = $PX1 - $PX0
$PH  = 124.0
$SPAN = 270.0
$scale = $PW / $SPAN
"PX0=$PX0 PW=$PW SPAN=$SPAN scale=$scale"
function X([double]$t) { $script:PX0 + ($t / $script:SPAN) * $script:scale }
"X(0)=" + (X 0) + "  X(100)=" + (X 100) + "  X(270)=" + (X 270)

# now the real scenario: values inside a here-imported script scope
$offs = @(0,10,35,60,75,100,130,170,180,220,250,270)
foreach ($o in $offs) { "off=$o -> X=" + (X $o) }
"script:scale=" + [string]$script:scale
"script:SPAN=" + [string]$script:SPAN
